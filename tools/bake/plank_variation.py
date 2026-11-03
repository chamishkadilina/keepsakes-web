"""Gives every floor board its own tone (real hardwood is never one flat colour). Keeps the tile seamless.
Board rows and board ends are found from the dark joint lines in the texture.
Usage: python plank_variation.py <albedo.jpg> [rows=8] [seed]"""
import sys, numpy as np
from PIL import Image
path = sys.argv[1]; rows = int(sys.argv[2]) if len(sys.argv) > 2 else 8; rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 5)
img = np.asarray(Image.open(path).convert("RGB"), np.float64) / 255
h, w, _ = img.shape; rh = h // rows
lum = img.mean(axis=2)
# horizontal joints: the darkest row inside each expected spacing -> offset of the board grid
offset = int(np.argmin([lum[np.arange(o, h, rh)].mean() for o in range(rh)]))
out = img.copy()
def rows_of(r):                                            # pixel rows of board row r (wraps around the tile)
    return np.arange(offset + r * rh, offset + (r + 1) * rh) % h
for r in range(rows):
    idx = rows_of(r)
    band = img[idx[4:-4]]
    col = band.mean(axis=(0, 2))                           # board ends show up as dark vertical lines
    thr = np.median(col) - 2.5 * col.std()
    seams = [x for x in range(1, w - 1) if col[x] < thr and col[x] <= col[x - 1] and col[x] <= col[x + 1]]
    seams = [x for i, x in enumerate(seams) if i == 0 or x - seams[i - 1] > 20]
    # shorter boards (real hardwood has random lengths): add board ends with a fine joint line
    for _ in range(40):
        if len(seams) >= max(2, w // 700): break
        x = int(rng.integers(40, w - 40))
        if all(abs(x - q) > 380 for q in seams):
            out[idx[3:-3], x:x + 2] *= 0.55
            seams = sorted(seams + [x])
    edges = [0] + seams + [w]
    gains = [rng.uniform(0.84, 1.16) for _ in edges[:-1]]
    if len(gains) > 1:
        gains[-1] = gains[0]                               # the board crossing the tile edge keeps one tone
    tints = [rng.uniform(-0.04, 0.04) for _ in gains]
    if len(tints) > 1:
        tints[-1] = tints[0]
    for (x0, x1), g, t in zip(zip(edges[:-1], edges[1:]), gains, tints):
        seg = out[idx, x0:x1]
        seg *= g
        seg[..., 0] *= 1 + t; seg[..., 2] *= 1 - t        # a little redder or browner
        out[idx, x0:x1] = seg
    print("row", r, "boards", len(gains))
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, quality=90, optimize=True, progressive=True)
