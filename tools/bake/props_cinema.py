"""The screen room's cinema: a projector hanging from the ceiling (the web draws its beam to the screen), the screen in
its black-and-gold frame above a little velvet stage, a "Now Showing" poster in a lightbox, popcorn and drinks, and deep
red velvet curtains (at the screen, the garden door and the foyer's door into the story), tied back with gold ropes
under a velvet pelmet. Local coordinates: floor at
z = 0; the curtains' wall is local y = 0 (the room is +y) and the door is centred on local x = 0."""
import bmesh, math
from mathutils import Vector, Matrix
from props_geometry import TAU, rbox, cuts, lathe, tube, track, set_uv


def projector(parts, rng, ceiling=4.32, drop=0.48, aim=(0.0, 8.25, -1.68), scale=1.0):
    """Ceiling-mounted cinema projector: a ceiling plate, a drop pole and a black cradle holding a satin-white body with
    black vents and a big black lens with a gold ring, tilted to look along `aim` (towards the screen); `scale` sizes the body. The lens is marked for the
    web (projector_lens)."""
    k = parts["projector_black"]
    lathe(k, [(0, ceiling), (0.09, ceiling), (0.09, ceiling - 0.012), (0.03, ceiling - 0.02), (0, ceiling - 0.02)], 24)
    lathe(k, [(0, ceiling - drop + 0.06 * scale), (0.022, ceiling - drop + 0.06 * scale), (0.022, ceiling - 0.02), (0, ceiling - 0.02)], 12)
    d = Vector(aim).normalized()
    pitch = math.atan2(d.z, math.hypot(d.x, d.y))
    yaw = math.atan2(-d.x, d.y)
    turn = Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "X")
    hub = Vector((0, 0, ceiling - drop))
    done = {n: track(parts[n]) for n in ("projector_black", "projector_white", "gold_metal", "lens_glow", "glass")}
    rbox(parts["projector_white"], (0.44, 0.38, 0.15), 0.025, 3, at=(0, 0, 0))         # the body (local: lens along +y)
    for i in range(7):                                                                   # vents on its sides
        for s in (-1, 1):
            rbox(k, (0.006, 0.16, 0.012), 0.002, 1, at=(s * 0.221, -0.03, -0.04 + 0.014 * i))
    rbox(k, (0.3, 0.06, 0.03), 0.01, 2, at=(0, 0.0, 0.088))                              # cradle bar on top
    barrel = [(0, 0.19), (0.07, 0.19), (0.072, 0.2), (0.068, 0.25), (0.074, 0.262), (0.074, 0.28), (0.064, 0.282), (0, 0.276)]
    lathe(k, [(r, z) for r, z in barrel], 32, at=(0.08, 0, 0))
    lathe(parts["gold_metal"], [(0.0745, 0.262), (0.0765, 0.264), (0.0765, 0.276), (0.0745, 0.278)], 32, at=(0.08, 0, 0))
    lathe(parts["lens_glow"], [(0, 0.281), (0.058, 0.281), (0, 0.2815)], 32, at=(0.08, 0, 0))
    for n, fn in done.items():                                                           # the lathes run along z: turn them to +y
        verts = fn()
        lens = [v for v in verts if math.hypot(v.co.x - 0.08, v.co.y) < 0.08 and v.co.z > 0.185]
        if lens:
            bmesh_rotate(lens, Matrix.Translation((0.08, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "X") @ Matrix.Translation((-0.08, 0, 0)))
        bmesh_rotate(verts, Matrix.Translation(hub) @ turn @ Matrix.Scale(scale, 4))
    lens = Matrix.Translation(hub) @ turn @ (Vector((0.08, 0.282, 0)) * scale)
    parts.markers["projector_lens"] = (lens, {"aim": [round(c, 4) for c in d]})
    return lens


def bmesh_rotate(verts, matrix):
    for v in verts:
        v.co = matrix @ v.co


def curtain_panel(parts, rng, side=1, opening=2.95, rod=3.62, tie=1.15, beyond=0.45, gather=10, top_inner=0.03, hook="wall"):
    """One velvet curtain at a door or the screen, hanging from under the pelmet to the floor and tied back to the side
    with a gold rope and tassel (side = -1: the panel on local -x, +1: on +x). Above the tie its inner edge sweeps up to
    `top_inner` at the rod (0.03: it meets the other panel in the middle; near the side: the two frame a square opening,
    as at the screen and the foyer's door); below the tie it falls straight, flaring a little. Deep pleats where it is
    gathered. The tie-back's hook is on the wall beside the opening (hook="wall") or on the side wall the panel's outer
    edge meets (hook="side": a door in a room's corner)."""
    v, g = parts["curtain_velvet"], parts["gold_metal"]
    half = opening / 2
    outer, tie_x = half + beyond, half - 0.12
    rows, cols = 26, gather * 4

    def inner(z):                                                                        # the panel's inner edge
        if z >= tie:
            return tie_x + (top_inner - tie_x) * ((z - tie) / (rod - tie)) ** 1.3       # sweeps up towards the middle
        return tie_x - 0.22 * ((tie - z) / tie) ** 1.4

    grid = []
    for j in range(rows + 1):
        z = 0.012 + (rod - 0.012) * j / rows
        x0 = inner(z)
        width = outer - x0
        deep = 0.035 + 0.1 * max(0.0, 1 - width / (outer - 0.03))                       # deeper folds where it is gathered
        pinch = math.exp(-((z - tie) / 0.12) ** 2)                                       # pulled in by the tie
        row = []
        for i in range(cols + 1):
            u = i / cols
            x = x0 + width * u
            y = 0.11 + deep * (0.5 - 0.5 * math.cos(TAU * gather * u)) * (1 - 0.6 * pinch) - 0.04 * pinch * (1 - u)
            row.append(v.verts.new((side * x, y, z)))
        grid.append(row)
    for j in range(rows):
        for i in range(cols):
            quad = (grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])
            f = v.faces.new(quad if side > 0 else quad[::-1])
            f.normal_update()
            if f.normal.y < 0:
                f.normal_flip()
    c = Vector((side * (tie_x + 0.18), 0.13, tie))                                       # the gold tie-back rope and tassel
    loop = [c + Vector((0.2 * math.cos(a), 0.11 * math.sin(a), 0.025 * math.sin(2 * a))) for a in (TAU * k / 24 for k in range(24))]
    tube(g, loop, 0.012, 8, closed=True, plane_normal=Vector((0, 0, 1)))
    if hook == "side":                                                                   # on the side wall, facing the opening
        at, off, turn = Vector((side * outer, 0.13, tie)), Vector((-side, 0, 0)), Matrix.Rotation(-side * math.pi / 2, 4, "Y")
    else:                                                                                # on the wall, facing the room
        at, off, turn = Vector((side * (outer + 0.02), 0.0, tie)), Vector((0, 1, 0)), Matrix.Rotation(-math.pi / 2, 4, "X")
    tube(g, [c + Vector((side * 0.2, 0, 0)), at + off * 0.04, at + off * 0.012], 0.01, 8)
    done = track(g)
    lathe(g, [(0, 0), (0.035, 0.0), (0.03, 0.012), (0, 0.016)], 16)                      # the hook's rosette
    bmesh_rotate(done(), Matrix.Translation(at) @ turn)
    tassel = [(0, -0.155), (0.02, -0.15), (0.03, -0.12), (0.022, -0.04), (0.012, -0.01), (0, 0)]
    lathe(g, tassel, 16, at=c + Vector((side * -0.05, 0.12, -0.02)))


def pelmet(parts, rng, width=4.0, height=0.4, depth=0.24, top=4.0):
    """Velvet-covered pelmet across the top of a door or the screen, hiding the curtain rod, with a gold braid along it."""
    v, g = parts["curtain_velvet"], parts["gold_metal"]
    cuts(v, rbox(v, (width, depth, height), 0.03, 3, at=(0, depth / 2, top - height / 2)), 0, -width / 2, width / 2, 0.4)
    for z in (top - height + 0.03, top - height + 0.07):
        rbox(g, (width + 0.004, 0.012, 0.012), 0.004, 1, at=(0, depth + 0.004, z))


def cinema_screen(parts, rng, width=4.8, height=2.7, middle=2.1, stage=(5.2, 0.7, 0.3)):
    """The screen at the front of the little cinema, so their video never plays on a bare wall: a matte white screen
    (screen_surface sits 1.5 cm in front of it: draw the video there) in a deep black masking frame with a fine gold
    edge, above a low stage skirted in wine-red velvet with a gold trim. The wall is local y = 0, the room +y."""
    k, g, v = parts["projector_black"], parts["gold_metal"], parts["curtain_velvet"]
    rbox(parts["screen_white"], (width + 0.02, 0.006, height + 0.02), 0.002, 1, at=(0, 0.012, middle))
    b = 0.14                                                                             # the black border round it
    w2, h2 = width / 2 + 0.01, height / 2 + 0.01
    for sx, sz, w, h in ((0, h2 + b / 2, width + 0.02 + 2 * b, b), (0, -h2 - b / 2, width + 0.02 + 2 * b, b),
                         (-w2 - b / 2, 0, b, height + 0.02), (w2 + b / 2, 0, b, height + 0.02)):
        cuts(k, rbox(k, (w, 0.07, h), 0.01, 2, at=(sx, 0.035, middle + sz)), 0 if w > h else 2, -4, 4, 0.5)
    W, H = w2 + b, h2 + b                                                                # a fine gold edge round the frame
    for sx, sz, w, h in ((0, H, 2 * W + 0.03, 0.03), (0, -H, 2 * W + 0.03, 0.03), (-W, 0, 0.03, 2 * H), (W, 0, 0.03, 2 * H)):
        cuts(g, rbox(g, (w, 0.08, h), 0.008, 2, at=(sx, 0.04, middle + sz)), 0 if w > h else 2, -4, 4, 0.5)
    sw, sd, sh = stage
    cuts(v, rbox(v, (sw, sd, sh), 0.02, 2, at=(0, sd / 2, sh / 2)), 0, -sw / 2, sw / 2, 0.3)
    cuts(v, [x for x in v.verts if x.co.z > sh - 0.03 and abs(x.co.x) < sw / 2], 1, 0, sd, 0.2)  # (the top, front to back)
    rbox(g, (sw + 0.01, 0.025, 0.02), 0.006, 1, at=(0, sd - 0.005, sh - 0.012))       # gold trim along the stage's edge


def poster(parts, rng, width=0.9, height=1.33, bottom=0.8, depth=0.06):
    """A "Now Showing" film poster in a slim lightbox on the wall: a black case with a fine gold frame, its face lit from
    within (poster_face: the web draws their poster on it; UVs across it, read from the front). Its soft glow on the
    floor in front is baked. The wall is local y = 0, the room +y."""
    k, g, f = parts["projector_black"], parts["gold_metal"], 0.03
    cuts(k, rbox(k, (width + 2 * f, depth, height + 2 * f), 0.006, 2, at=(0, depth / 2, bottom + height / 2)), 2,
         bottom, bottom + height, 0.3)
    W, H = width / 2 + f / 2, height / 2 + f / 2                                         # the gold frame round its face
    for sx, sz, w, h in ((0, H, width + 2 * f, f), (0, -H, width + 2 * f, f), (-W, 0, f, height), (W, 0, f, height)):
        rbox(g, (w, 0.012, h), 0.004, 1, at=(sx, depth + 0.002, bottom + height / 2 + sz))
    b = parts["poster_face"]
    x0, x1, z0, z1 = -width / 2, width / 2, bottom, bottom + height
    vs = [[b.verts.new((x0 + width * i / 6, depth + 0.001, z0 + height * j / 9)) for i in range(7)] for j in range(10)]
    face = [b.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i])) for j in range(9) for i in range(6)]
    for fc in face:
        fc.normal_update()
        if fc.normal.y < 0:
            fc.normal_flip()
    set_uv(b, face, lambda co: ((x1 - co.x) / width, (co.z - z0) / height))             # read from the front: u runs to -x
    parts.lights.append(dict(kind="AREA", pos=Vector((0, depth + 0.1, (z0 + z1) / 2)), normal=Vector((0, 1, 0)),
                             size=(width, height), colour=(1.0, 0.9, 0.78), watts=6.0))


def striped(parts, ring_lo, ring_hi, every=1):
    """Faces between two rings of verts (same count, going round), in red and cream stripes `every` faces wide."""
    n = len(ring_lo)
    for k in range(n):
        bm = parts["ribbon_red" if (k // every) % 2 == 0 else "trim_cream"]
        a, b = ring_lo[k].co, ring_lo[(k + 1) % n].co
        c, d = ring_hi[(k + 1) % n].co, ring_hi[k].co
        bm.faces.new([bm.verts.new(p) for p in (a, b, c, d)])


def popcorn_box(parts, rng, at=(0, 0, 0)):
    """A red-and-white striped popcorn box heaped with popcorn."""
    at = Vector(at)
    def square(half, z, n=6):                                                            # points round a square, n per side
        pts = []
        for sx, sy, dx, dy in ((-1, -1, 1, 0), (1, -1, 0, 1), (1, 1, -1, 0), (-1, 1, 0, -1)):
            pts += [Vector((half * (sx + 2 * dx * t / n), half * (sy + 2 * dy * t / n), z)) + at for t in range(n)]
        return pts
    tmp = bmesh.new()
    lo = [tmp.verts.new(p) for p in square(0.045, 0.002)]
    hi = [tmp.verts.new(p) for p in square(0.065, 0.17)]
    striped(parts, lo, hi)
    tmp.free()
    c = parts["trim_cream"]
    c.faces.new([c.verts.new(p) for p in reversed(square(0.045, 0.002))])                # its bottom
    pop = parts["popcorn"]
    for i in range(46):                                                                  # heaped above the rim
        u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
        top = 0.17 + 0.05 * (1 - max(abs(u), abs(v)) ** 2) + rng.uniform(-0.008, 0.008)
        p = at + Vector((0.058 * u, 0.058 * v, top))
        for vert in bmesh.ops.create_icosphere(pop, subdivisions=1, radius=rng.uniform(0.011, 0.016))["verts"]:
            vert.co = vert.co * Vector((1, 1, 0.8)) + p


def drink_cup(parts, rng, at=(0, 0, 0)):
    """A striped cinema cup with a domed lid and a straw."""
    at, seg = Vector(at), 16
    ring = lambda r, z: [Vector((r * math.cos(TAU * k / seg), r * math.sin(TAU * k / seg), z)) + at for k in range(seg)]
    tmp = bmesh.new()
    striped(parts, [tmp.verts.new(p) for p in ring(0.032, 0.002)], [tmp.verts.new(p) for p in ring(0.045, 0.16)])
    tmp.free()
    c = parts["trim_cream"]
    c.faces.new([c.verts.new(p) for p in reversed(ring(0.032, 0.002))])
    lathe(c, [(0.047, 0.158), (0.047, 0.166), (0.03, 0.18), (0, 0.184)], seg, at=at)       # the lid
    tube(parts["ribbon_red"], [at + Vector((0.008, 0, 0.15)), at + Vector((0.02, 0.004, 0.26))], 0.004, 8)   # the straw
