import argparse
import os
import sys
import wave

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

import a1800_codec


def encode_wav_to_a18(input_file, output_file, bitrate=16000):
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

    if channels != 1:
        raise ValueError(f"Expected mono audio, got {channels} channels")

    if sample_width != 2:
        raise ValueError(f"Expected 16-bit audio, got {sample_width * 8}-bit")

    if sample_rate != bitrate:
        raise ValueError(
            f"Expected {bitrate} Hz audio, got {sample_rate} Hz"
        )

    encoded = a1800_codec.encode(pcm_data, bitrate=bitrate)

    with open(output_file, "wb") as f:
        f.write(encoded)

    print(f"Output:      {output_file}")
    print(f"A18 bytes:   {len(encoded)}")


def decode_a18_to_wav(input_file, output_file, sample_rate=16000):
    with open(input_file, "rb") as f:
        a18_data = f.read()

    decoded_pcm = a1800_codec.decode(a18_data)

    print(f"Input:       {input_file}")
    print(f"A18 bytes:   {len(a18_data)}")
    print(f"PCM samples: {len(decoded_pcm) // 2}")

    with wave.open(output_file, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(decoded_pcm))

    print(f"Output:      {output_file}")
    print(f"WAV sample rate: {sample_rate} Hz")


def main():
    parser = argparse.ArgumentParser(
        description="Encode WAV to A1800 or decode A1800 back to WAV."
    )
    parser.add_argument(
        "mode",
        choices=["encode", "decode"],
        help="Operation to perform",
    )
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output file path")
    parser.add_argument(
        "--bitrate",
        type=int,
        default=16000,
        help="Bitrate for encoding (default: 16000)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate used when writing decoded WAV output (default: 16000)",
    )

    args = parser.parse_args()

    if args.mode == "encode":
        encode_wav_to_a18(args.input_file, args.output_file, bitrate=args.bitrate)
    else:
        decode_a18_to_wav(
            args.input_file,
            args.output_file,
            sample_rate=args.sample_rate,
        )


if __name__ == "__main__":
    main()
