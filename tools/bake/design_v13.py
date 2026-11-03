"""Burgundy romance (owner's reference image): deep burgundy panelled walls, cream crown moulding,
dark glossy mahogany planks, warm cream ceiling with small recessed downlights, moody amber light.
Usage: python design_v13.py <v10 museum.blend> <out.blend>"""
import bpy, bmesh, sys, math
from mathutils import Vector
src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
LIGHTS, STRUCT = bpy.data.collections["lights"], bpy.data.collections["structure"]
H = 4.0
AMBER = (1.0, 0.70, 0.44)       # ~2400 K
PICTURE = (1.0, 0.80, 0.60)

def srgb(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1)
def material(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(*rgb); p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    return m

# no sconces, candles or chandeliers
for n in ("sconces_brass", "sconces_candles", "candle_flames"):
    o = bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
for o in list(LIGHTS.objects):
    if o.name.startswith(("light_sconce_", "light_chandelier_")):
        bpy.data.objects.remove(o)

# palette
BURG_TRIM = material("trim_burgundy", (104, 40, 60), 0.5)     # panels, chair rail, skirting, door frames
CROWN = material("crown_cream", (236, 222, 200), 0.5)
material("ceiling", (214, 188, 158), 0.9)
for n in ("boiserie", "chair_rail", "skirting", "door_jambs"):
    o = bpy.data.objects.get(n)
    if o: o.data.materials.clear(); o.data.materials.append(BURG_TRIM)
cr = bpy.data.objects.get("crown_moulding")
if cr: cr.data.materials.clear(); cr.data.materials.append(CROWN)

# lights: picture lights amber, very soft hidden fill, small recessed downlights on a grid
for o in list(LIGHTS.objects):
    if o.name.startswith(("light_frame", "light_collage")):
        o.data.color = PICTURE; o.data.energy = 600 if "collage" in o.name else 300
        o.data.spot_size = math.radians(48 if "collage" in o.name else 34); o.data.spot_blend = 0.8
    elif o.name.startswith("light_cove_"):
        o.data.color = AMBER; o.data.energy *= 0.8

bm = bmesh.new()
def fixture(x, y, r=0.06):
    c = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r, radius2=r, depth=0.025)
    bmesh.ops.translate(bm, vec=(x, y, H - 0.012), verts=c["verts"])
def downlight(name, x, y, energy):
    ld = bpy.data.lights.new(name, "SPOT"); ld.energy = energy; ld.color = AMBER
    ld.spot_size = math.radians(70); ld.spot_blend = 0.9; ld.shadow_soft_size = 0.04
    ob = bpy.data.objects.new(name, ld); ob.location = (x, y, H - 0.03); LIGHTS.objects.link(ob)
    fixture(x, y)
GRID = {   # room centre-line rectangles -> downlights every ~3.3 m, kept 2.2 m from walls (clear of the picture lights)
    "foyer": (0, 0, 11, 10), "story": (0, 10, 11, 21), "heart": (11, 1.5, 23, 21),
    "right_top": (23, 13, 38, 21), "right_strip": (23, 1.5, 26.5, 13), "screen": (26.5, 1.5, 38, 13),
}
for room, (x0, y0, x1, y1) in GRID.items():
    m = 1.75 if room == "right_strip" else 2.2
    nx = max(1, round((x1 - x0 - 2 * m) / 3.3) + 1); ny = max(1, round((y1 - y0 - 2 * m) / 3.3) + 1)
    for i in range(nx):
        for j in range(ny):
            x = (x0 + x1) / 2 if nx == 1 else x0 + m + (x1 - x0 - 2 * m) * i / (nx - 1)
            y = (y0 + y1) / 2 if ny == 1 else y0 + m + (y1 - y0 - 2 * m) * j / (ny - 1)
            if room == "story" and abs(x - 5.5) < 0.6 and 12.5 < y < 18:
                continue                                    # not right above the partition
            downlight(f"light_down_{room}_{i}{j}", x, y, 70 if room == "screen" else 220)
fx = bpy.data.objects.get("ceiling_light_fixtures")
me = bpy.data.meshes.new("downlight_fixtures"); bm.to_mesh(me); bm.free()
me.materials.append(fx.data.materials[0] if fx else material("brass_soft", (214, 180, 128), 0.3, 1.0))
bpy.data.collections["decor"].objects.link(bpy.data.objects.new("downlight_fixtures", me))

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("ok lights", len(LIGHTS.objects), "downlights", len([o for o in LIGHTS.objects if o.name.startswith("light_down")]))
