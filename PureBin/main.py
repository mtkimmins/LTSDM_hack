import tkinter as tk

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
    runWindow = tk.Toplevel(window)
    runInstructions = tk.Label(runWindow)
    runInstructions.pack()

# Make a window
window = tk.Tk()
window.title = "Pure-BIN 5-to-1 Transformer"

# Make the buttons (Start, Exit)
startButton = tk.Button(window, text="Start", command=open_run_window)
startButton.pack()
exitButton = tk.Button(window, text="Exit")
exitButton.pack()
window.mainloop()


# Select for upload
# Upload exactly 5 (can upload many, but will overwrite the current arrangement and populate from 0)
# Display paths beside assigned name
# Run
# Save report
# Completion notification and report location