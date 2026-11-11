"""Her source made ready: upright, facing -Y (Blender front), 1.64 m, and a light copy for the web that keeps more of
her face and hands. python -I prep.py -- src.blend out.blend body_ratio,detail_ratio"""
import sys, math, time
import bpy
import numpy as np
from mathutils import Matrix

src, dst, ratio = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
scene = bpy.context.scene
for o in list(bpy.data.objects):
    if o.name != "WhiteWeddingDressGirl":
        bpy.data.objects.remove(o, do_unlink=True)
hi = bpy.data.objects["WhiteWeddingDressGirl"]
hi.name = "High"
hi.data.transform(hi.matrix_world)
hi.matrix_world = Matrix.Identity(4)
hi.data.transform(Matrix.Rotation(-math.pi / 2, 4, "Z"))           # she faced +X
co = np.empty(len(hi.data.vertices) * 3)
hi.data.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
k = 1.64 / (co[:, 2].max() - co[:, 2].min())
hi.data.transform(Matrix.Scale(k, 4))
hi.data.transform(Matrix.Translation((0, 0, -co[:, 2].min() * k)))
low = hi.copy()
low.data = hi.data.copy()
low.name = low.data.name = "Girl"
scene.collection.objects.link(low)
# simplified in two passes, so her face and hands keep more of their shape than her dress needs


def detail_of(me):
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    x, y, z = co.reshape(-1, 3).T
    face = np.clip((z - 1.40) / 0.03, 0, 1) * np.clip((0.02 - y) / 0.03, 0, 1) * (np.abs(x) < 0.1)
    hands = np.clip((np.abs(x) - 0.455) / 0.02, 0, 1) * (z > 1.1)
    return np.maximum(face, hands)


def simplify(ratio, weights):
    """Collapse to `ratio` of the faces; only where weights are 1 (anything less is kept)."""
    low.vertex_groups.clear()
    g = low.vertex_groups.new(name="simplify")
    w = np.round(weights, 2)
    for value in np.unique(w):
        g.add(np.where(w == value)[0].tolist(), float(value), "REPLACE")
    mod = low.modifiers.new("dec", "DECIMATE")
    mod.ratio, mod.vertex_group, mod.use_collapse_triangulate = ratio, "simplify", True
    with bpy.context.temp_override(object=low, active_object=low):
        bpy.ops.object.modifier_apply(modifier="dec")


t = time.time()
BODY, DETAIL = (float(v) for v in ratio.split(","))
simplify(BODY, 1 - detail_of(low.data))                            # everything but her face and hands
simplify(DETAIL, detail_of(low.data))                              # then those, more gently
low.vertex_groups.clear()
me = low.data
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
print("simplified to", len(me.polygons), "tris in", round(time.time() - t), "s; hand verts", int((np.abs(co[:, 0]) > 0.47).sum()),
      "face verts", int(((co[:, 2] > 1.42) & (co[:, 1] < 0.0) & (np.abs(co[:, 0]) < 0.09)).sum()))
bpy.ops.wm.save_as_mainfile(filepath=dst)
