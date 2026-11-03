"""Applies the textured floor and wall materials (albedo only: lighting is baked).
Usage: python apply_materials.py <museum.blend>   (saves in place; textures in ./textures next to it)"""
import bpy, sys, os
path = sys.argv[1]
bpy.ops.wm.open_mainfile(filepath=path)

# material -> (texture id, real-world texture width in m, roughness, objects)
MATS = {
    "mat_floor_wood":     ("laminate_floor_02", 2.0, 0.25, ["floor_1_foyer", "floor_2_story_gallery", "floor_3_heart_room", "floor_5_screen_room",
                                                          "floor_4_right_gallery_top", "floor_4_right_gallery_strip"]),
    "mat_wall_plaster":   ("beige_wall_001", 2.5, 0.90, [n for n in ("walls", "partition_cap") if n in bpy.data.objects]),
}
for mname, (tid, width, rough, objs) in MATS.items():
    m = bpy.data.materials.get(mname) or bpy.data.materials.new(mname)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    for n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:
        nt.nodes.remove(n)
    import glob
    fname = os.path.basename(sorted(glob.glob(os.path.join(os.path.dirname(bpy.data.filepath), "textures", tid, f"{tid}_albedo_*.jpg")))[-1])
    img = bpy.data.images.load(f"//textures/{tid}/{fname}", check_existing=True)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.location = (-400, 300)
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"; uv.location = (-600, 300)
    nt.links.new(uv.outputs[0], tex.inputs[0]); nt.links.new(tex.outputs[0], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = 0.0
    for name in objs:
        o = bpy.data.objects[name]
        o.data.materials.clear(); o.data.materials.append(m)
        for d in o.data.uv_layers["UVMap"].data:       # 1 UV unit = 1 m  ->  1 UV unit = one texture tile
            d.uv = (d.uv[0] / width, d.uv[1] / width)
    print("material", mname, tid, objs)

for old in ("floor_light", "wall_grey", "mat_floor_parquet", "mat_floor_marble", "mat_floor_laminate"):
    m = bpy.data.materials.get(old)
    if m and m.users == 0:
        bpy.data.materials.remove(m)
bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
print("saved")
