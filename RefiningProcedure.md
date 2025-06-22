# Procedure for Gleaning Gold-Standard Binary Data Files

1) Dump the same chip 5 separate times into different .bin files at Baud Rate 19200
2) Take a copy of the first file and mark as "BASE" for the file that will be directly edited to the most democratic data
3) The first file is now a reference backup
4) Diff the BASE against all other 4 files and mark the areas that are different
5) Manually go through the marked changes in BASE and change each region to the most agreed-upon answer (5-grade refined)
6) Repeat steps 1-5 with another copy of the same cartridge
7) Take these two refined files and copy the first one as "GS" (see step 2-3)
8) Diff the GS against the other file. If the diff does not reveal any point-changes, you have been successful (10-grade refined)
9) The resulting GS is the gold-standard if it passed step 8
10) If step 8 reveals any changes, this will have to be investigated for a certain specific stamp or wiring difficulty. Alternatively, the .bin could also be diffed with another GS if the variable region is fixed.

# Dealing With Disrepancies
|CONDITION|ACTION|
|:-:|:-:|
|BASE is the only outlier|Change to majority|
|BASE only shares discrepancy with 1 other file|Check that address in other bins and confirm complete agreeance. Change to majority. If >1 files differ at this address from each other, defer to further workup|
|2-3 files agree|Defer to further workup|

In ImHex, delete the single disagree bookmarks. Use the Hide feature for quad differences. Flag partial discrepancy.
