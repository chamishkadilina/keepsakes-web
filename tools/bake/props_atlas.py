"""The decor texture: rugs, marble, hedge foliage and the balloon colours in one image, so all of them draw
with one material. props.py maps its pieces onto these rectangles; this script paints the image (plain numpy, soft
anti-aliased shapes). Usage: python props_atlas.py <out.jpg>
The rugs are designed in metres at their real size: soft ivory wool with a dusty-rose border, gold lines and a rose
medallion (heart room) and a deep burgundy one for the screen room."""
import sys
import numpy as np

SIZE = 2048
PX = 0.0034                                   # rug texture: metres per pixel


def _rect(x, y, w, h):
    return (x, y, w, h)


# pixel rectangles (x, y from the bottom-left, Blender's UV convention), metres for the rugs
RUGS = {
    "heart": dict(size=(3.6, 2.6), rect=_rect(8, 8, round(3.6 / PX), round(2.6 / PX))),
    "screen": dict(size=(2.8, 2.0), rect=_rect(1075, 8, round(2.8 / PX), round(2.0 / PX))),
}
MARBLE_RECT = _rect(1075, 612, 512, 512)
HEDGE_RECT = _rect(8, 1045, 512, 512)                     # clipped boxwood
SWATCHES = ["red_foil", "blush_foil", "rosegold_foil", "gold_ribbon", "white_ribbon", "pink_ribbon"]   # plain colours
SWATCH_RECT = _rect(1595, 780, 32 * len(SWATCHES), 32)


def swatch_uv(name):
    """UV point in the middle of a plain colour swatch (balloons and their ribbons)."""
    x, y, _, h = SWATCH_RECT
    return ((x + 32 * SWATCHES.index(name) + 16) / SIZE, (y + h / 2) / SIZE)


def uv_rect(rect, inset=1.5):
    """(u0, v0, u1, v1) of a pixel rectangle, pulled in a little so filtering stays inside it."""
    x, y, w, h = rect
    return ((x + inset) / SIZE, (y + inset) / SIZE, (x + w - inset) / SIZE, (y + h - inset) / SIZE)


# ---------------------------------------------------------------- painting helpers (float sRGB, 0 ... 1)

def c(r, g, b):
    return np.array([r, g, b], np.float32) / 255


IVORY, IVORY_DK = c(236, 225, 208), c(222, 206, 186)
ROSE, ROSE_DK, BLUSH = c(196, 146, 148), c(158, 102, 110), c(228, 190, 184)
GOLD = c(198, 164, 114)
WINE, WINE_DK, WINE_LT = c(112, 36, 48), c(78, 22, 32), c(126, 48, 60)


def cover(d, px=PX):
    """Anti-aliased coverage of a shape from its signed distance (metres, negative inside)."""
    return np.clip(0.5 - d / px, 0, 1)[..., None]


def paint(img, d, colour, alpha=1.0):
    a = cover(d) * alpha
    img[:] = img * (1 - a) + colour * a


def band(t, t0, t1):
    """Signed distance to the band t0 < t < t1."""
    return np.maximum(t0 - t, t - t1)


def noise(rng, shape, cells):
    """Smooth value noise in 0 ... 1 with `cells` random values across the larger side."""
    h, w = shape
    ch, cw = max(1, round(cells * h / max(h, w))), max(1, round(cells * w / max(h, w)))
    g = rng.random((ch + 2, cw + 2)).astype(np.float32)
    y = np.linspace(0, ch, h, endpoint=False); x = np.linspace(0, cw, w, endpoint=False)
    yi, xi = y.astype(int), x.astype(int)
    yf, xf = y - yi, x - xi
    yf, xf = (yf * yf * (3 - 2 * yf))[:, None], xf * xf * (3 - 2 * xf)
    top = g[yi][:, xi] * (1 - xf) + g[yi][:, xi + 1] * xf
    bottom = g[yi + 1][:, xi] * (1 - xf) + g[yi + 1][:, xi + 1] * xf
    return top * (1 - yf) + bottom * yf


def fbm(rng, shape, cells, octaves=4):
    out, amp, total = np.zeros(shape, np.float32), 1.0, 0.0
    for k in range(octaves):
        out += noise(rng, shape, cells * 2 ** k) * amp
        total += amp; amp *= 0.5
    return out / total


def wool(img, rng, strength=1.0):
    """Wool pile: soft blotches, fine fibres and a faint weave so the rug never looks printed."""
    h, w, _ = img.shape
    soft = fbm(rng, (h, w), 6) - 0.5
    fine = noise(rng, (h, w), max(h, w) // 3) - 0.5
    grain = rng.random((h, w)).astype(np.float32) - 0.5
    weave = np.sin(np.arange(w) * 2.1)[None, :] * np.sin(np.arange(h) * 2.1)[:, None]
    k = 1 + strength * (0.05 * soft + 0.05 * fine + 0.035 * grain + 0.012 * weave)
    img *= k[..., None]


def petals(r, th, n, r0, depth, sharp=0.7):
    """Signed distance (approx.) to an n-petal rosette of outer radius r0."""
    return r - r0 * ((1 - depth) + depth * np.abs(np.cos(n * th / 2)) ** sharp)


def rosette(img, x, y, cx, cy, size, fill, line, centre):
    """Small eight-petal flower with a gold outline and a coloured centre."""
    r, th = np.hypot(x - cx, y - cy), np.arctan2(y - cy, x - cx)
    d = petals(r, th + np.pi / 8, 8, size, 0.35)
    paint(img, np.abs(d) - 0.0035, line)
    paint(img, d + 0.002, fill)
    paint(img, r - size * 0.3, centre)


def leafy(img, x, y, cx, cy, angle, length, width, colour, alpha=1.0):
    """A small pointed leaf from (cx, cy) along `angle`."""
    u = (x - cx) * np.cos(angle) + (y - cy) * np.sin(angle)
    v = -(x - cx) * np.sin(angle) + (y - cy) * np.cos(angle)
    t = np.clip(u / length, 0, 1)
    half = width / 2 * np.sin(np.pi * t) ** 0.8
    d = np.where((u > 0) & (u < length), np.abs(v) - half, 1.0)
    paint(img, d, colour, alpha)


def medallion(img, x, y, R, fill, field, line, centre, lobes=12, pendants=True):
    """Central rose medallion: beaded gold ring, a lobed rose field with a ring of leaves, a pointed eight-petal flower
    and a small rose in the middle; teardrop pendants along the rug's length."""
    r, th = np.hypot(x, y), np.arctan2(y, x)
    paint(img, np.abs(r - R * 1.13) - 0.0025, line)
    beads = th * 56 / (2 * np.pi)
    paint(img, np.hypot((beads - np.round(beads)) * 2 * np.pi * R * 1.065 / 56, r - R * 1.065) - 0.006, fill)
    if pendants:
        for sx in (-1, 1):
            u, v = sx * x - R * 1.3, y
            drop = np.hypot(u / (R * 0.17), v / (R * 0.075)) * R * 0.075 - R * 0.075
            paint(img, np.abs(drop) - 0.004, line)
            paint(img, drop + 0.003, fill)
            paint(img, np.hypot(u - R * 0.24, v) - R * 0.035, fill)
            leafy(img, x, y, sx * R * 1.16, 0, np.pi * (sx < 0), R * 0.1, R * 0.05, line)
    lobe = r - R * (0.93 + 0.07 * np.cos(lobes * th))
    paint(img, np.abs(lobe) - 0.006, line)
    paint(img, lobe + 0.005, fill)
    paint(img, np.abs(lobe + R * 0.07) - 0.0025, field, 0.8)
    for k in range(16):                                                           # ring of leaves inside the lobes
        a = (k + 0.5) * 2 * np.pi / 16
        leafy(img, x, y, R * 0.6 * np.cos(a), R * 0.6 * np.sin(a), a, R * 0.2, R * 0.075, BLUSH if fill is not BLUSH else field)
    star = r - R * 0.56 * (0.5 + 0.5 * np.abs(np.cos(4 * th)) ** 1.8)
    paint(img, np.abs(star) - 0.004, line)
    paint(img, star + 0.003, field)
    for k in range(8):                                                            # a fine vein along every petal
        a = k * np.pi / 4
        u = x * np.cos(a) + y * np.sin(a); v = -x * np.sin(a) + y * np.cos(a)
        paint(img, np.where((u > R * 0.22) & (u < R * 0.44), np.abs(v) - 0.002, 1.0), fill, 0.7)
    for k, (rk, col) in enumerate(((0.24, fill), (0.16, BLUSH), (0.09, centre))):  # the little rose in the middle
        paint(img, r - R * rk * (0.82 + 0.18 * np.cos(5 * th + k * 1.3)), col)
    paint(img, r - R * 0.035, fill)


# ---------------------------------------------------------------- rugs

def rect_rug(W, D, field, border, border_dk, accent, line, rng, lattice=True):
    w, h = round(W / PX), round(D / PX)
    x, y = np.meshgrid((np.arange(w) + 0.5) * PX - W / 2, (np.arange(h) + 0.5) * PX - D / 2)
    img = np.empty((h, w, 3), np.float32); img[:] = field
    tx, ty = W / 2 - np.abs(x), D / 2 - np.abs(y)
    t = np.minimum(tx, ty)
    B0, B1 = 0.052, 0.24
    if lattice:                                                                   # faint trellis over the field
        S = 0.26
        a, b = (x + y) / np.sqrt(2), (x - y) / np.sqrt(2)
        dl = np.minimum(np.abs(a - S * np.round(a / S)), np.abs(b - S * np.round(b / S)))
        fade = np.clip((np.hypot(x / 0.9, y / 0.75) - 1) * 3, 0, 1)
        dot = np.hypot(a - S * np.round(a / S), b - S * np.round(b / S))
        paint(img, dl - 0.0022, field * 0.93, 0.55 * fade[..., None])
        paint(img, dot - 0.011, accent, 0.6 * fade[..., None])
    # corner spandrels: scalloped quarter rings inside the border
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (W / 2 - 0.29), sy * (D / 2 - 0.29)
            r, th = np.hypot(x - cx, y - cy), np.arctan2(y - cy, x - cx)
            scallop = r - 0.36 * (0.93 + 0.07 * np.cos(14 * th))
            inside = (np.sign(x - cx) != sx) & (np.sign(y - cy) != sy)
            d = np.where(inside, scallop, 1.0)
            paint(img, np.where(inside, np.abs(scallop) - 0.004, 1.0), line)
            paint(img, d + 0.004, border, 0.85)
            paint(img, np.where(inside, np.abs(r - 0.2) - 0.003, 1.0), line)
    medallion(img, x, y, min(W, D) * 0.2, border, field, line, border_dk)
    # border: binding, gold lines, the rose band with a running vine, leaves and buds, rosettes in the corners
    paint(img, band(t, -1, 0.025), border_dk)
    paint(img, band(t, 0.045, 0.052), line)
    paint(img, band(t, B0, B1), border)
    paint(img, band(t, B1, B1 + 0.007), line)
    paint(img, band(t, 0.272, 0.277), border)
    corner = (tx < B1 + 0.007) & (ty < B1 + 0.007)
    side_x = tx > ty                                                              # on the top / bottom border
    s = np.where(side_x, x, y)
    span = np.where(side_x, W, D) - 2 * B1
    period = span / np.maximum(1, np.round(span / 0.31))
    q = t - (B0 + B1) / 2
    amp = 0.048
    phase = 2 * np.pi * s / period
    curve = amp * np.cos(phase)
    slope = -amp * 2 * np.pi / period * np.sin(phase)
    dv = np.abs(q - curve) / np.sqrt(1 + slope ** 2)
    in_band = (t > B0) & (t < B1) & ~corner
    paint(img, np.where(in_band, dv - 0.0035, 1.0), accent)
    for k in (0.25, 0.75):                                                        # leaves where the vine crosses the middle
        ph = 2 * np.pi * (s / period - k - np.round(s / period - k))
        u = ph * period / (2 * np.pi)
        tilt = np.where(k == 0.25, -1, 1)
        for side in (-1, 1):
            lu, lq = u - side * 0.026, q - side * tilt * 0.022
            leaf = np.hypot(lu / 0.03, lq / 0.012) * 0.012 - 0.012
            paint(img, np.where(in_band, leaf, 1.0), accent, 0.9)
    for k, sign in ((0.0, 1), (0.5, -1)):                                         # buds inside the vine's curls
        ph = s / period - k - np.round(s / period - k)
        bud = np.hypot(ph * period, q - sign * 0.008) - 0.016
        paint(img, np.where(in_band, bud, 1.0), BLUSH if border is not BLUSH else IVORY)
        paint(img, np.where(in_band, np.hypot(ph * period, q - sign * 0.008) - 0.006, 1.0), border_dk)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (W / 2 - (B0 + B1) / 2), sy * (D / 2 - (B0 + B1) / 2)
            rosette(img, x, y, cx, cy, 0.075, accent, line, border_dk)
    wool(img, rng)
    return img


# ---------------------------------------------------------------- marble, gift wrap, hedges

def marble(rng):
    """White marble with soft grey clouds, flowing grey veins and a few fine gold ones."""
    n = 512
    img = np.empty((n, n, 3), np.float32); img[:] = c(240, 237, 232)
    y, x = np.mgrid[0:n, 0:n] / n
    img *= (1 + 0.045 * (fbm(rng, (n, n), 4) - 0.5))[..., None]
    for colour, k, angle, warp, soft, core in ((c(150, 148, 146), 5.0, 0.6, 3.2, 0.22, 0.5), (c(176, 172, 168), 9.0, -0.4, 4.5, 0.15, 0.35),
                                               (c(196, 168, 120), 7.0, 1.1, 5.0, 0.0, 0.45)):
        w = fbm(rng, (n, n), 3, 5)
        v = np.sin(k * (x * np.cos(angle) + y * np.sin(angle)) + warp * w * 2)
        a = soft * np.exp(-(v / 0.16) ** 2) + core * np.exp(-(v / 0.02) ** 2)
        img[:] = img * (1 - a[..., None]) + colour * a[..., None]
    return img


def hedge(rng):
    """Clipped boxwood: small overlapping leaves in deep and fresh greens, darker in the gaps (tiles seamlessly)."""
    n = HEDGE_RECT[2]
    img = np.empty((n, n, 3), np.float32); img[:] = c(34, 58, 30)
    for _ in range(5200):
        cx, cy = rng.uniform(0, n, 2)
        r, a = rng.uniform(5, 10), rng.uniform(0, np.pi)
        tone = c(*[int(v) for v in rng.choice([(58, 96, 44), (72, 112, 52), (88, 128, 62), (48, 82, 40), (100, 138, 70)])])
        x0, x1, y0, y1 = int(cx - r - 2), int(cx + r + 3), int(cy - r - 2), int(cy + r + 3)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        u = (xx - cx) * np.cos(a) + (yy - cy) * np.sin(a); v = -(xx - cx) * np.sin(a) + (yy - cy) * np.cos(a)
        inside = (u / r) ** 2 + (v / (r * 0.55)) ** 2 < 1
        shade = (0.85 + 0.3 * (1 - np.clip((u / r) ** 2 + (v / (r * 0.55)) ** 2, 0, 1)))[..., None]
        img[yy[inside].astype(int) % n, xx[inside].astype(int) % n] = (tone * shade)[inside]
    return img


SWATCH_COLOURS = {"red_foil": (196, 30, 54), "blush_foil": (238, 164, 180), "rosegold_foil": (230, 172, 150),
                  "gold_ribbon": (230, 196, 128), "white_ribbon": (246, 242, 238), "pink_ribbon": (232, 136, 166)}


def swatches():
    img = np.empty((32, 32 * len(SWATCHES), 3), np.float32)
    for i, name in enumerate(SWATCHES):
        img[:, 32 * i:32 * (i + 1)] = c(*SWATCH_COLOURS[name])
    return img


def build():
    rng = np.random.default_rng(14)
    atlas = np.empty((SIZE, SIZE, 3), np.float32); atlas[:] = IVORY
    def put(img, rect):
        x, y, w, h = rect
        assert img.shape[:2] == (h, w), (img.shape, rect)
        atlas[y:y + h, x:x + w] = img
        atlas[y:y + h, x - 4:x] = img[:, :1]; atlas[y:y + h, x + w:x + w + 4] = img[:, -1:]   # bleed for filtering
        atlas[y - 4:y, x - 4:x + w + 4] = atlas[y:y + 1, x - 4:x + w + 4]
        atlas[y + h:y + h + 4, x - 4:x + w + 4] = atlas[y + h - 1:y + h, x - 4:x + w + 4]
    W, D = RUGS["heart"]["size"]
    put(rect_rug(W, D, IVORY, ROSE, ROSE_DK, IVORY_DK * 1.04, GOLD, rng), RUGS["heart"]["rect"])
    W, D = RUGS["screen"]["size"]
    put(rect_rug(W, D, WINE, c(186, 118, 124), WINE_DK, c(232, 206, 192), GOLD, rng), RUGS["screen"]["rect"])
    put(marble(rng), MARBLE_RECT)
    put(hedge(rng), HEDGE_RECT)
    put(swatches(), SWATCH_RECT)
    return np.clip(atlas, 0, 1)


if __name__ == "__main__":
    from PIL import Image
    img = (build()[::-1] * 255 + 0.5).astype(np.uint8)                           # image rows top-down
    Image.fromarray(img).save(sys.argv[1], quality=90, subsampling=0)
    print("saved", sys.argv[1])
