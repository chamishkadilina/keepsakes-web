"""The screen room's cinema: a projector hanging from the ceiling (the web draws its beam to the screen), the screen in
its black-and-gold frame above a little velvet stage, and deep red velvet curtains (at the screen and the garden door),
tied back with gold ropes under a velvet pelmet. Local coordinates: floor at
z = 0; the curtains' wall is local y = 0 (the room is +y) and the door is centred on local x = 0."""
import math
from mathutils import Vector, Matrix
from props_geometry import TAU, rbox, cuts, lathe, tube, track


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


def curtain_panel(parts, rng, side=1, opening=2.95, rod=3.62, tie=1.15, beyond=0.45, gather=10, top_inner=0.03, fold=0.035):
    """One velvet curtain at a door or the screen, hanging from under the pelmet to the floor and tied back to the side
    with a gold rope and tassel (side = -1: the panel on local -x, +1: on +x). Above the tie its inner edge sweeps up to
    `top_inner` at the rod (0.03: it meets the other panel in the middle; less than 0: a single swag across the whole
    opening; near the side: it frames the screen); below the tie it falls straight, flaring a little. Pleats `fold`
    deep where it hangs open, deeper where it is gathered."""
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
        deep = fold + 0.1 * max(0.0, 1 - width / (outer - 0.03))                        # deeper folds where it is gathered
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
    hook = Vector((side * (outer + 0.02), 0.0, tie))
    tube(g, [c + Vector((side * 0.2, 0, 0)), hook + Vector((0, 0.04, 0)), hook + Vector((0, 0.012, 0))], 0.01, 8)
    done = track(g)
    lathe(g, [(0, 0), (0.035, 0.0), (0.03, 0.012), (0, 0.016)], 16)                      # wall rosette, facing the room
    bmesh_rotate(done(), Matrix.Translation(hook) @ Matrix.Rotation(-math.pi / 2, 4, "X"))
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
