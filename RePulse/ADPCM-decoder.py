import struct
import wave

BLOCK_SIZE = 256 # try 256, 512, 1024, etc.
FILE_PATH = "RePulse\TEST-BSLSBS-Region1-4ee8.bin"

# Standard IMA ADPCM tables
INDEX_TABLE = [-1, -1, -1, -1, 2, 4, 6, 8,
               -1, -1, -1, -1, 2, 4, 6, 8]

STEP_TABLE = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31,
    34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143,
    157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658,
    724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024,
    3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
    15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767
]



def clamp16(x: int) -> int:
    return max(-32768, min(32767, x))

def ima_decode_nibble(nibble: int, predictor: int, index: int):
    step = STEP_TABLE[index]

    # compute diff
    diff = step >> 3
    if nibble & 1: diff += step >> 2
    if nibble & 2: diff += step >> 1
    if nibble & 4: diff += step
    if nibble & 8: diff = -diff

    predictor = clamp16(predictor + diff)

    index += INDEX_TABLE[nibble & 0x0F]
    index = max(0, min(88, index))

    return predictor, index

def decode_ima_block(block: bytes):
    # header: predictor (int16 LE), index (uint8), reserved (uint8)
    if len(block) < 4:
        return []

    predictor, = struct.unpack_from("<h", block, 0)
    index = block[2]
    # block[3] reserved
    if index > 88:
        # likely not IMA block
        raise ValueError(f"Bad IMA index {index}")

    pcm = [predictor]
    data = block[4:]

    for b in data:
        lo = b & 0x0F
        hi = (b >> 4) & 0x0F

        predictor, index = ima_decode_nibble(lo, predictor, index)
        pcm.append(predictor)

        predictor, index = ima_decode_nibble(hi, predictor, index)
        pcm.append(predictor)

    return pcm

def decode_ima_stream(raw: bytes, block_size: int) -> bytes:
    out = []
    for off in range(0, len(raw), block_size):
        blk = raw[off:off+block_size]
        if len(blk) < 4:
            break
        out.extend(decode_ima_block(blk))
    # pack int16 LE
    return struct.pack("<" + "h"*len(out), *out)

def write_wav(path: str, pcm16le: bytes, sample_rate: int, channels: int = 1):
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm16le)

# ---- usage example ----
raw = open(FILE_PATH,"rb").read()
pcm = decode_ima_stream(raw, block_size=BLOCK_SIZE)
write_wav("out.wav", pcm, sample_rate=16000)
