import sys
import wave
import a1800_codec

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} input.wav output.a18")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read WAV
with wave.open(input_file, "rb") as wav:
    channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()
    pcm_data = wav.readframes(wav.getnframes())

print(f"Input:       {input_file}")
print(f"Sample rate: {sample_rate} Hz")
print(f"Channels:    {channels}")
print(f"Bit depth:   {sample_width * 8}-bit")
print(f"PCM bytes:   {len(pcm_data)}")

# A1800 encoder expects mono 16-bit PCM.
if channels != 1:
    raise ValueError(f"Expected mono audio, got {channels} channels")

if sample_width != 2:
    raise ValueError(f"Expected 16-bit audio, got {sample_width * 8}-bit")

if sample_rate != 16000:
    raise ValueError(
        f"Expected 16000 Hz audio, got {sample_rate} Hz"
    )

# Encode
encoded = a1800_codec.encode(
    pcm_data,
    bitrate=16000,
)

# Write .a18
with open(output_file, "wb") as f:
    f.write(encoded)

print(f"Output:      {output_file}")
print(f"A18 bytes:   {len(encoded)}")
