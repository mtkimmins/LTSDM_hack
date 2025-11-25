# PureBin - A Democratic Filter for Merging Multiple Binary Files


## In Progress
## To Do
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






