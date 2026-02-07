<h1 align="center">
  Little Tikes Story Dream Machine (LTSDM)
  <br>
  Cartridge Reverse Engineering
</h1>
<div align="center">
  Creating custom stories for Little Tikes Story Dream Machine
  <br><br>
  
  [![Status](https://img.shields.io/badge/Status-Work_in_Progress-orange)]()
  [![License](https://img.shields.io/badge/License-GPL--3.0-blue)]()

  <b>It is not yet possible to create custom stories.</b>

  <br>
  
  ## ⚠️ DISCLAIMER ⚠️ 
  This repository is for <b>educational, non-commercial use only</b>. The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user. Please do not use this information to create or sell unauthorized commercial products.
</div>

---

## Directory
  [![QCDF](https://img.shields.io/badge/Repository-Forum-blue)](https://github.com/mtkimmins/LTSDM_hack)  
  [![Wiki](https://img.shields.io/badge/Wiki-Home-green)](https://github.com/mtkimmins/LTSDM_hack/wiki/)



---
Links to similar projects:
* [GainSec](https://github.com/GainSec/Little-Tikes-DreamProjector-Reverse-Engineering)
* [John-K](https://github.com/John-K/LittleTikesDreamProjector/)

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
## Keywords
Little Tikes Story Dream Machine, LTSDM, custom cartridge, SPI flash, P25D80SH, reverse engineering, file format, ADPCM, audio extraction, embedded, Arduino.
