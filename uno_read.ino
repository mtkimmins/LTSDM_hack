#include <SPI.h>

const uint32_t CHIP_SIZE = 1024 * 1024; // 1MB flash
const int CHIP_SELECT = 10;

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(CHIP_SELECT, OUTPUT);
  digitalWrite(CHIP_SELECT, HIGH);
  delay(1000);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() > 0 && Serial.read() == 'D') {
    Serial.println("DUMPING");

    for (uint32_t addr = 0; addr < CHIP_SIZE; addr++) {
      digitalWrite(CHIP_SELECT, LOW);
      SPI.transfer(0x03); // Read command
      SPI.transfer((addr >> 16) & 0xFF); // Address MSB
      SPI.transfer((addr >> 8) & 0xFF);
      SPI.transfer(addr & 0xFF);         // Address LSB
      byte data = SPI.transfer(0x00);    // Dummy byte to receive data
      digitalWrite(CHIP_SELECT, HIGH);
      Serial.write(data); // Send raw byte
    }

    Serial.println("DONE");
    while (true); // Stop loop after one dump
  }
}
