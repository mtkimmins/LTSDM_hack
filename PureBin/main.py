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
    


class HexFile:
    def __init__(self, hex:list)->None:
        self.hex:list = hex
        self.length:int =  1048576 # constant, files should be 1Mib exactly
        self.pointer_frame:int = 4
        self.total_pointers_n:int = 26
                
        self.segment_1_hex:list = self._getSegmentOneHex(self.hex)
        self.ltsdm_magic_n:list = self._getLTSDMMagicNumberList(self.segment_1_hex)
        self.cartridge_magic_n:list = self._getCartridgeMagicNumberList(self.segment_1_hex)
        self.segment_2_pointers:list = self._getPointers(self.segment_1_hex, 2) # Segment 2.1 and 2.2
        self.segment_3_pointers:list = self._getPointers(self.segment_1_hex, 3) # Segment 3, Regions 1 - 12
        self.segment_4_pointers:list = self._getPointers(self.segment_1_hex, 4) # Segment 4, Regions 13 - 24
                
        self.segment_2_1_hex:list = []
        self.segment_2_2_hexlist = []
        self.segment_3_regions:list = []
        self.segment_4_regions:list = []
        self.segment_5_hex:list = [] # this will be empty w 0xff
        self.segment_6_hex:list = self._getSegmentSix(self.hex)
        self.segment_7_hex:list = self._getSegmentSeven() # this will be empty w 0xff, this is constant

    def _getSegmentOneHex(self, full_hex:list)->list:
        return full_hex[0:108]
    
    def _getSegmentSeven(self)->list:
        seg_7_hex:list = []
        for i in range(112):
            seg_7_hex.append("0xff")
        return seg_7_hex
    
    def _getSegmentSix(self, full_hex:list)->list: #Verified
        return full_hex[1048448:1048464]
    
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
    
    def _getPointers(self, seg_1_hex:list, segment_n:int)->list:
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
                address.append(seg_1_hex[self.pointer_frame + (self.pointer_frame*i+(b))])
            pointers.append(address)
        return pointers
    
    def _getLTSDMMagicNumberList(self, seg_1_hex:list)->list:
        ltsdm_magic_n:list = [seg_1_hex[0], seg_1_hex[1]]
        return ltsdm_magic_n
    
    def _getCartridgeMagicNumberList(self, seg_1_hex:list)->list:
        cart_magic_n = [seg_1_hex[2], seg_1_hex[3]]
        return cart_magic_n
    
    def _ToNumberHex(self, item:str)->int:
        digit = 0
        match item:
            case "a":
                digit = 10
            case "b":
                digit = 11
            case "c":
                digit = 12
            case "d":
                digit = 13
            case "e":
                digit = 14
            case "f":
                digit = 15
            case _:
                digit = int(item)
        return digit
    
    def getRange(self, start:int, end:int)->list:
        hex_list:list = []
        for h in range(start,end):
            hex_list.append(self.hex[h])
        return hex_list
    
    def getSize(self)->int:
        return len(self.hex)
    
    def hexStringToDecimal(self, hex_string:str)->int: #Validated
        decimal = 0
        # Cut off the "0x" beginning
        cropped_hex:str = hex_string[2:]
        # Check if a hex
        decimal_parts = map(self._ToNumberHex, cropped_hex)
        # Times the parts accordingly
        ramp:int = len(cropped_hex)-1
        for part in decimal_parts:
            print(part)
            decimal += part * pow(16,ramp) 
            ramp -= 1
        return decimal
    
    def listToHexString(self, hex:list[str])->str: # Validated
        # LITTLE ENDIAN
        prefix:str = "0x"
        hex_string:str = ""
        hex_string_list:list = []
        for h in hex:
            cropped_hex:str = h[2:]
            hex_string_list.append(cropped_hex)
        for i in range(len(hex_string_list)):
            hex_piece = hex_string_list.pop()
            hex_string += hex_piece
        return prefix + hex_string




#######################################
#   RUNTIME
#######################################
hex_data = DataLoader().loadBinarytoMatrix(REFERENCE_FILE_1)
hex_file = HexFile(hex_data)
print(hex_file.hexStringToDecimal(hex_file.listToHexString(["0xff","0x1c","0x00","0xa4"])))