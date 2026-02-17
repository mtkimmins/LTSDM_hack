# Implementing A1800 Codec

## Pipeline
* Record appropriate audio .wavs (x12)
* Input audio into program
* ENCODE
    * for each .wav, turn into .bin region
    * make new .bin
    * keep track of pointers for each region
    * compile pointers into segment 1
    * write .bin by each segment
    * What to do for segment 6? (try copying another's segment 6)
* Makes an intact .bin