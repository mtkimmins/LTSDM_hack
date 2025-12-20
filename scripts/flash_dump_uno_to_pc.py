#must pip "serial" module to use
import serial

SERIAL_PORT = 'COM3'  # Change if needed
BAUD_RATE = 19200
OUTPUT_FILE = 'flash_dump.bin'
CHIP_SIZE = 1024 * 1024

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as ser:
    print("[*] Waiting for READY...")
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if "READY" in line:
            print("[✓] Arduino is ready.")
        elif "JEDEC ID" in line:
            print("[i] " + line)
        if "READY" in line:
            break

    print("[→] Sending dump trigger...")
    ser.write(b'START')

    print("[↓] Dumping data...")
    with open(OUTPUT_FILE, 'wb') as f:
        count = 0
        while count < CHIP_SIZE:
            byte = ser.read(1)
            if byte:
                f.write(byte)
                count += 1
                if count % 65536 == 0:
                    print(f"  [=] {count} bytes...")
            else:
                print(f"[!] Timeout at byte {count}")
                break

    print(f"[✓] Dump complete: {OUTPUT_FILE}")
