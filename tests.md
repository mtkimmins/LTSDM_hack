# Catalogue of Tests



## 24Aug2026-r1o-ft
24 August 2026

### Purpose
Isolate an incompatible a1800-codec "frame". A frame is a 40-byte block that follows the 'a18' header or another block. The duration represented by one frame is 20ms. It is confirmed by previous testing that the projector crashes upon ~1 second of ratadon3.bin audio, however, the mvp and original dumps all work. Let us isolate an incompatible frame from ratadon3.bin Region 1.

### Procedure
* [x] copy mvp.bin
* [x] copy ratadon3.bin
* [x] in only Region 1 of copy-mvp.bin, substitute the first frame for each of ratadon3.bin's frames from its Region 1. I will stop when 3 frames are confirmed to induce erroneous behaviour in, and/or crash, the projector.

### Results
|ratadon3.bin Frame (#)|Observations|
|:-:|:-:|
|1|Ran fine on projector.|
|2||
|...|...skipping to about 1 second where it crashed...|
|45|Ran fine on projector.|
|46|CRASHED!!! <br>No sound, just a light projected first frame then crash.|
|47|Binary looks suspicious as there are a string of `00`s at the end of this Frame... <br>No, it ran without error.|
|48||
|49||
|50||
|51||

### Conclusions
* The appearance of a string of `00` does not mandate an error.
* Erroneous audio can be isolated to a single Frame.
* Frame 46 of Region 1 of `ratadon3.bin` causes a projector crash.
