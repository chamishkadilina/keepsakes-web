"""The way in, outside the foyer's south door (entrance.py builds the clearing round it): an ivory doorway with gold
corner blocks under a wide frieze with a gold line, a little gold heart and a cornice, deep red double doors opened
right back against the wall, and a red carpet with cream edges from the clearing into the foyer. Each piece is
built at the wall's outer face (local y = 0, outside towards +y, the 0.4 m wall behind) and placed by props.LAYOUT.
The doorway's sides and doors are pieces of their own, so each gets its own footprint and the way in stays clear."""
import bmesh, math
from mathutils import Matrix, Vector
from props_geometry import rbox, cuts, grid, track, tube
from props_romance import puffy_heart

OPENING, HEAD = 3.0, 3.4             # m: the doorway's width, and the height the doors close under
LEAF = OPENING / 2 - 0.02            # m: each door's width
WALL = 0.4                           # m: the outer wall's thickness


def portal(parts, rng, width=OPENING, head=HEAD):
    """Above the doors: a lintel through the wall closing the opening, the architrave's head with a gold keystone and
    gold corner blocks, and a frieze as wide as the open doors, with a gold line and a little gold heart, under a cornice."""
    c, g = parts["trim_cream"], parts["gold_metal"]
    rbox(c, (width + 0.02, WALL, 4.0 - head), 0.01, 1, at=(0, -WALL / 2, (4.0 + head) / 2))
    rbox(c, (width + 0.32, 0.08, 0.16), 0.01, 2, at=(0, 0.04, head + 0.08))
    rbox(g, (0.2, 0.1, 0.26), 0.012, 2, at=(0, 0.05, head + 0.11))
    for s in (-1, 1):
        rbox(g, (0.18, 0.1, 0.18), 0.012, 2, at=(s * (width / 2 + 0.08), 0.05, head + 0.08))
    span = 2 * (width / 2 + LEAF + 0.3)                          # over the doors folded back
    cuts(c, rbox(c, (span, 0.12, 0.42), 0.01, 2, at=(0, 0.06, head + 0.37)), 0, -span / 2, span / 2, 0.4)
    rbox(g, (span - 0.1, 0.014, 0.014), 0.004, 1, at=(0, 0.125, head + 0.2))
    cuts(c, rbox(c, (span + 0.3, 0.26, 0.1), 0.02, 2, at=(0, 0.13, 3.95)), 0, -span / 2 - 0.2, span / 2 + 0.2, 0.4)
    done = track(g)
    puffy_heart(g, 0.26, 0.05)
    bmesh.ops.translate(g, vec=(0, 0.14, head + 0.4), verts=done())


def jamb(parts, rng, side=1, width=OPENING, head=HEAD):
    """One side of the doorway: an ivory architrave round the opening on a little plinth."""
    c = parts["trim_cream"]
    x = side * (width / 2 + 0.08)
    cuts(c, rbox(c, (0.16, 0.08, head), 0.01, 2, at=(x, 0.04, head / 2)), 2, 0, head, 0.4)
    rbox(c, (0.18, 0.1, 0.3), 0.012, 2, at=(x, 0.05, 0.15))


def door_leaf(parts, rng, side=1, width=OPENING, head=HEAD):
    """One of the double doors, deep red with two raised panels in fine gold beading and a gold handle on each face,
    hinged beside the architrave (side = -1 or +1) and opened right back, flat against the wall."""
    v, g = parts["curtain_velvet"], parts["gold_metal"]
    done = {bm: track(bm) for bm in (v, g)}
    w = LEAF
    mid = -side * w / 2                                          # the leaf's middle, from its hinge
    cuts(v, rbox(v, (w, 0.06, head - 0.02), 0.008, 2, at=(mid, 0.03, head / 2)), 2, 0, head, 0.4)
    for face in (1, -1):                                         # raised panels on both faces, each in a fine gold frame
        for z0, z1 in ((0.25, 1.3), (1.5, head - 0.25)):
            rbox(v, (w - 0.3, 0.025, z1 - z0), 0.01, 2, at=(mid, 0.03 + face * 0.04, (z0 + z1) / 2))
            for dx, dz, sx, sz in ((0, z0 - 0.02, w - 0.24, 0.014), (0, z1 + 0.02, w - 0.24, 0.014),
                                   (-(w - 0.24) / 2, (z0 + z1) / 2, 0.014, z1 - z0 + 0.04), ((w - 0.24) / 2, (z0 + z1) / 2, 0.014, z1 - z0 + 0.04)):
                rbox(g, (sx, 0.012, sz), 0.004, 1, at=(mid + dx, 0.03 + face * 0.036, dz))
    knob = -side * (w - 0.12)
    for face in (1, -1):                                         # a gold pull handle on each face
        y0, y1 = 0.03 + face * 0.04, 0.03 + face * 0.09
        tube(g, [Vector((knob, y0, 1.05)), Vector((knob, y1, 1.05)), Vector((knob, y1, 1.35)), Vector((knob, y0, 1.35))], 0.012, 8)
    turn = Matrix.Translation((side * (width / 2 + 0.16), 0.14, 0)) @ Matrix.Rotation(math.pi, 4, "Z")   # its back 8 cm off the wall
    for bm, verts in done.items():
        bmesh.ops.transform(bm, matrix=turn, verts=verts())


def runner(parts, rng, length=10.0, width=1.4, edge=0.08, thickness=0.01):
    """A red carpet along local +y, from its start at the origin: deep red with cream edges. You walk over it."""
    v, c = parts["curtain_velvet"], parts["velvet_cream"]
    grid(v, -width / 2 + edge, width / 2 - edge, 0, length, thickness, 0.35)
    for x0 in (-width / 2, width / 2 - edge):
        grid(c, x0, x0 + edge, 0, length, thickness, 0.35)
