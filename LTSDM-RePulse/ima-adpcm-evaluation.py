from collections import defaultdict

BLOCK_SIZE = 256 # try 256, 512, 1024, etc.
raw = "RePulse\TEST-BSLSBS-Region1-4ee8.bin"

def score_alignment(raw: bytes, block_size: int, start: int = 0):
    # Score by counting blocks whose index in 0..88 and reserved == 0
    ok = 0
    total = 0
    for off in range(start, len(raw) - 4, block_size):
        idx = raw[off + 2]
        rsv = raw[off + 3]
        total += 1
        if idx <= 88 and rsv == 0:
            ok += 1
    return ok, total

def find_best(raw: bytes, block_sizes=(128, 256, 512, 1024, 2048)):
    best = []
    for bs in block_sizes:
        # try plausible starts within the first block
        # (if your region begins mid-stream, start offset won't be 0)
        for start in range(0, min(bs, 512)):  # keep it bounded
            ok, total = score_alignment(raw, bs, start)
            if total > 10:  # ignore tiny samples
                best.append((ok / total, ok, total, bs, start))
    best.sort(reverse=True)
    return best[:20]

top = find_best(raw)
for frac, ok, total, bs, start in top[:10]:
    print(f"score={frac:.3f} ({ok}/{total})  block={bs}  start={start}")
