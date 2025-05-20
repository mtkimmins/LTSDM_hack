# A JOURNEY TO HACK A "LITTLE TIKES STORY DREAM MACHINE" BOOK CARTRIDGE - Customizing existing book cartridges


[!] DISCLAIMER [!]

This repository is for **educational, non-commercial use only**.  
No proprietary or copyrighted content is distributed.  
The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user.  
Please do not use this information to create or sell unauthorized commercial products.

Do not share the following:
- your raw extraction data at any stage of analysis
- modified extraction data (it will have unaltered copyrighted sections)
- microscopic decapping images of the hardware

---
# MILESTONES:
- **Chip data dump**
- Identify modifiable data
- Reupload mod data
- Create new film
- 3D printing a new case


# TO DO LIST:
- watch whole set of "junk" cartridges (1/3)
  - record number of frames used
  - record length of time for frame transitions and frame reads
  - record description of each frame
- measure dimensions of inner cartridge with calipers and post
- Datadump all 3 cartridges in the "junk" set
  - study the datasheet for the target flash chip
  - connect an ESP32 to the breadboard
  - ??? configure the ESP32 power and data lines appropriately
    - use 3.3V only (CHATGPT SUGGESTION)
    - use capacitors on breadboard between ESP32 and the SOIC8 clip for voltage stability - flash chip is very sensitive to voltage changes, readonly mode also voltage-dependant (CHATGPT SUGGESTION)
  - power on ESP32 via USB-computer
  - create a python script that will datadump the contents of the flash chip into a .bin
  - create a copy of the cartridge data that can be restored back onto the cartridge in case of compilation failure
  - ??? figure out how to restore cartridge data (in case of catastrophic failure)
    - upload a complete overwrite of cartridge data
    - test to see its function upon failure
  - connect the SOIC8 clip to the cartridge flash chip
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
- Determine the dimensions of the book cartridge sticker label
- Design a custom adhesive label
- Print and afix a custom adhesive label for the book cartridge
- durability testing (how many times can I play it without failure? Where are the failure points?)

# COMPLETED:
- order required equipment to read the cartridge
- get equipment to read and datadump
- take pictures of box back, manual warranty, and gear compartment of cartridge
- measure dimensions of outer cartridge with calipers and post
- determine how to open a cartridge without damaging the case or components/determine how to re-close a cartridge without damaging the case or components (you don't)
- open a cartridge with heat or solvent
- document inside chip (photos and text)


# WORKING LOG
**3 May 2025** -  
Ordered the cheapest set of cartridges for the LTSDM. Its the big shark series that comes with [3 cartridges](https://www.amazon.ca/Big-Shark-Little-Collection-PDQ/dp/B0BN4VSTRD?ref_=ast_sto_dp). It was on sale at the time.  
Additionally, talked with ChatGPT and it mentioned to buy a [SOIC8 clip](https://www.amazon.ca/Socket-Adpter-Programming-Adapter-Module/dp/B0892F713P/ref=sr_1_4_sspa?crid=34KHMA61T4S67&dib=eyJ2IjoiMSJ9.mC08kwn61HkPPj9OyWiaQiaexOSTiIbrIbWkNJuUiUJWL-rj8zriF_CtHZB_dJEwGccV5Z-IaPXFyiM8ZqBoEWk1r6MaEw1SZewn75uuxzkGVin0vIKFYcpDJxdYBc4YEVETOraVi4Hjf5007HDtKL9LhasBA2qtsNs7hhpbsKpq2qdpkxBsq0ol1bNRKwfajpP_jj0DsYBsmOhVsStWr-ik8XXgIxwdLabAh9rzMi94R59F-jP1cZxA0877Zqp-qu5OR4CQxffm7-wKi4L1mvPtm84SgFY4gew4XUPxJ28.wHFSvEb5untDLOGg4DbpsbbsGeQvo544EsMaGk4qaU8&dib_tag=se&keywords=soic8+clip&qid=1746330275&sprefix=soic8%2Caps%2C118&sr=8-4-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1) to read the flash chip that is on all the cartridges. I assume you could use little probes for each lead on the chip (x8), but perhaps would need a secondary board to interpret the electrical pulses. A clip seems much more efficient at this stage. This decision is based on three source consultations (1 user in the reddit thread identified the flash chip as a rewritable p25d80sh 3h1pb1a flash chip, another user in the reddit thread used ChatGPT to elaborate on the first-user's findings, and I also performed a secondary ChatGPT elaboration based on the first-user's findings).  
I already have an ESP32, so I will connect this to a breadboard and see if I can pull any data from it without frying the cartridge or microcontroller. This will be my first attempt working with an ESP32 ever. The odds are against me on this one.  
The ordered materials are coming from Amazon tomorrow evening.  
Had ChatGPT provide preliminary scripts for datadumping the cartridge onto my computer for analysis.  

**4 May 2025** -  
Received the shark book cartridges and the SOIC8 clip. Now to record the preliminary data about the books prior to cracking them open. I will also post pictures of fine print of the box rear and the generic limited warranty section of the manual - for reference purposes before I throw them out. I will also take photos of the gear and flash chip of one of the cartridges, as they are all the same structure (see Clip1.JPG, Clip2.JPG, Manual Warranty.JPG, Back of box.JPG).  
Recorded all three shark stories, and analyzing them with Microsoft Clipchamp for timestamps of transitions and events that happen during the play of the cartridge (see "preliminary_data.md"). Got through half of a cartridge.

**8 May 2025** -  
Completed the previous catalogue and created a table and preliminary data in preliminary_data.md. I plan to do the same for the other two stories likely after disassembling one of the cartridges. It is quite tedious work looking over a video -- however small -- and recording all flashes of light, film changes, and sound effect timing. Since the lights are timed with the audio and the film changes are during when the audio is off, I have a feeling that an audio file is compiled and uploaded to the cartridge along with a matching program code to execute certain commands. In creation, Little Tikes likely has a custom program like clipchamp that can edit an audio stream (combination of voice reading and sfx) next to transitions and light colours. I feel I may be able to replicate such program to facilitate the making of custom .bin files. This could circumvent the legal issue of sharing raw .bin files while also allowing a broader audience to create and upload custom stories to these cartridges. It appears that all stories have a 12-frame capacity. My father mentioned that they look like View-Masters in design. I also found a Reddit thread consulting about [View-Master-like film printing](https://www.reddit.com/r/toycameras/comments/12womtd/how_to_replicate_viewmaster_reels_with_my_own/). My father also mentioned the possibility of an x-ray prior to opening the cartridge versus using heat to make the plastic case pliable and resealable. Opening the case cold could bust the (what appears to be) snap or glue surfaces and render the case unusable. However, I could also have a case 3D printed and transfer the guts of the old busted cartridge to the new one. There is also a chance that both the x-ray and heat could damage the films attached to the cartridge. If they are being replaced anyway, perhaps this is not such a big deal. 3D printing a new case would require using calipers to measure the old case dimensions, which I have in my possession, but never used before.

**12 May 2025** -  
Over the past few days, I have measured the outer casing of the cartridge with a pair of digital calipers. The resulting photos have been posted for your reference (see side-measurements.png, port-end-measurements.png, back-measurements.png).

**17 May 2025** -  
I will have to refine the measurements of the cartridge for more clarity. I think I will use Figma to make a nice-looking diagram. Additionally, the measurements taken may be inaccurate and require some review. I will use an average of 2 measurements for each segment if possible to increase accuraccy. It is unclear if the measurements close to a whole number (ex: 7.8mm) are supposed to be a whole number and the caliper is showing its +-0.2mm variation, or if these measurements are meant to deviate slightly. The refinement of the diagrams will hopefully clarify these measurements. A 3D-print test will verify the measurements taken.  
I have gotten to a point where I have collected just about all the external information I could prior to opening the cartridge. Opening the cartridge is the most important part, yet I am unsure what the best approach would be. I should reach out to the initial Redditor that cited the type of the flash chip, as it sounds like they have had success in opening the cartridge and taking a look at the film carousel and the chip's wiring. I'll see if they have any documentation of what it looked like, or of any processes they used to open the cartridge themelves. 
In analyzing the functionality of the LTSDM + cartridge playback, it seems that the projector has a quantified distance that it spins the cartridge carousel to change frames. When I manually set the frame carousel between two frames and attempt to play it, the projector struggles to find the black square indicating the first frame and takes quite some time to cycle through to the detected beginning (if ever). If it does detect the black initialization square, it projects the two half-frames. Additionally, when I rewind the carousel to 1 frame before the initial frame the projector rapidly sets the cartridge to the first frame faster than normal. To verify this theory, I could do the following procedure: take a cartridge and manually spin the cartridge to halfway between frames again, play the cartridge and wait for it to detect the initialization marker, wait for it to display and change 1 frame. If the projector spins the carousel a fixed amount, then the following "frame" will also display the exact same amount of offset as previously displayed. I cannot think of a way the projector could correct this on its own. 
The projector will always undergo its protocol to seek the black initialization marker once a "new cartridge" is detected (a cartridge is completely pushed in the input slot).  
After the cartridge is opened, I plan to post the video of the opening and take specific pictures of the inside. Prior to hooking up the the ESP32 to power, I will wire up the data-dump clip setup and perhaps ask /r/electronics about what they think. A review of its datasheet would also help figuring out what I need to do to dump a .bin file.

**19 May 2025** -  
I have taken the cartridge apart with much effort. I had used heat gun to (try to) soften the plastic seam around the edges of the cartridge. Then I used a plastic lever to pry the casing apart where the flash chip sticks out, used the leads of my voltmeter to keep the case open, then finished it off with two butter knives to slowly pry the case apart the top. Recording a video of the opening was unsuccessful due to the effort required to pry the cartridge necessitated the removal of the cartridge out of frame of the video -- it wasn't capturing much of the "opening" part. Pictures are stored under the "internal" folder in this repo. It seems that the case is made of 2 parts snapped together by pillar-structures in the 4 corners, as well as glued around the pillars and seams -- some stringy substance revealed itself around the seams as I was trying to pry it open. The inner components are very bare: a chip, a wheel, and two halves of circular film. A reverse-image search of the circular film carousel only dug up images of viewmaster reels. A reverse-image search of the chip board also did not reveal anything useful -- just other small boards with small chips on them for cameras and flash drives. A reverse-image search of the whole internal picture revealed many images of yellow plastic toy casings, some toy camera internals, and the like. However, I have, presumably, found the datasheet for the flash chip, and have uploaded a copy to this repo.  
Borrowing some magnifying glasses, I have also identified that the chip itself has two lines of writing on it, with a divet in the bottom-left corner. The top line of writing is "P25D80SH" -- which corroborates what u/recursivemachines listed in the original thread. However, the bottom number varies from what was mentioned -- "4B1PN1F" (as opposed to the cited "3h1pb1a" by u/recursivemachines)-- I assume its a serial number for that manufactured part.  
The film carousel wheel (the white plastic reel) has the external cog on one end, and a series of nodules in a circle, some different sizes, some in different locations along the circumference. These nodules -- or raised bumps of plastic -- seem to be pegs where the two film hemispheres bite onto the wheel for it to turn and function. The nodule pattern is specific as to only allow the film hemispheres to be arranged in one enantiomeric configuration.  
A curiosity to discover -- why are there two halves of film? The circle of film is divided into two sections -- hemispheres, that make it more difficult to assemble and orient with the carousel. Perhaps it is a printing limitation, or an automated-assembly workaround. There is enough room for the film to be placed down as a whole piece under the carousel wheel, so it is unclear as to why its divided.  


___
# PROLOGUE
This is a good place to define some expectations and goals. Firstly, this will serve as a catalogue of my efforts to make a custom LTSDM book cartridge for my own daughter. If successful, I will not be accepting requests to make custom book cartridges for others. Since this journal is a legal grey area as it is, distributing custom content beyond this guide I feel is plainly illegal. This will simply serve as a a point of reference for modifying existing book cartridges to those with the urge, creativity, and determination to create a custom book cartridge themselves for personal use. I will attempt to reverse engineer the cartridge data, provide my tools here, and give as much description of the data (although likely vague) as open-source material for others to refer to. I hope my own pathway to success (hopefully) will enable others to make personal projects for their own children. Explicitely, I cannot show raw data on the chip to the public, so I will have to coach others through personal extractions to get their own modification blueprint, analysis and interpretation, and programming to make changes. Hopefully, I can figure out how to reduce the data analysis to something modifiable -- like a data map or something -- without breaching any laws. I will attempt to circumvent the headache of analyzing data oneself before any customization.


As this project is toeing the line of legality, a request:   
If successful, please do not create and distribute custom content to others. It may sound like a great business idea at first, but is plainly illegal and a breach of copyright law. I would also argue that such actions are unethical as this scheme would potentially undermine the profits of the original creators. In respect for Little Tikes who provided the original product, please do not distribute custom material. This information is meant to be publicly accessible for others' curiosity and ingenuity, albeit within the bounds of personal use.

# RESOURCES USED
**List of physical materials used:**
- ESP32
- SOIC8 clip + boards
- breadboard
- jumper wires
- Windows computer

**List of third-party software and programs used:**
- ChatGPT
- VSCode

**List of informational resources consulted:**
- ChatGPT conversation: https://chatgpt.com/share/6816df7a-c218-8006-b5d9-1f564e48376b
  - **Last updated:** May 3 2025
- Reddit thread with originally-documented idea: [Hack the Little Tikes Dream Machine](https://www.reddit.com/r/toddlers/comments/1hm9kzs/hack_the_little_tikes_dream_machine/)
- Reddit thread about custom film printing: [View-Master-like printing](https://www.reddit.com/r/toycameras/comments/12womtd/how_to_replicate_viewmaster_reels_with_my_own/)

# HOW A BOOK CARTRIDGE WORKS
**How a cartridge is prepared for play**  
- Setting the cartridge to the first frame  

**How frames move**  
**Playing audio**  
**Strobing lights**  


# SUMMARY OF CUSTOMIZATION PROCESS
**Planning your story**  
**Programming**  
**Overwrite process**  
**Physical alterations**  

# HOW TO PROGRAM YOUR CUSTOM STORY
**Planning out your story**  
**Audio**  
**Picture frames**  
**Light strobing**  

# HOW TO ADD YOUR STORY TO A CARTRIDGE
**Getting the data**  
**Editing the data**  
**Compilation and overwrite**  

# PHYSICAL MODIFICATIONS
**Custom film frames**
**Custom sticker label**

# TESTING AND ASSURANCE
**Durability**  

# COST ANALYSIS
**Initial acquisition costs**  
**Cost per custom cartridge**  
