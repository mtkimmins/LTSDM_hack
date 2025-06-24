# A JOURNEY TO HACK A "LITTLE TIKES STORY DREAM MACHINE" BOOK CARTRIDGE - Customizing existing book cartridges


[!] DISCLAIMER [!]

This repository is for **educational, non-commercial use only**.  
The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user.  
Please do not use this information to create or sell unauthorized commercial products.

---
# MILESTONES:
- ***Chip data dump***
- **Identify modifiable data**
- Reupload mod data
- Create new film
- 3D printing a new case

# CURRENT FOCUS
- My focus is to isolate similarities between the three chip dumps and create a template for my own data
  1) start with making gold standard bins
  2) compare gold standard (GS) bins
  3) pad and diff ending of all GS bins

# TEST QUERIES
- Can I turn the carousel <1 complete turn from the chip?
- How long can I play sound?
- How many times can I rotate the image carousel before the projector stops (is it 12 hardstop)?
- How quickly can I change light colours?
- How many colours can I change the light to?
- Can I play sound as the carousel is rotating?
- Can I use the lights when the carousel is rotating?


# WORKING LOG
## 3 May 2025 -  
Ordered the cheapest set of cartridges for the LTSDM. Its the big shark series that comes with [3 cartridges](https://www.amazon.ca/Big-Shark-Little-Collection-PDQ/dp/B0BN4VSTRD?ref_=ast_sto_dp). It was on sale at the time.  
Additionally, talked with ChatGPT and it mentioned to buy a [SOIC8 clip](https://www.amazon.ca/Socket-Adpter-Programming-Adapter-Module/dp/B0892F713P/ref=sr_1_4_sspa?crid=34KHMA61T4S67&dib=eyJ2IjoiMSJ9.mC08kwn61HkPPj9OyWiaQiaexOSTiIbrIbWkNJuUiUJWL-rj8zriF_CtHZB_dJEwGccV5Z-IaPXFyiM8ZqBoEWk1r6MaEw1SZewn75uuxzkGVin0vIKFYcpDJxdYBc4YEVETOraVi4Hjf5007HDtKL9LhasBA2qtsNs7hhpbsKpq2qdpkxBsq0ol1bNRKwfajpP_jj0DsYBsmOhVsStWr-ik8XXgIxwdLabAh9rzMi94R59F-jP1cZxA0877Zqp-qu5OR4CQxffm7-wKi4L1mvPtm84SgFY4gew4XUPxJ28.wHFSvEb5untDLOGg4DbpsbbsGeQvo544EsMaGk4qaU8&dib_tag=se&keywords=soic8+clip&qid=1746330275&sprefix=soic8%2Caps%2C118&sr=8-4-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1) to read the flash chip that is on all the cartridges. I assume you could use little probes for each lead on the chip (x8), but perhaps would need a secondary board to interpret the electrical pulses. A clip seems much more efficient at this stage. This decision is based on three source consultations (1 user in the reddit thread identified the flash chip as a rewritable p25d80sh 3h1pb1a flash chip, another user in the reddit thread used ChatGPT to elaborate on the first-user's findings, and I also performed a secondary ChatGPT elaboration based on the first-user's findings).  
I already have an ESP32, so I will connect this to a breadboard and see if I can pull any data from it without frying the cartridge or microcontroller. This will be my first attempt working with an ESP32 ever. The odds are against me on this one.  
The ordered materials are coming from Amazon tomorrow evening.  
Had ChatGPT provide preliminary scripts for datadumping the cartridge onto my computer for analysis.  

## 4 May 2025 -  
Received the shark book cartridges and the SOIC8 clip. Now to record the preliminary data about the books prior to cracking them open. I will also post pictures of fine print of the box rear and the generic limited warranty section of the manual - for reference purposes before I throw them out. I will also take photos of the gear and flash chip of one of the cartridges, as they are all the same structure (see Clip1.JPG, Clip2.JPG, Manual Warranty.JPG, Back of box.JPG).  
Recorded all three shark stories, and analyzing them with Microsoft Clipchamp for timestamps of transitions and events that happen during the play of the cartridge (see "preliminary_data.md"). Got through half of a cartridge.

## 8 May 2025 -  
Completed the previous catalogue and created a table and preliminary data in preliminary_data.md. I plan to do the same for the other two stories likely after disassembling one of the cartridges. It is quite tedious work looking over a video -- however small -- and recording all flashes of light, film changes, and sound effect timing. Since the lights are timed with the audio and the film changes are during when the audio is off, I have a feeling that an audio file is compiled and uploaded to the cartridge along with a matching program code to execute certain commands. In creation, Little Tikes likely has a custom program like clipchamp that can edit an audio stream (combination of voice reading and sfx) next to transitions and light colours. I feel I may be able to replicate such program to facilitate the making of custom .bin files. This could circumvent the legal issue of sharing raw .bin files while also allowing a broader audience to create and upload custom stories to these cartridges. It appears that all stories have a 12-frame capacity. My father mentioned that they look like View-Masters in design. I also found a Reddit thread consulting about [View-Master-like film printing](https://www.reddit.com/r/toycameras/comments/12womtd/how_to_replicate_viewmaster_reels_with_my_own/). My father also mentioned the possibility of an x-ray prior to opening the cartridge versus using heat to make the plastic case pliable and resealable. Opening the case cold could bust the (what appears to be) snap or glue surfaces and render the case unusable. However, I could also have a case 3D printed and transfer the guts of the old busted cartridge to the new one. There is also a chance that both the x-ray and heat could damage the films attached to the cartridge. If they are being replaced anyway, perhaps this is not such a big deal. 3D printing a new case would require using calipers to measure the old case dimensions, which I have in my possession, but never used before.

## 12 May 2025 -  
Over the past few days, I have measured the outer casing of the cartridge with a pair of digital calipers. The resulting photos have been posted for your reference (see side-measurements.png, port-end-measurements.png, back-measurements.png).

## 17 May 2025 -  
I will have to refine the measurements of the cartridge for more clarity. I think I will use Figma to make a nice-looking diagram. Additionally, the measurements taken may be inaccurate and require some review. I will use an average of 2 measurements for each segment if possible to increase accuraccy. It is unclear if the measurements close to a whole number (ex: 7.8mm) are supposed to be a whole number and the caliper is showing its +-0.2mm variation, or if these measurements are meant to deviate slightly. The refinement of the diagrams will hopefully clarify these measurements. A 3D-print test will verify the measurements taken.  
I have gotten to a point where I have collected just about all the external information I could prior to opening the cartridge. Opening the cartridge is the most important part, yet I am unsure what the best approach would be. I should reach out to the initial Redditor that cited the type of the flash chip, as it sounds like they have had success in opening the cartridge and taking a look at the film carousel and the chip's wiring. I'll see if they have any documentation of what it looked like, or of any processes they used to open the cartridge themelves. 
In analyzing the functionality of the LTSDM + cartridge playback, it seems that the projector has a quantified distance that it spins the cartridge carousel to change frames. When I manually set the frame carousel between two frames and attempt to play it, the projector struggles to find the black square indicating the first frame and takes quite some time to cycle through to the detected beginning (if ever). If it does detect the black initialization square, it projects the two half-frames. Additionally, when I rewind the carousel to 1 frame before the initial frame the projector rapidly sets the cartridge to the first frame faster than normal. To verify this theory, I could do the following procedure: take a cartridge and manually spin the cartridge to halfway between frames again, play the cartridge and wait for it to detect the initialization marker, wait for it to display and change 1 frame. If the projector spins the carousel a fixed amount, then the following "frame" will also display the exact same amount of offset as previously displayed. I cannot think of a way the projector could correct this on its own. 
The projector will always undergo its protocol to seek the black initialization marker once a "new cartridge" is detected (a cartridge is completely pushed in the input slot).  
After the cartridge is opened, I plan to post the video of the opening and take specific pictures of the inside. Prior to hooking up the the ESP32 to power, I will wire up the data-dump clip setup and perhaps ask /r/electronics about what they think. A review of its datasheet would also help figuring out what I need to do to dump a .bin file.

## 19 May 2025 -  
I have taken the cartridge apart with much effort. I had used heat gun to (try to) soften the plastic seam around the edges of the cartridge. Then I used a plastic lever to pry the casing apart where the flash chip sticks out, used the leads of my voltmeter to keep the case open, then finished it off with two butter knives to slowly pry the case apart the top. Recording a video of the opening was unsuccessful due to the effort required to pry the cartridge necessitated the removal of the cartridge out of frame of the video -- it wasn't capturing much of the "opening" part. Pictures are stored under the "internal" folder in this repo. It seems that the case is made of 2 parts snapped together by pillar-structures in the 4 corners, as well as glued around the pillars and seams -- some stringy substance revealed itself around the seams as I was trying to pry it open. The inner components are very bare: a chip, a wheel, and two halves of circular film. A reverse-image search of the circular film carousel only dug up images of viewmaster reels. A reverse-image search of the chip board also did not reveal anything useful -- just other small boards with small chips on them for cameras and flash drives. A reverse-image search of the whole internal picture revealed many images of yellow plastic toy casings, some toy camera internals, and the like. However, I have, presumably, found the datasheet for the flash chip, and have uploaded a copy to this repo.  
Borrowing some magnifying glasses, I have also identified that the chip itself has two lines of writing on it, with a divet in the bottom-left corner. The top line of writing is "P25D80SH" -- which corroborates what u/recursivemachines listed in the original thread. However, the bottom number varies from what was mentioned -- "4B1PN1F" (as opposed to the cited "3h1pb1a" by u/recursivemachines)-- I assume its a serial number for that manufactured part.  
The film carousel wheel (the white plastic reel) has the external cog on one end, and a series of nodules in a circle, some different sizes, some in different locations along the circumference. These nodules -- or raised bumps of plastic -- seem to be pegs where the two film hemispheres bite onto the wheel for it to turn and function. The nodule pattern is specific as to only allow the film hemispheres to be arranged in one enantiomeric configuration.  
A curiosity to discover -- why are there two halves of film? The circle of film is divided into two sections -- hemispheres, that make it more difficult to assemble and orient with the carousel. Perhaps it is a printing limitation, or an automated-assembly workaround. There is enough room for the film to be placed down as a whole piece under the carousel wheel, so it is unclear as to why its divided.  

## 20 May 2025 -  
Prior to attempting a datadump with the sketchy code ChatGPT vomited up, my father and I paroused the Little Tikes site for a patent number. This search was for the intent to uncover a patent diagram of the projector itself to lend some clue as to how the flash chips is naturally read. Perhaps this would reveal some hint as to a correct method for such a datadump. In curiosity, I directly contacted Little Tikes requesting directions to the patent along with directions to this repository in hopes that such patent information can be traded for transparency with Little Tikes. I feel it may be a risky move, however, I am more comfortable with revealing all my cards than attempting secrecy. Worst case scenario: something along the lines of a cease-and-desist. Best case senario, Little Tikes assists in the project. I do desire to take this project as far as I can run with it. Only one way to find out the outcome. I will post any answers received.

## 24 May 2025 -  
I have just realized as I attempted to clamp on the clip to the chip that the lead on the p25d80sh is way bigger than the SOIC8 clip leads I have bought. I will have to reassess how I will attach the chip to the ESP32. Maybe taping wires to the chip's leads -- I don't want to solder anything to this chip as I want to reuse it and have little experience with solder. Lead comparison photo uploaded as *[removed]*.  
*EDIT: I have since realized that this clip is not meant to go on the custom pcb golden fingers, but on the chip itself directly. Embarassing.*  

## 26 May 2025 -  
In trying to wire the p25d80sh to my ESP32, I have learned a few things (have not gotten any data yet): 1) I bought the ESP32 expansion board. I don't have an ESP32. Luckily, I do have an Uno 3, so that will be used in its stead. ChatGPT suggests that it will still be able to read the chip. I may have to edit the scripts, most likely. 2) The leads coming out of the PCB do not correlate directly with the pins on the p25d80sh. The front of the PCB labelled the leads (SO, /CS, SLCK, SI) from left to right. In checking continuity with a multimeter and referencing the datasheet, these are indeed labelled correctly -- however, they do not correlate with the order of pins on the chip at all. The tricky part is the back side. 4 leads on the PCB, none are labelled. A continuity check reveals the following pin connections (GND, GND, WP/HOLD/VCC, WP/HOLD/VCC) from left to right (same orientation upward as the front). The HOLD and WP are automatically tied to VCC -- which is what ChatGPT suggested to do in order to read the chip in the first place. It seems the PCB was designed in this way to ensure the chip would be read-only when played -- which makes sense. This means that it will be a bit harder for me to overwrite the chip. At this stage, I am thinking that I can just manually wire a lead directly to the exposed pin I want on the chip (leave WP and HOLD off -- on low). However, I do wonder what combination of these will allow me to rewrite the chip -- that is very likely revealed in the datasheet. The second perplexity is if directly connecting a lead to the pin will actually bypass the other two settings, as they are physically wired together. I am assuming that the shortest route will choose the pin for current to flow through, but I am unsure if that theory is enough to circumvent the other two pins hardwired together -- I am afraid of the possibility of desoldering the chip from the PCB in order to flash it again. If so, how do I even get it back in? In my mind, the easiest path hypothesis would infer that I don't need to desolder the chip, but I don't know enough just yet. I will consult ChatGPT, and possibly reddit if permitted to post in the right place. Either way, there is one way to really find out... try it.  

## 28 May 2025 -  
A correction from last entry, tying the HOLD and WP high will disable them. This means that the chip's pcb is designed to always be in write-permissible mode. Obviously the projector does not overwrite the chip each time it plays, so it must simply send read commands exclusively, and so can I! This makes it much easier to overwrite. I attempted to attach jumper wires to the pcb leads with electrical tape - no success, as the wire leads kept slipping off the pcb and not passing a continuity test -- no matter how much tape I put on. The electrical tape also left a residue on the pcb, luckily nothing too bad. If it had got bad, I would have used isopropyl 99% on a Q-tip to remove it, should be safe for electronics. Next I tried hot glue as a suggestion from ChatGPT. It almost worked! I tried hot gluing the leads on the pcb as if I was soldering them, but the glue would seep under and insulate the leads. So I put a bunch of hot glue directly on the flat surface of the pcb and let it harden. Then I used the leads to pry a hole under the sheet of glue hoping that the glue would keep the leads on the pcb. However, since the pcb leads were so close together the whole flap came loose, except for the top closer to the actual chip, so it would not exert pressure on the wire leads. I tried to electrical tape over the glue flap, but there was not enough pressure. I then used the alligator clips on my mounting stand, which kinda helped except it would not apply equal pressure, so the distal wires would still be loose, even when I used two clips from each side -- the middle would not contact. Defeat for the night. The next morning, I had a thought to use the SOIC8 clip (that I had thought was useless) directly on the chip (not the pcb) -- embarassingly, it was very clear that this was the intention of the clip the whole time. I thought I would be successful until I did a continuity test which revealed that the leads in the clip were not making contact with the chip pins, no matter how much glue debris I cleared or how far I pushed the clip -- the chip was just set too deep in the pcb. A whole day of brainstorming with ChatGPT led me to the idea of using an edge adapter. I think I will eventually get one since I have 2 more chips to dump and modify. I feel this is the most non-invadive way to connect it. I also thought about what the projector uses - ChatGPT did not recognize the pcb as any standard form factor, so the chances that the adapter the projector uses is proprietary. So that lead me to the final resort -- soldering. I did not want to mess with the board in this way, however I do have a spool of solder wick, and the pcb surface is flat, so I can clean it up nicely. This is the first thing that I have ever soldered, but it turned out functional! Initially, I had equipped the tiniest solder tip so I could be precise. Unfortunately, the distal point of the tip never got hot enough to ever melt the solder, even on max heat setting. So I set it down and let it cool so I could switch the tip to a larger flat edge tip. This worked way easier -- the tip edge of this head was melting solder well, and I soldered the rest of the wire jumpers on the pcb. with each solder, I would perform a continuity test with the multimeter to ensure the other end of the wire connected with its corresponding pin(s) of the chip itself. All soldered wires have passed! Now I can finally hook up the pcb to the uno and run the scripts. I also had ChatGPT update the scripts for the uno, and write some overwrite scripts too. I have uploaded the new dump scripts, and will upload the others tomorrow.  
The next step is to reduce the 5V of the uno to 3.3V for the p25d80sh. For that, I can use a series of resistors to make a "divider" on a breadboard. I used a top resistor of 2k ohms, and a bottom resistor of 3k ohms (made from chaining a 2k with a 1k). This setup should reduce the voltage to 3V, which is operational. The chip needs at least 2.6V to turn on pins and be functional (up to 3.6V), so 3V is right in a good range. These are seen in the photos with the soldered pcb. I will have to step down the /CS, MOSI, and SLCK pins, then use the 3.3V port on the uno for the triple-tied VCC/WP/HOLD pin. I will also have to learn how to get that script onto the uno so it works. Soon I will have an actual .bin file! So close now.  

## 30 May 2025 -  
I have finally received the .bin file! It took quite some time conversing with ChatGPT, but we made it work. From some preliminary checkup, it appears to be a genuine dump. I have posted the first 11 lines of the .bin file as hex. It primarily looks like a bunch of jumbled garbage. I have deleted the scripts that I did not use/work, and have uploaded the two scripts that actually did pull the data in (see under scripts; flash_dump_chip_to_uno.ino and flash_dump_uno_to_pc.py).  
Reflections on electronic preparation: Because of the temperment of the binary dump, I am glad that I had explicitely soldered the jumper leads directly to the pcb. This helped confirm that it was not my leads falling off that made the program stop. It really helped with keeping focus on programming instead of verifying continuity continually. Also had to reverse the orientation of the divider connections (the divider layout -- series of resistors in the breadboard --  depicted in soldered_back.jpg and soldered_front.jpg are correct), I just had to reconnect the jumper wires at the front and back to reverse the flow through just the 2k ohm resistor first. It appears that the file uploaded to the chip must -- by mandate -- equal 1MB precisely. So, this can result in a small amount of data uploaded with the rest of the bytes written as padding "FF" which makes up about 75%-80% of this cartridge. With this rough estimation, I would say that the maximum length of story based on the original length is about 10 minutes (2:29 * 4). This obviously depends on other variables like projector limitations.  
**Jumper wiring between chip, pcb, and uno:**  
|Chip pin|PCB lead|Arduino pin|Divider required?|
|:-:|:-:|:-:|:-:|
|CS (Chip Select)|/CS (front, middle left)|Arduino pin 10|YES|
|MOSI (SI)|SI (front, far right)|Arduino pin 11|YES|
|MISO (SO)|SO (front, far left)|Arduino pin 12|NO-straight from chip to uno|
|SCLK (SCK)|SLCK (front, middle right)|Arduino pin 13|YES|
|GND|GND (unlabeled, back, far left)|Arduino pin GND|NO|
|VCC/HOLD/WP|VCC/HOLD/WP (unlabelled, back, far right)|Arduino pin 3.3V|NO-straight from chip to uno|  

**Voltage divider wiring:**  
Top resistor (R1) from Arduino signal pin to chip input
Bottom resistor (R2) from chip input to GND
R1 = 2k ohms; R2 = 3k ohms


## 1 June 2025 -  
Soldered and dumped the other two chips into .bin files. Now i can diff the three together to isolate what is firmware code and what are variables. The serial numbers for the chips were the following: Big Shark, Little Shark (chip 12) = 4B1PN1F; Big Shark, Little Shark, Baby Shark (chip 11) = 4D1HZ2F.


## 3 June 2025 -  
Diffing 12_chip and 13_chip, I found the exact same ending with the following hex: 1E 79 30 78 66 2F 3D 40 3D 14 81 0F 23 53 17 FE B9 CF C3 43 50 06 F9 92 CA F6 D4 33 4C D4 D5 7E 12 53 53 BF 42 2C C6 80 8E AD 40 C4 8C 0B 4C 9F DA D7 C6 02 9D D4 92 FE 5F DC BB 22 00 AF 06 31 20 C8 C4 2C AC 22 29 67 44 C6 0B E8 31 9D 86 74 3A C0 E9 D2 B3 6E 1B DD 04 49 EF 3B C3 8F DC 4E. However, 11_chip is very dissimilar to 12_chip and 13_chip. Maybe different programmers? Perhaps a bad dump from 11_chip...


## 4 June 2025 -  
The difference in 11_chip.bin definitely was due to some data interruption. It looked like swiss cheese -- littered with holes of "00". A second dump revealed just strips of data surrounded by 00s, leaving some strips completely blank with FF. Now, a third dump changed the binary in those strips, so I knew it was unreliable. After replugging and recompiling the program, I got a fourth dump with gibberish. Just incoherent binary dotted with 00s again. A fifth dump revealed an initial structure similar to 12_chip and 13_chip, but still with glaring lines or holes of 00. A sixth dump on a different USB port showed a similar structure to 13_dump, however all the binary was really different except for periodic binary strips. This is much different than when I compare 12_chip to 13_chip where most of it is identical except for a handful of lines spread out where they differ. The first half of the written chips seem like directories to files later embedded in the chip, and then it hits a wall halfway through of dissimilarity. However, I believe this chunk is the actual audio file. Looking at the endings prior to the rest of the blank padding for each chip, they share the exact same ending sequence as well. 


## 5 June 2025 -  
I have caved and bought another projector. It was on sale from amazon, and the ones on marketplace were selling for much more. It is coming tomorrow, so hopefully I can figure out what plays the cartridges, what architecture it is, and I get an official pcb clip that fits (no more soldering hopefully). I have also uploaded a picture of a handwritten wiring diagram depicting the pc-arduino-pcb circuit ("arduino_wiring_diagram.jpg").


## 6 June 2025 -
I was skimming the binary 13_chip.bin and saw that every time there was a low entropy patch, there was a controlled patterns of 0481, 0880, 0C80 hex codes with about 3 bytes in between. It looked almost like a table or an array. I have bookmarked them for future reference. I have uploaded an example as "0880.png".  
The extra projector came this morning, and I have disassembled it tonight. I have uploaded respective photos of the disassembly on the GitHub under the folder "projector_dissassembly." I am now attempting to identify the microcontroller used and its various parts. Luckily, the cartridge reader section has a detatcheable adapter to the main board. This means all I have to do now is re-route the out-pins through the arduino circuit I made earlier and dump literally all the books without even having to bust them open. After the corruption of 11_chip, I am hesitant to break any more cartridges and hand-solder leads.

## 9 June 2025 -
Seems like the projector controller is not standard -- may be proprietary. Chip numbers are listed in the photo uploaded in projector_board_chips.jpg. I must gather a plan of attack in order to figure out what the functions of the cartridge formats are. I will have to procedurally compare the chip dumps. Luckily, the adapter from the projector guts can be easily rewired to the arduino, so I will dump my other 6 books (and redump the 11_chip from my daughter's good copy). Now I don't have to crack open a cartridge to interact with it. I will have to make a huge spreadsheet for the listing of each deviant region, as well as low-entropy regions of each chip comparatively. I will also start to make a "template" hex code that will be the basis for a whole new story. I also had the idea to take two good dumps and swap inject one variable region into the other and play them -- then see what aspects of the injected cartridge data reveals itself. This means I will have to be familiar with the runtime events of each cartridge to effectively isolate the functions of each region of bytes. Its a lot of work, but I can slowly trudge through it.

## 13 June 2025 -
Found another individual who is working to reverse-engineer the cartridge and projector too. They are much more versed in electronics and security than I, which led to the discovery that these .bins are encrypted. With that realization, I will post my two verified .bin files. Unfortunately, I have not been so lucky to get any more successful .bin dumps.

## 16 June 2025 -
Serially dumping the .bin files reveals slight changes to the binary when dumped. Verified GainSec's file - checked with muliple dumps. Seems to match my other "good" .bins except for the signature areas (beginning table, address 0x4EE8 onward). Must still padd a copy of a .bin to align with another to see how far the ending is similar from the back. The sign that my .bin is bad is if there are extra variation areas between the table and the shart of the custom audio (0x4EE8). The fact that my intact-cartridge dumps look similar to my chip-soldered dumps (most of them), suggests that there is variation in the dump, and requires further validation. I also realized that the .bin was absolute garbage until I powered both Vcc/HOLD/WP gold fingers and got the "good" copies consistently (with some slight variations). Changed the baud rate to 19200 for a slower, more methodical dump.  
The way that I validate my own dumps is if there is a perfect gap of identical bytes between the table and the 0x4EE8 address start (the unique data) between my dump and GainSec's. It also revealed that there were errors in my two previously "good" dumps labelled 12_dump.bin and 13_dump.bin. I will have to upload the better versions.
Another check is if I get the exact same .bin file with two consecutive dumps of the same cartridge. Its getting better, but any slight bump to the arduino and circuit seems to elicit variant regions.

## 17 June 2025 - 
More .bin diffing creates more questions. It seems that every time I dump a .bin, it varies by some small degree from each other. Luckily I think I figured out how to circumvent this:  
- I dump 5 consecutive dumps of 1 book
- I dump 5 consecutive dumps of the same book, but another physical copy.
- I choose 1 copy as my "base" copy
- I compare this base copy to the other 4 copies
- I mark and colour-code the unique changes between each copy-pair
- I manually adjust the "base" copy to reflect the democratic result for each variation
- I repeat these above steps for the second physical cartridge of the same story
- I then diff these two amalgamated base copies against each other
- I should get a purified version of the .bin that I can use as a gold standard  

This approach incurs some assumptions: 
  1) that the variable regions between consecutive dumps are in different spots;
  2) that the democratic average of what is mostly agreed upon by the most copies is the "right" binary sequence.

If the two amalgamated copies do not match perfectly, I will be back to square one. I really, really, really hope it works and match at the end of this! At the moment, I have turned the baud rate down and takes about 10 minutes per dump. 5x10x2=100 minutes of straight downloading data. Then I have to manually go through these binaries and mark the diffs. I got this.  
Additionally, I have taken down the 12_dump.bin and 13_dump.bin since I have discovered yesterday that they are not gold-standard bins. I will upload the groups of 5 consecutive dumps I will use to make the amalgamated diff.

## 18 June 2025 - 
Still grinding out file dumps. I have 1 set of "Big Shark, Little Shark, Baby Shark," 2 separate sets of "Pokey Little Puppy," and am now currently dumping a set of "Saggy, Baggy Elephant." I will dump a separate set of Elephant, 2 more Lion sets, and attempt another "Big Shark, Little Shark, Baby Shark" and 2 sets of "Big Shark, Little Shark Go To School." Additionally, I aim to quintuple-dump "The Very Quiet Cricket," "Slowly, Slowly, Slowly said the Sloth," and "Mister Seahorse" once each. I will upload my ImHex project files too.
While I wait for the data to dump (calculated at 500 minutes or 8:20H of straight download time), I wanted to dream up some ideas that I could use for my first modded project. It should be very simple, like a solid light colour per slide, and a different voice per slide. It would also be useful to test all my questions in one go.


TEST 1. AUDIO TIMING
|SLIDE|LIGHTS|AUDIO|COMMENTS|
|:-:|:-:|:-:|:-:|
|1|red|10 sec reading clip||
|2|red|8 sec reading clip||
|3|red|6 sec reading clip||
|4|red|4 sec reading clip||
|5|red|2 sec reading clip||
|6|red|1 sec reading clip||
|7|red|0.5 sec reading clip||
|8|red|0.1 sec reading clip||
|9|red|no audio|Attempt to skip over a slide|
|10|red|music|Attempt to play over the next slide change|
|11|red|10 sec no audio||
|12|red|music data to fill the rest of the chip|Attempt to turn the carousel a 13th time|  

*The reading clips could be a verbal countdown of seconds*


TEST 2. LIGHTS
|SLIDE|LIGHTS|AUDIO|COMMENTS|
|:-:|:-:|:-:|:-:|
|1|red|3|Control variable|
|2|orange|3|Attempt to keep the light on when changing slide|
|3|yellow|3|
|4|green|3|
|5|cyan|3|
|6|blue|3||
|7|brown|3|
|8|maroon|3|
|9|red->purple smooth transition|10|
|10|red->purple smooth transition|3|Attempting to see if the duration of lights are deduced by the duration of the slide|
|11|red->purple stocastic transition|10|
|12|red-> fast transition 0.1 sec between|10|Attempt to keep light on as long as possible|  

*Known colours: red, yellow, white, green, cyan, blue, pink, purple*


TEST 3. CAROUSEL
|SLIDE|LIGHTS|AUDIO|COMMENTS|
|:-:|:-:|:-:|:-:|
|1|red strobe|2|
|2|red strobe|2|Attempt to turn the carousel twice during next transition|
|3|red strobe|2|Attempt to turn the carousel half a slide next transition|
|4|red strobe|2|Turn the carousel another half a slide next transition|Normalize|
|5|red strobe|2|Attempt to end the story after next transition||

TEST 4. LENGTH
|SLIDE|LIGHTS|AUDIO|COMMENTS|
|:-:|:-:|:-:|:-:|
|1|red strobe|as long as possible|Max out chip space|  

*Finish with ending byte sequence*

## 24 June 2025 - 
I have painstakingly manually edited a pure copy of "**Big Shark, Little Shark, Baby Shark.**" Its uploaded now in Binary. I will now have to refine the other copy of the same book, then compare both good copies. I hope they match without any differences. I am unsure where to go if there are genuine differences between the two (not due to me being dumb and injecting errors).  
A list of changes is catalogued in **DiffSheet.xls**

___
___
# PROLOGUE
This is a good place to define some expectations and goals. Firstly, this will serve as a catalogue of my efforts to make a custom LTSDM book cartridge for my own daughter. If successful, I will not be accepting requests to make custom book cartridges for others. Since this journal is a legal grey area as it is, distributing custom content beyond this guide I feel is plainly illegal. This will simply serve as a a point of reference for modifying existing book cartridges to those with the urge, creativity, and determination to create a custom book cartridge themselves for personal use. I will attempt to reverse engineer the cartridge data, provide my tools here, and give as much description of the data (although likely vague) as open-source material for others to refer to. I hope my own pathway to success (hopefully) will enable others to make personal projects for their own children. Explicitely, I cannot show raw data on the chip to the public, so I will have to coach others through personal extractions to get their own modification blueprint, analysis and interpretation, and programming to make changes. Hopefully, I can figure out how to reduce the data analysis to something modifiable -- like a data map or something -- without breaching any laws. I will attempt to circumvent the headache of analyzing data oneself before any customization.


As this project is toeing the line of legality, a request:   
If successful, please do not create and distribute custom content to others. It may sound like a great business idea at first, but is plainly illegal and a breach of copyright law. I would also argue that such actions are unethical as this scheme would potentially undermine the profits of the original creators. In respect for Little Tikes who provided the original product, please do not distribute custom material. This information is meant to be publicly accessible for others' curiosity and ingenuity, albeit within the bounds of personal use.


# RESOURCES USED
**List of physical materials used:**
- Arduino Uno R3
- SOIC8 clip + boards
- breadboard
- jumper wires
- Windows computer
- 2k ohm resistors
- 1k ohm resistors

**List of third-party software and programs used:**
- ChatGPT
- VSCode
- ImHex
- Arduino IDE

**List of informational resources consulted:**
- ChatGPT conversation: https://chatgpt.com/share/6816df7a-c218-8006-b5d9-1f564e48376b
  - **Last updated:** 30 May 2025
- Reddit thread with originally-documented idea: [Hack the Little Tikes Dream Machine](https://www.reddit.com/r/toddlers/comments/1hm9kzs/hack_the_little_tikes_dream_machine/)
- Reddit thread about custom film printing: [View-Master-like printing](https://www.reddit.com/r/toycameras/comments/12womtd/how_to_replicate_viewmaster_reels_with_my_own/)
- Reddit thread about measuring found objects: [Measure and recreate real objects](https://www.reddit.com/r/AskEngineers/comments/ijsk7c/how_can_i_learn_to_measure_and_recreate_real/)
- Reddit thread asking about gleaning information from a binary differential: [Patterns in the Diff](https://www.reddit.com/r/HowToHack/comments/1l3pz6m/finding_patterns_using_imhex_in_a_differential/)
- Wikipedia: [Binary File](https://en.wikipedia.org/wiki/Binary_file)
- Wikipedia: [File Signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)
- Wikipedia: [Pulse-Code-Modulation](https://en.wikipedia.org/wiki/Pulse-code_modulation)
- GainSec: [Project Log](https://gainsec.com/2025/05/25/reverse-engineering-the-little-tikes-dream-machine-projector-part-1/)

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
