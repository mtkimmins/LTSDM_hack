# Data Structure of an LTSDM Cartridge
## Overview
* Data stored in *Little Endian* format
* Generally speaking, an LTSDM cartridge is comprised of an initial pointer table filled with addresses of `.a18` files $\pm$ sequences of LED commands
  
**Graphical Depiction of Official LTSDM Data Structure**
```mermaid
graph LR
	i1(LTSDM Cartridge)-->|1MiB| A(( ))
	A-->B(Segment 1)
	A-->C(Segment 2)
	A-->D(Segment 3)
	A-->E(Segment 4)
	A-->F(Segment 5)
	A-->G(Segment 6)
	A-->H(Segment 7)
	B-->BA(Magic Numbers)
	B-->BB(Pointer Table)
	BA-->BAA(2-byte sequence x 2 <br> non-essential)
	BB-->BBA(4-byte address x 26 <br> essential)
	C & D & E --> R0[.a18 file]
```
