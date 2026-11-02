"""Romantic, bright mood: blush/cream palette, warm rosy light, soft photo spotlights.
Usage: python romantic.py <in.blend> <out.blend> <ambient_w> <spot_w>"""
import bpy, sys, math
src, dst = sys.argv[1], sys.argv[2]
AMB, SPOT = float(sys.argv[3]), float(sys.argv[4])
bpy.ops.wm.open_mainfile(filepath=src)

PALETTE = {                      # placeholder colours until real textures (step: materials)
    "wall_grey": (0.95, 0.86, 0.84),     # blush ivory
    "ceiling": (0.98, 0.94, 0.92),       # warm cream
    "floor_light": (0.80, 0.63, 0.50),   # honey oak tone
    "skirting": (0.45, 0.22, 0.21),      # rosewood
    "door_jamb": (0.45, 0.22, 0.21),
    "garden_wall": (0.88, 0.80, 0.78),
    "grass": (0.30, 0.48, 0.28),
}
for name, rgb in PALETTE.items():
    m = bpy.data.materials.get(name)
    if m:
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*rgb, 1)
        p.inputs["Roughness"].default_value = 0.85; p.inputs["Metallic"].default_value = 0.0

ROSY = (1.0, 0.80, 0.74)      # soft rose-warm fill
WARM_WHITE = (1.0, 0.90, 0.80)  # spotlights: flattering, keeps photos natural
for o in bpy.data.collections["lights"].objects:
    L = o.data
    if o.name.startswith("light_ambient_"):
        L.color = ROSY; L.energy = AMB * (0.45 if "screen_room" in o.name else 1.0); L.size = 0.8
    elif o.name.startswith("light_collage_board"):
        L.color = WARM_WHITE; L.energy = SPOT * 2; L.spot_size = math.radians(55); L.spot_blend = 0.8
    else:
        L.color = WARM_WHITE; L.energy = SPOT; L.spot_size = math.radians(40); L.spot_blend = 0.8

g = bpy.data.materials["light_glow"].node_tree.nodes["Principled BSDF"]
g.inputs["Emission Color"].default_value = (*ROSY, 1); g.inputs["Emission Strength"].default_value = 4.0
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)
print("ok")
