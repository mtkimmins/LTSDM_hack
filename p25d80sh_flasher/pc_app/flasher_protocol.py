from __future__ import annotations

import dataclasses
import time
from typing import Optional

import serial


EXPECTED_FLASH_SIZE = 1_048_576
EXPECTED_JEDEC = "856014"


class FlasherError(RuntimeError):
    pass


@dataclasses.dataclass
class FlashInfo:
    size: int
    jedec: str
    sr1: int
    sr2: int
    cr: int


class P25D80SHFlasherClient:
    def __init__(self, port: str, baudrate: int = 250000, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

    def __enter__(self) -> "P25D80SHFlasherClient":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout, write_timeout=self.timeout)
        # Opening the port resets most Uno boards. Give the sketch time to come back.
        time.sleep(2.0)
        self._drain_input()
        # Try to catch the READY banner if it arrives slightly later.
        for _ in range(20):
            try:
                line = self._readline(timeout=0.25)
            except FlasherError:
                line = ""
            if line.startswith("READY"):
                return
            self.send_line("PING")
            reply = self._readline(timeout=0.5)
            if reply == "PONG":
                return
        raise FlasherError("Could not synchronize with the Arduino flasher sketch.")

    def close(self) -> None:
        if self.ser is not None:
            self.ser.close()
            self.ser = None

    def _require_open(self) -> serial.Serial:
        if self.ser is None:
            raise FlasherError("Serial port is not open.")
        return self.ser

    def _drain_input(self) -> None:
        ser = self._require_open()
        time.sleep(0.1)
        ser.reset_input_buffer()
        ser.reset_output_buffer()

    def _readline(self, timeout: Optional[float] = None) -> str:
        ser = self._require_open()
        old_timeout = ser.timeout
        if timeout is not None:
            ser.timeout = timeout
        try:
            raw = ser.readline()
        finally:
            if timeout is not None:
                ser.timeout = old_timeout
        if not raw:
            raise FlasherError("Timed out waiting for a response from the Arduino.")
        return raw.decode("utf-8", errors="replace").strip()

    def send_line(self, line: str) -> None:
        ser = self._require_open()
        ser.write((line + "\n").encode("ascii"))
        ser.flush()

    def ping(self) -> bool:
        self.send_line("PING")
        return self._readline() == "PONG"

    def reset_flash(self) -> None:
        self.send_line("RESET")
        self._expect_ok(timeout=2.0)

    def get_info(self) -> FlashInfo:
        self.send_line("INFO")
        line = self._readline(timeout=2.0)
        if not line.startswith("INFO "):
            raise FlasherError(f"Unexpected INFO reply: {line}")

        fields = {}
        for part in line.split()[1:]:
            key, value = part.split("=", 1)
            fields[key] = value

        try:
            return FlashInfo(
                size=int(fields["SIZE"]),
                jedec=fields["JEDEC"].upper(),
                sr1=int(fields["SR1"], 16),
                sr2=int(fields["SR2"], 16),
                cr=int(fields["CR"], 16),
            )
        except Exception as exc:
            raise FlasherError(f"Could not parse INFO reply: {line}") from exc

    def unprotect(self) -> None:
        self.send_line("UNPROTECT")
        self._expect_ok(timeout=2.0)

    def erase_chip(self) -> None:
        self.send_line("ERASE_CHIP")
        self._expect_ok(timeout=15.0)

    def write_page(self, address: int, data: bytes) -> None:
        if not data:
            return
        if len(data) > 256:
            raise FlasherError("A single WRITE command must be 256 bytes or less.")
        if ((address & 0xFF) + len(data)) > 256:
            raise FlasherError("WRITE command crosses a flash page boundary.")

        self.send_line(f"WRITE {address} {len(data)}")
        ready = self._readline(timeout=2.0)
        if ready != "READY":
            raise FlasherError(f"Arduino refused WRITE command: {ready}")

        ser = self._require_open()
        ser.write(data)
        ser.flush()
        self._expect_ok(timeout=5.0)

    def _expect_ok(self, timeout: float) -> None:
        reply = self._readline(timeout=timeout)
        if reply == "OK":
            return
        if reply.startswith("ERR "):
            raise FlasherError(reply[4:])
        raise FlasherError(f"Unexpected reply: {reply}")
