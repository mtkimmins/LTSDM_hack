## Making a parser that will store and slice the locations of each segment and region, then do an analysis on each and between.
OUT_FILE = "report.md"

BIN_PATH_1 = "RePulse\BSLSBSBaseF.bin"
BIN_PATH_2 = ""

############################################################
class RegionEncoder:
    # Purpose is to stuff BinaryRegions with formatted data
    def __init__(self, data:str, binary_region:BinaryRegion) -> None:
        self.raw_data = data
        self.list_data = []

    def convertRawList(self, raw_data:str)->list:
        b_list:list[str] = raw_data.split("\x")
        f_list:list = []
        for item in b_list:
            a = bytes(item)
            f_list.append(a)

        return f_list

class BinaryRegion:
    def __init__(self, name:str, start_address:int, last_address:int, data:list) -> None:
        self.name = name
        self.start_address = start_address
        self.last_address = last_address
        self.data = data
#---------------------------------------------------
class Segment1Header:
    pass
class Segment2ConservedRegion:
    pass
class UniqueRegion:
    pass
class Segment5ConservedRegion:
    pass
class Segment6PaddingRegion:
    pass
class Segment7Line:
    pass
class Segment8TerminalPadding:
    pass
#-----------------------------------------------------
class BinaryFile:
    def __init__(self, file_path:str) -> None:
        self.path:str = file_path

############################################################
with open(BIN_PATH_1,"rb") as full_bin:
    for line in full_bin:
        print(line)