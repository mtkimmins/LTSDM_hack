# Tail Snap - A program to perform retrograde alignment analysis between binary files

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
