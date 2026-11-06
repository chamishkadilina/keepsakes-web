"""Romantic pieces for the museum: pillar candles and gold lanterns (their flames burn on the web), heart foil balloons
that gently float, strings of golden bulbs, sheer curtains with little lights behind them, a gold dimmer switch,
velvet ropes, a neon sign, tall flower stands, a rose garland round the collage, the gramophone by the dance floor and
where the love notes hang. Candles, lanterns, the little lights behind the sheers and the neon also light the room in
the bake (Parts.lights). Local coordinates: floor at z = 0, a piece's front faces +y."""
import bmesh, math
from mathutils import Vector, Matrix
from props_geometry import TAU, UP, track, rbox, cuts, lathe, tube, place, set_uv, polar_grid
from props_flowers import RED_BLUSH_WHITE, bloom, leaf, roses, rose_leaves, pick
from props_atlas import swatch_uv

CANDLE_LIGHT = (1.0, 0.52, 0.22)        # candle flame (linear RGB), baked
NEON_LIGHT = (1.0, 0.3, 0.55)           # pink neon glow on the wall
FOILS = ("red_foil", "blush_foil", "red_foil", "rosegold_foil")   # half of them red


def plinth(parts, height=0.95, radius=0.24):
    """Round cream plinth with a fine gold ring under its cap and above its foot."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    R, r = radius, radius - 0.03
    shaft = [(0, 0.0), (R - 0.008, 0.0), (R, 0.006), (R, 0.034), (R - 0.008, 0.04), (r, 0.04)]
    shaft += [(r, z) for z in [0.06 + 0.07 * k for k in range(14) if 0.06 + 0.07 * k < height - 0.06]]
    shaft += [(r, height - 0.05), (R - 0.008, height - 0.05), (R, height - 0.044), (R, height - 0.006),
              (R - 0.008, height), (0, height)]
    lathe(c, shaft, 48)
    for z in (0.052, height - 0.062):
        lathe(g, [(r - 0.0005, z), (r + 0.0035, z + 0.001), (r + 0.0035, z + 0.009), (r - 0.0005, z + 0.01)], 48)


# ---------------------------------------------------------------- candles and lanterns

def candle(parts, at, height, radius):
    """Ivory pillar candle with a softly melted, dipped top and a short wick; its flame goes to parts.flames."""
    dip = min(0.012, radius * 0.25)
    lathe(parts["trim_cream"], [(0, 0), (radius * 0.97, 0), (radius, 0.004), (radius, height - 0.008), (radius * 0.985, height - 0.002),
                                (radius * 0.93, height - dip * 0.3), (radius * 0.55, height - dip), (0, height - dip * 0.85)], 16, at=at)
    top = Vector(at) + Vector((0, 0, height - dip * 0.85))
    tube(parts["soil"], [top, top + Vector((0.0008, 0, 0.011))], 0.0011, 4)              # wick
    parts.flames.append(top + Vector((0.0008, 0, 0.026)))


def candle_cluster(parts, rng, at=(0, 0, 0), count=3, size=1.0, light=True):
    """A few pillar candles of different heights standing close together, the tallest in the middle; with `light`,
    one warm baked light for the group."""
    at, golden = Vector(at), math.pi * (3 - math.sqrt(5))
    for i in range(count):
        r = 0.085 * size * math.sqrt(i + 0.3) if count > 1 else 0.0
        a = i * golden + rng.uniform(-0.3, 0.3)
        height = (0.3 - 0.17 * i / max(1, count - 1)) * size * rng.uniform(0.85, 1.1)
        candle(parts, at + Vector((r * math.cos(a), r * math.sin(a), 0)), height, rng.uniform(0.032, 0.046) * size)
    if light:
        centre = sum(parts.flames[-count:], Vector()) / count
        parts.lights.append(dict(kind="POINT", pos=centre + Vector((0, 0, 0.03)), colour=CANDLE_LIGHT, watts=5.0 * count))


def candle_tray(parts, rng, at, count=3):
    """Round gold tray with candles on it (tables, consoles)."""
    lathe(parts["gold_metal"], [(0, 0), (0.12, 0), (0.125, 0.004), (0.13, 0.016), (0.124, 0.017), (0.118, 0.006), (0, 0.006)], 32, at=at)
    candle_cluster(parts, rng, Vector(at) + Vector((0, 0, 0.006)), count, 0.7)


def pane(bm, centre, right, up, half_w, half_h):
    """One flat rectangle (glass), facing right x up."""
    return bm.faces.new([bm.verts.new(centre + right * (sx * half_w) + up * (sz * half_h)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def lantern(parts, rng, height=0.55, light=True):
    """Gold lantern: glass panes between slim posts, a pillar candle inside, a pyramid roof with a ring on top."""
    g, gl = parts["gold_metal"], parts["glass"]
    w, top = height * 0.42, height - 0.085
    rbox(g, (w + 0.03, w + 0.03, 0.035), 0.006, 2, at=(0, 0, 0.0175))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts(g, rbox(g, (0.014, 0.014, top - 0.035), 0.003, 1, at=(sx * w / 2, sy * w / 2, (top + 0.035) / 2)), 2, 0.035, top, 0.12)
    rbox(g, (w + 0.02, w + 0.02, 0.02), 0.004, 2, at=(0, 0, top + 0.01))
    place(g, lathe(g, [(0, top + 0.02), ((w + 0.02) * 0.72, top + 0.02), (0.02, top + 0.075), (0, top + 0.075)], 4), yaw=45)
    ring = [Vector((0, 0.024 * math.cos(TAU * k / 16), top + 0.1 + 0.024 * math.sin(TAU * k / 16))) for k in range(16)]
    tube(g, ring, 0.004, 6, closed=True, plane_normal=Vector((1, 0, 0)))
    for n in (Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))):
        pane(gl, n * (w / 2 - 0.002) + Vector((0, 0, (top + 0.035) / 2)), Vector((-n.y, n.x, 0)), UP, w / 2 - 0.007, (top - 0.035) / 2 - 0.002)
    candle(parts, (0, 0, 0.035), height * 0.38, w * 0.22)
    if light:
        parts.lights.append(dict(kind="POINT", pos=parts.flames[-1] + Vector((0, 0, 0.03)), colour=CANDLE_LIGHT, watts=6.0))


# ---------------------------------------------------------------- hearts and balloons

def heart_point(t):
    """Point on the classic heart curve, 2 wide (x -1 ... 1): lobes up to y 0.73, the tip down at y -1.06."""
    return math.sin(t) ** 3, (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16


def puffy_heart(bm, width, depth, seg=40, rings=5):
    """Inflated heart: two domed faces sewn together at the outline, standing in the xz plane (x across, z up, its
    middle near the origin), bulging towards +y and -y. Returns its verts."""
    done = track(bm)
    k, cz = width / 2, -0.15
    outline = [heart_point(TAU * i / seg) for i in range(seg)]
    edge = [bm.verts.new((x * k, 0, z * k)) for x, z in outline]
    for sign in (1, -1):
        rows = [[bm.verts.new((0, sign * depth / 2, cz * k))]]
        for j in range(1, rings):
            s = j / rings
            bulge = sign * depth / 2 * (1 - s ** 2.6) ** 0.5
            rows.append([bm.verts.new((s * x * k, bulge, (cz + s * (z - cz)) * k)) for x, z in outline])
        rows.append(edge)
        for i in range(seg):
            bm.faces.new((rows[0][0], rows[1][i], rows[1][(i + 1) % seg]))
        for a, b in zip(rows[1:], rows[2:]):
            for i in range(seg):
                bm.faces.new((a[i], b[i], b[(i + 1) % seg], a[(i + 1) % seg]))
    verts = done()
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in verts for f in v.link_faces}))
    return verts


def balloon(parts, rng, centre, facing, anchor, colour, ribbon="gold_ribbon", tied=True):
    """Heart foil balloon floating at `centre`, turned to `facing` (radians), its thin curling ribbon down to `anchor`.
    For the web's float (balloons.ts): UV "bob" = (phase, weight), the ribbon's weight fading towards where it is tied
    (`tied` = False: the ribbon hangs free and moves with the balloon); UV "pivot" = the balloon's middle (x, y), made
    world coordinates by build(). The glTF export flips v (v -> 1 - v), so "bob" stores 1 - weight here."""
    bm = parts["balloon_foil"]
    width = rng.uniform(0.38, 0.46)
    verts = puffy_heart(bm, width, width * 0.3, 36, 5)
    tilt = Matrix.Rotation(rng.uniform(-0.15, 0.15), 4, "Y") @ Matrix.Rotation(rng.uniform(-0.12, 0.12), 4, "X")
    bmesh.ops.transform(bm, matrix=Matrix.Translation(centre) @ Matrix.Rotation(facing, 4, "Z") @ tilt, verts=verts)
    tip = min((v.co for v in verts), key=lambda co: co.z).copy()
    phase = rng.uniform(0, TAU)
    pts = []
    for i in range(27):
        u = i / 26
        curl = 0.014 * (1 - u) ** 0.6
        a = phase + u * 9 * math.pi
        pts.append(tip.lerp(Vector(anchor), u) + Vector((curl * math.cos(a), curl * math.sin(a), 0)))
    string = tube(bm, pts, 0.0018, 3)
    faces = list({f for v in verts for f in v.link_faces})
    middle = Vector(centre)
    set_uv(bm, faces, lambda co: swatch_uv(colour))
    set_uv(bm, faces, lambda co: (phase, 0.0), "bob")
    rib = list({f for v in string for f in v.link_faces})
    set_uv(bm, rib, lambda co: swatch_uv(ribbon))
    span = max(1e-3, tip.z - anchor[2])
    set_uv(bm, rib, lambda co: (phase, 0.0 if not tied else 1.0 - min(1.0, max(0.0, (co.z - anchor[2]) / span)) ** 1.5), "bob")
    set_uv(bm, faces + rib, lambda co: (middle.x, middle.y), "pivot")


def balloon_bunch(parts, rng, count, anchor=(0, 0, 0), height=(1.4, 2.1), spread=0.35, weight=False):
    """Heart balloons in red, rose and pink, tied together at `anchor` and floating at different heights; `weight`: tied
    to a little gold heart weight on the floor."""
    anchor = Vector(anchor)
    if weight:
        heart = puffy_heart(parts["gold_metal"], 0.12, 0.05, 28, 3)
        bmesh.ops.transform(parts["gold_metal"], matrix=Matrix.Translation(anchor + Vector((0, 0, 0.065))), verts=heart)
        anchor = anchor + Vector((0, 0, 0.125))
    for i in range(count):
        a = TAU * i / count + rng.uniform(-0.4, 0.4)
        r = spread * rng.uniform(0.4, 1.0) if count > 1 else 0.0
        centre = anchor + Vector((r * math.cos(a), r * math.sin(a), rng.uniform(*height)))
        balloon(parts, rng, centre, rng.uniform(-0.7, 0.7), anchor, FOILS[i % len(FOILS)],
                ("gold_ribbon", "white_ribbon", "pink_ribbon")[i % 3])


def light_string(parts, rng, length, hook=1.9, sag=0.2, spacing=0.25, top=3.78, off=0.07):
    """A string of round golden bulbs draped along a wall just under the cornice, as couples hang them at home: a thin
    gold wire in shallow swags between hooks every ~`hook` metres, a bulb hanging from it every `spacing` metres.
    Runs along local x from 0 to `length`, `off` metres out from the wall (local y = 0, the room is +y). Only the bulbs
    glow, golden, on the web (bulb_glow): they throw no pools of light on the wall."""
    g, glow = parts["gold_metal"], parts["bulb_glow"]
    n = max(1, round(length / hook))
    span = length / n
    for i in range(n):
        x0 = i * span
        wire = [Vector((x0 + span * t, off, top - sag * 4 * t * (1 - t))) for t in (k / 12 for k in range(13))]
        tube(g, wire, 0.0025, 4)
        lathe(g, [(0, 0), (0.008, 0), (0.008, 0.012), (0, 0.012)], 6, at=(x0, off - 0.005, top - 0.006))   # hook
        count = max(2, round(span / spacing))
        for k in range(count):
            t = (k + 0.5) / count
            p = Vector((x0 + span * t, off, top - sag * 4 * t * (1 - t)))
            tube(g, [p, p - Vector((0, 0, 0.035))], 0.0018, 3)                          # the bulb's little cap
            bulb = p - Vector((0, 0, 0.058))
            for v in bmesh.ops.create_icosphere(glow, subdivisions=2, radius=0.022)["verts"]:
                v.co += bulb
    lathe(g, [(0, 0), (0.008, 0), (0.008, 0.012), (0, 0.012)], 6, at=(length, off - 0.005, top - 0.006))


FAIRY_LIGHT = (1.0, 0.7, 0.4)           # the curtain of little lights behind the sheers (linear RGB), their glow baked


def sheer_drape(parts, rng, length, height=3.7, off=0.15, pleat=0.16):
    """Ivory sheer curtains along a wall, floor to just under the cornice, softly pleated on a slim gold rod, with a
    curtain of little warm lights hanging between them and the wall, glowing through the voile. Runs along local x from
    0 to `length`, the wall at local y = 0 (the room is +y). The sheers are not baked (the light shows through them);
    the little lights go to parts.fairies (the web lights them) and warm the wall behind in the bake."""
    g, sheer = parts["gold_metal"], parts["sheer_ivory"]
    tube(g, [Vector((0, off, height + 0.04)), Vector((length, off, height + 0.04))], 0.009, 8)
    for x in (0.06, length / 2, length - 0.06):                                         # brackets
        tube(g, [Vector((x, 0.0, height + 0.04)), Vector((x, off + 0.012, height + 0.04))], 0.006, 6)
    for x in (-0.02, length + 0.02):                                                     # finials
        lathe(g, [(0, 0), (0.016, 0.004), (0.02, 0.02), (0.012, 0.035), (0, 0.04)], 10, at=(x, off, height + 0.04))
    cols, rows = max(8, round(length / pleat * 4)), 14
    grid = []
    for j in range(rows + 1):
        z = 0.004 + (height - 0.004) * j / rows
        row = []
        for i in range(cols + 1):
            x = length * i / cols
            wave = TAU * x / pleat + 0.7 * math.sin(x * 0.9) + 0.35 * math.sin(x * 2.3)    # soft folds, never quite even
            fold = math.sin(wave) * (0.035 + 0.012 * (1 - z / height)) * (0.8 + 0.2 * math.sin(x * 0.7 + 1.0))
            row.append(sheer.verts.new((x, off - 0.02 + fold, z)))
        grid.append(row)
    for j in range(rows):
        for i in range(cols):
            sheer.faces.new((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]))     # facing the room
    x = 0.14
    while x < length - 0.1:                                                              # strands of little lights
        top = height - 0.08 - rng.uniform(0, 0.06)
        z = top
        while z > 0.75:
            parts.fairies.append(Vector((x + rng.uniform(-0.015, 0.015), 0.07, z)))
            z -= rng.uniform(0.12, 0.17)
        x += 0.26
    n = max(1, round(length / 2.0))
    for i in range(n):                                                                   # their warm glow on the wall
        span = length / n
        parts.lights.append(dict(kind="AREA", pos=Vector((span * (i + 0.5), 0.1, 2.25)), normal=Vector((0, -1, 0)),
                                 size=(span * 0.9, 2.6), colour=FAIRY_LIGHT, watts=3.5 * span))


def dimmer_switch(parts, rng, z=1.3):
    """A gold dimmer on the wall by the heart room's door: a slim gold plate with an ivory inset and a round gold knob.
    Faces +y from the wall at y = 0; marked for the web (dimmer_switch: "aim" = the way it faces)."""
    g = parts["gold_metal"]
    rbox(g, (0.09, 0.008, 0.14), 0.004, 2, at=(0, 0.004, z))
    rbox(parts["trim_cream"], (0.064, 0.004, 0.11), 0.003, 1, at=(0, 0.009, z))
    done = track(g)
    lathe(g, [(0, 0), (0.019, 0), (0.019, 0.018), (0.016, 0.023), (0, 0.024)], 16)      # the knob, built along z ...
    for v in done():                                                                     # ... and turned to face +y
        v.co = Vector((v.co.x, 0.008 + v.co.z, z + 0.012 - v.co.y))
    parts.markers["dimmer_switch"] = (Vector((0, 0.04, z + 0.012)), {"aim": [0, 1, 0]})


def gramophone(parts, rng, height=0.8, lift=25):
    """A gramophone on a round cream plinth by the dance floor: a polished walnut case with gold bands, a gold crank and
    tone arm, a record on its turntable (gramophone_record: the web turns it and plays their song) and a big gold horn
    opening like a flower towards local +y, `lift` degrees up. Marked for the web (gramophone: the horn's mouth, "aim" =
    the way it plays)."""
    g, w = parts["gold_metal"], parts["wood_walnut"]
    plinth(parts, height, 0.22)
    cuts(w, rbox(w, (0.34, 0.34, 0.15), 0.012, 2, at=(0, 0, height + 0.075)), 0, -0.17, 0.17, 0.11)
    for z in (height + 0.008, height + 0.142):                                           # gold bands round the case
        rbox(g, (0.346, 0.346, 0.012), 0.004, 1, at=(0, 0, z))
    deck = height + 0.15
    lathe(g, [(0, deck), (0.15, deck), (0.15, deck + 0.012), (0, deck + 0.012)], 40)       # the turntable
    rec, r = deck + 0.012, 0.145
    _, ring = polar_grid(parts["gramophone_record"], r, rec + 0.004, 0.03, 40,
                            lambda co: (0.5 + co.x / (2 * r), 0.5 + co.y / (2 * r)))
    low = [parts["gramophone_record"].verts.new((v.co.x, v.co.y, rec)) for v in ring]
    edge = [parts["gramophone_record"].faces.new((low[k], low[(k + 1) % 40], ring[(k + 1) % 40], ring[k])) for k in range(40)]
    set_uv(parts["gramophone_record"], edge, lambda co: (0.5 + 0.49 * co.x / r, 0.5 + 0.49 * co.y / r))
    lathe(g, [(0, rec + 0.004), (0.005, rec + 0.004), (0.005, rec + 0.028), (0, rec + 0.03)], 12)   # spindle
    post = Vector((0.13, -0.12, deck))                                                   # tone arm, resting on the record
    lathe(g, [(0, 0), (0.022, 0), (0.022, 0.03), (0.012, 0.042), (0, 0.046)], 16, at=post)
    end = Vector((0.075, 0.075, rec + 0.03))
    tube(g, [post + Vector((0, 0, 0.044)), Vector((0.125, -0.02, rec + 0.07)), end], 0.007, 8)
    lathe(g, [(0, -0.012), (0.026, -0.012), (0.028, 0.0), (0.026, 0.01), (0, 0.012)], 20, at=end + Vector((0, 0, -0.008)))
    tube(g, [Vector((0.17, 0.0, height + 0.08)), Vector((0.23, 0.0, height + 0.08)), Vector((0.23, 0.0, height + 0.03))], 0.006, 8)
    lathe(g, [(0, 0), (0.012, 0), (0.014, 0.02), (0.012, 0.04), (0, 0.042)], 12, at=(0.23, 0.0, height - 0.012))   # crank knob
    base = Vector((0, -0.06, deck + 0.2))                                                # the horn, from the back of the case
    tube(g, [Vector((0, -0.13, deck - 0.03)), Vector((0, -0.17, deck + 0.08)), base], 0.022, 12)
    outer = [(0.022, 0.0), (0.03, 0.12), (0.045, 0.24), (0.075, 0.34), (0.13, 0.42), (0.21, 0.47), (0.27, 0.49), (0.276, 0.486)]
    inner = [(rr - 0.005, z - 0.004) for rr, z in reversed(outer[1:-1])] + [(0.017, 0.0)]
    done = track(g)
    lathe(g, outer + inner, 48)
    turn = Matrix.Translation(base) @ Matrix.Rotation(math.radians(lift - 90), 4, "X")
    for v in done():
        v.co = turn @ v.co
    aim = Vector((0, math.cos(math.radians(lift)), math.sin(math.radians(lift))))
    parts.markers["gramophone"] = (base + aim * 0.49, {"aim": [round(c, 4) for c in aim]})


def love_notes(parts, rng, width=4.0, depth=3.0, cols=6, rows=4, low=2.2, high=2.75, ceiling=4.32):
    """Where the love notes hang over the right gallery's open middle: cols × rows cards spread over `width` × `depth`
    (local x, y), between `low` and `high` above the floor, each on a ribbon from the ceiling, ordered so that any first
    few are spread out: the web hangs one card per reason (parts.notes: card middle, ribbon top)."""
    pts = [Vector((-width / 2 + width * (i + 0.5) / cols + rng.uniform(-0.15, 0.15),
                   -depth / 2 + depth * (j + 0.5) / rows + rng.uniform(-0.15, 0.15), rng.uniform(low, high)))
           for j in range(rows) for i in range(cols)]
    order = [min(pts, key=lambda p: p.xy.length)]                                        # from the middle outwards
    rest = [p for p in pts if p is not order[0]]
    while rest:
        far = max(rest, key=lambda p: min((p.xy - q.xy).length for q in order))
        order.append(far)
        rest.remove(far)
    parts.notes += [(p, ceiling) for p in order]


# ---------------------------------------------------------------- velvet ropes

def post(g, at):
    """Gold stanchion: weighted round foot, slim pole, a ball on top."""
    ball = [(0.032 * math.sin(math.radians(a)), 0.925 - 0.032 * math.cos(math.radians(a))) for a in range(30, 181, 30)]
    lathe(g, [(0, 0), (0.14, 0), (0.145, 0.006), (0.14, 0.02), (0.07, 0.035), (0.03, 0.06), (0.019, 0.08), (0.019, 0.3),
              (0.019, 0.55), (0.019, 0.8), (0.026, 0.86), (0.03, 0.88), (0.03, 0.895), (0.016, 0.9)] + ball, 16, at=at)


def velvet_ropes(parts, rng, posts, closed=False):
    """Gold posts with red velvet ropes hanging between them, round or in front of an exhibit."""
    g, rope = parts["gold_metal"], parts["rose_petal"]
    pts = [Vector((x, y, 0)) for x, y in posts]
    for p in pts:
        post(g, p)
    for a, b in zip(pts, pts[1:] + (pts[:1] if closed else [])):
        n = (b - a).normalized()
        a1, b1 = a + n * 0.034 + Vector((0, 0, 0.87)), b - n * 0.034 + Vector((0, 0, 0.87))
        tube(rope, [a1.lerp(b1, u) - Vector((0, 0, 0.64 * u * (1 - u))) for u in (i / 12 for i in range(13))], 0.016, 10)
        for end, d in ((a1, n), (b1, -n)):
            tube(g, [end - d * 0.012, end + d * 0.022], 0.02, 10)                        # gold hooks


# ---------------------------------------------------------------- neon, flowers

def neon_sign(parts, rng, width=1.5, height=0.52, z=1.78):
    """Neon sign on a clear acrylic panel held off the wall by four gold standoffs; the web writes the glowing words on
    neon_text (UVs across the panel). Local y = 0 is the wall; the sign faces +y. Its pink glow on the wall is baked."""
    g, t = parts["gold_metal"], parts["neon_text"]
    rbox(parts["glass"], (width, 0.01, height), 0.006, 2, at=(0, 0.045, z))
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, zz = sx * (width / 2 - 0.05), z + sz * (height / 2 - 0.05)
            tube(g, [Vector((x, 0.0, zz)), Vector((x, 0.056, zz))], 0.009, 12)
    x0, x1, z0, z2 = -width / 2 + 0.04, width / 2 - 0.04, z - height / 2 + 0.03, z + height / 2 - 0.03
    face = t.faces.new([t.verts.new((x, 0.052, zz)) for x, zz in ((x1, z0), (x0, z0), (x0, z2), (x1, z2))][::-1])
    face.normal_update()
    if face.normal.y < 0:
        face.normal_flip()
    set_uv(t, [face], lambda co: ((x1 - co.x) / (x1 - x0), (co.z - z0) / (z2 - z0)))   # read from the front: u runs to -x
    parts.lights.append(dict(kind="AREA", pos=Vector((0, 0.35, z)), normal=Vector((0, -1, 0)), size=(width, height), colour=NEON_LIGHT, watts=10))


def floral_stand(parts, rng, height=1.05):
    """Tall gold flower stand: a slim column on a round foot with a bowl of red, blush and white roses and trailing leaves."""
    lathe(parts["gold_metal"], [(0, 0), (0.17, 0), (0.175, 0.006), (0.165, 0.018), (0.06, 0.04), (0.03, 0.08), (0.022, 0.3), (0.022, 0.55),
                                (0.022, 0.8), (0.022, height - 0.12), (0.05, height - 0.08), (0.12, height - 0.03), (0.14, height),
                                (0.13, height + 0.005), (0, height - 0.02)], 32)
    centre = Vector((0, 0, height + 0.05))
    roses(parts, rng, centre, 0.2, 30, math.radians(108), 0.95, RED_BLUSH_WHITE, petals=9, grid=(4, 4))
    rose_leaves(parts, rng, centre, 0.2, 14, (1.65, 2.0), (0.08, 0.11))
    for i in range(4):                                                                   # trailing leaves
        a = TAU * i / 4 + rng.uniform(-0.3, 0.3)
        leaf(parts["rose_leaf"], centre + Vector((0.16 * math.cos(a), 0.16 * math.sin(a), -0.08)),
             Vector((0.5 * math.cos(a), 0.5 * math.sin(a), -1)).normalized(), 0.13, 0.045, 0.01)


def niche_garland(parts, rng, half_width=2.78, z_top=3.67, z_low=1.75, inset=0.07):
    """A lush garland of red, blush and white roses along the top of the collage niche's frame (on its face and resting
    on top of it), big clusters in its corners and cascades down both sides: roses only, no leaves. Local: x across the niche,
    z up, y = 0 the frame's face (the roses face +y; the frame's top runs back to y = -0.17). It stays on the frame,
    clear of the photos."""
    def rose(p, axis, k):
        bloom(parts[pick(rng, RED_BLUSH_WHITE)], p, axis.normalized(), k, rng.uniform(0, TAU), petals=7, grid=(4, 3))

    n = round(2 * half_width / 0.1)
    for i in range(n + 1):
        x = -half_width + 2 * half_width * i / n
        rose(Vector((x, 0.04, z_top + rng.uniform(-0.03, 0.03))), Vector((rng.uniform(-0.3, 0.3), 1, rng.uniform(0.0, 0.4))), rng.uniform(1.3, 1.6))
        rose(Vector((x + 0.05, -rng.uniform(0.03, 0.1), z_top + 0.12 + rng.uniform(0, 0.03))), Vector((rng.uniform(-0.3, 0.3), 0.7, 1)),
             rng.uniform(1.4, 1.7))                                                      # on top of the frame
    for s in (-1, 1):
        for _ in range(16):                                                              # corner clusters
            p = Vector((s * (half_width - 0.06) + rng.uniform(-0.15, 0.15), rng.uniform(-0.04, 0.08), z_top + rng.uniform(-0.18, 0.16)))
            rose(p, Vector((s * 0.35, 1, 0.25)), rng.uniform(1.6, 2.0))
        m = round((z_top - z_low) / 0.1)
        for j in range(1, m + 1):                                                        # cascades down the sides
            t = j / m
            z = z_top - (z_top - z_low) * t
            rose(Vector((s * (half_width - inset) + rng.uniform(-0.02, 0.02), 0.04, z)), Vector((s * 0.25, 1, 0.1)), 1.4 - 0.5 * t)
            if j % 2 or t < 0.5:
                rose(Vector((s * (half_width + 0.03), -rng.uniform(0.04, 0.1), z - 0.05)), Vector((s, 0.4, 0.1)), 1.25 - 0.4 * t)
