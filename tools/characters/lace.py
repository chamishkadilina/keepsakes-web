"""Lace, lace trim and tulle textures for the gown and veil, drawn with PIL (tileable where they repeat)."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _wrapped(draw_fn, size):
    """Draws a motif nine times (shifted by the tile size) so the tile repeats seamlessly."""
    w, h = size
    for dx in (-w, 0, w):
        for dy in (-h, 0, h):
            draw_fn(dx, dy)


def _rosette(d, x, y, r, fill):
    for k in range(6):
        a = k * math.pi / 3
        px, py = x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62
        d.ellipse((px - r * 0.42, py - r * 0.42, px + r * 0.42, py + r * 0.42), outline=fill, width=2)
    d.ellipse((x - r * 0.28, y - r * 0.28, x + r * 0.28, y + r * 0.28), fill=fill)


def lace_height(size=512):
    """Floral lace on a fine net: rosettes joined by vines, as a height map (0..1)."""
    h = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(h)
    step = 16
    for k in range(-size, 2 * size, step):                                              # the net
        d.line([(k, 0), (k + size, size)], fill=70, width=1)
        d.line([(k, size), (k + size, 0)], fill=70, width=1)
    cells = 4
    for i in range(cells):
        for j in range(cells):
            x = (i + 0.5 + (0.5 if j % 2 else 0)) * size / cells
            y = (j + 0.5) * size / cells
            def motif(dx, dy, x=x, y=y):
                _rosette(d, x + dx, y + dy, size / cells * 0.24, 235)
                for k in range(4):                                                      # vines and leaves
                    a = k * math.pi / 2 + math.pi / 4
                    ex, ey = x + dx + math.cos(a) * size / cells * 0.48, y + dy + math.sin(a) * size / cells * 0.48
                    d.arc((ex - 18, ey - 18, ex + 18, ey + 18), math.degrees(a) + 90, math.degrees(a) + 250, fill=200, width=3)
                    lx, ly = x + dx + math.cos(a) * size / cells * 0.3, y + dy + math.sin(a) * size / cells * 0.3
                    d.ellipse((lx - 5, ly - 3, lx + 5, ly + 3), fill=210)
            _wrapped(motif, (size, size))
    return np.asarray(h.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255


def normal_from(height, strength=2.0):
    gy, gx = np.gradient(height)
    n = np.dstack((-gx * strength, gy * strength, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


def lace(folder, size=512):
    """lace_albedo.png (white satin with soft lace) and lace_normal.png."""
    h = lace_height(size)
    albedo = 0.8 + 0.12 * h
    Image.fromarray((np.dstack([albedo, albedo * 0.985, albedo * 0.965]) * 255).astype(np.uint8), "RGB").save(f"{folder}/lace_albedo.png")
    normal_from(h).save(f"{folder}/lace_normal.png")


def trim(folder, w=1024, h=256):
    """lace_trim.png: a band of lace with a scalloped edge along its bottom (alpha: the lace)."""
    a = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(a)
    scallops = 8
    for k in range(scallops + 1):                                                        # the scalloped body of the band
        cx = k * w / scallops
        d.ellipse((cx - w / scallops * 0.6, h * 0.35, cx + w / scallops * 0.6, h * 0.98), fill=110)
    d.rectangle((0, 0, w, h * 0.62), fill=110)
    for k in range(scallops):                                                            # a rosette in each scallop
        cx = (k + 0.5) * w / scallops
        _rosette(d, cx, h * 0.62, h * 0.2, 255)
        _rosette(d, cx + w / scallops / 2, h * 0.28, h * 0.12, 235)
    for k in range(-h, w + h, 10):                                                        # net
        d.line([(k, 0), (k + h, h)], fill=150, width=1)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    for k in range(scallops + 1):
        cx = k * w / scallops
        md.ellipse((cx - w / scallops * 0.6, h * 0.35, cx + w / scallops * 0.6, h * 0.98), fill=255)
    md.rectangle((0, 0, w, h * 0.62), fill=255)
    alpha = np.minimum(np.asarray(a, np.float32), np.asarray(mask, np.float32))
    rgba = np.dstack([np.full((h, w), 240), np.full((h, w), 237), np.full((h, w), 230), alpha]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(f"{folder}/lace_trim.png")


def tulle(folder, w=256, h=512):
    """tulle.png: sheer white tulle (alpha 0.44) with a fine lace edge along its sides and bottom."""
    alpha = np.full((h, w), 112, np.float32)
    edge = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(edge)
    for y in range(0, h, 24):                                                            # little scallops down the sides
        for x in (0, w):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=255, width=3)
    for x in range(0, w, 24):                                                            # and along the bottom
        d.ellipse((x - 9, h - 9, x + 9, h + 9), outline=255, width=3)
    e = np.asarray(edge.filter(ImageFilter.GaussianBlur(0.6)), np.float32)
    alpha = np.maximum(alpha, e * 0.9)
    rgba = np.dstack([np.full((h, w), 250), np.full((h, w), 248), np.full((h, w), 244), alpha]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(f"{folder}/tulle.png")
