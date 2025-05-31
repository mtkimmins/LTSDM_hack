#include <SPI.h>

#define CHIP_SELECT 10  // CS pin connected to Arduino pin 10

const uint32_t chipSize = 0x100000; // 8 Mbit = 1 MByte

void setup() {
  Serial.begin(115200);
  while (!Serial) ; // Wait for Serial to be ready
  delay(1000);
  Serial.println("READY");

  pinMode(CHIP_SELECT, OUTPUT);
  digitalWrite(CHIP_SELECT, HIGH);

  SPI.begin();
  SPI.beginTransaction(SPISettings(500000, MSBFIRST, SPI_MODE0));
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("START")) {
      dumpFlash();
      Serial.println("Dump complete.");
    } else {
      Serial.println("Unknown command. Type START to begin.");
    }
  }
}

void dumpFlash() {
  digitalWrite(CHIP_SELECT, LOW);
  SPI.transfer(0x03); // READ command

  uint32_t addr = 0;

  while (addr < chipSize) {
    // Send 24-bit address
    SPI.transfer((addr >> 16) & 0xFF);
    SPI.transfer((addr >> 8) & 0xFF);
    SPI.transfer(addr & 0xFF);

    // Read a page (e.g. 32 bytes at a time)
    for (int i = 0; i < 32 && addr < chipSize; i++, addr++) {
      byte data = SPI.transfer(0x00);
      Serial.write(data); // Raw binary to serial
    }

    digitalWrite(CHIP_SELECT, HIGH);
    delayMicroseconds(1);
    digitalWrite(CHIP_SELECT, LOW);
    SPI.transfer(0x03); // RE-send READ command for next chunk
  }

  digitalWrite(CHIP_SELECT, HIGH);
}
