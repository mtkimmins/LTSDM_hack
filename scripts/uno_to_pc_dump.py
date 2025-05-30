import serial

SERIAL_PORT = 'COM3'  # Change to match your system (e.g., /dev/ttyUSB0 for Linux/Mac)
BAUD_RATE = 115200
OUTPUT_FILE = 'flash_dump.bin'
CHIP_SIZE = 1024 * 1024  # 1MB

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
    # Wait for READY signal
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if "READY" in line:
            print("[✓] Arduino is ready.")
            break

    # Send dump trigger
    print("[→] Sending dump trigger...")
    ser.write(b'D')

    # Read binary data
    with open(OUTPUT_FILE, 'wb') as f:
        print(f"[↓] Dumping {CHIP_SIZE} bytes...")
        count = 0
        while count < CHIP_SIZE:
            byte = ser.read(1)
            if byte:
                f.write(byte)
                count += 1
            else:
                print("[!] Timeout or disconnect.")
                break
        print(f"[✓] Dump complete: {OUTPUT_FILE}")
