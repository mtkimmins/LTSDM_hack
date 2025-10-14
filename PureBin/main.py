import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

BIN0PATH = ""
BIN1PATH = ""
BIN2PATH = ""
BIN3PATH = ""
BIN4PATH = ""
REPORTCSVPATH = ""

runOpeningText = "Here is the text for the new window. There should be a run function afterward an assignment of 5 bins."

currentPosition = 0
currentComparisonList = []

newBin = None
newByte = None

reportCSV = None
reportCSVLocation = None
reportCSVByte0 = None
reportCSVByte1 = None
reportCSVByte2 = None
reportCSVByte3 = None
reportCSVByte4 = None

# OnStart announce what to do -> "OK"
def open_run_window():
    runWindow = tk.Toplevel(root)
    runInstructions = tk.Label(runWindow)
    runInstructions.pack()

# Select for upload
def select_file(self):
    fileTypes = [("Binary Files", "*.bin"), ("All Files", "*.*")]
    filepaths = fd.askopenfilenames(
        title="Select 5 Binary Dump Files...",
        filetypes=fileTypes
    )


# Make a window
root = tk.Tk()
root.title("Pure-BIN 5-to-1 Transformer")

mainframe = ttk.Frame(root, padding=(3,3,12,12))
mainframe.grid(column=0,row=0,sticky=("N","W","E","S"))

# Make the buttons (Start, Exit)
startButton = tk.Button(mainframe, text="Start", command=open_run_window)
startButton.grid(column=0,row=0, sticky=("W","E"))
exitButton = tk.Button(mainframe, text="Exit")
exitButton.grid(column=0,row=1)
root.bind("<Return>", open_run_window)
root.mainloop()



# Upload exactly 5 (can upload many, but will overwrite the current arrangement and populate from 0)
# Display paths beside assigned name
# Run
# Save report
# Completion notification and report location