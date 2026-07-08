#TODO
- make LTSDM-specific wiring diagram for a resistor divider, upload, link
- count the jumper wires, insert #
- upload all pictures
- verify formatting on github

# Official Documentation of the LTSDM Cartridge Flasher
*The aim of this documentation is to explain this build so simply that a kid could build it like Legos. To report ambiguity, please submit a question to [the github](https://github.com/mtkimmins/LTSDM_hack/discussions/new?category=q-a).*

## Forword
This is certainly not the only way to set up a communication channel with a cartridge ([see John-K's repo](https://github.com/John-K/LittleTikesDreamProjector)). For my own sanity, I will document a validated setup guide to at least get to where I am now, and as a way to "save" my progress more consistently.

---

## Resources Used
### Software
- Linux Ubuntu LTS (as operating system)
- Arduino IDE (for arduino upload)
- VSCode (for scripts)

### Hardware
- A multimeter with continuity testing ability
- Arduino Uno 3 (ch340-based clone; idVendor=1a86, idProduct=7523) (x1)
- Arduino-PC USB cable (x1)
- [8-Pin Card Edge Connector Socket](https://www.amazon.ca/PATIKIL-Connector-Straight-Connection-Circuit/dp/B0BPP6SVRD/ref=sr_1_1?crid=3SD5X5ZE4ARQY&dib=eyJ2IjoiMSJ9.GwywV7adNi4bYUKEnAmGwoi8Cj8R3xQ3hvfNcI7W1madQKybneZVJFmq_3QhZo086ZvpuwppzLwyx6cfYAMdagSz5YL3-p-RojX36wqo8GypOTVAj7BMh5GIyDzsTaOAU-L_v80p04X8ua0dWKxLngkS3MxeEbEbiH5x128v1e374qnpxnPub5-HPgonC0trm6rC3z-6e7B--lGVDYiN8Be14Cu1KETValOcx9J17ZRbT8I3pXa4jVzpdIFKeaZ9g2AUtCnL3m9RfMJd97r5HF1W6BG37RwkVGqBGhRbx-U.Is_Ho0oJNT0eKuzeMnKd80bbB8Ou6U4z0QKUGB79-yI&dib_tag=se&keywords=PATIKIL+Card+Edge+Connector+Black+Socket+Straight+Connection+8+Pin+2.54mm+Pitch+for+PCB+Circuit+Board%2C+Game+Console%2C+Pack+of+5&qid=1783467357&sprefix=patikil+card+edge+connector+black+socket+straight+connection+8+pin+2+54mm+pitch+for+pcb+circuit+board%2C+game+console%2C+pack+of+5%2Caps%2C132&sr=8-1) (Thanks to [John-K](https://github.com/John-K) for finding this part in the wild) (x1)
- Breadboard/Protoboard (x1)
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
> The [PCB is in this orientation](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/CartridgeDissassembly/orientation_of_pcb.JPG) when the cartridge casing is (1) pointing the PCB golden fingers toward you, and (2) the book's cover label is face-down.The PCB golden fingers are DIFFERENT than the [pinout of the chip](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/Chips/P25D80SH.pdf). See [John-K's repository](https://github.com/John-K/LittleTikesDreamProjector) for further clarification.

**PCB Golden Finger Pinout**
||LEFT|||RIGHT|
|:-:|:-:|:-:|:-:|:-:|
|TOP-FACE|MISO|CS*|SLCK*|MOSI*|
|BOTTOM-FACE|WP/HOLD/VCC|WP/HOLD/VCC|GND|GND|

*\*must use resistor dividers*

Despite there being two sets of two bottom-facing fingers with WP/HOLD/VCC and GND, **both P25D80SH GND fingers must be connected to the arduino GND.

### Resistor Dividers
> [!CAUTION]
> Running 5V (PC USB voltage) through the P25D80SH will **fry the chip** making it potentially unusable.

Resistor dividers are essential (but not the only option, see *level shifters*) for the protection and proper operation (dump/flash) of the P25D80SH chip. The following P25D80SH pins need to be connected to the arduino through resistor dividers: **MOSI**, **SLCK**, and **CS**.

**Diagram of a Resistor Divider in the Context of the LTSDM Project**
![]()

Resistor dividers are partitioned into the "top resistor" and "bottom resistor." In the LTSDM project, we are reducing the voltage from the arduino pins (coming out at 5V; too high for the P25D80SH) to the operational ~3.3V.

Our top resistor (R1) = 2k ohms

Our bottom resistor (R2) = 3k ohms (direct chaining a 2k ohm resistor and a 1k ohm resistor together in series).

This resistor divider produces a current of about 3.0V, which is sufficient for the P25D80SH to operate.

### Arduino Pinout
For convention, one may use the following pins on the arduino:
- GND
- 3.3V
- PIN 10 through PIN 13 (this choice and assignment is largely arbitrary)
*the pinout is physically labeled on my arduino's PCB making the wiring much easier; Check your arduino's/microcontroller's datasheet if unsure of its pinout.*

> [!NOTE]
> Pins 10 through 13 output electricity at 5.0V, thus the need for resistor dividers despite there also being an actual *3.3V* pin. One cannot run all the P25D80SH pins through a single 3.3V arduino pin.

**Arduino-P25D0SH-Divider Mapping**
|P25D80SH pin|Arduino pin|Divider required?|
|:-:|:-:|:-:|:-:|
|CS (Chip Select)|Arduino pin 10|YES|
|MOSI (SI)|11|YES|
|MISO (SO)|12|NO|
|SCLK (SCK)|13|YES|
|GND|GND|NO|
|VCC/HOLD/WP|3.3V|NO|

---

## Hardware Setup Guide
**Full Circuit Diagram**
![]()

### Breadboard or Protoboard
Home circuity has been a messy endeavour, but using breadboards and then protoboards has connected the worlds of electronics and programming for me. Although I am quite awful with soldering, it has helped move this project along significantly even at my toddler-grade work. Consider soldering if connectivity is a bothersome issue. Alternatively, a solderless plastic breadboard is best to minimize health risk.

> [!WARNING]
> Have a responsible adult to supervise children operating soldering equipment. Soldering poses several health threats such as toxic fumes, physical contact with lead, and scalding-hot metal. Refer to a comprehensive soldering guide before attempting.

**Photo of One Plastic Breadboard (middle) and Two Protoboards**
![](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/WiringSetup/official-guide/boards.JPG)

### Adding the Cartridge Socket
**Photo of Socket and Header Pins**
![Upright](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/WiringSetup/official-guide/socket-up.JPG)  
![Upside-down](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/WiringSetup/official-guide/socket-down.JPG)

Originally, I had thought that this part was a proprietary piece of electronics. For mine, I bought an entire other projector off Amazon, gutted it, and stole its socket. Months later, I read in John-K's documentation that one may buy these sockets off Amazon by the handful. Either approach works as evident by both our repositories. As noted by John-K, the width of this socket is not sufficient by default to interface with most breadboards and protoboards, thus the pins may be bent to accomodate the extra width required.

**Photo of 8-pin Socket in Breadboard**
![](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/WiringSetup/official-guide/placed-socket.JPG)

**Photo of Soldered Socket in Protoboard**
![](https://github.com/mtkimmins/LTSDM_hack/blob/main/Images/WiringSetup/official-guide/soldered-socket.JPG)

#### Checking Electrical Continuity
In order to ensure that the socket works and is securely connected to the breadboard/protoboard a multimeter should be used to perform a continuity test on each of the socket's pins. If the socket passes the 

For breadboards one could use *header pins* to allow the multimeter leads to connect with the socket and the breadboard. Potentially, using two headers on either end of the breadboard's breakout rows can verify the validity of the *header pins* themselves. A disadvantage to plastic breadboards is the possibility of components shifting and slipping causing momentary or hidden circuit breaks.

For protoboards one could use the above-described "breadboard method," however, protoboards have the advantage over breadboards in that they can be soldered to hold components in place and increase the chance of a complete circuit connection. An additional advantage of a protoboard over a breadboard is that often the breakout rows are exposed versus on a conventional breadboard, thus allowing one to continuity test without *header pins*.

### Inserting the Cartridge, and Cartridge Orientation
One may notice that once the socket is placed on the board the LTSDM cartridge can be plugged in two conformations. Only 1 conformation will work -- they are not interchangeable as the P25D80SH pins will be flipped. This is where the builder must choose what orientation they would like their cartridge to fit into their socket. It is recommended to make a marking on the board and cartridge that align them properly.

**Photo of Cartridge in Socket**
![]()

### Resistor Dividers
As illustrated above, resistor dividers are used to reduce the voltage sent out of the arduino and into the P2D80SH chip. This protects the chip and allows it to function properly where it sends out signals classified in two states, "high" and "low."

**Photo of One Resistor Divider**
![]()

Ground (GND) will not need a divider as it receives any voltage of electricity sent through. Similarly, "master-in-slave-out" (MISO) will also conduct the output of the P25D80SH which will be within its tolerated 3.3V window by default. There also exists one 3.3V port on the arduino which can be used for the WP/HOLD/VCC. This leaves three P25D80SH pins: "master-out-slave-in (MOSI), "clock" (SCLK), and "chip select" (CS) to be reduced by resistor dividers. Three pins means three separate resistor dividers. One must connect each of those pins to a resistor divider *before* the arduino, thus positioning the resistor divider in the obligatory middle between the P25D80SH chip and the arduino.

**Photo of All Three Resistor Dividers**
![]()

To connect the P25D80SH chip pin to a resistor divider, one may use *jumper wires* to allow electricity to pass from the pin breakout row to the appropriate position in the resistor divider. The position of jumper wire connection *does* matter, so following the circuit diagram above as well as observing the reference photos may be of help.

**Photo of Chip-Resistor Divider Connection**
![]()

**Photo of All Chip-Resistor Divider Connections**
![]()

### Arduino-P25D80SH Connection
#### Resistor Dividers to Arduino
**Photo of Resistor Divider Connection to an Arbitrary Arduino Pin**
![]()

#### Direct Connections Between P25D80SH and Arduino
**Photo of Direct Connection Between P2D80SH and an Arbitrary Arduino Pin**
![]()

#### Complete Connection
**Photo of Physical Complete Connection Build**
![]()

For a technical building overview, refer to the "Full Circuit Diagram" above.

### Arduino-PC Connection
In order to control the flow of electricity (and thus information) one must plug in the Arduino to a PC where one can compile and upload a script the arduino may execute to push and pull data from the cartridge. Plug in the microcontroller to the PC.

**Photo of Arduino-PC Cable**
![]()


### Conclusion
Congratulations! The physical build is completed. The rest of the guide will reference the software used to interact with the P25D80SH chip.

**Photo of Overall Build**
![]()

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