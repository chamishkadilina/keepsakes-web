"""Clean walls around the photos: keeps the lower wainscot panels, removes the upper wall panels.
Aims each picture light at the centre of its photo so the pool sits evenly on the frame.
Usage: python design_v15.py <in.blend> <out.blend>"""
import bpy, bmesh, sys
from mathutils import Vector
src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
CHAIR_RAIL_TOP = 0.9

o = bpy.data.objects["boiserie"]
bm = bmesh.new(); bm.from_mesh(o.data)
upper = [f for f in bm.faces if min(v.co.z for v in f.verts) > CHAIR_RAIL_TOP]
bmesh.ops.delete(bm, geom=upper, context="FACES")
bm.to_mesh(o.data); bm.free()
print("boiserie faces removed", len(upper))

slots = {s.name.replace("slot_", ""): s for s in bpy.data.collections["frames_slots"].objects}
for l in bpy.data.collections["lights"].objects:
    key = l.name.replace("light_", "")
    s = slots.get(key)
    if s:
        target = s.matrix_world.translation - Vector((0, 0, 0.1))
        l.rotation_euler = (target - l.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("saved")
