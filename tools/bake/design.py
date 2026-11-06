"""Final gallery (owner's final reference video), lit like a real gallery.
Warm cream-beige plain walls with tall cream skirting and thin gold panel lines, cream tray ceilings with a small
cornice and gold lines, a few recessed downlights, track spots: every photo sits in its own pool of light.
A backlit collage niche in the heart room, glossy dark walnut-cherry floor. Furniture, exhibits and romantic decor
(props.py): the foyer's title wall between sheers with little lights glowing through them and velvet curtains at the
door where the story begins, a chapter board straight ahead as you come into the story gallery and the right gallery,
velvet sofas, the quote board and a grand dome of roses beside the collage, the dance floor in a pool of light with
its gramophone, love notes hanging over the right gallery, kentia palms, weeping figs, rose topiaries and urns of
roses, golden light strings along the heart room's walls, candles and lanterns that glow on the floors and walls
(accent lights), heart balloons, the screen room's ceiling projector, its screen on a little stage between velvet
curtains, popcorn and a "Now Showing" poster, velvet curtains at its garden door (a dimmer room, like a little cinema),
and the rose garden. The foyer has no photos of its own: the title wall is its exhibit; the chapter boards take two
photo places.
Usage: python design.py <in.blend> <out.blend>   (textures in ./textures next to out.blend)"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props

src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
STRUCT, DECOR, LIGHTS = (bpy.data.collections[n] for n in ("structure", "decor", "lights"))
for n in ("01", "02", "03", "12", "27"):                           # the foyer's photos: the title wall instead; 12 and 27:
    for name in (f"slot_frame_{n}", f"light_frame_{n}"):            # the story and right galleries' chapter boards
        bpy.data.objects.remove(bpy.data.objects[name])
H, TRAY_H = 4.0, 4.32                # ceiling band / raised tray
INSET, T = 1.45, 0.05                # band width, fascia thickness
WARM_WHITE = (1.0, 0.722, 0.446)     # ~2400 K: downlights, photo spots, wall wash
NICHE_WHITE = (1.0, 0.722, 0.422)    # collage niche LEDs, a touch warmer
SKY = (0.638, 0.484, 0.349)          # warm dusk through the doors and over the garden
LEVEL = {"down": 1.1, "spot": 1.25, "wash": 0.9, "niche": 0.3, "accent": 1.0}   # light levels, tuned against the reference
ROOMS = {                            # wall centre lines (Blender x, y); tray=False keeps a flat ceiling
    "foyer": [((0, 0, 11, 10), True)],
    "story_gallery": [((0, 10, 11, 21), True)],
    "heart_room": [((11, 1.5, 23, 21), True)],
    "right_gallery": [((23, 13, 38, 21), True), ((23, 1.5, 26.5, 13), False)],
    "screen_room": [((26.5, 1.5, 38, 13), True)],
}
PANEL_ROOMS = [(0, 0, 11, 10), (0, 10, 11, 21), (11, 1.5, 23, 21), (23, 13, 38, 21)]   # gold wall panels here

def srgb(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1)

def material(name, rgb, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(*rgb)
    if emit:
        p.inputs["Emission Color"].default_value = srgb(*rgb); p.inputs["Emission Strength"].default_value = emit
    return m

# ---------------- palette ----------------
bpy.data.materials["trim_burgundy"].name = "trim_cream"
material("trim_cream", (242, 236, 226)); material("crown_cream", (242, 236, 226))
CEIL = material("ceiling", (242, 235, 225))
TRIM = bpy.data.materials["trim_cream"]
GOLD = material("gold_trim", (240, 196, 110))          # gilt lines: lit like the mouldings, a touch brighter than paint
BLACK = material("track_black", (22, 22, 24))
WHITE = material("track_white", (236, 234, 230))
GLOW = material("led_glow", (255, 236, 205), emit=4.0)
BRASS = bpy.data.materials["brass_soft"]

# ---------------- remove what the reference does not have ----------------
for n in ("chair_rail", "boiserie", "ceiling_light_fixtures", "downlight_fixtures"):
    if n in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[n])
for o in [o for o in STRUCT.objects if o.name.startswith(("ceiling_", "cove_"))]:
    bpy.data.objects.remove(o)
for o in list(LIGHTS.objects):
    if not o.name.startswith(("light_frame", "light_collage")):          # keep only the photo spots
        bpy.data.objects.remove(o)
    else:
        o.data.color = WARM_WHITE; o.data.energy *= LEVEL["spot"]

# floor: the 2k board texture (floor_synth.py + plank_variation.py), 1 tile = 2.2 m (16 boards of ~14 cm)
for img in bpy.data.images:
    if img.filepath.startswith("//textures/laminate_floor_02/"):
        img.filepath = "//textures/laminate_floor_02/laminate_floor_02_albedo_2k.jpg"
for o in bpy.data.collections["floors"].objects:
    if o.data.materials and o.data.materials[0].name == "mat_floor_wood":
        for d in o.data.uv_layers["UVMap"].data:
            d.uv = (d.uv[0] * 2.0 / 2.2, d.uv[1] * 2.0 / 2.2)

# ---------------- helpers ----------------
def box(bm, x0, x1, y0, y1, z0, z1):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))

def obox(bm, origin, axes, size):
    """Oriented box: origin = min corner, axes = 3 unit vectors, size = extents along them."""
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = origin + sum((axes[i] * (size[i] if v.co[i] > 0 else 0) for i in range(3)), Vector())
    if axes[0].cross(axes[1]).dot(axes[2]) < 0:     # mirrored axes: turn the faces back outwards
        bmesh.ops.reverse_faces(bm, faces=list({f for v in r["verts"] for f in v.link_faces}))

def rect_line(bm, x0, x1, y0, y1, z, w=0.035, h=0.002):
    """Flat line rectangle (gold inlay on the ceiling: wide enough to stay a clean line when seen at a low angle)."""
    box(bm, x0, x1, y0, y0 + w, z - h, z); box(bm, x0, x1, y1 - w, y1, z - h, z)
    box(bm, x0, x0 + w, y0, y1, z - h, z); box(bm, x1 - w, x1, y0, y1, z - h, z)

def tray_edge(bm, a0, a1, b0, b1, t, c, z0, z1, z2):
    """Fascia + small cornice around a tray opening as one clean shell (only the faces you can see, no overlaps):
    inner face from z0 up to z2, soffit at z0 out to c beyond the opening, outer face from z0 up to z1 (the band)."""
    loops = []
    for x0, x1, y0, y1, z in [(a0 + t, a1 - t, b0 + t, b1 - t, z2), (a0 + t, a1 - t, b0 + t, b1 - t, z0),
                              (a0 - c, a1 + c, b0 - c, b1 + c, z0), (a0 - c, a1 + c, b0 - c, b1 + c, z1)]:
        loops.append([bm.verts.new((x, y, z)) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]])
    centre = Vector(((a0 + a1) / 2, (b0 + b1) / 2, z0))
    for k in range(4):
        n = (k + 1) % 4
        mid = (loops[1][k].co + loops[1][n].co) / 2
        inward = (centre - mid); inward.z = 0; inward.normalize()
        for (la, lb), want in [((0, 1), inward), ((1, 2), Vector((0, 0, -1))), ((2, 3), -inward)]:
            f = bm.faces.new((loops[la][k], loops[la][n], loops[lb][n], loops[lb][k]))
            f.normal_update()
            if f.normal.dot(want) < 0:
                f.normal_flip()

def cylinder(bm, a, b, r, seg=16):
    d = b - a
    c = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    m = Matrix.Translation((a + b) / 2) @ d.normalized().to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=m, verts=c["verts"])

def disc(bm, centre, normal, r, seg=20):
    c = bmesh.ops.create_circle(bm, cap_ends=True, segments=seg, radius=r)
    m = Matrix.Translation(centre) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=m, verts=c["verts"])

def mesh_object(name, bm, mat, collection, bake_visible=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); collection.objects.link(ob)
    ob.hide_render = not bake_visible          # small decor: no effect on the baked light
    return ob

bm_fix, bm_gold, bm_rail, bm_head, bm_lens = (bmesh.new() for _ in range(5))
n_down = 0
def downlight(x, y, z, energy):
    global n_down
    ld = bpy.data.lights.new(f"light_down_{n_down:03d}", "SPOT"); n_down += 1
    ld.energy = energy * LEVEL["down"]; ld.color = WARM_WHITE
    ld.spot_size = math.radians(60); ld.spot_blend = 1.0; ld.shadow_soft_size = 0.04     # soft-edged pools on the floor
    ob = bpy.data.objects.new(ld.name, ld); ob.location = (x, y, z - 0.03); LIGHTS.objects.link(ob)
    disc(bm_fix, Vector((x, y, z - 0.004)), Vector((0, 0, -1)), 0.06)

KEEP_CLEAR = [(4.85, 12.5, 6.15, 18.0)]   # story gallery partition: no lamp right above it
def grid(x0, x1, y0, y1, z, spacing):
    """Lamp positions on an even grid (not above the partition)."""
    nx, ny = max(1, round((x1 - x0) / spacing)), max(1, round((y1 - y0) / spacing))
    cells = [(x0 + (x1 - x0) * (i + 0.5) / nx, y0 + (y1 - y0) * (j + 0.5) / ny) for i in range(nx) for j in range(ny)]
    return [(x, y, z) for x, y in cells if not any(a <= x <= c and b <= y <= d for a, b, c, d in KEEP_CLEAR)]

# ---------------- ceilings: tray with cornice + gold lines, downlights on the tray ----------------
LIGHT_PER_M2 = 22                    # every room gets the same light per floor area (W/m²); the cinema less
for room, parts in ROOMS.items():
    lamps, area = [], sum((x1 - x0) * (y1 - y0) for (x0, y0, x1, y1), _ in parts)
    bm, bmc = bmesh.new(), bmesh.new()
    for (x0, y0, x1, y1), tray in parts:
        if not tray:
            box(bm, x0, x1, y0, y1, H, H + 0.12)
            lamps += grid((x0 + x1) / 2 - 0.1, (x0 + x1) / 2 + 0.1, y0 + 1.0, y1 - 1.0, H, 2.4)
            continue
        a0, b0, a1, b1 = x0 + INSET, y0 + INSET, x1 - INSET, y1 - INSET
        box(bm, x0, x1, y0, b0, H, H + 0.12); box(bm, x0, x1, b1, y1, H, H + 0.12)          # band
        box(bm, x0, a0, b0, b1, H, H + 0.12); box(bm, a1, x1, b0, b1, H, H + 0.12)
        box(bm, a0, a1, b0, b1, TRAY_H, TRAY_H + 0.1)                                      # raised tray
        tray_edge(bmc, a0, a1, b0, b1, T, 0.07, H - 0.05, H, TRAY_H)                        # fascia + small cornice
        rect_line(bm_gold, a0 - 0.32, a1 + 0.32, b0 - 0.32, b1 + 0.32, H - 0.001)            # gold line on the band
        rect_line(bm_gold, a0 + 0.35, a1 - 0.35, b0 + 0.35, b1 - 0.35, TRAY_H - 0.001)       # gold line in the tray
        lamps += grid(a0 + 0.9, a1 - 0.9, b0 + 0.9, b1 - 0.9, TRAY_H, 2.4)                  # a few lamps, like a real gallery
    energy = LIGHT_PER_M2 * area / len(lamps) * (0.3 if room == "screen_room" else 1.0)   # the screen room: a little dimmer, like a cinema
    for x, y, z in lamps:
        downlight(x, y, z, energy)
    print(room, "lamps", len(lamps), "W each", round(energy))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(f"ceiling_{room}"); bm.to_mesh(me); bm.free(); me.materials.append(CEIL)
    STRUCT.objects.link(bpy.data.objects.new(f"ceiling_{room}", me))
    me = bpy.data.meshes.new(f"cove_{room}"); bmc.to_mesh(me); bmc.free(); me.materials.append(CEIL)
    STRUCT.objects.link(bpy.data.objects.new(f"cove_{room}", me))

# ---------------- soft wall wash: every wall evenly lit like a real gallery (bake only, invisible) ----------------
WASH_PER_M2 = 1.7                    # W per m² of panel: a soft base, the photo spots still pop
for room, parts in ROOMS.items():
    if room == "screen_room":
        continue
    for (x0, y0, x1, y1), _ in parts:
        for (cx, cy, dx, dy, length) in [((x0 + x1) / 2, y0, 0, -1, x1 - x0), ((x0 + x1) / 2, y1, 0, 1, x1 - x0),
                                         (x0, (y0 + y1) / 2, -1, 0, y1 - y0), (x1, (y0 + y1) / 2, 1, 0, y1 - y0)]:
            span = (y1 - y0) if dy else (x1 - x0)
            d = min(2.0, span / 2 - 0.3)                                  # panel this far from the wall it washes
            face = Vector((dx, dy, 0))
            ld = bpy.data.lights.new(f"light_wash_{room}_{len(LIGHTS.objects)}", "AREA"); ld.shape = "RECTANGLE"
            ld.size, ld.size_y = length * 0.9, 2.4; ld.energy = WASH_PER_M2 * ld.size * ld.size_y * LEVEL["wash"]
            ld.color = WARM_WHITE
            ob = bpy.data.objects.new(ld.name, ld); ob.location = (cx - dx * d, cy - dy * d, 2.1)
            ob.rotation_euler = face.to_track_quat("-Z", "Y").to_euler()
            LIGHTS.objects.link(ob)

# ---------------- furniture, exhibits and decor (props.py): each exhibit in its own spot, candles that glow ----------------
PROPS = bpy.data.collections.new("props"); bpy.context.scene.collection.children.link(PROPS)
ATLAS = os.path.join(os.path.dirname(os.path.abspath(dst)), "textures", "decor", "decor_atlas.jpg")   # props_atlas.py
spots, accents = props.add(PROPS, material, ATLAS)
for i, a in enumerate(accents):                     # candles, lanterns, the sheers' lights, the neon, the dance floor's spot
    ld = bpy.data.lights.new(f"light_accent_{i:03d}", a["kind"])
    ld.color = a["colour"]; ld.energy = a["watts"] * LEVEL["accent"]
    if a["kind"] == "AREA":
        ld.shape = "RECTANGLE"; ld.size, ld.size_y = a["size"]
    elif a["kind"] == "SPOT":
        ld.spot_size = a["cone"]; ld.spot_blend = 0.6; ld.shadow_soft_size = 0.05
    else:
        ld.shadow_soft_size = 0.02
    ob = bpy.data.objects.new(ld.name, ld); ob.location = a["pos"]; LIGHTS.objects.link(ob)
    if "normal" in a:
        ob.rotation_euler = Vector(a["normal"]).to_track_quat("-Z", "Y").to_euler()
for name, rail, target, wall, radius in spots:
    ld = bpy.data.lights.new(f"light_exhibit_{name}", "SPOT"); ld.color = WARM_WHITE
    ob = bpy.data.objects.new(ld.name, ld); ob.location = (rail.x, rail.y, 3.96); LIGHTS.objects.link(ob)
    dist = (target - ob.location).length
    ld.energy = 640 * LEVEL["spot"] * (dist / 3.0) ** 2                              # as bright on the piece as a photo's spot
    ld.shadow_soft_size = 0.05; ld.spot_blend = 0.6
    ld.spot_size = 2 * math.atan(radius / dist)                                       # a soft pool just wider than the piece
    ob["target"] = list(target); ob["wall"] = list(wall)                              # hangs on that wall's rail

# ---------------- track lights: one rail per wall line, a spot head aimed at every photo and exhibit ----------------
slots = {o.name: o for o in bpy.data.collections["frames_slots"].objects}
board = slots["collage_board"]
heads = []
for l in [l for l in LIGHTS.objects if l.name.startswith(("light_frame", "light_collage", "light_exhibit"))]:
    if "target" in l:
        heads.append((l, Vector(l["target"]), Vector(l["wall"])))
        continue
    s = slots.get(l.name.replace("light_", "slot_")) or board
    target = s.matrix_world.translation.copy()
    target.z -= 0.1 if s is not board else 0.0
    if s is board:
        target.x = l.location.x
    n = (l.location - target); n.z = 0; n.normalize()          # from the wall towards the room
    n = Vector((round(n.x), round(n.y), 0)) if abs(n.x) > 0.9 or abs(n.y) > 0.9 else n
    heads.append((l, target, n))

lines = {}
for l, target, n in heads:
    key = (n.x, n.y, round(l.location.dot(n) / 0.3))
    lines.setdefault(key, []).append((l, target, n))
for key, items in lines.items():
    n = items[0][2]; t = Vector((-n.y, n.x, 0))
    items.sort(key=lambda it: it[0].location.dot(t))
    runs, cur = [], [items[0]]
    for it in items[1:]:
        if it[0].location.dot(t) - cur[-1][0].location.dot(t) > 3.5:
            runs.append(cur); cur = [it]
        else:
            cur.append(it)
    runs.append(cur)
    for run in runs:
        d = sum(it[0].location.dot(n) for it in run) / len(run)
        u0, u1 = run[0][0].location.dot(t) - 0.35, run[-1][0].location.dot(t) + 0.35
        origin = n * (d - 0.0175) + t * u0 + Vector((0, 0, H - 0.024))
        obox(bm_rail, origin, (t, n, Vector((0, 0, 1))), (u1 - u0, 0.035, 0.024))
        for l, target, _ in run:
            rail_pt = n * d + t * l.location.dot(t)
            pivot = Vector((rail_pt.x, rail_pt.y, H - 0.08))
            cylinder(bm_rail, Vector((pivot.x, pivot.y, H - 0.024)), pivot, 0.008, 8)     # stem
            aim = (target - pivot).normalized()
            cylinder(bm_head, pivot - aim * 0.035, pivot + aim * 0.1, 0.034)               # spot head
            disc(bm_lens, pivot + aim * 0.102, aim, 0.027)                                  # warm lens
            l.location = pivot + aim * 0.11
            l.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
            s = slots.get(l.name.replace("light_", "slot_"))
            if s is not None:                    # beam sized to the photo: a soft pool a little wider than the frame
                l.data.spot_size = 2 * math.atan((max(s.dimensions) / 2 + 0.45) / (target - l.location).length)
                l.data.spot_blend = 0.6

# ---------------- backlit collage niche (heart room back wall) ----------------
WALL_Y, D, B = 20.8, 0.17, 0.14
bx0, bx1, bz0, bz1 = 14.22, 19.78, 0.42, 3.74
bmn, bm_led = bmesh.new(), bmesh.new()
box(bmn, bx0, bx1, WALL_Y - D, WALL_Y, bz1 - B, bz1); box(bmn, bx0, bx1, WALL_Y - D, WALL_Y, bz0, bz0 + B)
box(bmn, bx0, bx0 + B, WALL_Y - D, WALL_Y, bz0 + B, bz1 - B); box(bmn, bx1 - B, bx1, WALL_Y - D, WALL_Y, bz0 + B, bz1 - B)
mesh_object("cove_collage_niche", bmn, TRIM, STRUCT)
ix0, ix1, iz0, iz1 = bx0 + B, bx1 - B, bz0 + B, bz1 - B
LY = WALL_Y - 0.07                                              # LED strips hidden in the niche sides
for (x0, x1, z0, z1, rot, size) in [
        (ix0, ix1, iz1 - 0.01, iz1, (0, 0, 0), (ix1 - ix0, 0.03)),                       # top, shines down
        (ix0, ix1, iz0, iz0 + 0.01, (math.pi, 0, 0), (ix1 - ix0, 0.03)),                 # bottom, shines up
        (ix0, ix0 + 0.01, iz0, iz1, (0, math.pi / 2, 0), (iz1 - iz0, 0.03)),             # left, shines right
        (ix1 - 0.01, ix1, iz0, iz1, (0, -math.pi / 2, 0), (iz1 - iz0, 0.03))]:           # right, shines left
    box(bm_led, x0, x1, LY - 0.012, LY + 0.012, z0, z1)
    ld = bpy.data.lights.new(f"light_niche_{len(LIGHTS.objects)}", "AREA"); ld.color = NICHE_WHITE
    ld.size, ld.size_y = size; ld.energy = 28 * max(size) * LEVEL["niche"]
    ob = bpy.data.objects.new(ld.name, ld); ob.location = ((x0 + x1) / 2, LY, (z0 + z1) / 2); ob.rotation_euler = rot
    LIGHTS.objects.link(ob)

# ---------------- thin gold panel lines on the gallery walls ----------------
walls = bpy.data.objects["walls"]; mw = walls.matrix_world
bvh = BVHTree.FromPolygons([mw @ v.co for v in walls.data.vertices], [p.vertices[:] for p in walls.data.polygons])
in_panel_room = lambda p: any(x0 + 0.05 < p.x < x1 - 0.05 and y0 + 0.05 < p.y < y1 - 0.05 for x0, y0, x1, y1 in PANEL_ROOMS)
frame_slots = [o for o in slots.values() if o.name.startswith("slot_frame")]
PZ0, PZ1, LW, LD = 0.45, 3.48, 0.018, 0.006                      # panel bottom/top, line width/depth
n_panels = 0
for poly in walls.data.polygons:
    n = (mw.to_3x3() @ poly.normal).normalized()
    if abs(n.z) > 0.1:
        continue
    vs = [mw @ walls.data.vertices[i].co for i in poly.vertices]
    if min(v.z for v in vs) > 1.0 or max(v.z for v in vs) < 3.0:
        continue
    c = sum(vs, Vector()) / len(vs)
    if not in_panel_room(c + n * 0.3):
        continue
    t = Vector((-n.y, n.x, 0)).normalized()
    a, b = min(v.dot(t) for v in vs), max(v.dot(t) for v in vs)
    plane = c.dot(n)
    # continuous wall (no door openings, no collage niche) along this face
    present = []
    k = a + 0.025
    while k < b:
        p = t * k + n * plane
        ok = all(bvh.ray_cast(Vector((p.x, p.y, z)) + n * 0.25, -n, 0.4)[0] is not None for z in (1.0, 3.3))
        if abs(n.y + 1) < 0.01 and abs(plane + WALL_Y) < 0.2 and bx0 - 0.3 < p.x < bx1 + 0.3:
            ok = False
        present.append((k, ok)); k += 0.05
    runs, start = [], None
    for k, ok in present + [(b, False)]:
        if ok and start is None: start = k
        if not ok and start is not None: runs.append((start, k)); start = None
    for ra, rb in runs:
        u0, u1 = ra + 0.3, rb - 0.3
        if u1 - u0 < 0.9:
            continue
        on_wall = sorted((s.matrix_world.translation.dot(t), max(s.dimensions) / 2) for s in frame_slots
                         if abs(s.matrix_world.translation.dot(n) - plane) < 0.15 and u0 < s.matrix_world.translation.dot(t) < u1)
        gaps = [((p + h + q - g) / 2) for (p, h), (q, g) in zip(on_wall, on_wall[1:]) if (q - g) - (p + h) > 0.4]
        cuts = []
        count = math.ceil((u1 - u0) / 5.5)
        for i in range(1, count):
            want = u0 + (u1 - u0) * i / count
            best = min(gaps, key=lambda g: abs(g - want), default=None)
            if best is not None and abs(best - want) < 1.4 and best not in cuts:
                cuts.append(best)
        edges = [u0] + sorted(cuts) + [u1]
        for e0, e1 in zip(edges[:-1], edges[1:]):
            p0, p1 = e0 + (0.15 if e0 != u0 else 0), e1 - (0.15 if e1 != u1 else 0)
            base = n * plane
            for (q0, q1, z0, z1) in [(p0, p1, PZ0, PZ0 + LW), (p0, p1, PZ1 - LW, PZ1), (p0, p0 + LW, PZ0, PZ1), (p1 - LW, p1, PZ0, PZ1)]:
                obox(bm_gold, base + t * q0 + Vector((0, 0, z0)), (t, n, Vector((0, 0, 1))), (q1 - q0, LD, z1 - z0))
            n_panels += 1

mesh_object("downlight_fixtures", bm_fix, BRASS, DECOR, bake_visible=False)
mesh_object("gold_lines", bm_gold, GOLD, DECOR, bake_visible=False)["bake_vertex"] = True    # lit like the trim (vertex colours)
mesh_object("track_rails", bm_rail, BLACK, DECOR, bake_visible=False)
mesh_object("track_heads", bm_head, WHITE, DECOR, bake_visible=False)
mesh_object("light_lenses", bm_lens, GLOW, DECOR, bake_visible=False)
mesh_object("niche_led_strips", bm_led, GLOW, DECOR, bake_visible=False)

# ---------------- lightmap UVs for the new ceilings ----------------
ceil = [o for o in STRUCT.objects if o.name.startswith("ceiling_")]
def select_only(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
for o in ceil:
    o.data.uv_layers.new(name="UVMap"); o.data.uv_layers.new(name="lightmap")
    select_only([o]); o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=1.0); bpy.ops.object.mode_set(mode="OBJECT")
select_only(ceil)
for o in ceil: o.data.uv_layers.active = o.data.uv_layers["lightmap"]
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.uv.select_all(action="SELECT")
bpy.ops.uv.pack_islands(rotate=True, margin_method="FRACTION", margin=0.012, shape_method="AABB")
bpy.ops.object.mode_set(mode="OBJECT")
for o in ceil:
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]; o["lightmap_group"] = "ceilings"

bpy.context.scene["sky_colour"] = SKY        # read by the bake scripts
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("ok downlights", n_down, "heads", len(heads), "panels", n_panels, "ceilings", len(ceil), "accents", len(accents))
