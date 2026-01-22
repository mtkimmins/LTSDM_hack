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



