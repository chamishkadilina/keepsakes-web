"""Her source made ready: upright, facing -Y (Blender front), 1.64 m, and a light copy for the web.
python -I prep.py -- src.blend out.blend ratio"""
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
t = time.time()
mod = low.modifiers.new("dec", "DECIMATE")
mod.ratio = float(ratio)
mod.use_collapse_triangulate = True
with bpy.context.temp_override(object=low, active_object=low):
    bpy.ops.object.modifier_apply(modifier="dec")
print("decimated to", len(low.data.polygons), "tris in", round(time.time() - t), "s")
bpy.ops.wm.save_as_mainfile(filepath=dst)
