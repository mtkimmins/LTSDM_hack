# UNTESTED!!! 3May2025

import serial
import time

# === Config ===
PORT = 'COM3'              # Replace with your ESP32 serial port
BAUD_RATE = 115200
OUTPUT_FILE = 'dump.bin'
EXPECTED_SIZE = 1024 * 1024  # 1MB

# === Connect ===
ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
print("Waiting for ESP32...")

# === Wait for "READY" ===
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if "READY" in line:
        print("ESP32 ready.")
        break

# === Trigger the ESP32 to start dump ===
print("Sending DUMP command...")
ser.write(b'DUMP\n')

# === Receive the binary ===
with open(OUTPUT_FILE, 'wb') as f:
    received = 0
    while received < EXPECTED_SIZE:
        chunk = ser.read(1024)
        if not chunk:
            print("Timeout or incomplete transfer.")
            break
        f.write(chunk)
        received += len(chunk)
        print(f"Received {received}/{EXPECTED_SIZE} bytes", end='\r')

# Optional: check for completion message
done_msg = ser.readline().decode(errors='ignore').strip()
if "DONE" in done_msg:
    print("\nDump completed successfully.")
else:
    print("\nUnexpected end. Check data integrity.")

ser.close()
print(f"Saved to: {OUTPUT_FILE}")
