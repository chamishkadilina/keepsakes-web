"""Prepares static meshes for baked lighting.
- Fixes empty material slots on walls.
- UV map 0 "UVMap": cube projection, 1 UV unit = 1 m (for tiling textures later).
- UV map 1 "lightmap": non-overlapping islands, packed per bake group.
Usage: python lightmap_uvs.py <in.blend> <out.blend>"""
import bpy, sys, math

src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)

GROUPS = {   # bake group -> objects (one lightmap image per group)
    "walls": ["walls"],
    "floors": [o.name for o in bpy.data.collections["floors"].objects],
    "ceilings": [o.name for o in bpy.data.objects if o.name.startswith("ceiling_") and o.name not in ("ceiling_light_fixtures", "ceiling_light_glow")],
    "garden_walls": ["garden_walls"],
    "trim": ["skirting", "door_jambs"],
}

# 1. walls: drop the empty material slot so every face uses the wall material
for name in ("walls", "garden_walls"):
    ob = bpy.data.objects[name]
    mats = [s.material for s in ob.material_slots if s.material]
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = 0

def select_only(objs):
    bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.object and bpy.context.object.mode != "OBJECT" else None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

for group, names in GROUPS.items():
    objs = [bpy.data.objects[n] for n in names]
    for o in objs:
        uv = o.data.uv_layers
        while len(uv):
            uv.remove(uv[0])
        uv.new(name="UVMap"); uv.new(name="lightmap")
    # UVMap: 1 m cube projection, per object
    for o in objs:
        select_only([o])
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=False, clip_to_bounds=False, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")
    # lightmap: all objects of the group share one UV square
    select_only(objs)
    for o in objs:
        o.data.uv_layers.active = o.data.uv_layers["lightmap"]
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(udim_source="CLOSEST_UDIM", rotate=True, margin_method="FRACTION", margin=0.012, shape_method="AABB")
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objs:
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        o.data.uv_layers["UVMap"].active_render = True
        o["lightmap_group"] = group
    print("uv", group, names)

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)
print("saved")
