"""Trees for the museum: potted olive trees, fiddle-leaf figs, kentia palms and weeping figs in cream planters with
gold rims, and rose topiaries (by the screen, each washed by a small warm floor light). Local coordinates: floor at
z = 0."""
import math
from mathutils import Vector, Matrix
from props_geometry import TAU, UP, lathe, tube, along, polar_grid
from props_flowers import bloom, rose_leaves, fibonacci_cap, pick, RED_BLUSH_WHITE


def planter(parts, style="tall", scale=1.0):
    """Cream planter with a gold rim and potting soil: "tall" (tapered: olive trees, palms and weeping figs, `scale` for a bigger
    one) or "fluted" (fiddle-leaf figs). Returns the soil height."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    if style == "tall":
        k = scale
        body = [(0, 0), (0.16, 0), (0.168, 0.006), (0.168, 0.034), (0.16, 0.042), (0.17, 0.1), (0.19, 0.2), (0.21, 0.3),
                (0.228, 0.4), (0.243, 0.5), (0.25, 0.54), (0.262, 0.55), (0.265, 0.565), (0.256, 0.575), (0.242, 0.57), (0.236, 0.53)]
        lathe(c, [(r * k, z * k) for r, z in body], 32)
        lathe(g, [(r * k, z * k) for r, z in ((0.1685, 0.012), (0.1705, 0.013), (0.1705, 0.028), (0.1685, 0.029))], 32)
        lathe(g, [(r * k, z * k) for r, z in ((0.264, 0.553), (0.267, 0.555), (0.267, 0.566), (0.264, 0.568))], 32)
        soil_z, soil_r = 0.53 * k, 0.236 * k
    else:
        n, flutes = 48, 12
        rings = []
        for r, z, fluted in ((0.15, 0.0, False), (0.158, 0.006, False), (0.158, 0.03, False), (0.2, 0.06, True), (0.208, 0.14, True),
                             (0.212, 0.24, True), (0.214, 0.34, True), (0.215, 0.41, True), (0.222, 0.43, False),
                             (0.226, 0.445, False), (0.218, 0.452, False), (0.206, 0.448, False), (0.204, 0.42, False)):
            ring = []
            for k in range(n):
                a = TAU * k / n
                rr = r + (0.008 * (abs(math.cos(flutes * a / 2)) ** 0.6 - 0.6) if fluted else 0.0)   # rounded flutes
                ring.append(c.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
            rings.append(ring)
        bottom = c.verts.new((0, 0, 0))
        for k in range(n):
            c.faces.new((bottom, rings[0][(k + 1) % n], rings[0][k]))
        for a, b in zip(rings, rings[1:]):
            for k in range(n):
                c.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
        lathe(g, [(0.1585, 0.01), (0.1605, 0.011), (0.1605, 0.026), (0.1585, 0.027)], 48)
        lathe(g, [(0.223, 0.428), (0.2275, 0.432), (0.2275, 0.446), (0.223, 0.45)], 48)
        soil_z, soil_r = 0.425, 0.204
    polar_grid(parts["soil"], soil_r, soil_z, 0.08, 24)
    return soil_z


def olive_tree(parts, rng):
    """Potted olive tree (~1.9 m): a braided trunk under a rounded, airy crown: eight branches fanning out into twigs
    with about 1600 narrow silvery leaves."""
    soil = planter(parts, "tall")
    bark, leaves = parts["bark"], parts["olive_leaf"]
    top = soil + 0.6
    for phase in (0, math.pi):                                                           # two stems twisted round each other
        pts = [Vector((0.017 * math.cos(phase + 2.6 * math.pi * t), 0.017 * math.sin(phase + 2.6 * math.pi * t), soil - 0.02 + (top - soil + 0.04) * t))
               for t in (k / 9 for k in range(10))]
        tube(bark, pts, [0.022 - 0.006 * k / 9 for k in range(10)], 8)

    def twig(start, d, length):
        pts = [start]
        for k in range(3):                                                               # curving out, the tip dipping a little
            d = (d + Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(-0.18, 0.08)))).normalized()
            pts.append(pts[-1] + d * length / 3)
        tube(bark, pts, [0.004, 0.003, 0.0022, 0.0015], 3)
        s = 0.025
        while s < length:                                                                # leaves in pairs, reaching forward
            p = along(pts, s / length)
            seg = (pts[min(3, int(s / length * 3) + 1)] - pts[min(2, int(s / length * 3))]).normalized()
            spin = rng.uniform(0, TAU)
            ortho = seg.cross(UP)
            ortho = (ortho if ortho.length > 1e-3 else Vector((1, 0, 0))).normalized()
            ortho = Matrix.Rotation(rng.uniform(-0.5, 0.5), 3, seg) @ ortho
            for side in (-1, 1):
                ld = (seg * 0.75 + ortho * side * 0.65 + Vector((0, 0, rng.uniform(-0.15, 0.2)))).normalized()
                olive_leaf(leaves, p, ld, rng.uniform(0.05, 0.07), rng.uniform(0.011, 0.014))
            s += rng.uniform(0.017, 0.023)
    for i in range(8):                                                                   # branches fanning out from the trunk
        a = TAU * i / 8 + rng.uniform(-0.25, 0.25)
        tilt = math.radians(rng.uniform(35, 62))
        d = Vector((math.sin(tilt) * math.cos(a), math.sin(tilt) * math.sin(a), math.cos(tilt)))
        length = rng.uniform(0.32, 0.46)
        pts = [Vector((0, 0, top - 0.03))]
        for k in range(4):
            d = (d + Vector((rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), 0.12))).normalized()
            pts.append(pts[-1] + d * length / 4)
        tube(bark, pts, [0.016 * (1 - 0.68 * k / 4) for k in range(5)], 6)
        across = d.cross(UP).normalized()
        for j in range(10):                                                              # twigs all along it, all round it
            start = along(pts, 0.2 + 0.8 * (j + rng.uniform(0, 0.7)) / 10)
            side = Matrix.Rotation(rng.uniform(0, TAU), 3, d) @ across
            twig(start, (d * 0.5 + side * 0.85 + Vector((0, 0, rng.uniform(-0.1, 0.35)))).normalized(), rng.uniform(0.14, 0.26))
        twig(pts[-1], d, rng.uniform(0.16, 0.22))


def olive_leaf(bm, root, d, length, width):
    """Narrow pointed olive leaf: two triangles facing up (drawn double-sided)."""
    side = d.cross(UP)
    side = (side if side.length > 1e-3 else Vector((1, 0, 0))).normalized()
    up = side.cross(d).normalized()
    mid = root + d * length * 0.42 - up * width * 0.1
    a, b, c, e = (bm.verts.new(p) for p in (root, mid + side * width / 2, root + d * length, mid - side * width / 2))
    for tri in ((a, b, c), (a, c, e)):
        f = bm.faces.new(tri)
        f.normal_update()
        if f.normal.dot(up) < 0:
            f.normal_flip()


def fig_leaf(bm, root, d, length, rng):
    """Fiddle-leaf fig leaf: narrow at the stalk, a waist, broad and round at the top, cupped, wavy edged and drooping."""
    side = d.cross(UP)
    side = (side if side.length > 1e-3 else Vector((1, 0, 0))).normalized()
    up = side.cross(d).normalized()
    width = length * rng.uniform(0.6, 0.7)
    ts = (0.0, 0.12, 0.3, 0.5, 0.68, 0.82, 0.93, 1.0)
    fs = (0.08, 0.5, 0.62, 0.86, 1.0, 0.9, 0.58, 0.0)
    droop = rng.uniform(0.2, 0.35) * length
    rows = []
    for t, f in zip(ts, fs):
        centre = root + d * (length * t) - up * (droop * t * t)
        row = []
        for u in (-1, 0, 1):
            wave = 0.006 * math.sin(t * 17 + u * 3) * abs(u)
            row.append(centre + side * (width / 2 * f * u) + up * (0.16 * width * f * u * u + wave))
        rows.append(row)
    vs = [[bm.verts.new(p) for p in row] for row in rows]
    for j in range(len(ts) - 1):
        for i in range(2):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))


def fig_tree(parts, rng):
    """Potted fiddle-leaf fig (~1.9 m): a slender trunk with two side shoots and about 46 big violin-shaped leaves,
    spiralling round the stems, rising and smaller towards the top."""
    soil = planter(parts, "fluted")
    bark, leaves = parts["bark"], parts["fig_leaf"]
    trunk = [Vector((0.02 * math.sin(t * 3), 0.015 * math.sin(t * 2), soil - 0.02 + 1.38 * t)) for t in (k / 8 for k in range(9))]
    tube(bark, trunk, [0.021 - 0.01 * k / 8 for k in range(9)], 8)
    stems = [(trunk, 0.45, 28)]                                                          # (stem, where leaves start, leaves)
    for z in (soil + 0.66, soil + 0.86):
        a = rng.uniform(0, TAU)
        d = Vector((0.55 * math.cos(a), 0.55 * math.sin(a), 0.85)).normalized()
        shoot = [along(trunk, (z - soil) / 1.3) + d * (0.33 * k / 4) + Vector((0, 0, 0.03 * (k / 4) ** 2)) for k in range(5)]
        tube(bark, shoot, [0.011 - 0.005 * k / 4 for k in range(5)], 6)
        stems.append((shoot, 0.3, 9))
    angle = rng.uniform(0, TAU)
    for stem, t0, n in stems:
        for i in range(n):
            t = t0 + (1 - t0) * i / (n - 1)
            p = along(stem, t)
            rise = i / (n - 1)                                                           # leaves near the tip point up
            angle += math.radians(137.5)
            out = Vector((math.cos(angle), math.sin(angle), 0))
            d = (out + UP * (0.05 + 1.0 * rise) + Vector([rng.uniform(-0.15, 0.15) for _ in range(3)])).normalized()
            stalk = p + d * 0.035
            tube(bark, [p, stalk], 0.004, 4)
            fig_leaf(leaves, stalk, d, rng.uniform(0.3, 0.4) * (1 - 0.25 * rise), rng)


# ---------------------------------------------------------------- big green house trees

def blade(bm, root, d, length, width, droop):
    """A long, narrow leaflet (a palm's): three segments, tapering to a point and arching down (drawn double-sided)."""
    side = d.cross(UP)
    side = (side if side.length > 1e-3 else Vector((1, 0, 0))).normalized()
    up = side.cross(d).normalized()
    rows = []
    for t, f in ((0.0, 0.25), (0.3, 1.0), (0.65, 0.8), (1.0, 0.0)):
        c = root + d * (length * t) - up * (droop * t * t)
        rows.append([bm.verts.new(c - side * width / 2 * f), bm.verts.new(c + side * width / 2 * f)])
    for j in range(3):
        bm.faces.new((rows[j][0], rows[j][1], rows[j + 1][1], rows[j + 1][0]))


def kentia_palm(parts, rng, height=2.3):
    """Potted kentia palm (~2.3 m), the classic elegant house palm: three slim canes rising from a big cream planter, each
    crowned with arching fronds of long, drooping, deep-green leaflets."""
    soil = planter(parts, "tall", 1.15)
    leaves = parts["fig_leaf"]
    for c in range(3):
        a = TAU * c / 3 + rng.uniform(-0.4, 0.4)
        out = Vector((math.cos(a), math.sin(a), 0))
        top = Vector((0, 0, soil + rng.uniform(0.55, 0.95))) + out * rng.uniform(0.06, 0.14)
        cane = [Vector((0, 0, soil - 0.02)).lerp(top, t) + out * (0.03 * t * t) for t in (k / 5 for k in range(6))]
        tube(parts["bark"], cane, [0.017 - 0.005 * k / 5 for k in range(6)], 6)
        for f in range(6):
            fa = a + TAU * f / 6 + rng.uniform(-0.3, 0.3)
            d0 = (Vector((math.cos(fa), math.sin(fa), 0)) * 0.55 + UP * rng.uniform(0.6, 1.1)).normalized()
            length = rng.uniform(0.85, 1.2) * (height - 1.3) / 1.0
            rachis = [cane[-1] + d0 * length * t - Vector((0, 0, 0.6 * length * t * t)) for t in (k / 10 for k in range(11))]
            tube(leaves, rachis, [0.006 - 0.004 * k / 10 for k in range(11)], 4)
            for k in range(2, 21):
                t = k / 20
                p = along(rachis, t)
                tangent = (along(rachis, min(1, t + 0.05)) - along(rachis, max(0, t - 0.05))).normalized()
                side = tangent.cross(UP)
                side = (side if side.length > 1e-3 else Vector((1, 0, 0))).normalized()
                for sgn in (-1, 1):
                    ld = (side * sgn * 0.8 + tangent * 0.5 - UP * 0.25).normalized()
                    blade(leaves, p, ld, (0.34 - 0.2 * t) * rng.uniform(0.9, 1.1), 0.026, 0.05)


def weeping_fig(parts, rng, height=2.25, spread=0.7):
    """Potted weeping fig (Ficus benjamina, ~2.2 m), the much-loved home tree: a braided trunk, branches arching up and
    out, and a full, natural crown of small glossy leaves on gently drooping twigs."""
    soil = planter(parts, "tall", 1.15)
    bark, leaves = parts["bark"], parts["ficus_leaf"]
    fork = soil + 0.85
    for phase in (0, math.pi):                                                           # two stems braided together
        pts = [Vector((0.02 * math.cos(phase + 3 * math.pi * t), 0.02 * math.sin(phase + 3 * math.pi * t), soil - 0.02 + (fork - soil + 0.04) * t))
               for t in (k / 10 for k in range(11))]
        tube(bark, pts, [0.024 - 0.007 * k / 10 for k in range(11)], 8)
    centre = Vector((0, 0, height - spread * 0.75))

    def twig(start, d, length):
        pts = [start]
        for k in range(4):                                                               # out, then drooping
            d = (d + Vector((rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), -0.22))).normalized()
            pts.append(pts[-1] + d * length / 4)
        tube(bark, pts, [0.004, 0.003, 0.0024, 0.0018, 0.0012], 3)
        s = 0.02
        while s < length:                                                                # small leaves, alternate
            p = along(pts, s / length)
            seg = (along(pts, min(1, s / length + 0.05)) - along(pts, max(0, s / length - 0.05))).normalized()
            ortho = seg.cross(UP)
            ortho = (ortho if ortho.length > 1e-3 else Vector((1, 0, 0))).normalized()
            ortho = Matrix.Rotation(rng.uniform(0, TAU), 3, seg) @ ortho
            ld = (seg * 0.6 + ortho * 0.8 + Vector((0, 0, rng.uniform(-0.2, 0.15)))).normalized()
            n = rng.uniform(0.06, 0.085)
            olive_leaf(leaves, p, ld, n, n * 0.48)
            s += rng.uniform(0.012, 0.016)
    for i in range(16):                                                                   # branches arching up and out
        a = TAU * i / 16 + rng.uniform(-0.2, 0.2)
        lift = rng.uniform(0.1, 1.0)                                                     # ends spread over a dome
        end = centre + Vector((math.cos(a) * spread * (1.0 - 0.8 * lift), math.sin(a) * spread * (1.0 - 0.8 * lift),
                               spread * 0.8 * lift))
        start = Vector((0, 0, fork))
        mid = start.lerp(end, 0.5) + Vector((0, 0, 0.12))
        pts = [start, start.lerp(mid, 0.6), mid, mid.lerp(end, 0.6), end]
        tube(bark, pts, [0.013 * (1 - 0.7 * k / 4) for k in range(5)], 6)
        for j in range(18):                                                              # twigs all along, all round
            p = along(pts, 0.35 + 0.65 * (j + rng.uniform(0, 0.8)) / 18)
            r = rng.uniform(0, TAU)
            d = (Vector((math.cos(r), math.sin(r), 0)) + UP * rng.uniform(0.0, 0.6)).normalized()
            twig(p, d, rng.uniform(0.24, 0.38))


UPLIGHT = (1.0, 0.7, 0.42)               # warm, like the candles' glow but a touch whiter (linear RGB), baked


def rose_topiary(parts, rng, height=1.5, ball=0.27, mix=RED_BLUSH_WHITE, uplight=False):
    """A rose topiary, a wedding classic: a ball of red, blush and white roses on a slim stem tied with a satin bow, in a
    cream urn with gold bands. `uplight`: a small floor light in front of it washes the roses and the wall behind with
    warm light (by the screen, where the room is dim)."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    urn = [(0, 0), (0.13, 0), (0.135, 0.008), (0.13, 0.03), (0.09, 0.05), (0.075, 0.08), (0.09, 0.11), (0.16, 0.18), (0.2, 0.28),
           (0.215, 0.36), (0.225, 0.4), (0.232, 0.42), (0.22, 0.425), (0.205, 0.415), (0, 0.395)]
    lathe(c, urn, 40)
    for r, z0, z1 in ((0.1355, 0.01, 0.026), (0.2295, 0.4, 0.418)):
        lathe(g, [(r - 0.002, z0), (r, z0 + 0.001), (r, z1 - 0.001), (r - 0.002, z1)], 40)
    polar_grid(parts["soil"], 0.2, 0.4, 0.08, 24)
    middle = Vector((0, 0, height - ball))
    stem = [Vector((0.006 * math.sin(k), 0.006 * math.cos(1.3 * k), 0.39 + (middle.z - 0.39) * k / 6)) for k in range(7)]
    tube(parts["bark"], stem, [0.017 - 0.004 * k / 6 for k in range(7)], 8)
    knot = Vector((0, 0, middle.z - ball * 0.95 - 0.06))
    r = parts["ribbon_red"]
    for s in (-1, 1):                                                                    # a satin bow under the ball
        loop = [knot + Vector((s * (0.012 + 0.035 * (1 - math.cos(a))), 0.012 * math.sin(a), 0.018 * math.sin(a))) for a in (TAU * k / 12 for k in range(12))]
        tube(r, loop, 0.006, 6, closed=True, plane_normal=Vector((0, 1, -0.6)).normalized())
        tube(r, [knot, knot + Vector((s * 0.03, 0.02, -0.08)), knot + Vector((s * 0.05, 0.03, -0.17))], 0.005, 4)
    lathe(r, [(0, -0.015), (0.022, -0.012), (0.024, 0.0), (0.022, 0.012), (0, 0.015)], 12, at=knot)
    core = [(ball * 0.9 * math.sin(math.radians(a)), middle.z - ball * 0.9 * math.cos(math.radians(a))) for a in range(0, 181, 30)]
    lathe(parts["fig_leaf"], [(0, core[0][1])] + core[1:-1] + [(0, core[-1][1])], 16)     # dark foliage between the roses
    for d in fibonacci_cap(92, math.radians(180)):                                      # roses packed all over the ball
        d = (d + Vector((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04)))).normalized()
        bloom(parts[pick(rng, mix)], middle + d * ball * rng.uniform(0.9, 0.95), d, rng.uniform(1.4, 1.6), rng.uniform(0, TAU), 7, (4, 3))
    rose_leaves(parts, rng, middle, ball * 1.05, 14, (1.2, 2.4), (0.07, 0.1))
    if uplight:                                                                          # a black puck with a glowing lens
        at = Vector((0, -0.34, 0))
        lathe(parts["projector_black"], [(0, 0), (0.055, 0), (0.06, 0.012), (0.05, 0.026), (0, 0.026)], 20, at=at)
        lathe(parts["gold_metal"], [(0.034, 0.026), (0.04, 0.0262), (0.04, 0.03), (0.034, 0.0302)], 20, at=at)
        lathe(parts["lens_glow"], [(0, 0.0272), (0.034, 0.0272), (0, 0.0277)], 20, at=at)
        parts.lights.append(dict(kind="AREA", pos=at + Vector((0, 0, 0.04)), normal=Vector((0, 0.3, 1)).normalized(), size=(0.1, 0.1),
                                 colour=UPLIGHT, watts=8.0))
    return middle
