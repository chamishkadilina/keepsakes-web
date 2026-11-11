"""Her web model: the light mesh keeps her own UVs and wears her own textures (colour and normal at 2048 px, roughness
at 1024 px), exported as glTF with WebP images. Her source's roughness map is near zero on her dress (it would shine like
wet plastic in the web's lighting), so it is remapped to soft cloth and skin, as her own preview images show her.
She also gets her one shape key, "Blink": her upper lids drawn down over her eyes.
python -I export.py -- rig.blend textures_dir out.glb [size]"""
import sys, os
import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
rig, texdir, out = a[:3]
SIZE = int(a[3]) if len(a) > 3 else 2048
NAME = "WhiteWeddingDressGirl_01_{}.jpg"
bpy.ops.wm.open_mainfile(filepath=rig, load_ui=False)
girl = bpy.data.objects["Girl"]


def image(kind, colour, size):
    im = bpy.data.images.load(os.path.join(texdir, NAME.format(kind)))
    im.colorspace_settings.name = "sRGB" if colour else "Non-Color"
    if max(im.size) > size:
        im.scale(size, size)
    return im


m = bpy.data.materials.new("girl")
m.use_nodes = True
nt = m.node_tree
b = nt.nodes["Principled BSDF"]
col = nt.nodes.new("ShaderNodeTexImage")
col.image = image("basecolor", True, SIZE)
nt.links.new(col.outputs[0], b.inputs["Base Color"])
nrm = nt.nodes.new("ShaderNodeTexImage")
nrm.image = image("normal", False, SIZE)
nmap = nt.nodes.new("ShaderNodeNormalMap")
nt.links.new(nrm.outputs[0], nmap.inputs["Color"])
nt.links.new(nmap.outputs[0], b.inputs["Normal"])

# roughness (G) and metalness (B) in one image, as glTF wants
half = SIZE // 2
r, mt = image("roughness", False, half), image("metallic", False, half)
rp = np.array(r.pixels[:]).reshape(half, half, 4)
mp = np.array(mt.pixels[:]).reshape(half, half, 4)
orm = np.ones_like(rp)
orm[..., 1], orm[..., 2] = np.clip(0.62 - 0.6 * rp[..., 0], 0.3, 0.7), 0.0
om = bpy.data.images.new("orm", half, half, alpha=False)
om.colorspace_settings.name = "Non-Color"
om.pixels.foreach_set(orm.astype(np.float32).ravel())
work = os.path.join(os.path.dirname(os.path.abspath(out)), "tex")
os.makedirs(work, exist_ok=True)
om.filepath_raw, om.file_format = os.path.join(work, "orm.png"), "PNG"
om.save()
o = nt.nodes.new("ShaderNodeTexImage")
o.image = om
sep = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(o.outputs[0], sep.inputs[0])
nt.links.new(sep.outputs[1], b.inputs["Roughness"])
nt.links.new(sep.outputs[2], b.inputs["Metallic"])
bpy.data.images.remove(r)
bpy.data.images.remove(mt)
girl.data.materials.clear()
girl.data.materials.append(m)

# her blink: seen from the front, each eye's opening closes onto its lower lid and the lid above it stretches down
EYES = {  # per eye, across it: (x, lower lid z, upper lid z), measured on her (metres)
    "r": [(-0.0464, 1.5031, 1.5031), (-0.0417, 1.4983, 1.5069), (-0.037, 1.4969, 1.508), (-0.0323, 1.4967, 1.5079),
          (-0.0276, 1.4974, 1.5067), (-0.0229, 1.4984, 1.5041), (-0.0182, 1.4995, 1.4995)],
    "l": [(0.0191, 1.4992, 1.4992), (0.024, 1.4985, 1.5043), (0.029, 1.498, 1.5071), (0.034, 1.4978, 1.5083),
          (0.039, 1.4981, 1.5085), (0.044, 1.4995, 1.5073), (0.0489, 1.5038, 1.5038)],
}
LASH, LID, SHUT = 0.0015, 0.011, 0.1          # the lash line above the opening, the lid above that, how thin it closes
co = np.empty(len(girl.data.vertices) * 3)
girl.data.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
shut = co.copy()
for curve in EYES.values():
    xs, lows, ups = (np.array(v) for v in zip(*curve))
    x, z = co[:, 0], co[:, 2]
    across = np.clip((x - xs[0]) / (xs[-1] - xs[0]), 0, 1)
    low = np.interp(x, xs, lows)
    up = np.interp(x, xs, ups) + LASH * np.sin(np.pi * across)
    top = up + LID * np.sin(np.pi * across) ** 0.5
    closed = low + (up - low) * SHUT
    inside = (x > xs[0]) & (x < xs[-1]) & (co[:, 1] < -0.04)
    eye = inside & (z > low) & (z <= up)
    lid = inside & (z > up) & (z < top)
    shut[eye, 2] = (low + (z - low) * SHUT)[eye]
    shut[lid, 2] = (closed + (z - up) / np.maximum(top - up, 1e-6) * (top - closed))[lid]
girl.shape_key_add(name="Basis", from_mix=False)
girl.shape_key_add(name="Blink", from_mix=False).data.foreach_set("co", shut.ravel())
print("blink moves", int((np.abs(shut - co).max(1) > 1e-5).sum()), "vertices")

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=True, export_optimize_animation_size=True,
                          export_anim_single_armature=True, export_skins=True, export_morph=True, export_morph_normal=False, export_yup=True,
                          use_visible=False, export_image_format="WEBP", export_image_quality=90)
print("exported", out, os.path.getsize(out) // 1024, "KB")
