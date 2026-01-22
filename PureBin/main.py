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
        self.built:bool = False
        self.hex:list = hex
        self.length:int =  1048576 # constant, files should be 1Mib exactly
        self.pointer_frame:int = 4
        self.total_pointers_n:int = 26
        self.segment_4_region_lengths:list = [326, 926, 1006, 1006, 806, 726, 606, 686, 446, 886, 406, 726]
                
        self.segment_1_hex:list = self._getSegmentOneHex(self.hex)
        self.ltsdm_magic_n:list = self._getLTSDMMagicNumberList(self.segment_1_hex)
        self.cartridge_magic_n:list = self._getCartridgeMagicNumberList(self.segment_1_hex)
        self.segment_2_pointers:list = self._getPointers(self.segment_1_hex, 2) # Segment 2.1 and 2.2 :: Validated
        self.segment_3_pointers:list = self._getPointers(self.segment_1_hex, 3) # Segment 3, Regions 1 - 12 :: Validated
        self.segment_4_pointers:list = self._getPointers(self.segment_1_hex, 4) # Segment 4, Regions 13 - 24 :: Validated
                
        self.segment_2_1_hex:list = self._getSegment(self.hex, self.segment_2_pointers[0],self.segment_2_pointers[1]) #Validated
        self.segment_2_2_hex:list = self._getSegment(self.hex, self.segment_2_pointers[1], self.segment_3_pointers[0]) #Validated
        self.segment_3_regions:list[list] = self._getS3Regions(self.segment_3_pointers, self.segment_4_pointers[0])
        self.segment_4_regions:list[list] = self._getS4Regions(self.segment_4_pointers, self.segment_4_region_lengths)
        self.segment_5_hex:list = self._getSegmentFive(self.listToDecimal(self.segment_4_pointers[-1]) + self.segment_4_region_lengths[-1]) # this will be empty w 0xff
        self.segment_6_hex:list = self._getSegmentSix(self.hex)
        self.segment_7_hex:list = self._getSegmentSeven() # this will be empty w 0xff, this is constant #TODO: for the future, we should switch to an initializing loop that assigns a starting address and a length in bytes

        # Signal that the hex is compiled
        self.built = True

    def __eq__(self, other)->bool:
        if isinstance(other, HexFile):
            if self.hex == other.hex:
                return True
            else:
                return False
        else:
            return False

    def _getSegmentOneHex(self, full_hex:list)->list: # Validated
        return full_hex[0:108]
    
    def _getSegment(self, full_hex:list, start_pointer:list, end_pointer:list)->list: #Validated
        start_address:int = self.listToDecimal(start_pointer)
        end_address:int = self.listToDecimal(end_pointer)
        seg_2_1_hex = full_hex[start_address:end_address]
        return seg_2_1_hex
    
    def _getS3Regions(self, pointers:list, last_pointer:list)->list[list]: #Validated
        seg3:list = []
        all_pointers:list = pointers + [last_pointer]
        # print(all_pointers)
        for p in range(len(all_pointers)):
            # skip the last pointer
            if p == (len(all_pointers) - 1):continue
            # get the pointer's hex
            pointer_hex:list = self._getSegment(self.hex, pointers[p],all_pointers[p + 1])
            seg3.append(pointer_hex)
        return seg3
    
    def _getS4Regions(self, pointers:list, region_lengths:list)->list[list]: #Validated
        seg4:list = []
        for i in range(len(pointers)):
            # get the initial address
            start_index:int = self.listToDecimal(pointers[i])
            last_index:int = (self.listToDecimal(pointers[i]) + region_lengths[i])
            hex:list = self._getSegment(self.hex, self.decimalToList(start_index), self.decimalToList(last_index))
            seg4.append(hex)
        return seg4

    def _getSegmentFive(self, start_index:int)->list: #Verified
        # Get number of bytes between start index and Segment 6
        seg5:list = self._getSegment(self.hex, self.decimalToList(start_index), self.decimalToList(1048447))
        return seg5

    def _getSegmentSix(self, full_hex:list)->list: #Verified
        return full_hex[1048448:1048464]
    
    def _getSegmentSeven(self)->list: # Validated
        seg_7_hex:list = []
        for i in range(112):
            seg_7_hex.append("0xff")
        return seg_7_hex
      
    def _isBuilt(self)->bool:
        return self.built
 
    def _verifySelf(self, hex_reference:HexFile)->bool:
        verified:bool = False
        # are the constant regions the same as GS? [Magic LTSDM, first 3 pointers, segment 2.1, segment 2.2, segment 4, segment 7]
        # Does the LTSDM magic number match?
        # Does the first 3 pointers match (seg 2.1, seg 2.2, region 1)?
        # Does segment 2.1 hex match?
        # Does segment 2.2 hex match?
        # Do the regions in segment 4 match?
        # Is segment 5 all blank? -- map to set, then len() should be 1
        # Does segment 7 match?
        return verified
    
    def _getPointers(self, seg_1_hex:list, segment_n:int)->list: #Validated
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
    
    def _getLTSDMMagicNumberList(self, seg_1_hex:list)->list: #Validated
        ltsdm_magic_n:list = [seg_1_hex[0], seg_1_hex[1]]
        return ltsdm_magic_n
    
    def _getCartridgeMagicNumberList(self, seg_1_hex:list)->list: #Validated
        cart_magic_n = [seg_1_hex[2], seg_1_hex[3]]
        return cart_magic_n
    
    def _StringToNumberHex(self, item:str)->int: # Validated
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
    
    def hexStringToDecimal(self, hex_string:str)->int: #Validated
        decimal = 0
        # Cut off the "0x" beginning
        cropped_hex:str = hex_string[2:]
        # Check if a hex
        decimal_parts = map(self._StringToNumberHex, cropped_hex)
        # Times the parts accordingly
        ramp:int = len(cropped_hex)-1
        for part in decimal_parts:
            # print(part)
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

    def listToDecimal(self, hex:list[str])->int: #Validated
        list_to_string:str = self.listToHexString(hex)
        decimal = self.hexStringToDecimal(list_to_string)
        return decimal
    
    def _hexToLetterString(self, hex:float)->str: #Validated
        # hex is float due to self.decimalToHexString formatting
        item:str = ""
        match hex:
            case 10:
                item = "a"
            case 11:
                item = "b"
            case 12:
                item = "c"
            case 13:
                item = "d"
            case 14:
                item = "e"
            case 15:
                item = "f"
            case _:
                item = str(hex)
        return item
    
    def decimalToHexString(self, decimal:int)->str: #Validated
        hex_string:str = ""
        prefix:str = "0x"
        hex:list = []
        quotient:int = decimal
        while quotient > 0:
            remainder:float = quotient % 16
            quotient = quotient // 16
            hex.append(remainder)
        hex.reverse()
        # Map the hex-str converter to the list
        str_list = map(self._hexToLetterString, hex)
        for item in str_list:
            hex_string += item

        return prefix + hex_string
    
    def hexStringToList(self, hex_string:str)->list: #Validated
        hex_list_intermediate:list = []
        padded_hex_str:str = ""
        hex_list:list = []
        # little endian
        prefix:str = "0x"
        # Cut off the prefix
        hex_item:str = hex_string[2:]
        # Get how long the string should be in pairs
        if (len(hex_item) % 2) is not int(): # If its odd
            # Pad front
            padded_hex_str = hex_item.zfill(len(hex_item) + 1)
        # print(padded_hex_str)
        # Get each pair
        for i in range(len(padded_hex_str) // 2):
            hex_list_intermediate.append([padded_hex_str[i * 2] + padded_hex_str[(i * 2) + 1]])
        # print(hex_list_intermediate)
        for item in hex_list_intermediate:
            byte:str = prefix + item[0]
            hex_list.append(byte)
        # little endian is backward, so reverse it
        hex_list.reverse()
        return hex_list
    
    def decimalToList(self, decimal:int)->list: #Validated
        # decimal to hex string
        hex_string:str = self.decimalToHexString(decimal)
        # hex string to list
        hex_list:list = self.hexStringToList(hex_string)
        return hex_list

#######################################
#   RUNTIME
#######################################
hex_data1 = DataLoader().loadBinarytoMatrix(REFERENCE_FILE_1)
hex_data2 = DataLoader().loadBinarytoMatrix(REFERENCE_FILE_2)
hex_file1 = HexFile(hex_data1)
hex_file2 = HexFile(hex_data2)
print(hex_file1 == hex_file1)