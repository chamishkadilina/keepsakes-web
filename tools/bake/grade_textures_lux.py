"""Colour-grade downloaded albedo textures to the romantic palette, keeping their natural detail.
Usage: python grade_textures.py <textures_in_dir> <textures_out_dir>"""
import sys, os
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
# id -> (target mean sRGB 0-255, how much of the original colour variation to keep 0-1, contrast)
GRADE = {
    "marble_01":         ((236, 226, 214), 0.35, 0.85),   # foyer: soft ivory stone
    "diagonal_parquet":  ((128, 86, 60), 0.40, 1.00),   # galleries: honey oak
    "beige_wall_001":    ((238, 226, 211), 0.30, 1.00),   # walls: blush ivory plaster
    "laminate_floor_02": ((146, 112, 92),  0.50, 1.00),   # screen room: warm mocha
}
to_lin = lambda s: np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
to_srgb = lambda l: np.where(l <= 0.0031308, l * 12.92, 1.055 * np.power(np.clip(l, 0, None), 1 / 2.4) - 0.055)
W = np.array([0.2126, 0.7152, 0.0722])
for tid, (target, keep, contrast) in GRADE.items():
    img = np.asarray(Image.open(os.path.join(src, tid, f"{tid}_diff_1k.jpg")).convert("RGB"), np.float64) / 255
    lin = to_lin(img); mean = lin.reshape(-1, 3).mean(0)
    ratio = lin / mean
    lum = (ratio @ W)[..., None] ** contrast
    out = to_lin(np.array(target) / 255) * (lum * (1 - keep) + ratio * keep)
    os.makedirs(os.path.join(dst, tid), exist_ok=True)
    path = os.path.join(dst, tid, f"{tid}_albedo_1k.jpg")
    Image.fromarray((np.clip(to_srgb(out), 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, quality=88, optimize=True, progressive=True)
    print(tid, os.path.getsize(path) // 1024, "KB")
