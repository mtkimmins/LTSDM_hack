//This code is to be uploaded to the ESP32
//must be put in a file with the same name on the ESP32, such as /ESP32_Flash_Dumper/ESP32_Flash_Dumper.ino

#include <SPI.h>

#define FLASH_CS 5  // Adjust for your wiring

const uint32_t FLASH_SIZE = 1024 * 1024; // 1MB

void setup() {
  Serial.begin(115200);
  SPI.begin();
  
  pinMode(FLASH_CS, OUTPUT);
  digitalWrite(FLASH_CS, HIGH);

  Serial.println("READY");  // Notify PC we're ready
}

void loop() {
  // Wait for a "DUMP" command
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // remove \r or whitespace
    if (cmd == "DUMP") {
      digitalWrite(FLASH_CS, LOW);

      SPI.transfer(0x03); // Read command
      SPI.transfer(0x00); // Address high byte
      SPI.transfer(0x00);
      SPI.transfer(0x00); // Address low byte

      for (uint32_t i = 0; i < FLASH_SIZE; i++) {
        uint8_t b = SPI.transfer(0x00);
        Serial.write(b);  // Stream binary
      }

      digitalWrite(FLASH_CS, HIGH);
      Serial.println("DONE");
    }
  }
}
