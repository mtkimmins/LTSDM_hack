# RePulse - A custom GeneralPlus PCM audio player for Little Tikes Story Dream Machine


## Roadmap
1) [Read up on requirements for PCM decoding]()
2) Make the custom PCM algorithm
3) Play audio to validate
4) Feed in PCM region-by-region
___
# Assumptions
* Target binary areas of LTSDM cartridge data are stored as Pulse-Code Modulation (likely just regions 1-12 -- the unique regions)

# Overview of Procedure
* Intake PCM data
* Separate compressed data from deltas
* Decompress PCM
* Write audio file

___
# Research
**[Wikipedia - PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation)**
* Typically used for uncompressed digital audio
* PCM usually = WAV or AIFF files
* PCM tracks amplitude of data stream at set intervals -- "sampling rate" -- (rounded to the nearest value of pre-determined quantum step)
    * For every sample, it rounds the amplitude to a step
    * "Sampling depths" = 8,16,20,24 bits/sample (would ours be 4 bytes? = 8 bit/byte * 4 bytes = 32 bits? Deeper than common depths described here..., but those rates are referring to LPCM)
* Many flavours of PCM (adaptive differential was identified by Google Gemini, perhaps explore ADPCM first)

**[Wikipedia - ADPCM](https://en.wikipedia.org/wiki/Adaptive_differential_pulse-code_modulation)**
* Developed for speech coding (validates our use case)
* Windows Sound System supports WAV files
* ["G.722"](https://en.wikipedia.org/wiki/G.722) is a standard format of PCM operating at 48,56,64 kbit/s. This may be more relevant for multiple streams???

**[Wikipedia - WAV](https://en.wikipedia.org/wiki/WAV)**
* Its an application of .RIFF files
* WAV files *can* contain compression
* Data divided into chunks and headers; Example from wikipedia:
<WAVE-form> → RIFF('WAVE'
                   <fmt-ck>            // Format of the file
                   [<fact-ck>]         // Fact chunk
                   [<cue-ck>]          // Cue points
                   [<playlist-ck>]     // Playlist
                   [<assoc-data-list>] // Associated data list
                   <wave-data> )       // Wave data

* Each chunk starts with a header. Each header includes a 4-character tag (FourCC) and the size of the chunk (which seems reminiscent of LTSDM regions).
* Interpretation depends on the FourCC tag used. There are many...
* 

**[Wikipedia - FourCC](https://en.wikipedia.org/wiki/FourCC)**
* sequence of 4 bytes (like what can be seen at the beginning of each region); usually in ASCII or hex (?validate which)
* These are written in **big-endian** relative to the underlying ASCII character sequence

**[Wikipedia - Audio Codec](https://en.wikipedia.org/wiki/Audio_codec)**
* A program, "Codec," that encodes/decodes audio -- perhaps an open-source program currently exists for our job?
* They transfer data through buses like SPI (format of our p25d80sh chip)
* Possible audio codecs to explore:
    * FLAC
    * WavPack