"""Roses and leaves for the arrangements: petals, blooms, domes of roses, leaves, vases of roses.
Rose colours are materials: rose_petal (deep red), rose_blush (blush pink), velvet_cream (white)."""
import bmesh, math
from mathutils import Vector, Matrix
from props_geometry import TAU, UP, track, lathe, tube, aim

def petal(bm, theta, s, z0, k=1.0, nu=5, nv=4):
    """One rose petal around the axis (cylindrical coordinates, so it cups around the bud). s = 0 innermost ... 1 outer:
    inner petals stand up and close over the centre, outer ones open wide and roll their edges back. k: size.
    One surface (drawn double-sided), facing out on the inner petals and up on the open ones (for the baked light)."""
    length = (0.04 + 0.012 * s) * k
    lean = [math.radians(a + (b - a) * s) for a, b in ((10, 68), (0, 12), (-20, 58))]  # from vertical: base, middle, tip
    width = (0.019 + 0.014 * s) * k
    reflex = 0.009 * s * s * k
    r, z, spine = (0.006 + 0.005 * s) * k, z0, []
    for j in range(nv):                                                                  # the petal's centre line
        t = j / (nv - 1)
        spine.append((r, z, t))
        a = lean[0] * (1 - t) ** 2 + lean[1] * 2 * t * (1 - t) + lean[2] * t * t            # out, up, then open (spoon-shaped)
        r += length / (nv - 1) * math.sin(a); z += length / (nv - 1) * math.cos(a)
    rows = []
    for r, z, t in spine:
        # outline: narrow at the base, widest at 60 %, then a round top
        half = width * (0.45 + 0.55 * t / 0.6 if t < 0.6 else math.sqrt(max(0.0, 1 - ((t - 0.6) / 0.4) ** 2)) * 0.88 + 0.12)
        wrap = min(2.3, half / max(r, 0.004))
        row = []
        for i in range(nu):
            u = (i / (nu - 1)) * 2 - 1
            rr = r + 0.0022 * k * (1 - u * u) * math.sin(math.pi * t) + reflex * max(0.0, t - 0.55) ** 2 / 0.2 * (0.35 + abs(u))
            zz = z - reflex * 0.4 * max(0.0, t - 0.7) ** 2 / 0.09 * abs(u)
            a = theta + u * wrap
            row.append(Vector((rr * math.cos(a), rr * math.sin(a), zz)))
        rows.append(row)
    vs = [[bm.verts.new(p) for p in row] for row in rows]
    for j in range(nv - 1):
        for i in range(nu - 1):
            quad = (vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i])
            bm.faces.new(quad[::-1] if s >= 0.55 else quad)


def leaf(bm, root, d, length, width, droop):
    """Pointed leaf from `root` along `d`, cupped and drooping by `droop` towards its tip: one surface facing up
    (drawn double-sided)."""
    side = Vector((-d.y, d.x, 0))
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    up = d.cross(side).normalized()
    rows = []
    for j in range(5):
        t = j / 4
        centre = root + d * (length * t) - up * (droop * t * t)
        half = width * math.sin(math.pi * min(1.0, 0.06 + 0.94 * t)) ** 0.8
        rows.append([bm.verts.new(centre + side * half * u + up * (0.18 * width * abs(u))) for u in (-1, 0, 1)])
    for j in range(4):
        for i in range(2):
            bm.faces.new((rows[j][i], rows[j + 1][i], rows[j + 1][i + 1], rows[j][i + 1]))


def bloom(bm, base, axis, k=1.0, spin=0.0, petals=10, grid=(5, 4)):
    """A rose head for arrangements: petals in a golden-angle spiral from a closed bud to open outer petals, standing
    on `base` and facing along `axis`. k = size (1 = about 10 cm across); grid = each petal's (across, along) vertices."""
    done = track(bm)
    for i in range(petals):
        s = i / (petals - 1)
        petal(bm, math.radians(137.5 * i), s, -0.006 * s * k, k, *grid)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(base) @ aim(axis.normalized(), spin), verts=done())


def fibonacci_cap(n, max_polar):
    """n evenly spread directions over a sphere cap from the top down to `max_polar` (radians)."""
    golden, low = math.pi * (3 - math.sqrt(5)), math.cos(max_polar)
    out = []
    for i in range(n):
        cz = 1 - (i + 0.5) / n * (1 - low)
        sz = math.sqrt(max(0.0, 1 - cz * cz))
        out.append(Vector((sz * math.cos(i * golden), sz * math.sin(i * golden), cz)))
    return out


RED_BLUSH = (("rose_petal", 0.72), ("rose_blush", 0.28))
RED_BLUSH_WHITE = (("rose_petal", 0.5), ("rose_blush", 0.28), ("velvet_cream", 0.22))


def pick(rng, mix):
    """A rose colour (material) from (material, weight) pairs."""
    r = rng.random() * sum(w for _, w in mix)
    for name, w in mix:
        r -= w
        if r <= 0:
            return name
    return mix[-1][0]


def roses(parts, rng, centre, radius, count, max_polar, k=1.0, mix=RED_BLUSH, lift=0.35, petals=10, grid=(5, 4)):
    """A dome of roses (red and blush, or `mix`) over a sphere cap around `centre`."""
    for d in fibonacci_cap(count, max_polar):
        d = (d + Vector((rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), 0))).normalized()
        axis = (d + UP * lift).normalized()
        mat = pick(rng, mix)
        bloom(parts[mat], centre + d * radius * rng.uniform(0.97, 1.03) - axis * 0.012 * k, axis,
              k * rng.uniform(0.9, 1.08), rng.uniform(0, TAU), petals, grid)


def rose_leaves(parts, rng, centre, radius, count, polar=(1.7, 2.0), size=(0.08, 0.11)):
    """Leaves around the base of a dome of roses, reaching out and down."""
    for i in range(count):
        a = TAU * (i + rng.uniform(-0.3, 0.3)) / count
        p = rng.uniform(*polar)
        d = Vector((math.sin(p) * math.cos(a), math.sin(p) * math.sin(a), math.cos(p)))
        length = rng.uniform(*size)
        leaf(parts["rose_leaf"], centre + d * radius * 0.82, (d + Vector((0, 0, 0.25))).normalized(),
             length, length * 0.42, length * 0.25)


def vase_of_roses(parts, rng, at, count=7, height=0.2):
    """A cream vase with a gold lip holding roses: one to three on short stems, or a full posy with leaves."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    k = height / 0.2
    slim = count <= 3
    if slim:                                                                             # bud vase
        lip, profile = 0.027, ((0, 0), (0.03, 0), (0.033, 0.004), (0.036, 0.04), (0.035, 0.1), (0.028, 0.15), (0.022, 0.18),
                               (0.024, 0.196), (0.027, 0.2), (0.021, 0.2), (0.017, 0.19), (0, 0.185))
    else:                                                                                # round vase
        lip, profile = 0.037, ((0, 0), (0.042, 0), (0.046, 0.004), (0.058, 0.04), (0.062, 0.085), (0.055, 0.125), (0.036, 0.16),
                               (0.03, 0.18), (0.033, 0.195), (0.037, 0.2), (0.03, 0.2), (0.024, 0.19), (0, 0.185))
    seg = 12 if slim else 16
    lathe(c, [(r * k, z * k) for r, z in profile], seg, at=at)
    lip *= k
    lathe(g, [(lip - 0.0008, 0.187 * k), (lip + 0.0008, 0.189 * k), (lip + 0.0008, 0.2 * k), (lip - 0.0008, 0.2015 * k)], seg, at=at)
    neck = Vector(at) + Vector((0, 0, 0.198 * k))
    if slim:
        for i in range(count):
            a = TAU * i / count + rng.uniform(-0.4, 0.4)
            lean = 0.0 if count == 1 else 0.28
            d = Vector((lean * math.cos(a), lean * math.sin(a), 1)).normalized()
            head = neck + d * rng.uniform(0.07, 0.11) * k
            tube(parts["rose_leaf"], [neck, neck.lerp(head, 0.5) + Vector((0.004, 0, 0)), head], 0.0028, 5)
            bloom(parts[pick(rng, RED_BLUSH)], head, d, 0.85 * k, rng.uniform(0, TAU), 8, (4, 4))
            leaf(parts["rose_leaf"], neck.lerp(head, 0.4), (d + Vector((math.cos(a), math.sin(a), -0.2))).normalized(), 0.05 * k, 0.022 * k, 0.008)
    else:
        radius = (0.03 + 0.016 * math.sqrt(count)) * k
        centre = neck + Vector((0, 0, radius * 0.25))
        roses(parts, rng, centre, radius, count, math.radians(80), 0.85 * k, lift=0.25, petals=8, grid=(4, 4))
        rose_leaves(parts, rng, centre, radius, max(5, count // 2), (1.55, 1.85), (0.06 * k, 0.08 * k))


def flower_urn(parts, rng, height=0.95):
    """A tall cream pedestal with gold bands holding an urn of roses that spill over its rim: a dome of red, blush and
    white roses with cascades of roses and leaves trailing down its sides, as at a wedding."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    column = [(0, 0), (0.2, 0), (0.2, 0.05), (0.17, 0.07), (0.15, 0.1), (0.125, 0.14)] + [(0.115, 0.14 + (height - 0.3) * k / 6) for k in range(1, 7)]
    column += [(0.125, height - 0.12), (0.15, height - 0.08), (0.18, height - 0.04), (0.18, height), (0, height)]
    lathe(c, column, 40)
    for r, z0, z1 in ((0.2005, 0.012, 0.03), (0.1805, height - 0.03, height - 0.012)):
        lathe(g, [(r - 0.002, z0), (r, z0 + 0.001), (r, z1 - 0.001), (r - 0.002, z1)], 40)
    urn = [(0, 0), (0.08, 0), (0.08, 0.02), (0.05, 0.04), (0.045, 0.07), (0.07, 0.1), (0.13, 0.15), (0.16, 0.2), (0.17, 0.24),
           (0.18, 0.255), (0.17, 0.262), (0, 0.24)]
    lathe(c, urn, 40, at=(0, 0, height))
    lathe(g, [(0.1795, height + 0.244), (0.1825, height + 0.247), (0.1825, height + 0.256), (0.1795, height + 0.259)], 40)
    rim = height + 0.255
    centre = Vector((0, 0, rim + 0.02))
    roses(parts, rng, centre, 0.21, 34, math.radians(100), 1.3, RED_BLUSH_WHITE, lift=0.3, petals=7, grid=(4, 3))
    rose_leaves(parts, rng, centre, 0.21, 12, (1.5, 1.9), (0.08, 0.11))
    for i in range(5):                                                                   # cascades over the rim
        a = TAU * i / 5 + rng.uniform(-0.3, 0.3)
        out = Vector((math.cos(a), math.sin(a), 0))
        for j in range(7):
            t = j / 6
            p = Vector((0, 0, rim)) + out * (0.2 + 0.06 * t) - Vector((0, 0, 0.42 * t * t + 0.05 * t))
            p += Vector((rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0))
            if j % 2 == 0:
                bloom(parts[pick(rng, RED_BLUSH_WHITE)], p, (out + Vector((0, 0, 0.3 - 0.6 * t))).normalized(), 1.15 - 0.4 * t,
                      rng.uniform(0, TAU), 7, (4, 3))
            leaf(parts["rose_leaf"], p, (out * 0.6 + Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), -0.6))).normalized(),
                 0.08 - 0.02 * t, 0.034, 0.012)
    return centre

