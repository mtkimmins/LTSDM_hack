import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import os
from collections import Counter
import datetime

#######################################
#   CONSTANTS/VARS
#######################################
REFERENCE_FILE_1 = "PureBin/samples/BSLSBSBaseM.bin"
REFERENCE_FILE_2 = "PureBin/samples/MLionGS.bin"

OUTPUT_FILE_NAME = "goldStandardBin"

runOpeningText = "Here is the text for the new window. There should be a run function afterward an assignment of 5 bins."

newBinFile = None
newByte = None

reportCSVFile = None
reportCSVLocation = None
reportCSVBytesList = []

#######################################
#   CLASSES/FUNC
#######################################

class Settings:
    def __init__(self)->None:
        pass

    # Add Setting

    # Remove Setting

    # Reset Setting

    # Set Setting

class MainWindow:
    def __init__(self)->None:
        pass

    # Init Main Window

    # Add Child Window

    # Remove Child Window

# Base class. All Segments will have a name, hex, and size
class Segment:
    def __init__(self, name:str, raw_hex_list:list)->None:
        self.name:str = name
        self.raw_hex_list:list = raw_hex_list
        self.size:int = self._getSize()

    def _getSize(self)->int:
        return len(self.raw_hex_list)


# This will have Segment's name, hex, size. It will also have a pointer and a table
class UniqueRegion(Segment):
    def __init__(self, name:str, data:list)->None:
        super().__init__(name, data)
        self.table:list = []


# This
class SegmentOne(Segment):
    def __init__(self, data)->None:
        super().__init__("one", data)
        self.ltsdm_magic_n:list = self._getLTSDMMagicNumberList()
        self.cartridge_magic_n:list = self._getCartridgeMagicNumberList()
        self.segment_2_pointers:list = self._getPointers(2) # Segment 2.1 and 2.2
        self.segment_3_pointers:list = self._getPointers(3) # Segment 3, Regions 1 - 12
        self.segment_4_pointers:list = self._getPointers(4) # Segment 4, Regions 13 - 24
        self.pointer_frame:int = 4
        self.total_pointers_n:int = 26
    
    def _getPointers(self, segment_n:int)->list:
        pointers:list = []
        for i in range(self.total_pointers_n):
            # Segment 2.1 = 0; Segment 2.2 = 1; Region 1 = 2; Region 2 = 3; ... Region 24 = 25
            match segment_n:
                case 2: # Get segment2 pointers (x2)
                    if i > 1: break
                case 3: # Get segment3 pointers (Regions 1-12, unique)
                    if i < 2: continue
                    if i > 13: break
                case 4: # Getm segment4 pointers (Regions 13-24, conserved)
                    if i < 14: continue
                case _:
                    print("UNKNOWN SEGMENT")
            address:list = []
            for b in range(self.pointer_frame):
                address.append(self.raw_hex_list[self.pointer_frame + (self.pointer_frame*i+(b))])
            pointers.append(address)
        return pointers
    
    def _getLTSDMMagicNumberList(self)->list:
        ltsdm_magic_n:list = [self.raw_hex_list[0], self.raw_hex_list[1]]
        return ltsdm_magic_n
    
    def _getCartridgeMagicNumberList(self)->list:
        cart_magic_n = [self.raw_hex_list[2], self.raw_hex_list[3]]
        return cart_magic_n
    
    def getSize(self)->int:
        return len(self.raw_hex_list)



class SegmentPointered(Segment):
    def __init__(self, name, data)->None:
        super().__init__(name, data)
        self.pointer:list = self._getPointer()

    def _getPointer(self)->list:
        return [self.raw_hex_list[0], self.raw_hex_list[1], self.raw_hex_list[2], self.raw_hex_list[3]]



class SegmentRegions(Segment):
    def __init__(self, name, data)->None:
        super().__init__(name, data)
        self.regions:list = []
        self.size:int = 0

    def addRegion(self, region:Segment)->None:
        if self.size < 12:
            self.regions.append(region)
            self._updateSize()
        else:
            print("CANNOT ADD REGION TO ",self,". >> FULL.")


    # def removeRegion(self, region:Segment)->None:

    def _updateSize(self)->None:
        self.size = len(self.regions)

class SegmentSix:
    def __init__(self)->None:
        self.name:str = "six"


class HexFile:
    def __init__(self, raw_hex_list, one:SegmentOne, two_one:SegmentSized, two_two:SegmentSized, three:SegmentRegions, four:SegmentRegions, five:Segment, six:SegmentSix, seven:Segment)->None:
        self.raw_hex_list:list = raw_hex_list
        self.segment_1:SegmentOne = one
        self.segment_2_1:SegmentSized = two_one
        self.segment_2_2:SegmentSized = two_two
        self.segment_3:SegmentRegions = three
        self.segment_4:SegmentRegions = four
        self.segment_5:Segment = five
        self.segment_6:SegmentSix = six
        self.segment_7:Segment = seven

    def getRange(self, start:int, end:int)->list:
        hex_list:list = []
        for h in range(start,end):
            hex_list.append(self.raw_hex_list[h])
        return hex_list



class HexManager:
    def __init__(self)->None:
        self.address_frame = 4
        self.line_frame = 16

    # Loading Binary
    def loadBinarytoMatrix(self, file_path:str)->list: # Validated
        file_list:list = []
        with open(file_path,"rb") as file:
            for line in file:
                for byte in line:
                    h = hex(byte)
                    file_list.append(h)
        return file_list

    # Tag Binary

    # Saving Binary

    # Checking Binary

    # Translating Binary

class Communicator:
    def __init__(self)->None:
        pass

    # Detect Completion

    # Add Signal Target

    # Remove Signal Target

    # Transmit Signal

    


# OnStart announce what to do -> "OK"
def open_run_window(root):
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



##########################################
#   RUNTIME
##########################################
bin = HexManager()
hex_area = bin.loadBinarytoMatrix(REFERENCE_FILE_1)
segment = SegmentOne()
print(segment._getPointers(4))
# Make main window
# root = tk.Tk()
# root.title("Pure-BIN 5-to-1 Transformer")

# mainframe = ttk.Frame(root, padding=(3,3,12,12))
# mainframe.grid()

# # Make the buttons (Start, Exit)
# startButton = tk.Button(mainframe, text="Start", command=open_run_window)
# startButton.grid()
# exitButton = tk.Button(mainframe, text="Exit", command=exit)
# exitButton.grid(column=0,row=1)
# root.mainloop()

# Upload exactly 5 (can upload many, but will overwrite the current arrangement and populate from 0)
# Display paths beside assigned name
# Run
# Save report
# Completion notification and report location