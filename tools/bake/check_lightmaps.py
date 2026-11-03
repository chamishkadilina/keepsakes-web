"""Renders the museum using ONLY the baked lightmaps (no lights), the way the web will draw it:
colour = albedo x lightmap. Photo slots show their stored light_rgb.
Usage: python check_lightmaps.py <museum.blend> <lightmaps_dir> <outdir>"""
import bpy, sys, json, os, math
from mathutils import Vector

src, lm_dir, outdir = sys.argv[1:4]
bpy.ops.wm.open_mainfile(filepath=src)
man = json.load(open(os.path.join(lm_dir, "lightmaps.json")))
K = man["intensity"]
ALBEDO = (0.75, 0.73, 0.70)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 8; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 0
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (*sc.get("sky_colour", (0.58, 0.5, 0.44)), 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
for o in bpy.data.collections["lights"].objects:
    o.hide_render = True

def unlit(mat_name, build):
    m = bpy.data.materials.new(mat_name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs[0])
    build(nt, em)
    return m

def albedo(o):
    """Base colour of the object's material: an image (textured) or an RGB tuple."""
    m = o.data.materials[0]
    p = m.node_tree.nodes.get("Principled BSDF")
    if not p:
        return ALBEDO
    link = p.inputs["Base Color"].links
    if link and link[0].from_node.type == "TEX_IMAGE":
        return link[0].from_node.image
    return tuple(p.inputs["Base Color"].default_value[:3])

for g, info in man["maps"].items():
    img = bpy.data.images.load(os.path.join(lm_dir, info["file"])); img.colorspace_settings.name = "sRGB"
    def build(nt, em, img=img, alb=ALBEDO):
        uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "lightmap"
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.interpolation = "Linear"
        nt.links.new(uv.outputs[0], tex.inputs[0])
        mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        nt.links.new(tex.outputs[0], mul.inputs[6])
        if isinstance(alb, tuple):
            mul.inputs[7].default_value = (*(c * K for c in alb), 1)
        else:   # textured: albedo image (UVMap) x K
            uv0 = nt.nodes.new("ShaderNodeUVMap"); uv0.uv_map = "UVMap"
            at = nt.nodes.new("ShaderNodeTexImage"); at.image = alb
            nt.links.new(uv0.outputs[0], at.inputs[0])
            k = nt.nodes.new("ShaderNodeMix"); k.data_type = "RGBA"; k.blend_type = "MULTIPLY"; k.inputs[0].default_value = 1.0
            nt.links.new(at.outputs[0], k.inputs[6]); k.inputs[7].default_value = (K, K, K, 1)
            nt.links.new(k.outputs[2], mul.inputs[7])
        nt.links.new(mul.outputs[2], em.inputs[0])
    for name in info["objects"]:
        o = bpy.data.objects[name]
        a = albedo(o)
        m = unlit(f"lm_{g}_{name}", lambda nt, em, img=img, a=a: build(nt, em, img, a))
        o.data.materials.clear(); o.data.materials.append(m)

# thin trim: light baked into vertices (colour attribute "light")
for o in [o for o in bpy.data.objects if o.get("light_vertex")]:
    a = albedo(o)
    def vbuild(nt, em, a=a):
        ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "light"
        mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
        nt.links.new(ca.outputs[0], mul.inputs[6]); mul.inputs[7].default_value = (*(c * K for c in a), 1)
        nt.links.new(mul.outputs[2], em.inputs[0])
    m = unlit(f"vl_{o.name}", vbuild)
    o.data.materials.clear(); o.data.materials.append(m)

# champagne-gold details: the web uses a gold matcap; approximate with a flat gold
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name == "brass_soft"]:
    m = unlit(f"gold_{o.name}", lambda nt, em: em.inputs[0].__setattr__("default_value", (0.80, 0.62, 0.38, 1)))
    o.data.materials.clear(); o.data.materials.append(m)

for o in bpy.data.collections["frames_slots"].objects:
    rgb = o.get("light_rgb")
    if rgb is None:
        continue
    c = (0.62, 0.56, 0.60, 1) if o.name.startswith(("slot_", "collage")) else (0.03, 0.03, 0.035, 1)
    m = unlit(f"photo_{o.name}", lambda nt, em, c=c: em.inputs[0].__setattr__("default_value", c))
    o.data.materials.clear(); o.data.materials.append(m)

def cam(name, loc, at, lens=16):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(c)
    c.data.lens = lens; c.location = loc; c.data.clip_end = 300
    c.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return c
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
VIEWS = [("foyer", (5.5, 0.8, 1.6), (5.0, 9.8, 1.8)), ("story", (9.6, 11.0, 1.6), (1.0, 19.5, 1.7)), ("heart", (17, 4.0, 1.6), (17, 20.8, 2.3)),
         ("screen", (32.25, 2.4, 1.6), (32.25, 12.8, 1.9)), ("right", (24.0, 14.5, 1.6), (37.5, 19.5, 1.8))]
only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
for name, loc, at in VIEWS:
    if only and name not in only:
        continue
    sc.camera = cam(name, loc, at); sc.render.filepath = os.path.join(outdir, f"baked-{name}.png")
    bpy.ops.render.render(write_still=True)
print("rendered")
