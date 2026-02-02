# LTSDM RePulse - A LTSDM Cartridge Data Handler
## Roadmap
1) ~~Read up on requirements for PCM decoding~~
2) Make the custom PCM algorithm
3) Play audio to validate
4) Feed in PCM region-by-region


# In Progress
OUT: gold standard .bin
* Scan and select arduino
    * loop through all ports (find "arduino"++ in VID/PID)
    * find ports with arduinos/raspPi/esp32
    * from port list, find any arduinos that already has the target firmware
    * return a list of ports with pre-config devices (popup asking to use the detected device that is already setup)
        * (IF NOT LAST SETP) return a list of ports with compatible devices
    * if many devices detected, select device
* Flash device
    * (IF PRE-CONFIGURED) check if firmware needs updating
        * (IF YES LAST STEP) update firmware
    * confirm the selected device (warning of wiping firmware, unless pre-configured)
    * flash the device with newest version of firmware
    * validate with handshake
* Dump data
    * set baud rate to device
    * Get first x bytes
    * validate those initial bytes as something other than blank
        * (IF BLANK) throw error
    * write and save dump
        * repeat x4 (5 in total)
* Validate dumps
    * compare all dumps (80-90% conserved)
    * consolidate for gold standard
    * target compare LTSDM magic number, # pointers, conserved pointers, segment 2.1, segment 2.2, segment 7, segment 6 length, segment 5 is all blank, segment 4 (from pointers)
* Output gold standard .bin




# To Do
* Validate an unknown .bin file as LTSDM cartridge data
* Make a wireframe navigation system
