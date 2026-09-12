/*
 * spi_flasher.ino
 *
 * Milestone 1: PC <-> Arduino serial handshake + runtime pin configuration
 * Milestone 2: Bit-banged SPI primitives (CS assert/deassert, byte transfer)
 *
 * Protocol (ASCII, newline-terminated, case-sensitive):
 *
 *   PING
 *     -> PONG
 *
 *   CONFIG,<cs>,<sclk>,<mosi>,<miso>
 *     Sets the four GPIO pin numbers used for bit-banged SPI.
 *     Pins must be distinct and within 2-13 (0/1 reserved for serial RX/TX).
 *     -> CONFIG_OK
 *     -> CONFIG_ERR:<reason>
 *
 *   XFER,<hexbytes>
 *     Asserts CS, clocks out each byte (MSB first, SPI mode 0),
 *     deasserts CS, and returns the bytes clocked in during the same
 *     transfer. <hexbytes> is a contiguous hex string, e.g. "9F0000".
 *     -> XFER_OK:<hexresponse>
 *     -> XFER_ERR:NOT_CONFIGURED   (if CONFIG hasn't been sent yet)
 *     -> XFER_ERR:BAD_HEX          (odd-length or non-hex input)
 *
 *   READ,<addr_hex6>,<len_decimal>
 *     Issues the flash's 0x03 READ command at the given 24-bit address
 *     and streams back <len_decimal> bytes as hex, followed by a
 *     16-bit rotate-XOR checksum (4 hex digits) so the PC can detect
 *     serial transmission corruption and retry just that chunk.
 *     Response is not buffered in RAM - bytes are printed as they're
 *     clocked off the chip, so len is bounded by READ_MAX_LEN below,
 *     not by SRAM.
 *     -> READ_OK:<hexdata>,<hexchecksum>
 *     -> READ_ERR:NOT_CONFIGURED
 *     -> READ_ERR:PARSE
 *     -> READ_ERR:LEN_RANGE        (len == 0 or len > READ_MAX_LEN)
 *
 * This sketch intentionally has no knowledge of flash-chip commands
 * (0x9F, 0x03, 0x02, etc). XFER is a generic pass-through so all
 * protocol-level logic (JEDEC ID, read, program, erase - Milestones
 * 3-6) lives in the PC app and can be changed without reflashing.
 *
 * SRAM note: lineBuf (550B) + the largest local buffer (260B, only
 * live during handleXfer) comfortably fit an ATmega328's 2KB SRAM
 * alongside Serial's own buffers. If porting to a smaller MCU, this
 * is the first place to look.
 */

#include <Arduino.h>

// Defaults match the wiring in the published guide:
// 13=MISO, 12=CS, 11=SCLK, 10=MOSI, 3.3V=VCC/WP/HOLD, GND=GND
uint8_t pinCS = 12;
uint8_t pinSCLK = 11;
uint8_t pinMOSI = 10;
uint8_t pinMISO = 13;
bool configured = false;

const uint16_t MAX_XFER_BYTES = 260;  // 1 cmd + 3 addr + 256 data (full page program)
const unsigned long READ_MAX_LEN = 65536UL;  // 64KB hard cap per READ call
char lineBuf[550];  // "XFER," + up to 520 hex chars (260 bytes) + margin

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* wait for USB serial on boards that need it */ }
}

void loop() {
  if (readLine(lineBuf, sizeof(lineBuf))) {
    handleLine(lineBuf);
  }
}

// ---------- Serial line reader ----------

bool readLine(char *buf, size_t bufSize) {
  static size_t idx = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (idx == 0) continue;  // ignore stray CR/LF
      buf[idx] = '\0';
      idx = 0;
      return true;
    }
    if (idx < bufSize - 1) {
      buf[idx++] = c;
    }
  }
  return false;
}

// ---------- Command dispatch ----------

void handleLine(char *line) {
  if (strcmp(line, "PING") == 0) {
    Serial.println("PONG");
    return;
  }

  if (strncmp(line, "CONFIG,", 7) == 0) {
    handleConfig(line + 7);
    return;
  }

  if (strncmp(line, "XFER,", 5) == 0) {
    handleXfer(line + 5);
    return;
  }

  if (strncmp(line, "READ,", 5) == 0) {
    handleRead(line + 5);
    return;
  }

  Serial.println("ERR:UNKNOWN_CMD");
}

void handleConfig(char *args) {
  int cs, sclk, mosi, miso;
  int n = sscanf(args, "%d,%d,%d,%d", &cs, &sclk, &mosi, &miso);
  if (n != 4) {
    Serial.println("CONFIG_ERR:PARSE");
    return;
  }

  int pins[4] = {cs, sclk, mosi, miso};
  for (uint8_t i = 0; i < 4; i++) {
    if (pins[i] < 2 || pins[i] > 13) {
      Serial.println("CONFIG_ERR:RANGE");
      return;
    }
    for (uint8_t j = i + 1; j < 4; j++) {
      if (pins[i] == pins[j]) {
        Serial.println("CONFIG_ERR:COLLISION");
        return;
      }
    }
  }

  pinCS = cs;
  pinSCLK = sclk;
  pinMOSI = mosi;
  pinMISO = miso;

  pinMode(pinCS, OUTPUT);
  pinMode(pinSCLK, OUTPUT);
  pinMode(pinMOSI, OUTPUT);
  pinMode(pinMISO, INPUT);

  digitalWrite(pinCS, HIGH);   // deasserted
  digitalWrite(pinSCLK, LOW);  // SPI mode 0 idle state
  digitalWrite(pinMOSI, LOW);

  configured = true;
  Serial.println("CONFIG_OK");
}

void handleXfer(char *hex) {
  if (!configured) {
    Serial.println("XFER_ERR:NOT_CONFIGURED");
    return;
  }

  size_t hexLen = strlen(hex);
  if (hexLen == 0 || hexLen % 2 != 0 || hexLen / 2 > MAX_XFER_BYTES) {
    Serial.println("XFER_ERR:BAD_HEX");
    return;
  }

  uint8_t outBytes[MAX_XFER_BYTES];
  size_t n = hexLen / 2;
  for (size_t i = 0; i < n; i++) {
    int hi = hexNibble(hex[i * 2]);
    int lo = hexNibble(hex[i * 2 + 1]);
    if (hi < 0 || lo < 0) {
      Serial.println("XFER_ERR:BAD_HEX");
      return;
    }
    outBytes[i] = (hi << 4) | lo;
  }

  Serial.print("XFER_OK:");
  csAssert();
  for (size_t i = 0; i < n; i++) {
    uint8_t in = spiTransfer(outBytes[i]);
    printHexByte(in);
  }
  csDeassert();
  Serial.println();
}

void handleRead(char *args) {
  if (!configured) {
    Serial.println("READ_ERR:NOT_CONFIGURED");
    return;
  }

  char addrStr[7];
  unsigned long len;
  int n = sscanf(args, "%6[0-9A-Fa-f],%lu", addrStr, &len);
  if (n != 2) {
    Serial.println("READ_ERR:PARSE");
    return;
  }
  if (len == 0 || len > READ_MAX_LEN) {
    Serial.println("READ_ERR:LEN_RANGE");
    return;
  }

  unsigned long addr = strtoul(addrStr, NULL, 16);

  Serial.print("READ_OK:");
  csAssert();
  spiTransfer(0x03);                    // flash READ command
  spiTransfer((addr >> 16) & 0xFF);
  spiTransfer((addr >> 8) & 0xFF);
  spiTransfer(addr & 0xFF);
  uint16_t checksum = 0;
  for (unsigned long i = 0; i < len; i++) {
    uint8_t b = spiTransfer(0x00);      // dummy byte out, data in
    printHexByte(b);
    // Rotate-left-1 then XOR in the byte. Cheap on an 8-bit MCU and
    // sensitive to both value changes and byte reordering, which a
    // plain additive checksum would miss.
    checksum = ((checksum << 1) | (checksum >> 15)) ^ b;
  }
  csDeassert();
  Serial.print(",");
  printHexByte((checksum >> 8) & 0xFF);
  printHexByte(checksum & 0xFF);
  Serial.println();
}

int hexNibble(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

void printHexByte(uint8_t b) {
  const char *hexDigits = "0123456789ABCDEF";
  Serial.print(hexDigits[(b >> 4) & 0x0F]);
  Serial.print(hexDigits[b & 0x0F]);
}

// ---------- Bit-banged SPI primitives (Milestone 2) ----------

void csAssert() {
  digitalWrite(pinCS, LOW);
}

void csDeassert() {
  digitalWrite(pinCS, HIGH);
}

// SPI Mode 0: clock idles low, data sampled on rising edge, MSB first.
uint8_t spiTransfer(uint8_t out) {
  uint8_t in = 0;
  for (int8_t i = 7; i >= 0; i--) {
    digitalWrite(pinMOSI, (out >> i) & 0x01);
    digitalWrite(pinSCLK, HIGH);
    in = (in << 1) | digitalRead(pinMISO);
    digitalWrite(pinSCLK, LOW);
  }
  return in;
}
