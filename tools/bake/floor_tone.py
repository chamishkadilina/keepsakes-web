"""Re-tones the floor boards to a darker walnut-cherry (keeps every board and grain detail).
Usage: python floor_tone.py <in.jpg> <out.jpg>   (last step of the floor texture, after plank_variation.py)"""
import sys
import numpy as np
from PIL import Image
TARGET = (76, 44, 29)                       # mean colour, sRGB 0-255: dark walnut-cherry, like the reference
to_lin = lambda s: np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
to_srgb = lambda l: np.where(l <= 0.0031308, l * 12.92, 1.055 * np.power(np.clip(l, 0, None), 1 / 2.4) - 0.055)
lin = to_lin(np.asarray(Image.open(sys.argv[1]).convert("RGB"), np.float64) / 255)
lin *= to_lin(np.array(TARGET) / 255) / lin.reshape(-1, 3).mean(0)
Image.fromarray((np.clip(to_srgb(lin), 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2], quality=90, optimize=True, progressive=True)
print("toned", sys.argv[2])
