"""Warm amber ceiling (like the reference). Lightmaps hold light only, so the colour changes without re-baking.
Usage: python set_ceiling_colour.py <final.blend>"""
import bpy, sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
srgb = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
AMBER = (232, 184, 132)
mats = {m for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("ceiling_", "cove_")) and o.name != "ceiling_light_fixtures" for m in o.data.materials if m}
for m in mats:
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*map(srgb, AMBER), 1)
    print("ceiling material", m.name)
bpy.ops.wm.save_as_mainfile(filepath=sys.argv[1], compress=True, relative_remap=False)
