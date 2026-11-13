"""The bench's soft things, made in code (garden_wood.py builds the bench): a long seat cushion, two plump pillows leaning
on its back, and a knitted throw folded over its right arm. One object, `bench_cushions`, in the bench's own frame:
local -y is where the sitters look; the back leans BENCH_TILT degrees, pivoting at y 0.19, z 0.42 (garden_wood.BENCH)."""
import bpy, bmesh, math
from mathutils import Matrix, Vector

LINEN, ROSE = (0.62, 0.55, 0.46), (0.52, 0.27, 0.29)    # oatmeal linen, dusty rose
BENCH_TILT, SEAT, ARM_X = 14.0, 0.45, 0.70               # degrees, m: as garden_wood.BENCH
CUSHION = dict(size=(1.3, 0.44, 0.07), puff=0.45)        # m, how much thinner it gets at its edges
PILLOW = dict(size=(0.4, 0.14, 0.38), puff=0.85, at=0.43, lean=10.0, turn=8.0)   # m; x of each; degrees more lean, turn
THROW = dict(width=(-0.25, 0.2), sag=0.012, steps=14)    # m along the arm, its folds (m), rows across


def plump(bm, size, thin, puff, matrix, index):
    """A soft box: thickest in the middle, pinched thin at its seams, its sides a little drawn in."""
    piece = bmesh.new(); bmesh.ops.create_cube(piece, size=2.0)
    bmesh.ops.subdivide_edges(piece, edges=piece.edges[:], cuts=7, use_grid_fill=True)
    a, b = [i for i in range(3) if i != thin]
    for v in piece.verts:
        n = v.co.copy()
        v.co[thin] = n[thin] * (1 - puff * abs(n[a]) ** 3) * (1 - puff * abs(n[b]) ** 3)
        v.co[a] = n[a] * (1 - 0.06 * n[b] ** 2); v.co[b] = n[b] * (1 - 0.06 * n[a] ** 2)
        v.co = Vector(tuple(v.co[i] * size[i] / 2 for i in range(3)))
    for f in piece.faces:
        f.smooth = True; f.material_index = index
    bmesh.ops.transform(piece, matrix=matrix, verts=piece.verts)
    me = bpy.data.meshes.new("_soft"); piece.to_mesh(me); piece.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def throw(bm, index):
    """A throw over the right arm: over its top, hanging a little inside onto the cushion and longer outside, in folds."""
    profile = [(-0.08, 0.53), (-0.075, 0.6), (-0.055, 0.665), (0, 0.69), (0.055, 0.665), (0.08, 0.6), (0.095, 0.45), (0.1, 0.3)]
    w, rows = THROW["width"], THROW["steps"]
    grid = []
    for r in range(rows + 1):
        y = w[0] + (w[1] - w[0]) * r / rows
        grid.append([bm.verts.new((ARM_X + x + THROW["sag"] * math.sin(y * 24 + k) * (k / len(profile)), y, z))
                     for k, (x, z) in enumerate(profile)])
    for r in range(rows):
        for k in range(len(profile) - 1):
            f = bm.faces.new((grid[r][k], grid[r][k + 1], grid[r + 1][k + 1], grid[r + 1][k]))
            f.smooth = True; f.material_index = index


def build(coll):
    bm = bmesh.new()
    c = CUSHION
    plump(bm, c["size"], 2, c["puff"], Matrix.Translation((0, -0.02, SEAT + c["size"][2] / 2)), 0)
    back = Matrix.Translation((0, 0.19, 0.42)) @ Matrix.Rotation(math.radians(-BENCH_TILT), 4, "X")
    p = PILLOW
    for side, index in ((-1, 1), (1, 0)):                     # a rose pillow on the left, a linen one on the right
        tilt = Matrix.Rotation(math.radians(-p["lean"]), 4, "X") @ Matrix.Rotation(math.radians(side * p["turn"]), 4, "Z")
        plump(bm, p["size"], 1, p["puff"], back @ Matrix.Translation((side * p["at"], -0.08, 0.27)) @ tilt, index)
    throw(bm, 1)
    me = bpy.data.meshes.new("bench_cushions"); bm.to_mesh(me); bm.free()
    for name, colour in (("garden_cushion_linen", LINEN), ("garden_cushion_rose", ROSE)):
        m = bpy.data.materials.new(name); m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*colour, 1)
        me.materials.append(m)
    ob = bpy.data.objects.new("bench_cushions", me); ob["garden_asset"] = "garden_bench"; coll.objects.link(ob)
