#!/usr/bin/env python3
"""
pc_app.py

Milestone 1: PC <-> Arduino serial handshake + pin configuration UI
Milestone 2: SerialLink.xfer() exercises the Arduino's bit-banged SPI
             primitives generically (used here to preview Milestone 3:
             reading the JEDEC ID, as an end-to-end sanity check).

Requires: pip install pyserial

Run:
    python pc_app.py
"""

import hashlib
import json
import random
import time
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import serial
import serial.tools.list_ports

BAUD_RATE = 115200
SERIAL_TIMEOUT = 5.0  # seconds - bumped from 2.0s to give large READ chunks room
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "pinmap.json")

DEFAULT_CHUNK_SIZE = 2048   # bytes per READ request (tunable, see Milestone 4 notes)
DEFAULT_FLASH_SIZE = 1024 * 1024  # 1MB, matches P25D80SH (JEDEC capacity 0x14)
MAX_CHUNK_RETRIES = 3       # re-request a chunk this many times on checksum mismatch

# Standard SPI NOR flash commands (Puya P25D80SH follows the common
# Winbond/GD-style opcode set).
CMD_WRITE_ENABLE = 0x06
CMD_READ_STATUS = 0x05
CMD_SECTOR_ERASE = 0x20   # 4KB granularity
CMD_CHIP_ERASE = 0xC7
CMD_PAGE_PROGRAM = 0x02

STATUS_WIP_BIT = 0x01     # write-in-progress / busy bit in status register
STATUS_WEL_BIT = 0x02     # write enable latch (should read 1 right after WREN)
STATUS_BP_MASK = 0x1C     # BP0-BP2, block-protect bits (bits 2-4) - common
                          # factory default on many SPI NOR chips is to
                          # ship with some/all sectors write-protected,
                          # often the top of the address range
PAGE_SIZE = 256           # program operations must not cross a page boundary
SECTOR_SIZE = 4096

# Defaults match the published wiring guide:
# 13=MISO, 12=CS, 11=SCLK, 10=MOSI
DEFAULT_PINS = {"cs": 12, "sclk": 11, "mosi": 10, "miso": 13}


class SerialLink:
    """Thin wrapper around the line-based Arduino protocol."""

    def __init__(self):
        self.ser = None

    def connect(self, port):
        self.ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
        # Many Arduino boards reset on port open; give the bootloader
        # a moment before we start talking.
        import time
        time.sleep(2.0)
        self.ser.reset_input_buffer()

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def _send_line(self, line):
        self.ser.write((line + "\n").encode("ascii"))

    def _read_line(self):
        raw = self.ser.readline()
        if not raw:
            raise TimeoutError("No response from Arduino (timeout)")
        return raw.decode("ascii", errors="replace").strip()

    def ping(self):
        self._send_line("PING")
        resp = self._read_line()
        if resp != "PONG":
            raise RuntimeError(f"Unexpected PING response: {resp!r}")
        return True

    def send_config(self, cs, sclk, mosi, miso):
        self._send_line(f"CONFIG,{cs},{sclk},{mosi},{miso}")
        resp = self._read_line()
        if resp != "CONFIG_OK":
            raise RuntimeError(f"Config rejected: {resp}")
        return True

    def xfer(self, out_bytes: bytes) -> bytes:
        """Send bytes over SPI (CS asserted for the whole transfer),
        return the bytes clocked in during the same transfer."""
        hex_out = out_bytes.hex().upper()
        self._send_line(f"XFER,{hex_out}")
        resp = self._read_line()
        if not resp.startswith("XFER_OK:"):
            raise RuntimeError(f"XFER failed: {resp}")
        hex_in = resp[len("XFER_OK:"):]
        return bytes.fromhex(hex_in)

    def read_jedec_id(self) -> bytes:
        """0x9F + 3 dummy bytes -> manufacturer ID, memory type, capacity.
        Early preview of Milestone 3; useful here as an end-to-end test
        that CONFIG + XFER actually reach real flash-chip silicon."""
        resp = self.xfer(bytes([0x9F, 0x00, 0x00, 0x00]))
        return resp[1:]  # first byte echoed during command byte is junk

    def read_chunk(self, addr: int, length: int) -> bytes:
        """One or more READ,<addr>,<len> round trips. Verifies the
        firmware's rotate-XOR checksum against the received bytes and
        retries the chunk (up to MAX_CHUNK_RETRIES times) on mismatch,
        since a single garbled chunk shouldn't force restarting the
        whole dump."""
        last_error = None
        for attempt in range(1, MAX_CHUNK_RETRIES + 1):
            try:
                return self._read_chunk_once(addr, length)
            except ChecksumError as e:
                last_error = e
        raise RuntimeError(
            f"Chunk at 0x{addr:06X} failed checksum {MAX_CHUNK_RETRIES} times: {last_error}"
        )

    def _read_chunk_once(self, addr: int, length: int) -> bytes:
        self._send_line(f"READ,{addr:06X},{length}")
        resp = self._read_line()
        if not resp.startswith("READ_OK:"):
            raise RuntimeError(f"READ failed at addr 0x{addr:06X}: {resp}")

        payload = resp[len("READ_OK:"):]
        hex_data, _, hex_checksum = payload.rpartition(",")
        if not hex_data or not hex_checksum:
            raise RuntimeError(f"Malformed READ_OK response at 0x{addr:06X}: {resp!r}")

        data = bytes.fromhex(hex_data)
        if len(data) != length:
            raise RuntimeError(
                f"Short read at addr 0x{addr:06X}: expected {length} bytes, got {len(data)}"
            )

        expected_checksum = int(hex_checksum, 16)
        actual_checksum = rotate_xor_checksum(data)
        if actual_checksum != expected_checksum:
            raise ChecksumError(
                f"Checksum mismatch at 0x{addr:06X}: "
                f"device={expected_checksum:04X} computed={actual_checksum:04X}"
            )
        return data

    def dump_flash(self, total_len, chunk_size=DEFAULT_CHUNK_SIZE, progress_cb=None) -> bytes:
        """Reads the full chip in chunk_size pieces. progress_cb(bytes_done,
        total_len) is called after each chunk if provided, so the GUI can
        drive a progress bar without blocking on the whole transfer."""
        data = bytearray()
        addr = 0
        while addr < total_len:
            n = min(chunk_size, total_len - addr)
            data += self.read_chunk(addr, n)
            addr += n
            if progress_cb:
                progress_cb(addr, total_len)
        return bytes(data)

    # ---------- Milestone 6: write-enable + status polling ----------
    # All of this rides on the existing generic xfer() primitive - no
    # new firmware commands were needed for these, only the MAX_XFER_BYTES
    # bump (to fit a full page program payload, see Milestone 6b below).

    def write_enable(self):
        """Must precede every single program/erase operation - the WEL
        (write enable latch) bit auto-clears after each write cycle, so
        there's no 'enable once' shortcut."""
        self.xfer(bytes([CMD_WRITE_ENABLE]))

    def read_status(self) -> int:
        # First response byte is junk clocked out during the command byte;
        # the second is the actual status register value.
        resp = self.xfer(bytes([CMD_READ_STATUS, 0x00]))
        return resp[1]

    def wait_ready(self, timeout=5.0, poll_interval=0.01):
        """Polls the status register's busy/WIP bit until it clears.
        Each poll is a full serial round trip, so poll_interval mostly
        just caps how hard we hammer the link during long erases -
        it doesn't meaningfully add to total wait time versus the
        chip's own busy duration."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            status = self.read_status()
            if not (status & STATUS_WIP_BIT):
                return
            time.sleep(poll_interval)
        raise TimeoutError(f"Flash busy longer than {timeout}s timeout - status stuck at 0x{status:02X}")

    def write_status_register(self, value: int, timeout=5.0):
        """WRSR (0x01) - used here to clear block-protect bits (BP0-2)
        that many chips ship with enabled by default, protecting some
        address range (often the top of the chip) from erase/program.
        This is a whole-chip setting, not scoped to one region."""
        self.write_enable()
        self.xfer(bytes([0x01, value & 0xFF]))
        self.wait_ready(timeout=timeout)

    # ---------- Milestone 6a: erase primitives ----------

    def erase_sector(self, addr, timeout=5.0):
        """Erases the 4KB sector containing addr, setting it to 0xFF.
        Required before programming any bytes in that sector - NOR
        flash can only flip bits 1->0 on program, never 0->1."""
        self.write_enable()
        self.xfer(bytes([CMD_SECTOR_ERASE, (addr >> 16) & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF]))
        self.wait_ready(timeout=timeout)

    def erase_chip(self, timeout=30.0):
        """Erases the entire chip. Slow (can take several seconds to
        tens of seconds depending on chip) - default timeout reflects
        that, not a bug in wait_ready."""
        self.write_enable()
        self.xfer(bytes([CMD_CHIP_ERASE]))
        self.wait_ready(timeout=timeout)

    # ---------- Milestone 6b: page program ----------

    def program_page(self, addr, data: bytes, timeout=5.0):
        """Programs up to PAGE_SIZE (256) bytes starting at addr. Caller
        is responsible for the target region already being erased
        (0xFF) and for not crossing a page boundary - the chip silently
        wraps within the page instead of erroring, which corrupts data
        without any protocol-visible failure."""
        if len(data) == 0 or len(data) > PAGE_SIZE:
            raise ValueError(f"program_page: data length must be 1-{PAGE_SIZE} bytes, got {len(data)}")
        if (addr // PAGE_SIZE) != ((addr + len(data) - 1) // PAGE_SIZE):
            raise ValueError(
                f"program_page: write at 0x{addr:06X} length {len(data)} crosses a page boundary"
            )

        self.write_enable()
        payload = bytes([CMD_PAGE_PROGRAM, (addr >> 16) & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF]) + data
        self.xfer(payload)
        self.wait_ready(timeout=timeout)

    def flash_data(self, addr, data: bytes, progress_cb=None):
        """Erases and programs an arbitrary-length region starting at
        addr. Erases whole sectors as needed (so this can erase bytes
        outside [addr, addr+len) if the region doesn't align to sector
        boundaries - that's inherent to NOR flash, not a bug) and then
        writes in PAGE_SIZE chunks respecting page boundaries."""
        self._erase_region(addr, len(data))
        self._program_region(addr, data, progress_cb=progress_cb)

    def _erase_region(self, addr, length):
        """Erases every sector that overlaps [addr, addr+length)."""
        start_sector = (addr // SECTOR_SIZE) * SECTOR_SIZE
        end_sector = ((addr + length - 1) // SECTOR_SIZE) * SECTOR_SIZE
        sector = start_sector
        while sector <= end_sector:
            self.erase_sector(sector)
            sector += SECTOR_SIZE

    def _program_region(self, addr, data: bytes, progress_cb=None):
        """Writes data in PAGE_SIZE chunks, respecting page boundaries.
        Does not erase first - caller must ensure the target is already
        erased (0xFF)."""
        pos = 0
        while pos < len(data):
            page_addr = addr + pos
            space_in_page = PAGE_SIZE - (page_addr % PAGE_SIZE)
            n = min(space_in_page, len(data) - pos)
            self.program_page(page_addr, data[pos:pos + n])
            pos += n
            if progress_cb:
                progress_cb(pos, len(data))

    # ---------- Milestone 7: full round-trip validation ----------

    def round_trip_test(self, addr, size=SECTOR_SIZE, progress_cb=None) -> dict:
        """Backs up a region, erases it, writes a known test pattern,
        verifies the write, then ALWAYS attempts to restore the
        original data - even if the write step failed partway through.
        Never raises for test/restore failures; returns a result dict
        so a partial failure still leaves a full diagnostic picture
        (in particular, whether restore succeeded) instead of losing
        it to an exception.

        progress_cb(pct: int, message: str) is called throughout, if
        provided.
        """
        if addr % SECTOR_SIZE != 0 or size <= 0 or size % SECTOR_SIZE != 0:
            raise ValueError("round_trip_test: addr and size must be non-zero multiples of SECTOR_SIZE")

        def report(pct, msg):
            if progress_cb:
                progress_cb(pct, msg)

        result = {
            "addr": addr, "size": size,
            "erase_ok": None, "write_ok": None, "restore_ok": None,
            "restore_attempted": False, "error": None, "restore_error": None,
            "original": None, "pattern": None, "written": None, "restored": None,
        }

        # No backup, no safe way to proceed - let this raise uncaught.
        report(0, "Backing up original data...")
        original = self.read_chunk(addr, size)
        result["original"] = original

        try:
            report(10, "Erasing test region...")
            self._erase_region(addr, size)

            report(20, "Verifying erase...")
            erased = self.read_chunk(addr, size)
            result["erase_ok"] = all(b == 0xFF for b in erased)

            report(30, "Writing test pattern...")
            pattern = _deterministic_pattern(size)
            result["pattern"] = pattern
            self._program_region(
                addr, pattern,
                progress_cb=lambda done, total: report(30 + int(done / total * 30), "Writing test pattern..."),
            )

            report(60, "Verifying write...")
            written = self.read_chunk(addr, size)
            result["written"] = written
            result["write_ok"] = (written == pattern)

        except (TimeoutError, RuntimeError, ValueError) as e:
            result["error"] = str(e)

        # Restore is not optional cleanup - if we got past the erase
        # step above, the user's real data is gone until this succeeds.
        report(70, "Restoring original data...")
        result["restore_attempted"] = True
        try:
            self._erase_region(addr, size)
            self._program_region(
                addr, original,
                progress_cb=lambda done, total: report(70 + int(done / total * 20), "Restoring original data..."),
            )
            report(90, "Verifying restore...")
            restored = self.read_chunk(addr, size)
            result["restored"] = restored
            result["restore_ok"] = (restored == original)
        except (TimeoutError, RuntimeError) as e:
            result["restore_error"] = str(e)
            result["restore_ok"] = False

        report(100, "Done")
        return result

    # ---------- Milestone 8: flash an arbitrary file to the chip ----------

    def flash_image(self, image: bytes, base_addr=0, chip_size=None, progress_cb=None, max_sector_retries=2) -> dict:
        """Writes `image` starting at base_addr, touching only sectors
        whose target content actually differs from what's currently on
        the chip. For a sector that only partially overlaps the image
        (the tail sector when len(image) isn't sector-aligned), the
        bytes outside the image's range are read back and preserved,
        not erased away - only the exact image bytes are considered
        for the diff/write decision.

        Returns a dict: total_sectors, changed_sectors (list of addrs),
        skipped_sectors (int), failed_sectors (list of {addr, offset}).
        Does not raise on a per-sector write failure - it records it
        and continues, so one bad sector doesn't lose progress on the
        rest of the image.

        progress_cb(sector_index, total_sectors, sector_addr) is called
        after each sector, if provided.
        """
        if len(image) == 0:
            raise ValueError("flash_image: image is empty")
        end_addr = base_addr + len(image)
        if chip_size is not None and end_addr > chip_size:
            raise ValueError(
                f"flash_image: image would extend to 0x{end_addr:06X}, past chip_size 0x{chip_size:06X}"
            )

        start_sector = (base_addr // SECTOR_SIZE) * SECTOR_SIZE
        end_sector = ((end_addr - 1) // SECTOR_SIZE) * SECTOR_SIZE
        sector_addrs = list(range(start_sector, end_sector + SECTOR_SIZE, SECTOR_SIZE))
        total_sectors = len(sector_addrs)

        result = {
            "total_sectors": total_sectors,
            "changed_sectors": [],
            "skipped_sectors": 0,
            "failed_sectors": [],
        }

        for i, sector_addr in enumerate(sector_addrs):
            current = self.read_chunk(sector_addr, SECTOR_SIZE)

            # Overlay image bytes onto the existing sector content, so
            # anything outside [base_addr, end_addr) within this sector
            # is preserved exactly as read.
            target = bytearray(current)
            overlap_start = max(sector_addr, base_addr)
            overlap_end = min(sector_addr + SECTOR_SIZE, end_addr)
            image_slice = image[overlap_start - base_addr:overlap_end - base_addr]
            target[overlap_start - sector_addr:overlap_end - sector_addr] = image_slice
            target = bytes(target)

            if target == current:
                result["skipped_sectors"] += 1
            else:
                success = False
                written = None
                for _attempt in range(max_sector_retries):
                    self.erase_sector(sector_addr)
                    self._program_region(sector_addr, target)
                    written = self.read_chunk(sector_addr, SECTOR_SIZE)
                    if written == target:
                        success = True
                        break
                if success:
                    result["changed_sectors"].append(sector_addr)
                else:
                    offset = _first_diff_offset(target, written)
                    result["failed_sectors"].append({"addr": sector_addr, "offset": offset})

            if progress_cb:
                progress_cb(i + 1, total_sectors, sector_addr)

        return result


def _deterministic_pattern(length, seed=0xC0FFEE) -> bytes:
    """Reproducible pseudo-random bytes for round-trip testing. Not
    cryptographic - just needs to be clearly distinguishable from
    blank/erased flash (0xFF) and from an all-zero failure mode, and
    to give the same pattern across runs for easier debugging."""
    rng = random.Random(seed)
    return bytes(rng.getrandbits(8) for _ in range(length))


class ChecksumError(Exception):
    """Raised when a chunk's data doesn't match the firmware's checksum."""


def rotate_xor_checksum(data: bytes) -> int:
    """Must exactly mirror the Arduino firmware's checksum: 16-bit,
    rotate-left-1 then XOR in each byte. Not cryptographic - just
    sensitive enough to catch dropped/reordered/flipped bytes in transit."""
    checksum = 0
    for b in data:
        checksum = ((checksum << 1) | (checksum >> 15)) & 0xFFFF
        checksum ^= b
    return checksum


def _first_diff_offset(a: bytes, b: bytes):
    """Returns the index of the first differing byte between a and b,
    or None if they're equal (up to the shorter length - a length
    mismatch is reported separately by the caller)."""
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)


def load_pinmap():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            return {**DEFAULT_PINS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_PINS)


def save_pinmap(pins):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(pins, f, indent=2)
    except OSError:
        pass  # non-fatal; just means it won't persist across sessions


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("P25D80SH Flasher - Setup")
        self.geometry("420x380")
        self.link = SerialLink()
        self.pins = load_pinmap()
        self.last_dump_bytes = None
        self.last_dump_path = None
        self.flash_image_bytes = None
        self.flash_image_path = None

        self._build_ui()
        self._refresh_ports()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # Everything lives inside a scrollable canvas because the content
        # (now through Milestone 8) is taller than fits in one screen on
        # most laptops. `body` is the actual parent for every widget below
        # instead of `self` directly.
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        body = ttk.Frame(canvas)
        body_window = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_body_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            # Keep the inner frame's width matched to the canvas so widgets
            # using fill="x" expand correctly instead of staying icon-width.
            canvas.itemconfigure(body_window, width=event.width)

        body.bind("<Configure>", _on_body_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            # Windows/macOS deliver delta in multiples of 120; Linux
            # (Button-4/5) doesn't set event.delta at all.
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)   # Windows / macOS
        canvas.bind_all("<Button-4>", _on_mousewheel)     # Linux scroll up
        canvas.bind_all("<Button-5>", _on_mousewheel)     # Linux scroll down

        port_frame = ttk.LabelFrame(body, text="Connection")
        port_frame.pack(fill="x", **pad)

        ttk.Label(port_frame, text="Port:").grid(row=0, column=0, sticky="w")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(port_frame, text="Refresh", command=self._refresh_ports).grid(row=0, column=2)
        port_frame.columnconfigure(1, weight=1)

        pin_frame = ttk.LabelFrame(body, text="Pin Map (bit-banged SPI)")
        pin_frame.pack(fill="x", **pad)

        self.pin_vars = {}
        for i, role in enumerate(["cs", "sclk", "mosi", "miso"]):
            ttk.Label(pin_frame, text=role.upper() + ":").grid(row=i, column=0, sticky="w", padx=4, pady=2)
            var = tk.IntVar(value=self.pins[role])
            self.pin_vars[role] = var
            ttk.Spinbox(pin_frame, from_=2, to=13, textvariable=var, width=5).grid(row=i, column=1, sticky="w")

        ttk.Button(body, text="Connect", command=self._on_connect).pack(**pad)

        self.status_var = tk.StringVar(value="Not connected")
        ttk.Label(body, textvariable=self.status_var, foreground="gray").pack(**pad)

        ttk.Separator(body).pack(fill="x", pady=8)

        ttk.Button(body, text="Read JEDEC ID (test)", command=self._on_read_id).pack(**pad)
        self.id_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.id_var, font=("Courier", 11)).pack(**pad)

        ttk.Separator(body).pack(fill="x", pady=8)

        dump_frame = ttk.LabelFrame(body, text="Dump Flash (Milestone 4)")
        dump_frame.pack(fill="x", **pad)

        ttk.Label(dump_frame, text="Size (bytes):").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.size_var = tk.IntVar(value=DEFAULT_FLASH_SIZE)
        ttk.Entry(dump_frame, textvariable=self.size_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(dump_frame, text="Chunk size:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.chunk_var = tk.IntVar(value=DEFAULT_CHUNK_SIZE)
        ttk.Entry(dump_frame, textvariable=self.chunk_var, width=10).grid(row=1, column=1, sticky="w")

        self.dump_button = ttk.Button(dump_frame, text="Dump to File...", command=self._on_dump)
        self.dump_button.grid(row=0, column=2, rowspan=2, padx=8)

        self.progress = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.progress.pack(fill="x", **pad)
        self.dump_status_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.dump_status_var, foreground="gray").pack(**pad)

        self.verify_button = ttk.Button(
            body, text="Verify (re-dump & compare)", command=self._on_verify, state="disabled"
        )
        self.verify_button.pack(**pad)
        self.verify_status_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.verify_status_var, foreground="gray").pack(**pad)

        ttk.Separator(body).pack(fill="x", pady=8)

        diag_frame = ttk.LabelFrame(body, text="Status Register Diagnostics")
        diag_frame.pack(fill="x", **pad)

        ttk.Button(diag_frame, text="Read Status Register", command=self._on_read_status).grid(
            row=0, column=0, padx=4, pady=2
        )
        self.clear_protect_button = ttk.Button(
            diag_frame, text="Clear Protection Bits", command=self._on_clear_protection, state="disabled"
        )
        self.clear_protect_button.grid(row=0, column=1, padx=4, pady=2)
        self.status_reg_var = tk.StringVar(value="")
        ttk.Label(diag_frame, textvariable=self.status_reg_var, font=("Courier", 10), justify="left").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=4, pady=2
        )

        ttk.Separator(body).pack(fill="x", pady=8)

        rt_frame = ttk.LabelFrame(body, text="Round-Trip Test (Milestone 7) - DESTRUCTIVE")
        rt_frame.pack(fill="x", **pad)

        ttk.Label(rt_frame, text="Test address:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        # Defaults to the chip's last sector rather than address 0, since
        # cartridge header/boot data is more likely to live at the start.
        # Still just a default - the user should pick a region they're
        # actually comfortable erasing.
        self.rt_addr_var = tk.IntVar(value=DEFAULT_FLASH_SIZE - SECTOR_SIZE)
        ttk.Entry(rt_frame, textvariable=self.rt_addr_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(rt_frame, text="Test size (sector-aligned):").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.rt_size_var = tk.IntVar(value=SECTOR_SIZE)
        ttk.Entry(rt_frame, textvariable=self.rt_size_var, width=10).grid(row=1, column=1, sticky="w")

        self.rt_button = ttk.Button(rt_frame, text="Run Round-Trip Test", command=self._on_round_trip)
        self.rt_button.grid(row=0, column=2, rowspan=2, padx=8)

        ttk.Label(
            rt_frame,
            text="Backs up the region, erases it, writes a test pattern,\n"
                 "verifies it, then always restores the original data.",
            foreground="gray", justify="left",
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=4, pady=(4, 0))

        self.rt_progress = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.rt_progress.pack(fill="x", **pad)
        self.rt_status_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.rt_status_var, foreground="gray", wraplength=380, justify="left").pack(**pad)

        ttk.Separator(body).pack(fill="x", pady=8)

        flash_frame = ttk.LabelFrame(body, text="Flash File to Chip (Milestone 8)")
        flash_frame.pack(fill="x", **pad)

        ttk.Button(flash_frame, text="Load Image...", command=self._on_load_image).grid(
            row=0, column=0, padx=4, pady=2
        )
        self.image_label_var = tk.StringVar(value="No image loaded")
        ttk.Label(flash_frame, textvariable=self.image_label_var, foreground="gray").grid(
            row=0, column=1, columnspan=2, sticky="w", padx=4
        )

        ttk.Label(flash_frame, text="Base address:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.flash_addr_var = tk.IntVar(value=0)
        ttk.Entry(flash_frame, textvariable=self.flash_addr_var, width=10).grid(row=1, column=1, sticky="w")

        self.flash_button = ttk.Button(
            flash_frame, text="Flash to Chip", command=self._on_flash_image, state="disabled"
        )
        self.flash_button.grid(row=1, column=2, padx=8)

        self.flash_progress = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.flash_progress.pack(fill="x", **pad)
        self.flash_status_var = tk.StringVar(value="")
        ttk.Label(
            body, textvariable=self.flash_status_var, foreground="gray", wraplength=380, justify="left"
        ).pack(**pad)


    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def _set_status(self, text, error=False):
        self.status_var.set(text)

    def _on_connect(self):
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("No port", "Select a serial port first.")
            return
        self._set_status("Connecting...")
        threading.Thread(target=self._connect_worker, args=(port,), daemon=True).start()

    def _connect_worker(self, port):
        try:
            self.link.connect(port)
            self.link.ping()

            pins = {role: var.get() for role, var in self.pin_vars.items()}
            self.link.send_config(pins["cs"], pins["sclk"], pins["mosi"], pins["miso"])
            save_pinmap(pins)

            self.after(0, self._set_status, f"Connected on {port} - handshake OK")
        except serial.SerialException as e:
            # On Ubuntu this is frequently a /dev/tty permissions issue -
            # add the user to the 'dialout' group and re-login if so.
            self.after(0, self._connect_fail, f"Serial error: {e}")
        except (TimeoutError, RuntimeError) as e:
            self.after(0, self._connect_fail, str(e))

    def _connect_fail(self, msg):
        self._set_status("Connection failed")
        messagebox.showerror("Connection failed", msg)

    def _on_read_id(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return
        threading.Thread(target=self._read_id_worker, daemon=True).start()

    def _read_id_worker(self):
        try:
            id_bytes = self.link.read_jedec_id()
            text = " ".join(f"{b:02X}" for b in id_bytes)
            self.after(0, self.id_var.set, f"JEDEC ID: {text}")
        except (TimeoutError, RuntimeError) as e:
            self.after(0, self._connect_fail, str(e))


    def _on_dump(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return

        total_len = self.size_var.get()
        chunk_size = self.chunk_var.get()
        if total_len <= 0 or chunk_size <= 0:
            messagebox.showwarning("Invalid size", "Size and chunk size must be positive.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".bin",
            filetypes=[("Binary dump", "*.bin"), ("All files", "*.*")],
            initialfile="dump.bin",
        )
        if not save_path:
            return

        self.dump_button.state(["disabled"])
        self.progress["value"] = 0
        self.dump_status_var.set("Starting dump...")
        threading.Thread(
            target=self._dump_worker, args=(total_len, chunk_size, save_path), daemon=True
        ).start()

    def _dump_worker(self, total_len, chunk_size, save_path):
        def progress_cb(done, total):
            pct = (done / total) * 100
            self.after(0, self._update_dump_progress, pct, done, total)

        try:
            data = self.link.dump_flash(total_len, chunk_size=chunk_size, progress_cb=progress_cb)
            with open(save_path, "wb") as f:
                f.write(data)
            digest = hashlib.sha256(data).hexdigest()
            with open(save_path + ".sha256", "w") as f:
                f.write(digest + "\n")
            self.last_dump_bytes = data
            self.last_dump_path = save_path
            self.after(0, self._dump_done, save_path, len(data), digest)
        except (TimeoutError, RuntimeError, OSError) as e:
            self.after(0, self._dump_fail, str(e))

    def _update_dump_progress(self, pct, done, total):
        self.progress["value"] = pct
        self.dump_status_var.set(f"{done}/{total} bytes ({pct:.1f}%)")

    def _dump_done(self, save_path, length, digest):
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])
        self.dump_status_var.set(f"Done - {length} bytes saved to {save_path}\nSHA256: {digest}")
        messagebox.showinfo("Dump complete", f"Saved {length} bytes to:\n{save_path}")

    def _dump_fail(self, msg):
        self.dump_button.state(["!disabled"])
        self.dump_status_var.set("Dump failed")
        messagebox.showerror("Dump failed", msg)

    def _on_verify(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return
        if self.last_dump_bytes is None:
            messagebox.showwarning("No dump yet", "Run a dump before verifying.")
            return

        self.verify_button.state(["disabled"])
        self.dump_button.state(["disabled"])
        self.progress["value"] = 0
        self.verify_status_var.set("Re-dumping for comparison...")
        total_len = len(self.last_dump_bytes)
        chunk_size = self.chunk_var.get()
        threading.Thread(
            target=self._verify_worker, args=(total_len, chunk_size), daemon=True
        ).start()

    def _verify_worker(self, total_len, chunk_size):
        def progress_cb(done, total):
            pct = (done / total) * 100
            self.after(0, self._update_dump_progress, pct, done, total)

        try:
            second_dump = self.link.dump_flash(total_len, chunk_size=chunk_size, progress_cb=progress_cb)
            self.after(0, self._verify_done, second_dump)
        except (TimeoutError, RuntimeError) as e:
            self.after(0, self._verify_fail, str(e))

    def _verify_done(self, second_dump):
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])

        if second_dump == self.last_dump_bytes:
            self.verify_status_var.set(f"Verified: two independent reads of {len(second_dump)} bytes match exactly.")
            messagebox.showinfo("Verification passed", "Both dumps match byte-for-byte.")
            return

        # Find the first differing offset to make debugging concrete
        # rather than just reporting "they differ somewhere."
        first_diff = _first_diff_offset(self.last_dump_bytes, second_dump)
        if first_diff is not None:
            a = self.last_dump_bytes[first_diff]
            b = second_dump[first_diff]
            detail = f"First mismatch at offset 0x{first_diff:06X}: first dump=0x{a:02X}, second dump=0x{b:02X}"
        else:
            detail = "Dumps differ in length."

        self.verify_status_var.set(f"MISMATCH - {detail}")
        messagebox.showwarning("Verification failed", f"Dumps do not match.\n\n{detail}")

    def _verify_fail(self, msg):
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])
        self.verify_status_var.set("Verify failed")
        messagebox.showerror("Verify failed", msg)

    def _on_read_status(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return
        threading.Thread(target=self._read_status_worker, daemon=True).start()

    def _read_status_worker(self):
        try:
            status = self.link.read_status()
            self.after(0, self._read_status_done, status)
        except (TimeoutError, RuntimeError) as e:
            self.after(0, lambda: messagebox.showerror("Read status failed", str(e)))

    def _read_status_done(self, status):
        bp_bits = (status & STATUS_BP_MASK) >> 2
        lines = [
            f"Status register: 0x{status:02X} ({status:#010b})",
            f"WIP (busy): {'1' if status & STATUS_WIP_BIT else '0'}   "
            f"WEL: {'1' if status & STATUS_WEL_BIT else '0'}   "
            f"BP0-2: {bp_bits:03b}",
        ]
        if bp_bits != 0:
            lines.append("Block-protect bits are set - this likely explains erase/program having no effect.")
            self.clear_protect_button.state(["!disabled"])
        else:
            lines.append("No block protection bits set - write failures have a different cause.")
        self.status_reg_var.set("\n".join(lines))

    def _on_clear_protection(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return
        confirmed = messagebox.askyesno(
            "Confirm clear protection",
            "This writes 0x00 to the status register, clearing ALL block-protect bits "
            "for the whole chip (not just one region). This removes write protection "
            "chip-wide.\n\nProceed?",
            icon="warning",
        )
        if not confirmed:
            return
        threading.Thread(target=self._clear_protection_worker, daemon=True).start()

    def _clear_protection_worker(self):
        try:
            self.link.write_status_register(0x00)
            status = self.link.read_status()
            self.after(0, self._read_status_done, status)
            self.after(0, lambda: messagebox.showinfo(
                "Protection cleared", f"Status register now 0x{status:02X}. Try the round-trip test again."
            ))
        except (TimeoutError, RuntimeError) as e:
            self.after(0, lambda: messagebox.showerror("Clear protection failed", str(e)))

    def _on_round_trip(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return

        addr = self.rt_addr_var.get()
        size = self.rt_size_var.get()
        if addr % SECTOR_SIZE != 0 or size <= 0 or size % SECTOR_SIZE != 0:
            messagebox.showwarning(
                "Invalid region", f"Address and size must both be non-zero multiples of {SECTOR_SIZE}."
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm destructive test",
            f"This will ERASE 0x{addr:06X}-0x{addr + size - 1:06X} ({size} bytes) on the "
            "connected chip, write a test pattern, verify it, then restore the original "
            "data.\n\nIf the connection drops mid-test, this region may be left erased "
            "or with test data instead of your original content.\n\n"
            "Proceed?",
            icon="warning",
        )
        if not confirmed:
            return

        self.rt_button.state(["disabled"])
        self.dump_button.state(["disabled"])
        self.verify_button.state(["disabled"])
        self.rt_progress["value"] = 0
        self.rt_status_var.set("Starting round-trip test...")
        threading.Thread(target=self._round_trip_worker, args=(addr, size), daemon=True).start()

    def _round_trip_worker(self, addr, size):
        def progress_cb(pct, msg):
            self.after(0, self._update_rt_progress, pct, msg)

        try:
            result = self.link.round_trip_test(addr, size=size, progress_cb=progress_cb)
            self.after(0, self._round_trip_done, result)
        except (TimeoutError, RuntimeError, ValueError) as e:
            # This path only fires if the initial backup read itself
            # failed - at that point nothing was erased, so there's
            # nothing to restore.
            self.after(0, self._round_trip_fail, str(e))

    def _update_rt_progress(self, pct, msg):
        self.rt_progress["value"] = pct
        self.rt_status_var.set(msg)

    def _round_trip_done(self, result):
        self.rt_button.state(["!disabled"])
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])

        lines = [
            f"Region: 0x{result['addr']:06X}, {result['size']} bytes",
            f"Erase verified blank: {self._fmt_ok(result['erase_ok'])}",
            f"Write verified: {self._fmt_ok(result['write_ok'])}",
            f"Restore verified: {self._fmt_ok(result['restore_ok'])}",
        ]

        if result["error"]:
            lines.append(f"Test error: {result['error']}")

        if result["write_ok"] is False:
            offset = _first_diff_offset(result["pattern"], result["written"])
            if offset is not None:
                lines.append(
                    f"First write mismatch at 0x{offset:06X}: "
                    f"expected 0x{result['pattern'][offset]:02X}, got 0x{result['written'][offset]:02X}"
                )

        if result["restore_ok"] is False:
            if result["restore_error"]:
                lines.append(f"Restore error: {result['restore_error']}")
            elif result["restored"] is not None:
                offset = _first_diff_offset(result["original"], result["restored"])
                if offset is not None:
                    lines.append(
                        f"First restore mismatch at 0x{offset:06X}: "
                        f"original 0x{result['original'][offset]:02X}, "
                        f"restored 0x{result['restored'][offset]:02X}"
                    )

        summary = "\n".join(lines)
        self.rt_status_var.set(summary)

        if result["restore_ok"] is False:
            messagebox.showerror(
                "Restore incomplete - data at risk",
                summary + "\n\nThe original data in this region may not be fully restored. "
                "Do not disconnect - consider re-running or manually reprogramming this region.",
            )
        elif result["write_ok"] is False or result["erase_ok"] is False:
            messagebox.showwarning("Round-trip test found issues", summary)
        else:
            messagebox.showinfo("Round-trip test passed", summary)

    @staticmethod
    def _fmt_ok(value):
        if value is None:
            return "skipped"
        return "OK" if value else "FAILED"

    def _round_trip_fail(self, msg):
        self.rt_button.state(["!disabled"])
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])
        self.rt_status_var.set("Round-trip test failed before any data was modified.")
        messagebox.showerror("Round-trip test failed", msg)

    def _on_load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Binary image", "*.bin"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            messagebox.showerror("Load failed", str(e))
            return

        self.flash_image_bytes = data
        self.flash_image_path = path
        self.image_label_var.set(f"{os.path.basename(path)} - {len(data)} bytes")
        self.flash_button.state(["!disabled"])

    def _on_flash_image(self):
        if not self.link.ser or not self.link.ser.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return
        if self.flash_image_bytes is None:
            messagebox.showwarning("No image loaded", "Load a .bin file first.")
            return

        base_addr = self.flash_addr_var.get()
        chip_size = self.size_var.get()
        end_addr = base_addr + len(self.flash_image_bytes)
        if base_addr < 0 or end_addr > chip_size:
            messagebox.showerror(
                "Image out of range",
                f"Image would occupy 0x{base_addr:06X}-0x{end_addr - 1:06X}, "
                f"which exceeds the configured chip size (0x{chip_size:06X}).",
            )
            return

        self.flash_button.state(["disabled"])
        self.dump_button.state(["disabled"])
        self.verify_button.state(["disabled"])
        self.rt_button.state(["disabled"])
        self.flash_progress["value"] = 0
        self.flash_status_var.set("Checking write protection...")
        threading.Thread(
            target=self._flash_image_worker, args=(base_addr, chip_size), daemon=True
        ).start()

    def _flash_image_worker(self, base_addr, chip_size):
        # Pre-flight: block-protect bits silently no-op erase/program,
        # which would otherwise look identical to a real (but wrong)
        # failure. Check first rather than let the user rediscover this.
        try:
            status = self.link.read_status()
        except (TimeoutError, RuntimeError) as e:
            self.after(0, self._flash_image_fail, f"Status register read failed: {e}")
            return

        if status & STATUS_BP_MASK:
            proceed = self._ask_yes_no_blocking(
                "Write protection detected",
                f"Status register 0x{status:02X} has block-protect bits set - "
                "erase/program will likely silently fail.\n\n"
                "Clear protection bits now (writes 0x00 to the status register, "
                "chip-wide) and continue flashing?",
            )
            if not proceed:
                self.after(0, self._flash_image_fail, "Cancelled - write protection was not cleared.")
                return
            try:
                self.link.write_status_register(0x00)
            except (TimeoutError, RuntimeError) as e:
                self.after(0, self._flash_image_fail, f"Failed to clear protection: {e}")
                return

        def progress_cb(done, total, addr):
            pct = (done / total) * 100
            self.after(0, self._update_flash_progress, pct, done, total, addr)

        try:
            result = self.link.flash_image(
                self.flash_image_bytes, base_addr=base_addr, chip_size=chip_size, progress_cb=progress_cb
            )
            self.after(0, self._flash_image_done, result)
        except (TimeoutError, RuntimeError, ValueError) as e:
            self.after(0, self._flash_image_fail, str(e))

    def _ask_yes_no_blocking(self, title, message):
        """Runs a messagebox from a background thread by round-tripping
        through the Tk main thread via a small event + shared result."""
        result_holder = {}
        done_event = threading.Event()

        def ask():
            result_holder["value"] = messagebox.askyesno(title, message, icon="warning")
            done_event.set()

        self.after(0, ask)
        done_event.wait()
        return result_holder.get("value", False)

    def _update_flash_progress(self, pct, done, total, addr):
        self.flash_progress["value"] = pct
        self.flash_status_var.set(f"Sector {done}/{total} (0x{addr:06X})...")

    def _flash_image_done(self, result):
        self.flash_button.state(["!disabled"])
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])
        self.rt_button.state(["!disabled"])

        lines = [
            f"Total sectors touched: {result['total_sectors']}",
            f"Changed: {len(result['changed_sectors'])}",
            f"Skipped (already matched): {result['skipped_sectors']}",
            f"Failed: {len(result['failed_sectors'])}",
        ]
        for f in result["failed_sectors"]:
            lines.append(f"  - 0x{f['addr']:06X} (first mismatch at offset {f['offset']})")

        summary = "\n".join(lines)
        self.flash_status_var.set(summary)

        if result["failed_sectors"]:
            messagebox.showerror("Flash completed with failures", summary)
        else:
            messagebox.showinfo("Flash complete", summary)

    def _flash_image_fail(self, msg):
        self.flash_button.state(["!disabled"])
        self.dump_button.state(["!disabled"])
        self.verify_button.state(["!disabled"])
        self.rt_button.state(["!disabled"])
        self.flash_status_var.set("Flash failed")
        messagebox.showerror("Flash failed", msg)


if __name__ == "__main__":
    App().mainloop()
