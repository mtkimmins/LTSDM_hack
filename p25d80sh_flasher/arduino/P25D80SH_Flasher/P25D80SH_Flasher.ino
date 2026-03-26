#include <SPI.h>
#include <stdlib.h>
#include <string.h>

// -------------------------------
// User-configurable settings
// -------------------------------
static const uint8_t FLASH_CS_PIN = 10;    // Edit if your cartridge adapter uses a different CS pin
static const unsigned long SERIAL_BAUD = 250000;
static const uint32_t FLASH_SIZE_BYTES = 1048576UL;  // 8 Mbit = 1 MiB
static const uint16_t PAGE_SIZE_BYTES = 256;
static const unsigned long SPI_HZ = 2000000UL;       // Conservative, standard SPI only

// P25D80SH opcodes used by this sketch
static const uint8_t CMD_WREN = 0x06;
static const uint8_t CMD_WRDI = 0x04;
static const uint8_t CMD_RDSR = 0x05;
static const uint8_t CMD_RDSR1 = 0x35;
static const uint8_t CMD_RDCR = 0x15;
static const uint8_t CMD_READ = 0x03;
static const uint8_t CMD_PP = 0x02;
static const uint8_t CMD_CE = 0xC7;
static const uint8_t CMD_RDID = 0x9F;
static const uint8_t CMD_WRSR = 0x01;
static const uint8_t CMD_RSTEN = 0x66;
static const uint8_t CMD_RST = 0x99;

static const uint8_t EXPECTED_JEDEC_MFR = 0x85;
static const uint8_t EXPECTED_JEDEC_TYPE = 0x60;
static const uint8_t EXPECTED_JEDEC_CAP = 0x14;

static SPISettings flashSpiSettings(SPI_HZ, MSBFIRST, SPI_MODE0);
static char g_lineBuffer[96];
static size_t g_lineLength = 0;
static uint8_t g_pageBuffer[PAGE_SIZE_BYTES];
static uint8_t g_verifyBuffer[PAGE_SIZE_BYTES];

void flashSelect() {
  digitalWrite(FLASH_CS_PIN, LOW);
}

void flashDeselect() {
  digitalWrite(FLASH_CS_PIN, HIGH);
}

uint8_t flashXfer(uint8_t value) {
  return SPI.transfer(value);
}

void flashBeginTransaction() {
  SPI.beginTransaction(flashSpiSettings);
  flashSelect();
}

void flashEndTransaction() {
  flashDeselect();
  SPI.endTransaction();
}

void sendSimpleCommand(uint8_t opcode) {
  flashBeginTransaction();
  flashXfer(opcode);
  flashEndTransaction();
}

void softwareResetFlash() {
  sendSimpleCommand(CMD_RSTEN);
  sendSimpleCommand(CMD_RST);
  delay(2);
}

uint8_t readStatus1() {
  flashBeginTransaction();
  flashXfer(CMD_RDSR);
  uint8_t value = flashXfer(0x00);
  flashEndTransaction();
  return value;
}

uint8_t readStatus2() {
  flashBeginTransaction();
  flashXfer(CMD_RDSR1);
  uint8_t value = flashXfer(0x00);
  flashEndTransaction();
  return value;
}

uint8_t readConfigReg() {
  flashBeginTransaction();
  flashXfer(CMD_RDCR);
  uint8_t value = flashXfer(0x00);
  flashEndTransaction();
  return value;
}

bool waitWhileBusy(unsigned long timeoutMs) {
  const unsigned long start = millis();
  while ((millis() - start) < timeoutMs) {
    if ((readStatus1() & 0x01) == 0) {
      return true;
    }
    delay(1);
  }
  return ((readStatus1() & 0x01) == 0);
}

void writeEnable() {
  sendSimpleCommand(CMD_WREN);
}

void writeDisable() {
  sendSimpleCommand(CMD_WRDI);
}

bool readJedecId(uint8_t &mfr, uint8_t &type, uint8_t &cap) {
  flashBeginTransaction();
  flashXfer(CMD_RDID);
  mfr = flashXfer(0x00);
  type = flashXfer(0x00);
  cap = flashXfer(0x00);
  flashEndTransaction();
  return true;
}

void readBytes(uint32_t address, uint8_t *dst, uint16_t length) {
  flashBeginTransaction();
  flashXfer(CMD_READ);
  flashXfer((address >> 16) & 0xFF);
  flashXfer((address >> 8) & 0xFF);
  flashXfer(address & 0xFF);
  for (uint16_t i = 0; i < length; ++i) {
    dst[i] = flashXfer(0x00);
  }
  flashEndTransaction();
}

bool clearArrayProtection() {
  // BP4..BP0 live in SR1 bits 6..2. If they are already zero, the array is unprotected.
  if ((readStatus1() & 0x7C) == 0) {
    return true;
  }

  if (!waitWhileBusy(1000)) {
    return false;
  }

  writeEnable();
  flashBeginTransaction();
  flashXfer(CMD_WRSR);
  flashXfer(0x00); // Clear SRP0/BP4..BP0/WEL/WIP writable bits in SR1.
  flashEndTransaction();

  if (!waitWhileBusy(1000)) {
    return false;
  }

  return ((readStatus1() & 0x7C) == 0);
}

bool chipErase() {
  if (!waitWhileBusy(1000)) {
    return false;
  }

  writeEnable();
  flashBeginTransaction();
  flashXfer(CMD_CE);
  flashEndTransaction();

  // Datasheet max is short, but allow a generous timeout for real hardware conditions.
  return waitWhileBusy(10000);
}

bool pageProgram(uint32_t address, const uint8_t *src, uint16_t length) {
  if (length == 0 || length > PAGE_SIZE_BYTES) {
    return false;
  }
  if ((address + length) > FLASH_SIZE_BYTES) {
    return false;
  }
  if (((address & 0xFFu) + length) > PAGE_SIZE_BYTES) {
    return false; // Do not cross a page boundary in one PP command.
  }
  if (!waitWhileBusy(1000)) {
    return false;
  }

  writeEnable();
  flashBeginTransaction();
  flashXfer(CMD_PP);
  flashXfer((address >> 16) & 0xFF);
  flashXfer((address >> 8) & 0xFF);
  flashXfer(address & 0xFF);
  for (uint16_t i = 0; i < length; ++i) {
    flashXfer(src[i]);
  }
  flashEndTransaction();

  return waitWhileBusy(1000);
}

bool verifyBytes(uint32_t address, const uint8_t *expected, uint16_t length) {
  readBytes(address, g_verifyBuffer, length);
  for (uint16_t i = 0; i < length; ++i) {
    if (g_verifyBuffer[i] != expected[i]) {
      return false;
    }
  }
  return true;
}

bool readExactBytes(uint8_t *dst, uint16_t length, unsigned long timeoutMs) {
  uint16_t received = 0;
  const unsigned long start = millis();
  while (received < length) {
    if (Serial.available() > 0) {
      dst[received++] = (uint8_t)Serial.read();
      continue;
    }
    if ((millis() - start) > timeoutMs) {
      return false;
    }
  }
  return true;
}

void printHex2(uint8_t value) {
  if (value < 0x10) {
    Serial.print('0');
  }
  Serial.print(value, HEX);
}

void printInfoLine() {
  uint8_t mfr = 0, type = 0, cap = 0;
  readJedecId(mfr, type, cap);
  const uint8_t sr1 = readStatus1();
  const uint8_t sr2 = readStatus2();
  const uint8_t cr = readConfigReg();

  Serial.print(F("INFO SIZE="));
  Serial.print(FLASH_SIZE_BYTES);
  Serial.print(F(" JEDEC="));
  printHex2(mfr);
  printHex2(type);
  printHex2(cap);
  Serial.print(F(" SR1="));
  printHex2(sr1);
  Serial.print(F(" SR2="));
  printHex2(sr2);
  Serial.print(F(" CR="));
  printHex2(cr);
  Serial.println();
}

void printError(const __FlashStringHelper *msg) {
  Serial.print(F("ERR "));
  Serial.println(msg);
}

void printErrorText(const char *msg) {
  Serial.print(F("ERR "));
  Serial.println(msg);
}

void handleWriteCommand(char *args) {
  char *addrToken = strtok(args, " ");
  char *lenToken = strtok(NULL, " ");

  if (addrToken == NULL || lenToken == NULL) {
    printError(F("WRITE_ARGS"));
    return;
  }

  const uint32_t address = strtoul(addrToken, NULL, 0);
  const uint16_t length = (uint16_t)strtoul(lenToken, NULL, 0);

  if (length == 0 || length > PAGE_SIZE_BYTES) {
    printError(F("WRITE_LEN"));
    return;
  }
  if ((address + length) > FLASH_SIZE_BYTES) {
    printError(F("WRITE_RANGE"));
    return;
  }
  if (((address & 0xFFu) + length) > PAGE_SIZE_BYTES) {
    printError(F("WRITE_BOUNDARY"));
    return;
  }

  Serial.println(F("READY"));
  if (!readExactBytes(g_pageBuffer, length, 5000)) {
    printError(F("WRITE_TIMEOUT"));
    return;
  }

  if (!pageProgram(address, g_pageBuffer, length)) {
    printError(F("WRITE_FAIL"));
    return;
  }

  if (!verifyBytes(address, g_pageBuffer, length)) {
    printError(F("VERIFY_FAIL"));
    return;
  }

  Serial.println(F("OK"));
}

void processLine(char *line) {
  if (strcmp(line, "PING") == 0) {
    Serial.println(F("PONG"));
    return;
  }

  if (strcmp(line, "INFO") == 0) {
    printInfoLine();
    return;
  }

  if (strcmp(line, "RESET") == 0) {
    softwareResetFlash();
    if (!waitWhileBusy(1000)) {
      printError(F("RESET_BUSY"));
      return;
    }
    Serial.println(F("OK"));
    return;
  }

  if (strcmp(line, "UNPROTECT") == 0) {
    if (!clearArrayProtection()) {
      printError(F("UNPROTECT_FAIL"));
      return;
    }
    Serial.println(F("OK"));
    return;
  }

  if (strcmp(line, "ERASE_CHIP") == 0) {
    if (!chipErase()) {
      printError(F("ERASE_FAIL"));
      return;
    }
    Serial.println(F("OK"));
    return;
  }

  if (strncmp(line, "WRITE ", 6) == 0) {
    handleWriteCommand(line + 6);
    return;
  }

  if (strcmp(line, "RDID") == 0) {
    uint8_t mfr = 0, type = 0, cap = 0;
    readJedecId(mfr, type, cap);
    Serial.print(F("RDID "));
    printHex2(mfr);
    printHex2(type);
    printHex2(cap);
    Serial.println();
    return;
  }

  printError(F("UNKNOWN_CMD"));
}

void serviceSerial() {
  while (Serial.available() > 0) {
    const char c = (char)Serial.read();
    if (c == '\r') {
      continue;
    }
    if (c == '\n') {
      g_lineBuffer[g_lineLength] = '\0';
      if (g_lineLength > 0) {
        processLine(g_lineBuffer);
      }
      g_lineLength = 0;
      continue;
    }
    if (g_lineLength < (sizeof(g_lineBuffer) - 1)) {
      g_lineBuffer[g_lineLength++] = c;
    } else {
      g_lineLength = 0;
      printError(F("LINE_TOO_LONG"));
    }
  }
}

void setup() {
  pinMode(FLASH_CS_PIN, OUTPUT);
  flashDeselect();

  SPI.begin();
  Serial.begin(SERIAL_BAUD);

#if defined(USBCON)
  while (!Serial) {
    ;
  }
#endif

  delay(50);
  softwareResetFlash();
  waitWhileBusy(1000);

  uint8_t mfr = 0, type = 0, cap = 0;
  readJedecId(mfr, type, cap);

  Serial.print(F("READY JEDEC="));
  printHex2(mfr);
  printHex2(type);
  printHex2(cap);
  Serial.print(F(" EXPECT="));
  printHex2(EXPECTED_JEDEC_MFR);
  printHex2(EXPECTED_JEDEC_TYPE);
  printHex2(EXPECTED_JEDEC_CAP);
  Serial.println();
}

void loop() {
  serviceSerial();
}
