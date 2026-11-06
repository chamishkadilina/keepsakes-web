"""Bakes light into the vertices of thin trim (mouldings, skirting, door frames) and of the props instead of a texture.
Thin strips (2-5 cm) are narrower than a lightmap texel, so a texture leaves black gaps; per-corner colours do not.
Usage: python bake_trim_vertex.py <final.blend> <lightmaps.json> <samples>
Stores colour attribute "light" (linear, divided by the lightmaps intensity) and saves in place."""
import bpy, bmesh, sys, json
import numpy as np

path, man_path, samples = sys.argv[1], sys.argv[2], int(sys.argv[3])
bpy.ops.wm.open_mainfile(filepath=path)
man = json.load(open(man_path)); K = man["intensity"]
TRIM = ["skirting", "door_jambs", "chair_rail", "crown_moulding", "boiserie"]
objs = [bpy.data.objects[n] for n in TRIM if n in bpy.data.objects] + [o for o in bpy.data.objects if o.name.startswith("cove_") or o.get("bake_vertex")]

# finer vertices so light pools along long mouldings stay smooth (every 0.4 m); props are modelled fine enough
for o in objs:
    if not o.get("prop"):
        bm = bmesh.new(); bm.from_mesh(o.data)
        lo = [min(v.co[i] for v in bm.verts) for i in range(3)]; hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
        for axis in (0, 1, 2):
            step = 0.4 if axis < 2 else 0.5
            k = lo[axis] + step
            while k < hi[axis]:
                co = [0, 0, 0]; co[axis] = k; no = [0, 0, 0]; no[axis] = 1
                bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co, plane_no=no)
                k += step
        bm.to_mesh(o.data); bm.free()
    if "lightmap" in o.data.uv_layers:
        o.data.uv_layers.remove(o.data.uv_layers["lightmap"])
    if "lightmap_group" in o:
        del o["lightmap_group"]
    for a in [a for a in o.data.color_attributes]:
        o.data.color_attributes.remove(a)
    ca = o.data.color_attributes.new("light", "FLOAT_COLOR", "CORNER")
    o.data.color_attributes.active_color = ca
    o["light_vertex"] = True


# bake-only roof: sky light may enter only through doors and the garden, never over the wall tops
_rm = bpy.data.meshes.new("_bake_roof"); _rm.from_pydata([(-1, -1, 4.62), (39, -1, 4.62), (39, 22, 4.62), (-1, 22, 4.62)], [], [(0, 1, 2, 3)])
_roof = bpy.data.objects.new("_bake_roof", _rm); bpy.context.scene.collection.objects.link(_roof)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = samples
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 3
w = bpy.data.worlds.new("bake_sky"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*sc.get("sky_colour", (0.58, 0.5, 0.44)), 1)   # as bake_lightmaps.py
for o in bpy.data.collections["frames_slots"].objects:
    o.hide_render = True
decor = [o for o in objs if o.hide_render]          # e.g. the gold lines: left out of the lightmap bake, lit here
for o in decor:
    o.hide_render = False
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, target="VERTEX_COLORS")

for o in objs:   # same encoding as the lightmaps: value / intensity, clamped to 1
    data = o.data.color_attributes["light"].data
    a = np.empty(len(data) * 4, np.float32); data.foreach_get("color", a); a = a.reshape(-1, 4)
    a[:, :3] = np.clip(a[:, :3] / K, 0, 1); a[:, 3] = 1
    data.foreach_set("color", a.ravel())
    print(o.name, "corners", len(data), "mean", a[:, :3].mean().round(3), "black%", round(float((a[:, :3].max(1) < 0.01).mean() * 100), 1), flush=True)

for o in bpy.data.collections["frames_slots"].objects:
    o.hide_render = False
for o in decor:
    o.hide_render = True
bpy.data.worlds.remove(w)
bpy.data.objects.remove(_roof)
bpy.ops.wm.save_as_mainfile(filepath=path, compress=True, relative_remap=False)
print("saved")
