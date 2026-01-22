# LTSDM RePulse - A LTSDM Cartridge Data Handler
## Roadmap
1) [Read up on requirements for PCM decoding]()
2) Make the custom PCM algorithm
3) Play audio to validate
4) Feed in PCM region-by-region

## Assumptions
* Target binary areas of LTSDM cartridge data are stored as Pulse-Code Modulation (likely just regions 1-12 -- the unique regions)

# Overview of Procedure
* Intake PCM data
* Separate compressed data from deltas
* Decompress PCM
* Write audio file

## Research
**[Wikipedia - PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation)**
* Typically used for uncompressed digital audio
* PCM usually = WAV or AIFF files
* PCM tracks amplitude of data stream at set intervals -- "sampling rate" -- (rounded to the nearest value of pre-determined quantum step)
    * For every sample, it rounds the amplitude to a step
    * "Sampling depths" = 8,16,20,24 bits/sample (would ours be 4 bytes? = 8 bit/byte * 4 bytes = 32 bits? Deeper than common depths described here..., but those rates are referring to LPCM)
* Many flavours of PCM (adaptive differential was identified by Google Gemini, perhaps explore ADPCM first)

**[Wikipedia - ADPCM](https://en.wikipedia.org/wiki/Adaptive_differential_pulse-code_modulation)**
* Developed for speech coding (validates our use case)
* Windows Sound System supports WAV files
* ["G.722"](https://en.wikipedia.org/wiki/G.722) is a standard format of PCM operating at 48,56,64 kbit/s. This may be more relevant for multiple streams???

**[Wikipedia - WAV](https://en.wikipedia.org/wiki/WAV)**
* Its an application of .RIFF files
* WAV files *can* contain compression
* Data divided into chunks and headers; Example from wikipedia:
<WAVE-form> → RIFF('WAVE'
                   <fmt-ck>            // Format of the file
                   [<fact-ck>]         // Fact chunk
                   [<cue-ck>]          // Cue points
                   [<playlist-ck>]     // Playlist
                   [<assoc-data-list>] // Associated data list
                   <wave-data> )       // Wave data

* Each chunk starts with a header. Each header includes a 4-character tag (FourCC) and the size of the chunk (which seems reminiscent of LTSDM regions).
* Interpretation depends on the FourCC tag used. There are many...
* 

**[Wikipedia - FourCC](https://en.wikipedia.org/wiki/FourCC)**
* sequence of 4 bytes (like what can be seen at the beginning of each region); usually in ASCII or hex (?validate which)
* These are written in **big-endian** relative to the underlying ASCII character sequence

**[Wikipedia - Audio Codec](https://en.wikipedia.org/wiki/Audio_codec)**
* A program, "Codec," that encodes/decodes audio -- perhaps an open-source program currently exists for our job?
* They transfer data through buses like SPI (format of our p25d80sh chip)
* Possible audio codecs to explore:
    * FLAC
    * WavPack
---
# LTSDM PureBin - A Multipurpose Tool for Handling LTSDM Cartridge Data Dumps


## In Progress
## To Do
* Be able to consolidate gold standards
* Be able to sense arduino, trigger dump cartridges
* Have a console-based navigation system, no GUI yet
* Auto-validate length compatibility as you upload files as inputs
* Cap the number of files you can input to 10
* Popup window when 2:3 ratio mutation is found (implement pre-settings)
* Display an accuracy assessment for each mutation choice
* Display statistic report for confidence of output
* Make a way to alert me on my phone when consolidation is completed.
* Suggest tie-breaker sample if even sampling
* Option to read files to shortest length (show length)
___
# Assumptions
* All .bins are the same length

# Overview of Procedure
* Open 5 .bin files
* Create a list X 
* Create a new .bin to write to, Y
* Create a position tracker i
* Create a new byte variable b
* Create a new .csv sheet C
* Loop
* At position i of each .bin file, read byte
* Extract the most common byte sequence
* If there is no discrepancy, pass byte to b
* If discrepancy is 1:4, pass the democratic value to b
* If discrepancy is 2:3, stop the program and throw a warning. Reveal the values of each file side-by-side. Offer to manually approve the most common value.
* Write byte b to the new file
* If discrepancy: write location, all file bytes, most democratic value entered.
* Repeat until all bytes read
* Provide sheet C

# Official Documentation
## Required Concepts: children (attributes)
Hex file: segments 1-7 (codified segment attributes)
Hex Body: segment 5, segment 6, segment 7 (list of hex)
Segment 1: LTSDM magic, cartridge magic, pointer table (magic numbers x2, list of pointers)
Conserved Areas: Segment 2.1, Segment 2.2, Regions 13-24 (initial pointer, hex body)
Unique Areas: Regions 1-12 (conserved area, table hex)



---
# Tail Snap - A Sub-program of LTSDM RePulse to perform retrograde alignment analysis between binary file regions

## Introduction
The binary files from LTSDM cartridges reveal a pattern of unique data sandwiched between two sections of boilerplate data. To complicate straight comparison, such unique sections are of variable length, thus preventing an even address alignment. The manual cutting and pasting of binary data is tedious and bad for mental health. A program could potentially be made to locate such unique sections between .bin files and subsequently reveal the extent of the latter constant section. There is a sea of FF bytes between the end of the actual data and the end of the chips' memory capacity (ignoring the late strip of bytes speculated as a crypto-key of some kind by GainSec). So, one could potentially start the cursor X-bytes prior to the end of the memory capacity (since the chips' memories are required to be a finite amount). Then an interation could scan the data until it reads a byte other than FF and return its address. Then from each unique address, you make two new lists of bytes, and compare each byte until you get a discrepancy. THIS address will be where the unique data for each cartridge ends. I will have to run the program several times with different pairs (or comparing 3+ .bin files) in order to ensure there are not a few terminal bytes that match by chance (I lean toward the 3+ file approach... we can observe first-past-the-post models are prone to statistical error).

This program, I arbitrarily dubbed "Tail Snap," is meant to automate the alignment and comparison of terminal .bin file sections. Such a step of data analysis will narrow down the location of the unique data pockets of the cartridges. This revelation will hopefully progress the effort of making a custom data template for alternative storytelling.

## Narrative layout of the Program
1) Take up to 5 input bin files (they must be high-fidelity, *purified* bin files)
2) For each bin, put the pointer X bytes away from the end (on the beginning-end of the crypto-key)
3) Iterate over the data retroactively until you read a non-empty byte (besides FF).
4) Mark this position down in a directory.
5) Create a new list to hold all the instant-comparison values
6) From each unique terminal data position, place the pointer at the end of each file's non-empty data.
7) Iterate backward and capture each file's relative positioned byte.
8) Stop when a discrepancy happens, and return that byte address.
9) Also return a flipped list of bytes recorded between step 4 and step 8 (one instance).

## Conclusion
This last byte address will be unique to each analyzed .bin file. However, the final section of non-empty data should be identical between cartridges. From here, we glean the latter part of data.

The tricky part will be ensuring there are no other constant pockets within the unique data section that are offset for each cartridge somehow. I'll have to think about how to analyze such areas -- perhaps excise each unique section and go over them slowly to detect any consistencies...