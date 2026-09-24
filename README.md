<!-- Little Tikes Story Dream Machine LTSDM custom cartridge SPI flash P25D80SH reverse engineering hex hexadecimal file format PCM audio extraction embedded Arduino a1800 codec general plus collection imhex hack .a18 .wav 16khz 16-bit signed mono -->
<h1 align="center">:construction:Under Construction:construction:</h1>

<h1 align="center">
  Custom Stories for the
  <br>
  Little Tikes Story Dream Machine (LTSDM)
</h1>

![License](https://img.shields.io/badge/License-GPL--3.0-blue)
[![YT](https://img.shields.io/badge/YouTube-red?logo=youtube)](https://youtu.be/TxU2IYq_FqY)

[![headline](./headline.svg)](https://github.com/mtkimmins/LTSDM_hack/wiki/19-September-2026)

🔜 ![byos](https://img.shields.io/badge/Build_My_Own_story-grey?style=for-the-badge)
  
<h1 align="center">What Is This?</h1>
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6T85_2Bq7C5ENhbM_02QsqHP0uwPh_4JUz7wYPDEt2z_kRJ-Nr4eMbuc-&s=10" alt="Little Tikes Story Dream Machine Projector & Cartridges"> <i>not my image</i><br><br><br>


<body>
  The <a href="https://www.littletikes.com/collections/story-dream-machine?srsltid=AU7gw4WqiQ8R5CqPzf9FcHDLHLqfhu1rZ22Jz5EO_xHfze3l0G6kVn3B">Little Tikes Story Dream Machine (LTSDM)</a> is a toy projector geared towards young children. Each story is kept in a cartridge, or "book," that is physically inserted into the projector. Inside, the cartridge holds the following:
  
  1) audio data to be played on the projector's speakers
  2) digital instructions for the projector's rear light display
  3) twelve film slides depicting the pages of the book which the projector shines out

  Despite the appeal, the LTSDM has a few notable drawbacks:
  * Stories are highly condensed narrations spanning only about 2-3 minutes per cartridge
  * Little Tikes currently offers stories in a limited number of languages, namely: English, French, and Spanish
  * Although Little Tikes offers quite a decent collection of stories, they must be purchased in fixed bundles. This restricts the amount of freedom consumers have over story collection
  * Triple-set bundles cost roughly $24 CAD per set. This works out to about $8 per cartridge. I wonder if these could be modded for cheaper
  * Custom stories personalized to one's own children are not officially supported

  These drawbacks have led to many parents abandoning or returning the LTSDM for other audiovisual products, like [Yoto](https://ca.yotoplay.com/).

  I aim to allow any parent, caregiver, or individual to design and build their own custom cartridges compatible with the LTSDM, permitting personalized audiovisual media to be depicted by their projector.
</body>

<h1 align="center">Where Are We At?</h1>

The project consists of reverse engineering all aspects of an LTSDM cartridge to allow for fully customizable narratives. These aspects are namely: 

![data](https://img.shields.io/badge/Data-Custom_audio_playable)

![case](https://img.shields.io/badge/Case-Deconstructed)

![circuitry](https://img.shields.io/badge/Circuitry-PCB_mapped)

![film](https://img.shields.io/badge/Film-Story_brainstorm)

```mermaid
graph TD
A[Dissect LTSDM hardware]-->B[Data]
A-->C[Case]
A-->D[Circuitry]
A-->E[Film]

B-->BA[Dump existing data off official cartridges]
BA-->BB[Determine data structure]

C-->CA[Measure dimensions of case parts]

D-->DA[Source P25D80SH chips or similar]
D-->DB[Design modded PCB]
D-->DC[Determine all components on official PCBs]

E-->EA[Measure dimensions of film components]
E-->EB[design test images]

%% STYLE DEFINITIONS
classDef done fill:#00ff00
classDef prog fill:#888800
classDef lock fill:#ff0000

%% STYLE ASSIGNMENTS
class A,BA done;
class B,C,D,E prog;
class EB lock;
```








<h2>As of 19 September 2026, the first custom audio cartridge data was successfully ran on the LTSDM! A huge thank-you to the community of followers for assistance and encouragement over the past 16.5 months.</h2>
  <p>This repository documents the holistic process of hacking the Little Tikes Story Dream Machine.</p>
  <p>Frontier of progress of custom cartridges:</p>
  
  [![Devlog](https://img.shields.io/badge/Devlog-green)](https://github.com/mtkimmins/LTSDM_hack/wiki/Working-Developer-Log)

  *see [19 September](https://github.com/mtkimmins/LTSDM_hack/wiki/19-September-2026)*
  
  [![YouTube](https://img.shields.io/badge/YouTube-red)](https://youtu.be/TxU2IYq_FqY)
  <br><br><br>
  
  <h2>Project Roadmap</h2>
  
  ### START
  
  ~~Crack a cartridge open~~  
  ~~Dump cartridge data~~  
  ~~Analyze dumped data~~  
  ~~Construct an encoder/decoder~~  
  ~~Package encoder/decoder~~  
  ~~Upload custom data~~  
  Make reliable audio production line  
  Print custom film reel  
  Develop 3D cartridge case model  
  Develop case cover sticker template  
  Assemble custom cartridge  
  ### FINISH
  
  <br><br><br>
  
  ## ⚠️ DISCLAIMER ⚠️ 
  This repository is for <b>educational use only</b>. The scripts and tools provided here are intended to support legal reverse engineering and modding of content already owned by the user. Please do not use this information to distribute unauthorized copyright products.
</div>

<br><br><br>

<div align="center">

  ## Directory
  [![Makers](https://img.shields.io/badge/Making_a_Cartridge-red)]()
  [![Contributors](https://img.shields.io/badge/Contribute_to_Project-yellow)]()

  [![QCDF](https://img.shields.io/badge/Repository-Forum-blue)](https://github.com/mtkimmins/LTSDM_hack/discussions)
  [![Wiki](https://img.shields.io/badge/Wiki-Home-green)](https://github.com/mtkimmins/LTSDM_hack/wiki/)
  [![Todo](https://img.shields.io/badge/Repository-To_Do_List-purple)](https://github.com/mtkimmins/LTSDM_hack/issues)

</div>

### What this Repository Contains
- **Cartridge dumping** workflows (noise reduction, repeatability, verification)
- **Container/region parsing** (documentation about segments/regions/pointers/tables)
- **Audio pipeline experiments** (codec investigations)
- **Hardware notes** for reading cartridges (breakouts/shields, wiring, voltage)


## Links to similar projects:
* [GainSec](https://github.com/GainSec/Little-Tikes-DreamProjector-Reverse-Engineering)
* [John-K](https://github.com/John-K/LittleTikesDreamProjector/)
