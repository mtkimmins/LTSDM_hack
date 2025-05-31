#include <SPI.h>

const int CHIP_SELECT = 10;

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(CHIP_SELECT, OUTPUT);
  digitalWrite(CHIP_SELECT, HIGH);
  delay(1000);
  Serial.println("Reading JEDEC ID...");

  digitalWrite(CHIP_SELECT, LOW);
  SPI.transfer(0x9F);  // JEDEC ID command
  byte manufacturer = SPI.transfer(0x00);
  byte memoryType = SPI.transfer(0x00);
  byte capacity = SPI.transfer(0x00);
  digitalWrite(CHIP_SELECT, HIGH);

  Serial.print("Manufacturer ID: 0x");
  Serial.println(manufacturer, HEX);
  Serial.print("Memory Type: 0x");
  Serial.println(memoryType, HEX);
  Serial.print("Capacity: 0x");
  Serial.println(capacity, HEX);
}

void loop() {}
