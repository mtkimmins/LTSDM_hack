# LTSDM_hack — Little Tikes Story Dream Machine (LTSDM) Cartridge Reverse Engineering

Reverse engineering the **Little Tikes Story Dream Machine** cartridge format (SPI flash dumps), with tooling and notes for **data dumping**, **format analysis**, and **audio/asset extraction**.

> **Scope & ethics:** This project focuses on **interoperability, preservation, and research**. It does **not** provide instructions intended to bypass access controls for infringing distribution. Use your own hardware and legally obtained media.

<nav>
  <a href="https://github.com/mtkimmins/LTSDM_hack/discussions">Questions, Comments, Discussion, & Forum</a><br>
  <a href="https://github.com/mtkimmins/LTSDM_hack/wiki/Working-Developer-Log">The Developer Log</a><br>
  <a href="https://github.com/mtkimmins/LTSDM_hack/wiki/File-Structure-Analysis">Cartridge Data Structure</a><br>
</nav>

⚠️ DISCLAIMER ⚠️

This repository is for **educational, non-commercial use only**.  
The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user.  
Please do not use this information to create or sell unauthorized commercial products.

---

## PROJECT STATUS: 
### ⏳ **Work in Progress** ⏳

**The Goal:** To create our own custom story cartridges for our kids.
This project is currently in the **reverse-engineering phase** actively figuring out data patterns.

**It is not yet possible to create custom stories.**

---

## What this Repository Contains
- **Cartridge dumping** workflows (noise reduction, repeatability, verification)
- **Container/region parsing** + documented hypotheses about pointers/regions/maps
- **Audio pipeline experiments** (e.g., suspected ADPCM/codec investigations)
- **Hardware notes** for reading cartridges (breakouts/shields, wiring, voltage sanity)

---
## Directory
>### **I'm a Parent & I Want to Use This**
>* **[Getting Started Guide](https://github.com/mtkimmins/LTSDM_hack/wiki/Getting-Started-Guide)**
>* **[Questions, Comments, Discussion & Forum](https://github.com/mtkimmins/LTSDM_hack/discussions)**

### **I'm a Maker/Developer & I Want to Help**
* **[Technical Deep Dive](https://github.com/mtkimmins/LTSDM_hack/wiki/Technical-Specifications)** (Chip info, physical measurements, etc.)
* **[The Developer Log](https://github.com/mtkimmins/LTSDM_hack/wiki/Working-Developer-Log)** (A detailed history log of the project)
* **[Cartridge Data Structure](https://github.com/mtkimmins/LTSDM_hack/wiki/File-Structure-Analysis)** (Data structure, data template, etc.)
* **[Open Issues](https://github.com/mtkimmins/LTSDM_hack/issues)** (Current "To Do" List)

---
## How to contribute

If you can help with any of the following, you’re extremely useful:
- additional **cartridge dumps** (with hashes + metadata)
- **format validation** (pointer table / region boundaries)
- codec identification (ADPCM variants, framing, sample rates)
- firmware analysis / instrumentation notes

To start: open an Issue with what you’re testing


---
## Keywords (for search)
Little Tikes Story Dream Machine, LTSDM, custom cartridge, SPI flash, P25D80SH, reverse engineering, file format, ADPCM, audio extraction, embedded, Arduino.