"""Her web model: the light mesh keeps her own UVs and wears her own textures (colour and normal at 2048 px, roughness
and metalness packed together at 1024 px), exported as glTF with WebP images.
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
orm[..., 1], orm[..., 2] = rp[..., 0], mp[..., 0]
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

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=True, export_optimize_animation_size=True,
                          export_anim_single_armature=True, export_skins=True, export_morph=False, export_yup=True,
                          use_visible=False, export_image_format="WEBP", export_image_quality=90)
print("exported", out, os.path.getsize(out) // 1024, "KB")
