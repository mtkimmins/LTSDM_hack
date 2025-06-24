See [file signatures](https://en.wikipedia.org/wiki/List_of_file_signatures) for target filters

# ImHex using "Find" function
|Search Type|Minimum Length (Bytes)/Alignment|Filter|# results|Comments|
|:-:|:-:|:-:|:-:|:-:|
|STRING|13||1|Es4cp0BR[2~e-  <br>This is the longest string in the .bin file. Not within diff section|
|STRING|12||2|*p-_aTV;_7:U  <br>This is the second longest string in the .bin file. Not within diff section|
|STRING|11||4||
|STRING|10||11||
|STRING|9||33||
|STRING|8||79||
|STRING|7||183||
|STRING|1||59161||
|STRING|1|FORM|0|"FORM" could reveal AIFF, IFF 8-bit sampled voice formats|
|STRING|1|AIFF|0|"AIFF" could reveal AIFF formats|
|STRING|1|RIFF|0|"RIFF" could reveal WAV, AVI, Qualcomm PureVoice formats|
|STRING|1|WAV|0|"WAV" could reveal WAV formats|
|STRING|1|AVI|0|"AVI" could reveal AVI formats|
|STRING|1|OggS|0|could reveal ogg formats|
|STRING|1|fLaC|0|could reveal FLAC formats|
|STRING|1|MThd|0|could reveal MIDI formats|
|STRING|1|.snd|0|could reveal au audio formats|
|STRING|1|#!|4|none were #!AMR or #!SILK␊ indicating ACELP or Skype audio respectively|
|BINARY|1|43 72 65 61 74 69 76 65 20 56 6F 69 63 65 20 46 69 6C 65 1A 1A 00|0|could reveal Creative Voice File format|
|BINARY|1|52 49 46 46|0|could reveal .wav|
|BINARY|1|08 80|261|appears in low entropy patches in regular intervals, always followed by 3 bits, then sandwiched with another 08 80 <br>not within any diff sections|

