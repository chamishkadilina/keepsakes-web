"""Builds a larger, non-repeating floor texture from the graded plank texture: every board row of the
2x2 output is a randomly chosen, randomly shifted row of the source, so the pattern repeats only every 2.2 m.
Usage: python floor_synth.py <albedo_1k.jpg> <out_albedo_2k.jpg> [rows=8] [seed]"""
import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
rows = int(sys.argv[3]) if len(sys.argv) > 3 else 8
rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 3)
img = np.asarray(Image.open(src).convert("RGB"))
h, w, _ = img.shape; rh = h // rows
lum = img.mean(axis=2)
offset = int(np.argmin([lum[np.arange(o, h, rh)].mean() for o in range(rh)]))   # board joints
out = np.zeros((2 * h, 2 * w, 3), np.uint8)
for r in range(2 * rows):
    s = int(rng.integers(rows)); shift = int(rng.integers(w))
    band = img[(offset + s * rh + np.arange(rh)) % h]
    band = np.roll(band, shift, axis=1)
    out[r * rh:(r + 1) * rh] = np.concatenate([band, np.roll(band, int(rng.integers(w)), axis=1)], axis=1)
Image.fromarray(out).save(dst, quality=90, optimize=True, progressive=True)
print("floor", out.shape)
