"""Lighting that tells a story as the couple walks:
foyer bright and welcoming -> golden evening galleries -> the heart room as a dimmed date night,
with one fairy-light feature wall (behind the collage) and red hearts. Photo lights stay full everywhere.
Writes the strand + heart layout for the web (three.js coordinates, y up) and bakes the glow they cast.
Usage: python design_v18.py <in.blend> <out.blend> <fairy_lights.json> <moods.json>"""
import bpy, sys, json, random, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

src, dst, out_json, moods_json = sys.argv[1:5]
bpy.ops.wm.open_mainfile(filepath=src)
LIGHTS = bpy.data.collections["lights"]
# room -> rectangles (Blender x, y) and how bright its ceiling lamps are
MOODS = {
    "foyer": ([(0, 0, 11, 10)], 1.0),                              # welcome: warm and bright
    "story_gallery": ([(0, 10, 11, 21)], 0.75),                    # golden evening
    "heart_room": ([(11, 1.5, 23, 21)], 0.3),                      # date night: the climax
    "right_gallery": ([(23, 13, 38, 21), (23, 1.5, 26.5, 13)], 0.75),
    "screen_room": ([(26.5, 1.5, 38, 13)], 1.0),                   # already a dim cinema
}
ROOMS = [r for rects, _ in MOODS.values() for r in rects]
def mood_at(p):
    for rects, level in MOODS.values():
        if any(x0 <= p.x <= x1 and y0 <= p.y <= y1 for x0, y0, x1, y1 in rects):
            return level
    return 1.0
Z0, Z1 = 0.97, 3.7            # curtain: from the chair rail up to the crown moulding
STEP, OFF = 0.14, 0.035       # strand spacing, distance from the wall
AMBER = (1.0, 0.52, 0.22)
rnd = random.Random(14)

inside = lambda p: any(x0 + 0.05 < p.x < x1 - 0.05 and y0 + 0.05 < p.y < y1 - 0.05 for x0, y0, x1, y1 in ROOMS)
walls = bpy.data.objects["walls"]
mw = walls.matrix_world
bvh = BVHTree.FromPolygons([mw @ v.co for v in walls.data.vertices], [p.vertices[:] for p in walls.data.polygons])

slots = []
for s in bpy.data.collections["frames_slots"].objects:
    c = s.matrix_world.translation
    half = max(s.dimensions) / 2 + 0.2
    slots.append((c, half))
def near_frame(p):
    return any((Vector((p.x, p.y, 0)) - Vector((c.x, c.y, 0))).length < half and abs(p.z - c.z) < half * 0.75 for c, half in slots)

strands, hearts, segments = [], [], []
for poly in walls.data.polygons:
    n = (mw.to_3x3() @ poly.normal).normalized()
    if abs(n.z) > 0.1:
        continue
    vs = [mw @ walls.data.vertices[i].co for i in poly.vertices]
    if min(v.z for v in vs) > 1.0 or max(v.z for v in vs) < 3.0:
        continue
    c = sum(vs, Vector()) / len(vs)
    if not inside(c + n * 0.3):
        continue
    if not (11 < c.x < 23 and c.y > 20 and n.y < -0.9):   # feature wall only: heart room, back wall
        continue
    t = Vector((-n.y, n.x, 0)).normalized()
    a = min(v.dot(t) for v in vs); b = max(v.dot(t) for v in vs)
    if b - a < 0.6:
        continue
    base = c - t * c.dot(t)                      # wall plane point with zero along-wall coordinate
    kept = 0
    k = a + STEP / 2
    while k < b - STEP / 4:
        p = base + t * k
        ok = all((h := bvh.ray_cast(Vector((p.x, p.y, z)) + n * 0.25, -n, 0.4))[0] is not None for z in (1.2, 3.4))
        if ok:
            top, bottom = p + n * OFF + Vector((0, 0, Z1 - p.z)), p + n * OFF + Vector((0, 0, Z0 - p.z))
            strands.append([round(v, 3) for v in (top.x, top.z, -top.y, bottom.x, bottom.z, -bottom.y)])
            kept += 1
            if rnd.random() < 0.45:              # a heart hangs on some strands
                hp = p + n * (OFF + 0.02) + Vector((0, 0, rnd.uniform(Z0 + 0.35, Z1 - 0.3) - p.z))
                if not near_frame(hp):
                    hearts.append([round(hp.x, 3), round(hp.z, 3), round(-hp.y, 3), round(n.x, 3), round(-n.y, 3), round(rnd.uniform(0.14, 0.34), 3)])
        k += STEP
    if kept:
        L, H = b - a, Z1 - Z0
        mid = base + t * ((a + b) / 2) + Vector((0, 0, (Z0 + Z1) / 2 - base.z))
        segments.append((mid, n, L, H))

# glow of the curtains (bake only): one panel washes the wall behind the bulbs, one fills the room
for i, (mid, n, L, H) in enumerate(segments):
    for name, offset, facing, power in (("wash", 0.14, -n, 2.4), ("fill", 0.05, n, 0.6)):
        ld = bpy.data.lights.new(f"fairy_{name}_{i}", "AREA"); ld.shape = "RECTANGLE"
        ld.size, ld.size_y = L, H; ld.energy = power * L * H; ld.color = AMBER
        ob = bpy.data.objects.new(ld.name, ld); ob.location = mid + n * offset
        ob.rotation_euler = facing.to_track_quat("-Z", "Y").to_euler()
        LIGHTS.objects.link(ob)

for o in list(LIGHTS.objects):
    if o.name.startswith(("light_down", "light_cove")):
        o.data.energy *= mood_at(o.location)      # each room's lamps set to its mood

json.dump({"strands": strands, "hearts": hearts}, open(out_json, "w"), separators=(",", ":"))
json.dump({"rooms": [{"name": k, "lamps": level, "rects": [[x0, -y1, x1, -y0] for x0, y0, x1, y1 in rects]}
                     for k, (rects, level) in MOODS.items()]}, open(moods_json, "w"), indent=1)
print("strands", len(strands), "hearts", len(hearts), "segments", len(segments))
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("saved")
