#include <Arduino.h>
#include <stdlib.h>
#include <string.h>

// Bit-banged flasher for marginal breadboard wiring.
// Keeps the same serial protocol as the existing GUI.

static const uint8_t FLASH_CS_PIN   = 10;
static const uint8_t FLASH_MOSI_PIN = 11;
static const uint8_t FLASH_MISO_PIN = 12;
static const uint8_t FLASH_SCK_PIN  = 13;

static const unsigned long SERIAL_BAUD = 250000;
static const uint32_t FLASH_SIZE_BYTES = 1048576UL;
static const uint16_t PAGE_SIZE_BYTES = 256;
static const uint8_t PROGRAM_CHUNK_BYTES = 8;

// Very slow edges for resistor dividers / long wires.
static const uint8_t HALF_CLOCK_US = 8;

static const uint8_t CMD_WREN  = 0x06;
static const uint8_t CMD_WRDI  = 0x04;
static const uint8_t CMD_RDSR  = 0x05;
static const uint8_t CMD_RDSR2 = 0x35;
static const uint8_t CMD_RDCR  = 0x15;
static const uint8_t CMD_READ  = 0x03;
static const uint8_t CMD_PP    = 0x02;
static const uint8_t CMD_CE    = 0xC7;
static const uint8_t CMD_RDID  = 0x9F;
static const uint8_t CMD_WRSR  = 0x01;
static const uint8_t CMD_RSTEN = 0x66;
static const uint8_t CMD_RST   = 0x99;

static const uint8_t EXPECTED_JEDEC_MFR = 0x85;
static const uint8_t EXPECTED_JEDEC_TYPE = 0x60;
static const uint8_t EXPECTED_JEDEC_CAP = 0x14;

static char g_lineBuffer[96];
static size_t g_lineLength = 0;
static uint8_t g_pageBuffer[PAGE_SIZE_BYTES];
static uint8_t g_verifyBuffer[PAGE_SIZE_BYTES];
static char g_lastOpError[48] = "NONE";

void setLastOpError(const char *msg) {
  strncpy(g_lastOpError, msg, sizeof(g_lastOpError) - 1);
  g_lastOpError[sizeof(g_lastOpError) - 1] = '\0';
}

void clearLastOpError() {
  setLastOpError("NONE");
}

void flashSelect() {
  digitalWrite(FLASH_CS_PIN, LOW);
  delayMicroseconds(HALF_CLOCK_US);
}

void flashDeselect() {
  delayMicroseconds(HALF_CLOCK_US);
  digitalWrite(FLASH_CS_PIN, HIGH);
  delayMicroseconds(HALF_CLOCK_US);
}

uint8_t flashXfer(uint8_t value) {
  uint8_t in = 0;
  for (uint8_t mask = 0x80; mask != 0; mask >>= 1) {
    digitalWrite(FLASH_SCK_PIN, LOW);
    digitalWrite(FLASH_MOSI_PIN, (value & mask) ? HIGH : LOW);
    delayMicroseconds(HALF_CLOCK_US);

    digitalWrite(FLASH_SCK_PIN, HIGH);
    delayMicroseconds(HALF_CLOCK_US);
    if (digitalRead(FLASH_MISO_PIN)) {
      in |= mask;
    }
  }
  digitalWrite(FLASH_SCK_PIN, LOW);
  return in;
}

void flashBeginTransaction() {
  digitalWrite(FLASH_SCK_PIN, LOW);
  flashSelect();
}

void flashEndTransaction() {
  digitalWrite(FLASH_SCK_PIN, LOW);
  flashDeselect();
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
  const uint8_t value = flashXfer(0x00);
  flashEndTransaction();
  return value;
}

uint8_t readStatus2() {
  flashBeginTransaction();
  flashXfer(CMD_RDSR2);
  const uint8_t value = flashXfer(0x00);
  flashEndTransaction();
  return value;
}

uint8_t readConfigReg() {
  flashBeginTransaction();
  flashXfer(CMD_RDCR);
  const uint8_t value = flashXfer(0x00);
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

bool writeEnable() {
  sendSimpleCommand(CMD_WREN);
  delayMicroseconds(20);
  return (readStatus1() & 0x02) != 0;
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
  if ((readStatus1() & 0x7C) == 0) {
    return true;
  }
  if (!waitWhileBusy(1000)) {
    setLastOpError("UNPROTECT_BUSY");
    return false;
  }
  if (!writeEnable()) {
    setLastOpError("UNPROTECT_WEL");
    return false;
  }
  flashBeginTransaction();
  flashXfer(CMD_WRSR);
  flashXfer(0x00);
  flashEndTransaction();
  if (!waitWhileBusy(1000)) {
    setLastOpError("UNPROTECT_TIMEOUT");
    return false;
  }
  if ((readStatus1() & 0x7C) != 0) {
    setLastOpError("UNPROTECT_STILL_LOCKED");
    return false;
  }
  clearLastOpError();
  return true;
}

bool chipErase() {
  if (!waitWhileBusy(1000)) {
    setLastOpError("ERASE_BUSY");
    return false;
  }
  if (!writeEnable()) {
    setLastOpError("ERASE_WEL");
    return false;
  }
  flashBeginTransaction();
  flashXfer(CMD_CE);
  flashEndTransaction();
  const uint8_t sr1AfterCmd = readStatus1();
  if ((sr1AfterCmd & 0x01) == 0) {
    setLastOpError("ERASE_NOT_ACCEPTED");
    return false;
  }
  if (!waitWhileBusy(10000)) {
    setLastOpError("ERASE_TIMEOUT");
    return false;
  }
  clearLastOpError();
  return true;
}

bool pageProgram(uint32_t address, const uint8_t *src, uint16_t length) {
  if (length == 0 || length > PAGE_SIZE_BYTES) {
    setLastOpError("PP_LENGTH");
    return false;
  }
  if ((address + length) > FLASH_SIZE_BYTES) {
    setLastOpError("PP_RANGE");
    return false;
  }
  if (((address & 0xFFu) + length) > PAGE_SIZE_BYTES) {
    setLastOpError("PP_BOUNDARY");
    return false;
  }
  if (!waitWhileBusy(1000)) {
    setLastOpError("PP_BUSY");
    return false;
  }
  if (!writeEnable()) {
    setLastOpError("PP_WEL");
    return false;
  }

  flashBeginTransaction();
  flashXfer(CMD_PP);
  flashXfer((address >> 16) & 0xFF);
  flashXfer((address >> 8) & 0xFF);
  flashXfer(address & 0xFF);
  for (uint16_t i = 0; i < length; ++i) {
    flashXfer(src[i]);
  }
  flashEndTransaction();

  const uint8_t sr1AfterCmd = readStatus1();
  if ((sr1AfterCmd & 0x01) == 0) {
    setLastOpError("PP_NOT_ACCEPTED");
    return false;
  }
  if (!waitWhileBusy(1000)) {
    setLastOpError("PP_TIMEOUT");
    return false;
  }
  clearLastOpError();
  return true;
}

bool verifyBytes(uint32_t address, const uint8_t *expected, uint16_t length, uint16_t &badOffset, uint8_t &got, uint8_t &want) {
  readBytes(address, g_verifyBuffer, length);
  for (uint16_t i = 0; i < length; ++i) {
    if (g_verifyBuffer[i] != expected[i]) {
      badOffset = i;
      got = g_verifyBuffer[i];
      want = expected[i];
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
  if (value < 0x10) Serial.print('0');
  Serial.print(value, HEX);
}

void printHex8(uint32_t value) {
  for (int shift = 28; shift >= 0; shift -= 4) {
    Serial.print((value >> shift) & 0x0F, HEX);
  }
}

void printInfoLine() {
  uint8_t mfr = 0, type = 0, cap = 0;
  readJedecId(mfr, type, cap);
  Serial.print(F("INFO SIZE="));
  Serial.print(FLASH_SIZE_BYTES);
  Serial.print(F(" JEDEC="));
  printHex2(mfr); printHex2(type); printHex2(cap);
  Serial.print(F(" SR1=")); printHex2(readStatus1());
  Serial.print(F(" SR2=")); printHex2(readStatus2());
  Serial.print(F(" CR=")); printHex2(readConfigReg());
  Serial.println();
}

void printError(const __FlashStringHelper *msg) {
  Serial.print(F("ERR "));
  Serial.println(msg);
}

void printDetailedVerifyFail(uint32_t address, uint16_t offset, uint8_t want, uint8_t got) {
  Serial.print(F("ERR VERIFY_FAIL ADDR=0x"));
  printHex8(address + offset);
  Serial.print(F(" PAGE=0x"));
  printHex8(address);
  Serial.print(F(" OFF=0x"));
  printHex2((uint8_t)offset);
  Serial.print(F(" EXP=0x"));
  printHex2(want);
  Serial.print(F(" GOT=0x"));
  printHex2(got);
  Serial.print(F(" SR1=0x"));
  printHex2(readStatus1());
  Serial.print(F(" SR2=0x"));
  printHex2(readStatus2());
  Serial.print(F(" CR=0x"));
  printHex2(readConfigReg());
  Serial.println();
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

  for (uint16_t chunkStart = 0; chunkStart < length; chunkStart += PROGRAM_CHUNK_BYTES) {
    const uint16_t chunkLen = (uint16_t)min((uint16_t)PROGRAM_CHUNK_BYTES, (uint16_t)(length - chunkStart));
    bool wrote = false;
    for (uint8_t attempt = 1; attempt <= 3; ++attempt) {
      clearLastOpError();
      if (pageProgram(address + chunkStart, g_pageBuffer + chunkStart, chunkLen)) {
        wrote = true;
        break;
      }
      delay(5);
    }
    if (!wrote) {
      Serial.print(F("ERR WRITE_FAIL REASON="));
      Serial.print(g_lastOpError);
      Serial.print(F(" CHUNK_OFF=0x"));
      printHex2((uint8_t)chunkStart);
      Serial.print(F(" CHUNK_LEN="));
      Serial.print(chunkLen);
      Serial.print(F(" SR1=0x")); printHex2(readStatus1());
      Serial.print(F(" SR2=0x")); printHex2(readStatus2());
      Serial.print(F(" CR=0x")); printHex2(readConfigReg());
      Serial.println();
      return;
    }
  }

  uint16_t badOffset = 0;
  uint8_t got = 0;
  uint8_t want = 0;
  if (!verifyBytes(address, g_pageBuffer, length, badOffset, got, want)) {
    printDetailedVerifyFail(address, badOffset, want, got);
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
      Serial.print(F("ERR UNPROTECT_FAIL REASON="));
      Serial.print(g_lastOpError);
      Serial.print(F(" SR1=0x")); printHex2(readStatus1());
      Serial.print(F(" SR2=0x")); printHex2(readStatus2());
      Serial.print(F(" CR=0x")); printHex2(readConfigReg());
      Serial.println();
      return;
    }
    Serial.println(F("OK"));
    return;
  }
  if (strcmp(line, "ERASE_CHIP") == 0) {
    if (!chipErase()) {
      Serial.print(F("ERR ERASE_FAIL REASON="));
      Serial.print(g_lastOpError);
      Serial.print(F(" SR1=0x")); printHex2(readStatus1());
      Serial.print(F(" SR2=0x")); printHex2(readStatus2());
      Serial.print(F(" CR=0x")); printHex2(readConfigReg());
      Serial.println();
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
    printHex2(mfr); printHex2(type); printHex2(cap);
    Serial.println();
    return;
  }
  printError(F("UNKNOWN_CMD"));
}

void serviceSerial() {
  while (Serial.available() > 0) {
    const char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      g_lineBuffer[g_lineLength] = '\0';
      if (g_lineLength > 0) processLine(g_lineBuffer);
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
  pinMode(FLASH_MOSI_PIN, OUTPUT);
  pinMode(FLASH_MISO_PIN, INPUT);
  pinMode(FLASH_SCK_PIN, OUTPUT);

  digitalWrite(FLASH_CS_PIN, HIGH);
  digitalWrite(FLASH_SCK_PIN, LOW);
  digitalWrite(FLASH_MOSI_PIN, LOW);

  Serial.begin(SERIAL_BAUD);
  delay(50);
  softwareResetFlash();
  waitWhileBusy(1000);

  uint8_t mfr = 0, type = 0, cap = 0;
  readJedecId(mfr, type, cap);
  Serial.print(F("READY JEDEC="));
  printHex2(mfr); printHex2(type); printHex2(cap);
  Serial.print(F(" EXPECT="));
  printHex2(EXPECTED_JEDEC_MFR); printHex2(EXPECTED_JEDEC_TYPE); printHex2(EXPECTED_JEDEC_CAP);
  Serial.print(F(" BITBANG=1 HALF_US="));
  Serial.println(HALF_CLOCK_US);
}

void loop() {
  serviceSerial();
}
