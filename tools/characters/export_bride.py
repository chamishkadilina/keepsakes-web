"""Exports bride.blend as one glb with all its animations: python -I export_bride.py -- bride.blend bride_raw.glb"""
import sys
import bpy
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
arm.animation_data.action = bpy.data.actions["Idle"]
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=True, export_optimize_animation_size=True, export_anim_single_armature=True,
                          export_skins=True, export_morph=False, export_yup=True, use_visible=False,
                          export_image_format="WEBP", export_image_quality=88)
print("ok", out)
