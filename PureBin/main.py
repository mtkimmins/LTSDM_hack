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


class DataLoader:
    def __init__(self):
        pass

    def loadBinarytoMatrix(self, file_path:str)->list: # Validated
        file_list:list = []
        with open(file_path,"rb") as file:
            for line in file:
                for byte in line:
                    h = hex(byte)
                    file_list.append(h)
        return file_list
    
    def verifyLength(self, hex:list)->bool:
        verified:bool = False
        # is it the right size?
        if (len(hex) == 1048576):
            verified = True
        return verified



class HexFile:
    def __init__(self, hex:list)->None:
        self.hex:list = hex
        self.length:int =  1048576 # constant, files should be 1Mib exactly
        self.segment_1:SegmentOne|None = None
        self.segment_2_1:Region|None = None
        self.segment_2_2:Region|None = None
        self.segment_3:list[UniqueRegion] = []
        self.segment_4:list[Region] = []
        self.segment_5:list = [] # this will be empty w 0xff
        self.segment_6:list = []
        self.segment_7:list = ['0xff'] # this will be empty w 0xff, this is constant
        self.build()

    def build(self)->None:
        # Check if data is compatible

        # Create pointer table
        self.segment_1 = SegmentOne(self.hex[0:(112 - 1)])
        # break out all starting addresses
        #TODO

    def _mapHexToRegion(self, hex, region):
        pass

    def getRange(self, start:int, end:int)->list:
        hex_list:list = []
        for h in range(start,end):
            hex_list.append(self.hex[h])
        return hex_list
    
    def _compareAgainstGS(self, raw_hex:list)->bool:
        is_compatible:bool = False
        return is_compatible
    
    def _isBuilt(self)->bool:
        is_built:bool = False
        return is_built
    
    def _isFilled(self)->bool:
        is_filled:bool = False
        return is_filled

    def _verifySelf(self, hex_reference:HexFile)->bool:
        verified:bool = False
        # are the constant regions the same as GS? [Magic LTSDM, first 3 pointers, segment 2.1, segment 2.2, segment 4, segment 7]
        return verified



# This is a special segment with magic numbers and a pointer table 
class SegmentOne:
    def __init__(self, hex:list)->None:
        self.pointer_frame:int = 4
        self.total_pointers_n:int = 26
        self.hex:list = hex
        self.ltsdm_magic_n:list = self._getLTSDMMagicNumberList()
        self.cartridge_magic_n:list = self._getCartridgeMagicNumberList()
        self.segment_2_pointers:list = self._getPointers(2) # Segment 2.1 and 2.2
        self.segment_3_pointers:list = self._getPointers(3) # Segment 3, Regions 1 - 12
        self.segment_4_pointers:list = self._getPointers(4) # Segment 4, Regions 13 - 24

    
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
                address.append(self.hex[self.pointer_frame + (self.pointer_frame*i+(b))])
            pointers.append(address)
        return pointers
    
    def _getLTSDMMagicNumberList(self)->list:
        ltsdm_magic_n:list = [self.hex[0], self.hex[1]]
        return ltsdm_magic_n
    
    def _getCartridgeMagicNumberList(self)->list:
        cart_magic_n = [self.hex[2], self.hex[3]]
        return cart_magic_n
    
    def getSize(self)->int:
        return len(self.hex)




class Region:
    def __init__(self, hex:list):
        self.hex:list = hex
        self.pointer:list = [hex[0],hex[1],hex[2],hex[3]]




class UniqueRegion(Region):
    def __init__(self, hex:list, table:list):
        super().__init__(hex)
        self.table:list = table

#######################################
#   RUNTIME
#######################################
hex_data = DataLoader().loadBinarytoMatrix(REFERENCE_FILE_1)
print(DataLoader().verifyLength(hex_data))
hex_file = HexFile(hex_data)
