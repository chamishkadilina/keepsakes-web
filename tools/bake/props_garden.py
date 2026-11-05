"""The garden finale: from the screen room's garden door through an arch of climbing roses, lanterns along a path of
rose petals lead to a cream bench for two (on the garden seat markers) in front of a heart-shaped arch of roses,
framed by clipped hedges and rose bushes. Local coordinates: ground at z = 0, a piece's front faces +y."""
import math
from mathutils import Vector, noise
from props_geometry import TAU, rbox, cuts, lathe, tube, place, uv_layer, in_rect
from props_flowers import RED_BLUSH_WHITE, bloom, leaf, rose_leaves, pick, fibonacci_cap
from props_romance import heart_point
from props_atlas import HEDGE_RECT, uv_rect

TILE = 0.5                               # one tile of the boxwood texture every 50 cm


def leafy_uv(bm, verts):
    """Boxwood texture on a part, projected along each face's main axis, one tile every TILE metres. Each face keeps to
    the tile of its middle; the tile's outer 10 % is left as margin, so corners reaching a little into the next tile
    still sample inside the texture."""
    rect, layer = uv_rect(HEDGE_RECT, 2), uv_layer(bm)
    for f in {f for v in verts for f in v.link_faces}:
        f.normal_update()
        a = max(range(3), key=lambda i: abs(f.normal[i]))
        u, v = [i for i in range(3) if i != a]
        c = f.calc_center_median()
        tu, tv = math.floor(c[u] / TILE), math.floor(c[v] / TILE)
        for loop in f.loops:
            co = loop.vert.co
            loop[layer].uv = in_rect(rect, 0.1 + 0.8 * (co[u] / TILE - tu), 0.1 + 0.8 * (co[v] / TILE - tv))


def hedge(parts, rng, length, height=0.95, depth=0.6):
    """Clipped boxwood hedge along local x: one block with softly rounded edges, cut on the texture's tile lines."""
    bm = parts["decor_atlas"]
    verts = rbox(bm, (length, depth, height), 0.06, 2, at=(0, 0, height / 2))
    for axis, lo, hi in ((0, -length / 2, length / 2), (1, -depth / 2, depth / 2), (2, 0, height)):
        verts = cuts(bm, verts, axis, math.floor(lo / (TILE / 2)) * TILE / 2, hi, TILE / 2)
    leafy_uv(bm, verts)


def rose_bush(parts, rng, radius=0.42, mix=RED_BLUSH_WHITE):
    """Round rose bush: a leafy, gently lumpy ball resting on the ground, studded with roses."""
    bm = parts["decor_atlas"]
    h = radius * 1.7
    ball = lambda d: Vector((d.x * radius, d.y * radius, h / 2 * (1 + d.z)))            # its surface, towards d
    dome = lathe(bm, [(0, 0), (radius * 0.55, 0)] + [(radius * math.sin(a), h / 2 * (1 - math.cos(a)))
                                                    for a in (math.pi * (0.2 + 0.8 * k / 9) for k in range(9))] + [(0, h)], 24)
    seed = Vector((rng.uniform(0, 50), rng.uniform(0, 50), 0))
    for v in dome:
        if v.co.z > 0.02:
            v.co += Vector((v.co.x, v.co.y, v.co.z - h / 2)).normalized() * radius * 0.09 * noise.noise(v.co * 5 + seed)
    leafy_uv(bm, dome)
    for d in fibonacci_cap(40, math.radians(100)):
        d = (d + Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0))).normalized()
        bloom(parts[pick(rng, mix)], ball(d) - d * 0.012, (d + Vector((0, 0, 0.35))).normalized(), rng.uniform(0.95, 1.15),
              rng.uniform(0, TAU), petals=7, grid=(4, 3))
    rose_leaves(parts, rng, Vector((0, 0, h / 2)), radius * 1.2, 12, (1.3, 1.7), (0.07, 0.1))


def climbing_roses(parts, rng, path, spacing=0.05, size=1.0):
    """Climbing roses along a frame (an arch): blooms either side of it facing out front and back, leaves all along,
    a few buds; dense enough to hide the frame."""
    total = sum((b - a).length for a, b in zip(path, path[1:]))
    s = 0.0
    while s < total:
        d, k = s, 0
        while k < len(path) - 2 and d > (path[k + 1] - path[k]).length:
            d -= (path[k + 1] - path[k]).length
            k += 1
        seg = (path[k + 1] - path[k]).normalized()
        p = path[k] + seg * d
        across = seg.cross(Vector((0, 1, 0))).normalized()                 # in the frame's plane, across the path
        for side in (-1, 1):
            off = across * rng.uniform(-0.06, 0.06) + Vector((0, side * rng.uniform(0.02, 0.07), 0))
            axis = (Vector((0, side, 0)) + across * rng.uniform(-0.6, 0.6) + seg * rng.uniform(-0.3, 0.3)).normalized()
            bloom(parts[pick(rng, RED_BLUSH_WHITE)], p + off, axis, size * rng.uniform(0.75, 1.1), rng.uniform(0, TAU), petals=7, grid=(4, 3))
        for _ in range(2):
            out = (across * rng.choice((-1, 1)) + Vector((0, rng.uniform(-0.8, 0.8), 0)) + seg * rng.uniform(-0.5, 0.5)).normalized()
            length = rng.uniform(0.06, 0.09)
            leaf(parts["rose_leaf"], p + out * 0.02, out, length, length * 0.42, length * 0.2)
        s += spacing * rng.uniform(0.8, 1.2)


def rose_arch(parts, rng, width=1.6, height=2.45):
    """Garden arch of two slim gold hoops covered in climbing roses; you walk through it along local y."""
    g, r = parts["gold_metal"], width / 2
    path = [Vector((-r, 0, z)) for z in (0.0, 0.5, 1.0, height - r)]
    path += [Vector((-r * math.cos(a), 0, height - r + r * math.sin(a))) for a in (math.pi * k / 12 for k in range(1, 12))]
    path += [Vector((r, 0, z)) for z in (height - r, 1.0, 0.5, 0.0)]
    for dy in (-0.14, 0.14):
        tube(g, [p + Vector((0, dy, 0)) for p in path], 0.012, 8)
    for p in path[1:-1:2]:
        tube(g, [p + Vector((0, -0.14, 0)), p + Vector((0, 0.14, 0))], 0.008, 6)
    climbing = [Vector((-r, 0, 0.25))] + [p for p in path if p.z > 0.3] + [Vector((r, 0, 0.25))]
    climbing_roses(parts, rng, climbing, 0.06, 1.05)


def heart_arch(parts, rng, width=2.3):
    """A heart-shaped frame covered in roses: the garden's backdrop behind the bench. It stands in the xz plane facing
    +y, its tip on a cream foot, two slim gold legs behind it holding it up."""
    g, k = parts["gold_metal"], width / 2
    lift = 1.0625 * k + 0.16
    outline = [Vector((x * k, 0, y * k + lift)) for x, y in (heart_point(TAU * i / 48) for i in range(48))]
    tube(g, outline, 0.018, 10, closed=True, plane_normal=Vector((0, 1, 0)))
    lathe(parts["trim_cream"], [(0, 0), (0.2, 0), (0.2, 0.03), (0.08, 0.06), (0.05, 0.17), (0, 0.17)], 24)
    for s in (-1, 1):
        low = min((p for p in outline if p.x * s > 0.5 * k), key=lambda p: p.z)
        tube(g, [low, Vector((low.x * 1.15, -0.25, 0.0))], 0.012, 8)
    climbing_roses(parts, rng, outline + outline[:1], 0.055, 1.15)


def garden_bench(parts, rng, width=1.5):
    """A cream wooden bench for two with a slatted, slightly reclined back, gold legs and curved gold armrests."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    for i in range(5):                                                                   # seat slats
        cuts(c, rbox(c, (width, 0.08, 0.035), 0.008, 2, at=(0, -0.2 + 0.1 * i, 0.44)), 0, -width / 2, width / 2, 0.25)
    for i in range(4):                                                                   # back slats, leaning back
        slat = cuts(c, rbox(c, (width, 0.07, 0.03), 0.008, 2, at=(0, -0.26, 0.56 + 0.1 * i)), 0, -width / 2, width / 2, 0.25)
        place(c, slat, tilt=(14, (0, -0.24, 0.45)))
    for sx in (-1, 1):
        x = sx * (width / 2 - 0.06)
        for y in (-0.22, 0.2):
            tube(g, [Vector((x, y, 0.0)), Vector((x, y, 0.2)), Vector((x, y, 0.42))], 0.016, 10)
        tube(g, [Vector((x, 0.2, 0.42)), Vector((x, 0.2, 0.6)), Vector((x, 0.05, 0.66)), Vector((x, -0.22, 0.66)), Vector((x, -0.33, 0.62))], 0.014, 10)
        tube(g, [Vector((x, -0.22, 0.42)), Vector((x, -0.32, 0.95))], 0.014, 10)
