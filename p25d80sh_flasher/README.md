# P25D80SH Cartridge Flasher

This project contains:

- `arduino/P25D80SH_Flasher.ino` - Arduino Uno sketch that talks to the P25D80SH over standard SPI and exposes a small serial protocol.
- `pc_app/p25d80sh_gui.py` - Tkinter desktop app that lets you choose a `.bin`, connect to the Arduino, and trigger a full-chip erase + reflash.
- `pc_app/flasher_protocol.py` - Serial protocol helper used by the GUI.
- `requirements.txt` - Python dependency list.

## What the workflow does

1. Resets the flash and reads JEDEC ID.
2. Clears array protection bits if needed.
3. Erases the whole chip.
4. Programs the image page-by-page with the `PP (0x02)` command.
5. Reads each page back immediately and verifies it before continuing.
6. Skips pages that are already `0xFF` in the selected image to reduce upload time.

## Important hardware note

The P25D80SH is a 2.3 V to 3.6 V part. Do **not** connect Uno 5 V SPI lines directly to the flash chip unless your adapter already includes correct level shifting / resistor dividers and the flash itself is powered at 3.3 V.

## Default wiring assumptions

The sketch uses Arduino hardware SPI plus one chip-select pin:

- CS -> D10 (editable at the top of the sketch)
- MOSI -> Uno hardware SPI MOSI
- MISO -> Uno hardware SPI MISO
- SCK -> Uno hardware SPI SCK
- VCC -> 3.3 V
- GND -> GND

If your cartridge adapter already routes WP# and HOLD# high, leave that arrangement as-is.

## Arduino setup

1. Open `arduino/P25D80SH_Flasher.ino` in the Arduino IDE.
2. Confirm `FLASH_CS_PIN` matches your adapter.
3. Upload the sketch to the Uno.

## Python setup

From the `p25d80sh_flasher` folder:

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\pc_app\p25d80sh_gui.py
```

### Windows CMD

```cmd
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python .\pc_app\p25d80sh_gui.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ./pc_app/p25d80sh_gui.py
```

## Using the GUI

1. Connect the Uno.
2. Click **Refresh** and pick the correct serial port.
3. Optionally click **Test connection**.
4. Browse to your edited `.bin` file.
5. Click **Flash selected file**.
6. Confirm the erase/program action.

## Notes

- The GUI expects a 1 MiB flash image. Smaller images are padded with `0xFF` to the full device size.
- Images larger than 1 MiB are rejected.
- The GUI blocks unexpected JEDEC IDs by default. You can override that with the checkbox if you intentionally want to try a compatible variant.
- Default baud rate is 250000. If your USB-serial path is unstable, drop to 115200 in both the GUI and the sketch.
