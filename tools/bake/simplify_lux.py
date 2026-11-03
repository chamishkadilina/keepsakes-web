"""Owner feedback: no sconces/chandeliers/candles, no wall panel frames or chair rail, warmer (less white) palette.
Usage: python simplify_lux.py <in.blend> <out.blend>"""
import bpy, sys, math
src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
for n in ("boiserie", "chair_rail", "sconces_brass", "sconces_candles", "candle_flames"):
    o = bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
for o in list(bpy.data.collections["lights"].objects):
    if o.name.startswith(("light_sconce_", "light_chandelier_")):
        bpy.data.objects.remove(o)
def srgb(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1)
def base(mat, rgb):
    m = bpy.data.materials.get(mat)
    if m: m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb(*rgb)
base("ceiling", (236, 222, 208))        # warm cream
base("trim_ivory", (226, 205, 192))     # crown + skirting: a touch lighter than the walls
base("door_jamb", (226, 205, 192))
# light: no chandeliers any more -> stronger hidden uplight, warm (not pink), picture lights stay
WARM = (1.0, 0.82, 0.66)
for o in bpy.data.collections["lights"].objects:
    if o.name.startswith("light_cove_"):
        o.data.color = WARM; o.data.energy *= 2.2
    elif o.name.startswith(("light_frame", "light_collage")):
        o.data.energy *= 1.15
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("ok", sorted(o.name for o in bpy.data.collections["decor"].objects), len(bpy.data.collections["lights"].objects))
