from __future__ import annotations

import pathlib
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from serial.tools import list_ports

from flasher_protocol import (
    EXPECTED_FLASH_SIZE,
    EXPECTED_JEDEC,
    FlasherError,
    P25D80SHFlasherClient,
)


class FlasherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("P25D80SH Cartridge Flasher")
        self.root.geometry("820x620")

        self.messages: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None

        self.port_var = tk.StringVar()
        self.baud_var = tk.StringVar(value="250000")
        self.file_var = tk.StringVar()
        self.allow_mismatch_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Idle")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_ui()
        self.refresh_ports()
        self.root.after(100, self._poll_messages)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        controls = ttk.LabelFrame(frame, text="Connection")
        controls.pack(fill="x", pady=(0, 10))

        ttk.Label(controls, text="Serial port").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.port_combo = ttk.Combobox(controls, textvariable=self.port_var, state="readonly", width=25)
        self.port_combo.grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Button(controls, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=8, pady=8)
        ttk.Button(controls, text="Test connection", command=self.test_connection).grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(controls, text="Baud").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        baud_combo = ttk.Combobox(
            controls,
            textvariable=self.baud_var,
            state="readonly",
            values=["115200", "230400", "250000", "500000"],
            width=12,
        )
        baud_combo.grid(row=1, column=1, sticky="w", padx=8, pady=8)

        ttk.Checkbutton(
            controls,
            text="Allow unexpected JEDEC ID",
            variable=self.allow_mismatch_var,
        ).grid(row=1, column=2, columnspan=2, sticky="w", padx=8, pady=8)

        file_box = ttk.LabelFrame(frame, text="Firmware image")
        file_box.pack(fill="x", pady=(0, 10))
        ttk.Entry(file_box, textvariable=self.file_var).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        file_box.columnconfigure(0, weight=1)
        ttk.Button(file_box, text="Browse .bin", command=self.browse_file).grid(row=0, column=1, padx=8, pady=8)

        action_box = ttk.LabelFrame(frame, text="Action")
        action_box.pack(fill="x", pady=(0, 10))
        self.flash_button = ttk.Button(action_box, text="Flash selected file", command=self.start_flash)
        self.flash_button.grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Label(action_box, textvariable=self.status_var).grid(row=0, column=1, padx=8, pady=8, sticky="w")

        self.progress = ttk.Progressbar(frame, variable=self.progress_var, maximum=100.0)
        self.progress.pack(fill="x", pady=(0, 10))

        log_box = ttk.LabelFrame(frame, text="Log")
        log_box.pack(fill="both", expand=True)
        self.log = tk.Text(log_box, wrap="word", state="disabled", height=20)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def log_message(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def refresh_ports(self) -> None:
        ports = [p.device for p in list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and self.port_var.get() not in ports:
            self.port_var.set(ports[0])
        if not ports:
            self.port_var.set("")

    def browse_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select a binary image",
            filetypes=[("Binary images", "*.bin"), ("All files", "*.*")],
        )
        if filename:
            self.file_var.set(filename)

    def _selected_baud(self) -> int:
        return int(self.baud_var.get())

    def _selected_port(self) -> str:
        port = self.port_var.get().strip()
        if not port:
            raise FlasherError("Choose a serial port first.")
        return port

    def test_connection(self) -> None:
        try:
            port = self._selected_port()
            baud = self._selected_baud()
            with P25D80SHFlasherClient(port, baudrate=baud) as client:
                info = client.get_info()
            self.log_message(
                f"Connected. JEDEC={info.jedec} SIZE={info.size} SR1=0x{info.sr1:02X} SR2=0x{info.sr2:02X} CR=0x{info.cr:02X}"
            )
            self.status_var.set("Connection OK")
        except Exception as exc:
            messagebox.showerror("Connection failed", str(exc))
            self.status_var.set("Connection failed")

    def start_flash(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo("Busy", "A flash job is already running.")
            return

        try:
            port = self._selected_port()
            baud = self._selected_baud()
            image_path = pathlib.Path(self.file_var.get().strip())
            if not image_path.is_file():
                raise FlasherError("Select a valid .bin file first.")
        except Exception as exc:
            messagebox.showerror("Cannot start", str(exc))
            return

        confirm = messagebox.askyesno(
            "Confirm flash",
            "This will erase the whole chip and write the selected image. Continue?",
        )
        if not confirm:
            return

        self.progress_var.set(0.0)
        self.status_var.set("Flashing...")
        self.flash_button.configure(state="disabled")
        self.worker = threading.Thread(
            target=self._flash_worker,
            args=(port, baud, image_path, self.allow_mismatch_var.get()),
            daemon=True,
        )
        self.worker.start()

    def _flash_worker(self, port: str, baud: int, image_path: pathlib.Path, allow_mismatch: bool) -> None:
        try:
            image = image_path.read_bytes()
            if len(image) > EXPECTED_FLASH_SIZE:
                raise FlasherError(
                    f"Image is too large: {len(image)} bytes. Maximum supported size is {EXPECTED_FLASH_SIZE} bytes."
                )

            padded = image + (b"\xFF" * (EXPECTED_FLASH_SIZE - len(image)))
            pages_written = 0
            pages_skipped = 0
            total_pages = (EXPECTED_FLASH_SIZE + 255) // 256

            self.messages.put(("log", f"Loaded {image_path.name} ({len(image)} bytes)."))
            self.messages.put(("log", "Opening serial connection..."))

            with P25D80SHFlasherClient(port, baudrate=baud) as client:
                info = client.get_info()
                self.messages.put(
                    (
                        "log",
                        f"Flash reports JEDEC={info.jedec} SIZE={info.size} SR1=0x{info.sr1:02X} SR2=0x{info.sr2:02X} CR=0x{info.cr:02X}",
                    )
                )

                if info.size != EXPECTED_FLASH_SIZE:
                    raise FlasherError(
                        f"Unexpected flash size {info.size}. Expected {EXPECTED_FLASH_SIZE}."
                    )

                if info.jedec != EXPECTED_JEDEC and not allow_mismatch:
                    raise FlasherError(
                        f"Unexpected JEDEC ID {info.jedec}. Expected {EXPECTED_JEDEC}. Enable the override if you really want to continue."
                    )

                self.messages.put(("log", "Clearing write protection bits if needed..."))
                client.unprotect()

                self.messages.put(("log", "Erasing entire chip..."))
                client.erase_chip()
                self.messages.put(("log", "Chip erase complete. Programming modified image..."))

                for page_index, address in enumerate(range(0, EXPECTED_FLASH_SIZE, 256), start=1):
                    chunk = padded[address : address + 256]
                    if chunk == b"\xFF" * len(chunk):
                        pages_skipped += 1
                    else:
                        client.write_page(address, chunk)
                        pages_written += 1

                    progress = (page_index / total_pages) * 100.0
                    self.messages.put(("progress", progress))
                    if page_index % 64 == 0 or page_index == total_pages:
                        self.messages.put(
                            (
                                "status",
                                f"Programming page {page_index}/{total_pages} (written={pages_written}, skipped_blank={pages_skipped})",
                            )
                        )

            self.messages.put(("log", f"Done. Wrote {pages_written} page(s); skipped {pages_skipped} blank page(s)."))
            self.messages.put(("done", "Flash completed successfully."))
        except Exception as exc:
            self.messages.put(("error", str(exc)))

    def _poll_messages(self) -> None:
        try:
            while True:
                kind, payload = self.messages.get_nowait()
                if kind == "log":
                    self.log_message(str(payload))
                elif kind == "progress":
                    self.progress_var.set(float(payload))
                elif kind == "status":
                    self.status_var.set(str(payload))
                elif kind == "done":
                    self.status_var.set(str(payload))
                    self.flash_button.configure(state="normal")
                    messagebox.showinfo("Success", str(payload))
                elif kind == "error":
                    self.status_var.set("Flash failed")
                    self.flash_button.configure(state="normal")
                    self.log_message(f"ERROR: {payload}")
                    messagebox.showerror("Flash failed", str(payload))
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_messages)


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    app = FlasherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
