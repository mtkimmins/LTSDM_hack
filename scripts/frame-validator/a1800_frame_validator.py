#!/usr/bin/env python3
"""
a1800_frame_validator.py

Checks A1800-codec frames (raw bit strings, hex, or real .a18 cartridge
files) for the out-of-bounds gain-index bug that crashes the Little
Tikes Story Dream Machine projector.

ROOT CAUSE
----------
Confirmed by reproducing the crash against John-K's a1800_codec
reimplementation (https://github.com/John-K/a1800_codec), which the
project's own reverse-engineering notes tie closely to the original
A1800.DLL / firmware tables and logic.

decode_gains() accumulates a per-subband "gain" value from a
Huffman-coded differential stream:

    gain[0]   = initial_5bit_index - 7
    gain[i+1] = gain[i] + differential[i] - 12

Each subband's gain is then used, UNCLAMPED, as an index into a
128-entry table:

    SCALE_FACTOR_BITS[gain[i] + 24]

If the differential stream drifts the cumulative gain below -24
(index < 0) or above 103 (index > 127), the lookup reads outside the
table. In the Rust reimplementation this panics; on the real embedded
firmware -- which appears to use the same unclamped table lookup --
the equivalent read almost certainly lands in unmapped or unrelated
memory, which is the most likely explanation for the hardware crash.

This script re-implements only the gain-decode stage of the codec
(bitstream reader + Huffman gain tree + cumulative gain calc) -- the
exact code path where the crash occurs -- so you can screen candidate
.a18 frames before flashing a cartridge, without needing the rest of
the decoder/encoder pipeline.

USAGE
-----
    # Validate one frame given as a 320-bit binary string (as pasted
    # straight out of a bit-level dump)
    python3 a1800_frame_validator.py --bits 0101010010110001...

    # Validate one frame given as hex (40 bytes = 80 hex chars at 16 kbps)
    python3 a1800_frame_validator.py --hex 54b16904a932...

    # Validate every frame in a real .a18 cartridge file
    python3 a1800_frame_validator.py --a18 mycartridge.a18

    # Validate every frame in a raw frame-data file with no .a18 header
    python3 a1800_frame_validator.py --raw frames.bin --bitrate 16000

Exit code is 0 if every frame checked is safe, 1 if any frame would
hit the out-of-bounds access.
"""

import argparse
import struct
import sys
from dataclasses import dataclass
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Tables extracted verbatim from a1800_codec's src/tables.rs (John-K,
# https://github.com/John-K/a1800_codec, crate version 1.0.0).
#
# GAIN_HUFFMAN_TREE: 14 sections of 23 nodes (flat binary tree; section 0
# is an unused sentinel, matching decoder.rs's tree_base starting at 23).
# Positive entries are child node indices *within the current section*;
# entries <= 0 are leaves (negate to get the decoded differential symbol).
#
# SCALE_FACTOR_BITS: the 128-entry table that gets indexed out of bounds.
# Only its length (128) matters for the bounds check; the actual values
# are included so this script can also replicate the scale-parameter (sp)
# derivation and check the *second* table access in decode_gains (the
# per-subband scale-factor lookup), not just the first (total_cost) one.
# ---------------------------------------------------------------------------

GAIN_HUFFMAN_TREE: List[Tuple[int, int]] = [
    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 2),
    (3, 4), (5, 6), (7, 8), (9, 10), (11, -12), (-11, -10),
    (-8, -9), (-7, -6), (-13, 12), (-5, -4), (0, 13), (-3, -14),
    (-2, 14), (-1, 15), (-15, 16), (-16, 17), (-17, 18), (19, 20),
    (21, 22), (-18, -19), (-20, -21), (-22, -23), (1, 2), (3, 4),
    (5, 6), (7, 8), (-10, -9), (-8, -11), (-7, -6), (9, -5),
    (10, -12), (-4, 11), (-13, -3), (12, -2), (13, -14), (-1, 14),
    (15, -15), (0, 16), (-16, 17), (-17, 18), (-18, 19), (20, 21),
    (22, -19), (-20, -21), (-22, -23), (1, 2), (3, 4), (5, 6),
    (7, 8), (9, 10), (-12, 11), (-11, -13), (-10, -9), (12, -14),
    (-8, -7), (-15, -6), (13, -5), (-16, -4), (14, -17), (15, -3),
    (16, -18), (-2, 17), (18, -19), (-1, 19), (-20, 20), (0, 21),
    (22, -21), (-22, -23), (1, 2), (3, 4), (5, 6), (-11, -10),
    (7, -12), (8, -9), (9, -13), (-14, 10), (-8, -15), (-16, 11),
    (-7, 12), (-17, -6), (13, 14), (-18, 15), (-5, -4), (16, 17),
    (-3, -2), (-19, 18), (-1, 19), (-20, 20), (21, 22), (0, -21),
    (-22, -23), (1, 2), (3, 4), (5, 6), (-12, -11), (-13, 7),
    (8, -14), (-10, 9), (10, -15), (-9, 11), (-8, 12), (-16, 13),
    (-7, -6), (-17, 14), (-5, -18), (15, -4), (16, -19), (17, -3),
    (-20, 18), (-2, 19), (-21, 20), (0, 21), (22, -1), (-22, -23),
    (1, 2), (3, 4), (5, 6), (-11, 7), (-12, -10), (-13, -9),
    (8, 9), (-14, -8), (10, -15), (-7, 11), (-16, 12), (-6, -17),
    (13, 14), (-5, 15), (-18, 16), (-4, 17), (-3, -19), (18, -2),
    (-20, 19), (-1, 20), (0, 21), (22, -21), (-22, -23), (1, 2),
    (3, 4), (5, -12), (6, -11), (-10, -13), (-9, 7), (8, -14),
    (9, -8), (-15, 10), (-7, -16), (11, -6), (12, -17), (13, -5),
    (-18, 14), (15, -4), (-19, 16), (17, -3), (-20, 18), (19, 20),
    (21, 22), (0, -2), (-1, -21), (-22, -23), (1, 2), (3, 4),
    (5, -12), (6, -13), (-11, -10), (7, -14), (8, -9), (9, -15),
    (-8, 10), (-7, -16), (11, 12), (-6, -17), (-5, 13), (14, 15),
    (-18, -4), (-19, 16), (-3, 17), (18, -2), (-20, 19), (20, 21),
    (22, 0), (-1, -21), (-22, -23), (1, 2), (3, 4), (5, 6),
    (-11, -10), (-12, -9), (7, 8), (-13, -8), (9, -14), (-7, 10),
    (-6, -15), (11, 12), (-5, -16), (13, 14), (-17, 15), (-4, 16),
    (17, -18), (18, -3), (-2, 19), (-1, 0), (-19, 20), (-20, 21),
    (22, -21), (-22, -23), (1, 2), (3, 4), (5, 6), (-11, 7),
    (-10, -12), (-9, 8), (-8, -13), (9, -7), (10, -14), (-6, 11),
    (-15, 12), (-5, 13), (-16, -4), (14, 15), (-17, -3), (-18, 16),
    (17, -19), (-2, 18), (-20, 19), (-1, 20), (21, 22), (0, -21),
    (-22, -23), (1, 2), (3, 4), (5, -12), (6, -11), (7, 8),
    (-10, -13), (-9, 9), (-8, -14), (10, -7), (11, -15), (-6, 12),
    (-5, 13), (-4, -16), (14, 15), (-3, -17), (16, 17), (-18, -2),
    (18, -19), (-1, 19), (-20, 20), (-21, 21), (22, 0), (-22, -23),
    (1, 2), (3, 4), (5, -12), (-13, 6), (-11, 7), (-14, 8),
    (-10, 9), (-15, -9), (-8, 10), (-7, -16), (11, -6), (12, -5),
    (-17, 13), (14, -18), (15, -4), (16, -19), (17, -3), (18, -2),
    (19, -1), (-20, 20), (21, 22), (0, -21), (-22, -23), (1, 2),
    (3, 4), (-12, 5), (-11, -13), (6, -14), (-10, 7), (8, -15),
    (-9, 9), (-16, 10), (-8, -17), (11, 12), (-7, -18), (-6, 13),
    (14, -5), (15, -19), (-4, 16), (-20, 17), (18, 19), (20, 21),
    (22, 0), (-1, -3), (-2, -21), (-22, -23),
]

SCALE_FACTOR_BITS: List[int] = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
    1, 1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45,
    64, 91, 128, 181, 256, 362, 512, 724, 1024, 1448, 2048, 2896,
    4096, 5793, 8192, 11585, 16384, 23170, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767,
    32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767,
    32767, 32767, 32767, 32767, 32767, 23170, 16384, 11585, 8192, 5793, 4096, 2896,
    2048, 1448, 1024, 724, 512, 362, 256, 181, 128, 91, 64, 45,
    32, 23, 16, 11, 8, 6, 4, 3, 2, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0,
]

SCALE_FACTOR_BITS_LEN = len(SCALE_FACTOR_BITS)  # 128
NODES_PER_SECTION = 23


def num_subbands_for_bitrate(bitrate: int) -> int:
    if bitrate >= 16000:
        return 14
    elif bitrate >= 12000:
        return 12
    elif bitrate >= 9600:
        return 10
    else:
        return 8


def _i16(val: int) -> int:
    """Match the codec's saturating i16 semantics. Gain-path values stay
    tiny in practice, so this is effectively just a sanity clamp."""
    if val > 0x7FFF:
        return 0x7FFF
    if val < -0x8000:
        return -0x8000
    return val


class BitReader:
    """MSB-first bit reader over 16-bit words, matching a1800_codec's
    BitstreamReader::read_bit exactly."""

    def __init__(self, words: List[int]):
        self.words = words
        self.pos = 0
        self.bits_remaining = 0
        self.current_word = 0

    def read_bit(self) -> int:
        if self.bits_remaining == 0:
            self.current_word = self.words[self.pos]
            self.pos += 1
            self.bits_remaining = 16
        self.bits_remaining -= 1
        return (self.current_word >> self.bits_remaining) & 1

    def read_bits(self, n: int) -> int:
        val = 0
        for _ in range(n):
            val = (val << 1) | self.read_bit()
        return val


@dataclass
class GainDecodeResult:
    num_subbands: int
    initial_gain: int
    differentials: List[int]
    gains: List[int]            # cumulative per-subband gain
    cost_indices: List[int]     # gain[i] + 24, used in the total_cost loop
    cost_oob: List[int]         # subband indices OOB in the total_cost loop
    sp: int                     # derived scale_param (only meaningful if cost_oob is empty)
    final_indices: List[int]    # gain[i] + sp*2 + 24, used in the final scale-factor loop
    final_oob: List[int]        # subband indices OOB in the final scale-factor loop

    @property
    def would_crash(self) -> bool:
        return bool(self.cost_oob) or bool(self.final_oob)

    @property
    def first_crash_subband(self):
        if self.cost_oob:
            return ("total_cost loop", self.cost_oob[0])
        if self.final_oob:
            return ("final scale-factor loop", self.final_oob[0])
        return None


def decode_gains(words: List[int], bitrate: int) -> GainDecodeResult:
    """Reimplements decoder.rs::decode_gains in full: the gain
    accumulation, BOTH SCALE_FACTOR_BITS lookup loops, and the sp
    (scale_param) derivation in between. This is the exact code path
    that panics on the crashing frame (decoder.rs line ~188/205)."""
    ns = num_subbands_for_bitrate(bitrate)
    br = BitReader(words)

    initial_index = br.read_bits(5)
    initial_gain = _i16(initial_index - 7)

    differentials = []
    tree_base = NODES_PER_SECTION  # section 0 is an unused sentinel
    for _ in range(ns - 1):
        node = 0
        while True:
            bit = br.read_bit()
            entry = tree_base + node
            node = GAIN_HUFFMAN_TREE[entry][bit]
            if node <= 0:
                break
        differentials.append(-node)
        tree_base += NODES_PER_SECTION

    gains = [0] * ns
    gains[0] = initial_gain
    for i in range(ns - 1):
        gains[i + 1] = _i16(gains[i] + differentials[i] - 12)

    # --- first SCALE_FACTOR_BITS access: total_cost / max_eff_gain loop ---
    cost_indices = [g + 24 for g in gains]
    cost_oob = [i for i, idx in enumerate(cost_indices)
                if idx < 0 or idx >= SCALE_FACTOR_BITS_LEN]

    total_cost = 0
    max_eff_gain = 0
    for idx in cost_indices:
        if idx > max_eff_gain:
            max_eff_gain = idx
        # Only accumulate real cost if in-bounds; if it's OOB the real
        # decoder would already have crashed here, so downstream sp/
        # final-index numbers past that point are not meaningful.
        safe_idx = min(max(idx, 0), SCALE_FACTOR_BITS_LEN - 1)
        total_cost = _i16(total_cost + SCALE_FACTOR_BITS[safe_idx])

    # --- scale_param (sp) derivation, matching decoder.rs exactly ---
    sp = 9
    cost_check = total_cost - 8
    gain_check = max_eff_gain - 0x1C
    while True:
        if cost_check < 0 and gain_check < 1:
            break
        sp -= 1
        total_cost = total_cost >> 1 if total_cost >= 0 else -((-total_cost) >> 1)
        max_eff_gain -= 2
        cost_check = total_cost - 8
        gain_check = max_eff_gain - 0x1C
        if sp < 0:
            break

    # --- second SCALE_FACTOR_BITS access: final per-subband scale factor ---
    offset = sp * 2 + 0x18
    final_indices = [g + offset for g in gains]
    final_oob = [i for i, idx in enumerate(final_indices)
                 if idx < 0 or idx >= SCALE_FACTOR_BITS_LEN]

    return GainDecodeResult(
        num_subbands=ns,
        initial_gain=initial_gain,
        differentials=differentials,
        gains=gains,
        cost_indices=cost_indices,
        cost_oob=cost_oob,
        sp=sp,
        final_indices=final_indices,
        final_oob=final_oob,
    )


def words_from_bits(bitstring: str) -> List[int]:
    bitstring = "".join(bitstring.split())
    if len(bitstring) % 16 != 0:
        raise ValueError(f"bit string length {len(bitstring)} is not a multiple of 16")
    return [int(bitstring[i:i + 16], 2) for i in range(0, len(bitstring), 16)]


def words_from_bytes(raw: bytes) -> List[int]:
    if len(raw) % 2 != 0:
        raise ValueError("frame byte length must be even (16-bit words)")
    # a1800_codec reads every 16-bit quantity (header fields AND frame
    # words) as little-endian, per src/main.rs (i16::from_le_bytes).
    return [v - 0x10000 if v >= 0x8000 else v
            for v in struct.unpack_from(f"<{len(raw)//2}H", raw)]


def words_from_hex(hexstring: str) -> List[int]:
    raw = bytes.fromhex("".join(hexstring.split()))
    return words_from_bytes(raw)


def report(name: str, result: GainDecodeResult, quiet: bool):
    if quiet:
        print(f"{name}: {'CRASH' if result.would_crash else 'safe'}")
        return

    print(f"=== {name} ===")
    print(f"  num_subbands      : {result.num_subbands}")
    print(f"  initial_gain      : {result.initial_gain}")
    print(f"  differentials     : {result.differentials}")
    print(f"  cumulative gain   : {result.gains}")
    print(f"  total_cost indices: {result.cost_indices}  (valid: 0-{SCALE_FACTOR_BITS_LEN - 1})")
    if not result.cost_oob:
        print(f"  derived sp        : {result.sp}")
        print(f"  final indices     : {result.final_indices}  (valid: 0-{SCALE_FACTOR_BITS_LEN - 1})")

    if result.would_crash:
        where, sb = result.first_crash_subband
        print(f"  VERDICT           : *** WOULD CRASH *** out-of-bounds table index "
              f"first hit at subband {sb} ({where})")
        if result.cost_oob:
            print(f"                      total_cost loop OOB subbands: {result.cost_oob}")
        if result.final_oob:
            print(f"                      final scale-factor loop OOB subbands: {result.final_oob}")
    else:
        margin_low = min(min(result.cost_indices), min(result.final_indices))
        margin_high = (SCALE_FACTOR_BITS_LEN - 1) - max(max(result.cost_indices), max(result.final_indices))
        print(f"  VERDICT           : safe  "
              f"(margin: {margin_low} above the low bound, {margin_high} below the high bound)")
    print()


def iter_a18_frames(path: str):
    with open(path, "rb") as f:
        data = f.read()
    data_length, bitrate = struct.unpack_from("<IH", data, 0)
    frame_words = bitrate // 800
    frame_bytes = frame_words * 2
    offset = 6
    idx = 0
    end = 6 + data_length
    while offset + frame_bytes <= end:
        raw = data[offset:offset + frame_bytes]
        yield idx, words_from_bytes(raw), bitrate
        offset += frame_bytes
        idx += 1


def main():
    ap = argparse.ArgumentParser(
        description="Check A1800 frames for the out-of-bounds gain-index "
                    "bug that crashes the Little Tikes Story Dream Machine.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bits", help="single frame as a binary string (320 chars of 0/1 at 16 kbps)")
    g.add_argument("--hex", help="single frame as a hex string (80 hex chars = 40 bytes at 16 kbps)")
    g.add_argument("--a18", help="path to a real .a18 cartridge file; validates every frame in it")
    g.add_argument("--raw", help="path to a raw frame-data file with no .a18 header; requires --bitrate")
    ap.add_argument("--bitrate", type=int, default=16000,
                    help="bitrate to assume for --bits/--hex/--raw (default: 16000)")
    ap.add_argument("--quiet", action="store_true",
                    help="print only one summary line per frame plus the final verdict")
    args = ap.parse_args()

    any_crash = False

    if args.bits:
        words = words_from_bits(args.bits)
        result = decode_gains(words, args.bitrate)
        report("frame", result, args.quiet)
        any_crash = result.would_crash

    elif args.hex:
        words = words_from_hex(args.hex)
        result = decode_gains(words, args.bitrate)
        report("frame", result, args.quiet)
        any_crash = result.would_crash

    elif args.a18:
        for idx, words, bitrate in iter_a18_frames(args.a18):
            result = decode_gains(words, bitrate)
            any_crash = any_crash or result.would_crash
            report(f"frame {idx}", result, args.quiet)

    elif args.raw:
        with open(args.raw, "rb") as f:
            data = f.read()
        frame_words = args.bitrate // 800
        frame_bytes = frame_words * 2
        for idx in range(len(data) // frame_bytes):
            raw = data[idx * frame_bytes:(idx + 1) * frame_bytes]
            result = decode_gains(words_from_bytes(raw), args.bitrate)
            any_crash = any_crash or result.would_crash
            report(f"frame {idx}", result, args.quiet)

    print()
    if any_crash:
        print("RESULT: one or more frames would trigger the out-of-bounds gain-index crash.")
        sys.exit(1)
    else:
        print("RESULT: all frames stay within safe gain bounds.")
        sys.exit(0)


if __name__ == "__main__":
    main()
