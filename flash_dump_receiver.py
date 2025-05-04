import serial

# === Configuration ===
PORT = 'COM3'          # Replace with your ESP32's serial port (e.g. /dev/ttyUSB0 on Linux)
BAUD_RATE = 115200     # Match the baud rate used in your ESP32 sketch
OUTPUT_FILE = 'dump.bin'
CHUNK_SIZE = 1024      # bytes per read
EXPECTED_SIZE = 1024 * 1024  # 1MB flash chip, adjust as needed

# === Open Serial Port ===
ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
print(f"Listening on {PORT}...")

# === Read and Save Binary Data ===
with open(OUTPUT_FILE, 'wb') as f:
    received = 0
    while received < EXPECTED_SIZE:
        data = ser.read(CHUNK_SIZE)
        if not data:
            print("Timeout or end of transmission.")
            break
        f.write(data)
        received += len(data)
        print(f"Received {received}/{EXPECTED_SIZE} bytes", end='\r')

ser.close()
print(f"\nDone. Data saved to {OUTPUT_FILE}")
