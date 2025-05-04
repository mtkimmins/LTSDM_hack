# A JOURNEY TO HACK A "LITTLE TIKES STORY DREAM MACHINE" BOOK CARTRIDGE - customizing existing book cartridges


[!] DISCLAIMER [!]

This repository is for **educational, non-commercial use only**.  
No proprietary or copyrighted content is distributed.

The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user.

Please do not use this information to create or sell unauthorized commercial products.

Do not share the following directly to the public:
- your personal .bin extraction data at any stage of analysis
- microscopic decapping images

---
# TO DO LIST:
- get equipment to read and datadump
- watch whole set of "junk" cartridges
  - record number of frames used
  - record script
  - record description of each frame
- determine how to open a cartridge without damaging the case or components
- determine how to re-close a cartridge without damaging the case or components
- Datadump all 3 cartridges in the "junk" set
  - open a cartridge with heat or solvent
  - document inside chip (photos and text)
  - connect an ESP32 to the breadboard
  - ??? configure the ESP32 power and data lines appropriately
    - use 3.3V only (CHATGPT SUGGESTION)
    - use capacitors on breadboard between ESP32 and the SOIC8 clip for voltage stability - flash usb is very sensitive to voltage changes, readonly mode also voltage-dependant (CHATGPT SUGGESTION)
  - power on ESP32 via USB-computer
  - create a python script that will datadump the contents of the flash usb into a .bin
  - create a copy of the cartridge data that can be restored back onto the cartridge in case of compilation failure
  - ??? figure out how to restore cartridge data (in case of catastrophic failure)
    - upload a complete overwrite of cartridge data
    - test to see its function upon failure
  - connect the SOIC8 clip to the cartridge flash USB
  - connect the SOIC8 clip to a breadboard
  - read data through ESP32 and Python script
  - use hex reader to analyze resulting .bin file
  - identify any file types used
  - identify any string text
  - identify any patterns
  - determine how it triggers moving to the next frame
  - determine when and how it plays sound
  - determine when and how it flashes LTSDM lights
- cross reference data between all 3 cartridges
- ??? determine what places I need to edit to make:
  - different sounds
  - different LTSDM light strobe patterns
- ??? determine how to edit .bin file target places
- ??? determine how to upload and overwrite the custom code back onto the cartridge
- test the custom cartridge (audio patterns only)
- ??? make new transparent film frames
  - use transparency film, print at a photolab (CHATGPT SUGGESTION)
- ??? replace frames with custom transparent film frames
- durability testing (how many times can I play it without failure? Where are the failure points?)

# COMPLETED:
- order required equipment to read the cartridge


# WORKING LOG
**3 May 2025** - Ordered the cheapest set of cartridges for the LTSDM. Its the big shark series that comes with 3 cartridges (https://www.amazon.ca/Big-Shark-Little-Collection-PDQ/dp/B0BN4VSTRD?ref_=ast_sto_dp). 
It was on sale at the time. Additionally, talked with CHAT and mentioned to buy a SOIC8 clip to read the flash usb that is on all the cartridges (https://www.amazon.ca/Socket-Adpter-Programming-Adapter-Module/dp/B0892F713P/ref=sr_1_4_sspa?crid=34KHMA61T4S67&dib=eyJ2IjoiMSJ9.mC08kwn61HkPPj9OyWiaQiaexOSTiIbrIbWkNJuUiUJWL-rj8zriF_CtHZB_dJEwGccV5Z-IaPXFyiM8ZqBoEWk1r6MaEw1SZewn75uuxzkGVin0vIKFYcpDJxdYBc4YEVETOraVi4Hjf5007HDtKL9LhasBA2qtsNs7hhpbsKpq2qdpkxBsq0ol1bNRKwfajpP_jj0DsYBsmOhVsStWr-ik8XXgIxwdLabAh9rzMi94R59F-jP1cZxA0877Zqp-qu5OR4CQxffm7-wKi4L1mvPtm84SgFY4gew4XUPxJ28.wHFSvEb5untDLOGg4DbpsbbsGeQvo544EsMaGk4qaU8&dib_tag=se&keywords=soic8+clip&qid=1746330275&sprefix=soic8%2Caps%2C118&sr=8-4-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1). I assume you could use little probes for each lead on the USB (x8), but perhaps would need a secondary board to interpret the electrical pulses. A clip seems much more efficient at this stage.
I already have an ESP32, so I will connect this to a breadboard and see if I can pull any data from it without frying the cartridge or microcontroller. This will be my first attempt working with an ESP32 ever. The odds are against me on this one.
The materials are coming tomorrow evening.
Had CHAT provide a preliminary scripts for datadumping the cartridge onto my computer for analysis.

---
# CREDITS:
- CHATGPT -- spec info and howto
- Reddit -- general confirmation and guide howto (https://www.reddit.com/r/toddlers/comments/1hm9kzs/hack_the_little_tikes_dream_machine/)
 

# RESOURCES:
- ChatGPT conversation: https://chatgpt.com/share/6816df7a-c218-8006-b5d9-1f564e48376b
  - **Last updated:** May 3 2025
- Reddit thread with originally-documented idea: https://www.reddit.com/r/toddlers/comments/1hm9kzs/hack_the_little_tikes_dream_machine/


# Table of contents:
- prologue
- equipment used
- how a book cartridge works
- summary of customization process (program, overwrite, physical mods)
- how to program your custom story
- how to add your story to a cartridge
- physical modifications
- testing and assurance

## PROLOGUE
This is a good place to define some expectations and goals. Firstly, this will serve as a catalogue of my efforts to make a custom LTSDM book cartridge for my own daughter. If successful, I will not be accepting requests to make custom book cartridges for others. Since this journal is a legal grey area as it is, distributing custom content beyond this guide I feel is plainly illegal. This will simply serve as a a point of reference for modifying existing book cartridges to those with the urge, creativity, and determination to create a custom book cartridge themselves for personal use. I will attempt to reverse engineer the cartridge data, provide my tools here, and give as much description of the data (although likely vague) as open-source material for others to refer to. I hope my own pathway to success (hopefully) will enable others to make personal projects for their own children.


As this project is toeing the line of legality, a request: If successful, please do not create and distribute custom content to others. It may sound like a great business idea at first, but is plainly illegal and a breach of copyright law. I would also argue that such actions are unethical as this scheme would potentially undermine the profits of the original creators. In respect for Little Tikes who provided the original product, please do not distribute custom material. This information is meant to be publicly accessible for others' curiosity and ingenuity, albeit within the bounds of personal use.
