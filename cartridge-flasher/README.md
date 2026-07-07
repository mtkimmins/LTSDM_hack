#TODO
- count the jumper wires, insert #
- make LTSDM-specific wiring diagram for a resistor divider, upload, link
- verify formatting on github

# Official Documentation of the LTSDM Cartridge Flasher
*The aim of this documentation is to explain this build so simply that a kid could build it like Legos. To report ambiguity, please submit an issue to [the github](https://github.com/mtkimmins/LTSDM_hack/issues/new).*

## Resources Used
### Software
- Linux Ubuntu LTS (as operating system)
- Arduino IDE (for arduino upload)
- VSCode (for scripts)

### Hardware
- Arduino Uno 3 (ch340-based clone; idVendor=1a86, idProduct=7523) (x1)
- Arduino-PC USB cable (x1)
- [LTSDM port](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/Projector_disassembly/cartridge%20edge%20adapter.JPG) (proprietary component scavenged from an LTSDM projector; the black plastic port that interfaces with the wires and cartridge PCB fingers; its a black plastic port that fits the PCB edge and breaks it out into 8 headers, 1 per finger) (x1)
- Breadboard (x1)
- jumper wires
    - female-male (arduino-breadboard; LTSDM port-breadboard) (x#)
    - male-male (breadboard-breadboard) (x#)
- 1k ohm resistors (x3)
- 2k ohm resistors (x6)
- intact LTSDM cartridge (x1)

---

## Circuitry Wiring
### P25D80SH PCB
It is important to note that the P25D80SH chip is the black integrated circuit (IC) that sits on the topside of the green PCB inside the cartridge housing. The cartridge uses the PCB's golden fingers to conduct electrical information from the embedded chip (IC) and the projector.

#### **PINOUT** for P25D80SH *PCB*
> [!NOTE]
> For the description below, the PCB orientation is with (1) the golden fingers pointing toward you, (2) the black IC chip facing up, and (3) this position is held when describing both the top-face and bottom-face.
> The [PCB is in this orientation](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/CartridgeDissassembly/orientation_of_pcb.JPG) when the cartridge casing is (1) pointing the PCB golden fingers toward you, and (2) the book's cover label is face-down.The PCB golden fingers are DIFFERENT than the [pinout of the chip](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/Chips/P25D80SH.pdf).

**Table 1. PCB Golden Finger Pinout**
||LEFT|||RIGHT|
|:-:|:-:|:-:|:-:|:-:|
|TOP-FACE|MISO|CS*|SLCK*|MOSI*|
|BOTTOM-FACE|WP/HOLD/VCC|WP/HOLD/VCC|GND|GND|

*\*must use resistor dividers*

### Resistor Dividers
> [!CAUTION]
> Running 5V (PC USB voltage) through the P25D80SH will **fry the chip** making it potentially unusable.

Resistor dividers are essential (but not the only option, see *level shifters*) for the protection and proper operation (dump/flash) of the P25D80SH chip. The following P25D80SH pins need to be connected to the arduino through resistor dividers: **MOSI**, **SLCK**, and **CS**.

**Figure 1. Diagram of a Resistor Divider in the Context of the LTSDM Project**
![]()

Resistor dividers are partitioned into the "top resistor" and "bottom resistor." In the LTSDM project, we are reducing the voltage from the arduino pins (coming out at 5V; too high for the P25D80SH) to the operational ~3.3V.

Our top resistor (R1) = 2k ohms

Our bottom resistor (R2) = 3k ohms (direct chaining a 2k and a 1k ohm resistors together).

This resistor divider produces a current of 3.0V, which is sufficient for the P25D80SH to operate.

### Arduino Pinout
We will use the following pins on the arduino:
- GND
- 3.3V
- PIN 10 through PIN 13
*the pinout is explicitely labeled on my arduino's PCB; Check your arduino's/microcontroller's datasheet if unsure*

> [!NOTE]
> Pins 10 through 13 output electricity at 5.0V, thus the need for resistor dividers despite there also being an actual *3.3V* pin. One cannot run all the P25D80SH pins through a single 3.3V arduino pin.

**Table 2. Arduino-P25D0SH-Divider Mapping**
|P25D80SH pin|Arduino pin|Divider required?|
|:-:|:-:|:-:|:-:|
|CS (Chip Select)|Arduino pin 10|YES|
|MOSI (SI)|11|YES|
|MISO (SO)|12|NO|
|SCLK (SCK)|13|YES|
|GND|GND|NO|
|VCC/HOLD/WP|3.3V|NO|

---

## Flasher GUI


---

## Milestones
TIER 0 — Hardware safety gate (must pass before ANY wiring)
 [0] Voltage-domain check: confirm 3.3V logic on chip, plan level-shifting
      └─> feeds: 1, 2

TIER 1 — Physical wiring
 [1] Build 3.3V rail for chip VCC (Uno's onboard 3.3V pin, NOT the 5V pin)
 [2] Level-shift Uno→chip lines (CS, SCK, MOSI, WP#, HOLD#); MISO chip→Uno can go direct
      └─> feeds: 3, 4

TIER 2 — Link verification (your requirement #1 and #2)
 [3] Arduino ⟷ PC serial link verified   (PING/PONG handshake)
 [4] Arduino ⟷ chip electrical link verified (JEDEC ID read ≠ 0x00/0xFF)
      └─> [3] feeds: 5, 7, 9   |   [4] feeds: 5

TIER 3 — Read path
 [5] Single-block READ command working (addr, len) → hex payload over serial
      └─> feeds: 6

TIER 4 — Requirement #3: verified dump
 [6] Full-chip dump loop with double-read compare + retry/majority-vote on mismatch
      └─> feeds: 10

TIER 5 — Write path (each depends on the read path existing, for verify)
 [7] STATUS/WIP polling + WRITE ENABLE handling
 [8] ERASE (sector/chip) using [7]
 [9] PAGE PROGRAM (256B) using [7]
      └─> [8],[9] feed: 10 (need [5] too, for readback verify)

TIER 6 — Requirement #4: flash + verify
 [10] Erase→flash→read-back-verify orchestration for custom .bin

TIER 7 — Integration
 [11] GUI ties 3,4,6,10 into one workflow with logging + abort-safety
 [12] End-to-end test: dump stock cartridge → hash it → flash test pattern → dump again → diff