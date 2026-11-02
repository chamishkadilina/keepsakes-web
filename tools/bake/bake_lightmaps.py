"""Bakes the museum lighting (light only, no surface colour) into one lightmap per group.
Usage: python bake_lightmaps.py <uv.blend> <outdir> <samples> [scale]
Writes <outdir>/lm_<group>.exr (linear float) for each group."""
import bpy, sys, time

src, outdir, samples = sys.argv[1], sys.argv[2], int(sys.argv[3])
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
only = sys.argv[5].split(",") if len(sys.argv) > 5 else None   # bake just these groups
RES = {"walls": 2048, "floors": 1024, "ceilings": 512, "garden_walls": 512, "trim": 1024}
RES = {k: max(64, int(v * scale)) for k, v in RES.items()}

bpy.ops.wm.open_mainfile(filepath=src)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
sc.cycles.samples = samples
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 1
sc.cycles.transmission_bounces = 0; sc.cycles.volume_bounces = 0
sc.render.bake.margin = 12; sc.render.bake.margin_type = "EXTEND"
sc.render.bake.use_pass_direct = True; sc.render.bake.use_pass_indirect = True; sc.render.bake.use_pass_color = False

SKY = (0.62, 0.42, 0.55, 1)   # romantic pink-violet twilight
# twilight sky (lights the garden and spills softly through the doors)
w = bpy.data.worlds.new("bake_sky"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = SKY; bg.inputs[1].default_value = 1.0

# photo slots must not cast shadows into the bake (the web builds frames later)
for o in bpy.data.collections["frames_slots"].objects:
    o.hide_render = True

groups = {}
for o in bpy.data.objects:
    g = o.get("lightmap_group")
    if g:
        groups.setdefault(g, []).append(o)

# surfaces keep their real colours, so light bouncing off blush walls tints the rooms softly rosy

for group, objs in groups.items():
    if only and group not in only:
        continue
    img = bpy.data.images.new(f"lm_{group}", RES[group], RES[group], float_buffer=True, alpha=False)
    for o in objs:
        o.data.uv_layers.active = o.data.uv_layers["lightmap"]
        for m in o.data.materials:
            nt = m.node_tree
            node = nt.nodes.get("bake_target") or nt.nodes.new("ShaderNodeTexImage")
            node.name = "bake_target"; node.image = img
            nt.nodes.active = node
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    t = time.time()
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=12, use_clear=True, target="IMAGE_TEXTURES")
    img.filepath_raw = f"{outdir}/lm_{group}.exr"; img.file_format = "OPEN_EXR"
    img.save()
    print(f"baked {group} {RES[group]}px in {time.time() - t:.0f}s", flush=True)
print("done", flush=True)
