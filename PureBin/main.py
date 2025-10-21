import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import os
from collections import Counter
import datetime

OUTPUT_FILE_NAME = "goldStandardBin"

runOpeningText = "Here is the text for the new window. There should be a run function afterward an assignment of 5 bins."

newBinFile = None
newByte = None

reportCSVFile = None
reportCSVLocation = None
reportCSVBytesList = []

# OnStart announce what to do -> "OK"
def open_run_window():
    runWindow = tk.Toplevel(root)
    runInstructions = tk.Label(runWindow, text=runOpeningText)
    runOkButton = tk.Button(runWindow, text="OK", command=select_file)
    runInstructions.pack()
    runOkButton.pack()

# Select for upload
def select_file():
    fileTypes = [("Binary Files", "*.bin"), ("All Files", "*.*")]
    filePaths = fd.askopenfilenames(
        title="Select 5 Binary Dump Files...",
        filetypes=fileTypes
    )
    print(filePaths)
    open_files(filePaths, OUTPUT_FILE_NAME)

def open_files(filePaths, outputFile):
# open all the inputs
    try:
        openInputsList = [open(file, 'rb') for file in filePaths]
        # verify they are all the same length
        lengths = [os.path.getsize(file) for file in filePaths]
        agreeance = set(lengths)
        setLength = len(agreeance)
        print(f">>Variance in file lengths (=1): {setLength}")
        if setLength <=1:
            print(">>All files are equal length")
        else:
            print(">>WARNING: Files selected are of unequal lengths")
        # open the output file
        now = datetime.datetime.now()
        rng = now.second + now.minute + now.hour + now.day + now.month + now.year
        print(rng)
        with open(outputFile+str(rng)+".bin", 'wb') as outF:
            #go through each byte
            for _ in range(lengths[0]):
                currentByteList = [byte.read(1) for byte in openInputsList]
                #assess agreeance between bytes
                majorityByte, count = Counter(currentByteList).most_common(1)[0]
                print(">> " + str(majorityByte) + " was counted " + str(count) + " times.")
                if count > 3:
                    print(">> Odd one out")
                    outF.write(majorityByte)
                else:
                    print(">>ERROR: no unanimous agreeance!")
                    print(f">> {currentByteList}")
                    print(f">> Random bin assigned number: {rng}")
                    return()
            
            print(f"Democratic BIN file: {outputFile, rng} .bin created.")

        
    except Exception as e:
        print(f">>ERROR: {e}")


#     try:
#         filesToOpen = [open(file, 'rb') for file in filepaths]
#         minLength = str([os.path.getsize(file) for file in filepaths])
#         print(f"All files will be read as these sizes: {minLength} in bytes.")

#         with open(newBinFile, 'wb') as out_f:
#             for _ in range(minLength[0]):
#                 bytes_at_position = [fh.read(1) for fh in filesToOpen]

#                 majority_byte, count = Counter(bytes_at_position).most_common(1)[0]

#                 out_f.write(majority_byte)

# Clear all variables, reset
def clear_reset():
    pass

#---------------------------------------------------------------------------------
# Make main window
root = tk.Tk()
root.title("Pure-BIN 5-to-1 Transformer")

mainframe = ttk.Frame(root, padding=(3,3,12,12))
mainframe.grid(column=0,row=0,sticky=("N","W","E","S"))

# Make the buttons (Start, Exit)
startButton = tk.Button(mainframe, text="Start", command=open_run_window)
startButton.grid(column=0,row=0, sticky=("W","E"))
exitButton = tk.Button(mainframe, text="Exit", command=exit)
exitButton.grid(column=0,row=1)
root.mainloop()

# Upload exactly 5 (can upload many, but will overwrite the current arrangement and populate from 0)
# Display paths beside assigned name
# Run
# Save report
# Completion notification and report location