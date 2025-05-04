#include <SPI.h>

#define FLASH_CS 5  // Change to your flash chip's CS pin

void setup() {
  Serial.begin(115200);
  SPI.begin();

  digitalWrite(FLASH_CS, HIGH);
  pinMode(FLASH_CS, OUTPUT);
  delay(100);

  // Example: read 1MB
  digitalWrite(FLASH_CS, LOW);
  SPI.transfer(0x03);          // Read command
  SPI.transfer(0x00);          // Address byte 1
  SPI.transfer(0x00);          // Address byte 2
  SPI.transfer(0x00);          // Address byte 3

  for (uint32_t i = 0; i < 1024 * 1024; i++) {
    uint8_t b = SPI.transfer(0x00);
    Serial.write(b);           // Send over serial
  }

  digitalWrite(FLASH_CS, HIGH);
}

void loop() {
  // Nothing
}
