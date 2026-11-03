"""Paris honeymoon gallery: boiserie panels, crown moulding, chair rail, tall skirting,
brass candle sconces, brass candle chandeliers, warm layered light, refined palette.
Usage: python add_luxury.py <in.blend> <out.blend>"""
import bpy, bmesh, sys, math
from mathutils import Vector
from shapely.geometry import LineString, Point, box as sbox
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, polygonize

src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
STRUCT, DECOR, LIGHTS = (bpy.data.collections[n] for n in ("structure", "decor", "lights"))
SLOTS = bpy.data.collections["frames_slots"]
H = 4.0
CANDLE = (1.0, 0.68, 0.42)        # ~2200 K candle glow
PICTURE = (1.0, 0.86, 0.72)       # warm picture light, keeps photos natural
FILL = (1.0, 0.88, 0.76)

def srgb(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b))

def material(name, rgb, rough=0.6, metal=0.0, emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit[0], 1); p.inputs["Emission Strength"].default_value = emit[1]
    return m

# ---------------- palette ----------------
IVORY_TRIM = material("trim_ivory", srgb(246, 239, 228), 0.45)
BRASS = material("brass_soft", srgb(196, 152, 92), 0.35, 1.0)
CANDLE_WAX = material("candle_wax", srgb(250, 244, 232), 0.5)
FLAME = material("candle_flame", (1, 1, 1), 0.5, 0, (CANDLE, 12.0))
material("ceiling", srgb(232, 212, 206), 0.9)                 # muted rose ceiling
for old in ("skirting", "door_jamb"):                          # ivory woodwork, like Parisian apartments
    m = bpy.data.materials.get(old)
    if m:
        p = m.node_tree.nodes["Principled BSDF"]; p.inputs["Base Color"].default_value = (*srgb(246, 239, 228), 1)

# ---------------- hang frames so they sit inside the wall panels (bottom edge at 1.10 m) ----------------
for o in SLOTS.objects:
    if o.name.startswith("slot_frame_"):
        o.location.z = 1.10 + o.dimensions.y / 2
        lt = bpy.data.objects.get("light_" + o.name[len("slot_"):])
        if lt:
            lt.rotation_euler = (o.location - lt.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()

# ---------------- remove the office-style ceiling lamps ----------------
for n in ("ceiling_light_fixtures", "ceiling_light_glow", "skirting"):
    o = bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
for o in list(LIGHTS.objects):
    if o.name.startswith("light_ambient_"):
        bpy.data.objects.remove(o)

# ---------------- wall footprint and interior faces ----------------
ROOMS = [sbox(0, 0, 11, 10), sbox(0, 10, 11, 21), sbox(11, 1.5, 23, 21), sbox(23, 13, 38, 21),
         sbox(23, 1.5, 26.5, 13), sbox(26.5, 1.5, 38, 13)]
INTERIOR = unary_union(ROOMS)
walls = bpy.data.objects["walls"]

def footprint_at(z):
    bm = bmesh.new(); bm.from_mesh(walls.data)
    cut = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z), plane_no=(0, 0, 1))
    segs = [LineString([(e.verts[0].co.x, e.verts[0].co.y), (e.verts[1].co.x, e.verts[1].co.y)])
            for e in cut["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bm.free()
    return unary_union(list(polygonize(segs)))

FOOT = footprint_at(1.5)
ROOM_AIR = INTERIOR.difference(FOOT)

def band(depth, z0, z1, bm):
    """Moulding strip of given depth wrapping every inside wall face between z0 and z1."""
    shape = FOOT.buffer(depth, join_style=2).difference(FOOT).intersection(ROOM_AIR).buffer(0)
    for poly in getattr(shape, "geoms", [shape]):
        if poly.area < 1e-5:
            continue
        rings = [poly.exterior] + list(poly.interiors)
        loops = []
        for ring in rings:
            pts = list(ring.coords)[:-1]
            b = [bm.verts.new((x, y, z0)) for x, y in pts]; t = [bm.verts.new((x, y, z1)) for x, y in pts]
            for i in range(len(pts)):
                j = (i + 1) % len(pts)
                bm.faces.new((b[i], b[j], t[j], t[i]))
            loops.append((b, t))
        for idx in (0, 1):
            edges = []
            for b, t in loops:
                vs = b if idx == 0 else t
                edges += [bm.edges.get((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
            bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)

def to_object(name, bm, mat, coll=STRUCT):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

# skirting 20 cm with a small top lip, chair rail, three-step crown moulding
bm = bmesh.new()
band(0.022, 0.0, 0.20, bm); band(0.012, 0.20, 0.225, bm)
to_object("skirting", bm, IVORY_TRIM)
bm = bmesh.new(); band(0.026, 0.84, 0.885, bm); to_object("chair_rail", bm, IVORY_TRIM)
bm = bmesh.new()
band(0.11, 3.88, 4.0, bm); band(0.07, 3.81, 3.88, bm); band(0.035, 3.76, 3.81, bm)
to_object("crown_moulding", bm, IVORY_TRIM)

# ---------------- boiserie panels around the photos ----------------
faces = []
for poly in getattr(FOOT, "geoms", [FOOT]):
    poly = orient(poly.simplify(0.002), 1.0)
    for ring in [poly.exterior] + list(poly.interiors):
        c = list(ring.coords)
        for a, b in zip(c[:-1], c[1:]):
            p0, p1 = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
            L = (p1 - p0).length
            if L < 0.9:
                continue
            t = (p1 - p0) / L
            n = Vector((t.y, -t.x, 0))                       # points away from the wall solid
            mid = (p0 + p1) / 2 + n * 0.1
            if ROOM_AIR.contains(Point(mid.x, mid.y)):
                faces.append((p0, t, n, L))

slot_info = []
for ob in SLOTS.objects:
    nn = (ob.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    w = ob.dimensions.x; h = ob.dimensions.y
    c = ob.matrix_world.translation
    slot_info.append((ob.name, Vector((c.x, c.y, 0)), nn, w, c.z - h / 2, c.z + h / 2))

STRIP, DEPTH = 0.045, 0.014
UP_Z, LOW_Z = (0.98, 3.45), (0.26, 0.72)
bm = bmesh.new()
def quad_box(p0, t, n, s0, s1, z0, z1, d0, d1):
    vs = []
    for s, z, d in [(s0, z0, d0), (s1, z0, d0), (s1, z1, d0), (s0, z1, d0), (s0, z0, d1), (s1, z0, d1), (s1, z1, d1), (s0, z1, d1)]:
        q = p0 + t * s + n * d; vs.append(bm.verts.new((q.x, q.y, z)))
    for f in [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]:
        bm.faces.new([vs[i] for i in f])
def panel(p0, t, n, s0, s1, z0, z1):
    quad_box(p0, t, n, s0, s1, z0, z0 + STRIP, 0, DEPTH)
    quad_box(p0, t, n, s0, s1, z1 - STRIP, z1, 0, DEPTH)
    quad_box(p0, t, n, s0, s0 + STRIP, z0 + STRIP, z1 - STRIP, 0, DEPTH)
    quad_box(p0, t, n, s1 - STRIP, s1, z0 + STRIP, z1 - STRIP, 0, DEPTH)

sconce_spots = []
MARGIN, GAP = 0.22, 0.16
for p0, t, n, L in faces:
    on = []
    for name, c, nn, w, zb, zt in slot_info:
        d = (c - p0).dot(n); s = (c - p0).dot(t)
        if 0.0 < d < 0.12 and nn.dot(n) > 0.9 and -0.1 < s < L + 0.1:
            on.append((s - w / 2 - 0.22, s + w / 2 + 0.22, zb, zt, name))
    on.sort()
    cols = []   # (s0, s1, z0, z1, has_slot, low_ok)
    cursor = MARGIN
    def fill(a, b):
        span = b - a
        if span < 0.55:
            return
        k = max(1, round(span / 1.5))
        wdt = (span - GAP * (k - 1)) / k
        for i in range(k):
            s0 = a + i * (wdt + GAP); cols.append((s0, s0 + wdt, UP_Z[0], UP_Z[1], False, True))
    for s0, s1, zb, zt, name in on:
        s0, s1 = max(s0, MARGIN), min(s1, L - MARGIN)
        fill(cursor, s0 - GAP)
        z0 = min(UP_Z[0], zb - 0.12); z1 = min(3.70, max(UP_Z[1], zt + 0.12))
        cols.append((s0, s1, z0, z1, True, z0 >= UP_Z[0] - 1e-6))
        cursor = s1 + GAP
    fill(cursor, L - MARGIN)
    for s0, s1, z0, z1, has, low_ok in cols:
        panel(p0, t, n, s0, s1, z0, z1)
        if low_ok:
            panel(p0, t, n, s0, s1, LOW_Z[0], LOW_Z[1])
    # sconces: between two neighbouring photo panels with enough room
    slots_here = [c for c in cols if c[4]]
    for a, b in zip(slots_here[:-1], slots_here[1:]):
        if b[0] - a[1] >= 0.35:
            sconce_spots.append((p0, t, n, (a[1] + b[0]) / 2))
to_object("boiserie", bm, IVORY_TRIM)

# ---------------- brass candle sconces ----------------
bm_brass, bm_wax, bm_flame = bmesh.new(), bmesh.new(), bmesh.new()
def cyl(bm, center, r, h, seg=12):
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, vec=center, verts=res["verts"])
def sphere(bm, center, r):
    res = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
    bmesh.ops.translate(bm, vec=center, verts=res["verts"])

def candle(at, scale=1.0):
    cyl(bm_brass, at + Vector((0, 0, 0.012 * scale)), 0.04 * scale, 0.025 * scale)
    cyl(bm_wax, at + Vector((0, 0, 0.085 * scale)), 0.017 * scale, 0.12 * scale, 10)
    sphere(bm_flame, at + Vector((0, 0, 0.165 * scale)), 0.016 * scale)
    return at + Vector((0, 0, 0.17 * scale))

def light(name, kind, loc, energy, color, radius=0.05, rot=None, size=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == "POINT": ld.shadow_soft_size = radius
    if kind == "AREA": ld.shape = "RECTANGLE"; ld.size, ld.size_y = size
    ob = bpy.data.objects.new(name, ld); ob.location = loc
    if rot: ob.rotation_euler = rot
    LIGHTS.objects.link(ob)

for i, (p0, t, n, s) in enumerate(sconce_spots, 1):
    base = p0 + t * s
    plate = base + n * 0.012
    cyl(bm_brass, Vector((plate.x, plate.y, 2.30)), 0.08, 0.025)         # wall plate
    arm_end = base + n * 0.22
    for k in range(9):                                                    # curved brass arm
        u = k / 8; q = base + n * (0.02 + 0.20 * u)
        sphere(bm_brass, Vector((q.x, q.y, 2.30 + 0.10 * math.sin(u * math.pi / 2))), 0.016)
    flame = candle(Vector((arm_end.x, arm_end.y, 2.40)), 1.5)
    light(f"light_sconce_{i:02d}", "POINT", flame, 22, CANDLE, 0.04)

# ---------------- brass candle chandeliers ----------------
def chandelier(name, cx, cy, r, n_candles, z=3.0, power=220):
    ring = bmesh.ops.create_circle(bm_brass, cap_ends=False, segments=48, radius=r)
    bmesh.ops.translate(bm_brass, vec=(cx, cy, z), verts=ring["verts"])
    edges = list({e for v in ring["verts"] for e in v.link_edges})
    geom = bmesh.ops.extrude_edge_only(bm_brass, edges=edges)
    vs = [g for g in geom["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm_brass, vec=(0, 0, 0.035), verts=vs)
    inner = bmesh.ops.create_circle(bm_brass, cap_ends=True, segments=24, radius=r * 0.18)
    bmesh.ops.translate(bm_brass, vec=(cx, cy, z - 0.06), verts=inner["verts"])
    cyl(bm_brass, Vector((cx, cy, (z + H) / 2)), 0.015, H - z, 8)            # stem to ceiling
    cyl(bm_brass, Vector((cx, cy, H - 0.02)), 0.09, 0.04, 16)                # ceiling rose
    sphere(bm_brass, Vector((cx, cy, z - 0.02)), 0.07)                       # central bulb ornament
    for k in range(n_candles):
        a = 2 * math.pi * k / n_candles
        at = Vector((cx + r * math.cos(a), cy + r * math.sin(a), z + 0.035))
        candle(at, 1.15)
        for j in range(4):                                                  # spokes
            u = (j + 1) / 5
            sphere(bm_brass, Vector((cx + r * u * math.cos(a), cy + r * u * math.sin(a), z - 0.04 + 0.06 * u)), 0.01)
    light(f"light_chandelier_{name}", "POINT", (cx, cy, z + 0.2), power, CANDLE, r * 0.9)

chandelier("heart", 17.0, 11.25, 0.75, 12, 3.0, 380)
chandelier("foyer", 5.5, 5.0, 0.55, 8, 3.1, 220)
chandelier("right", 31.5, 17.0, 0.6, 10, 3.1, 260)
chandelier("story", 5.5, 15.25, 0.5, 8, 3.15, 180)

to_object("sconces_brass", bm_brass, BRASS, DECOR)
to_object("sconces_candles", bm_wax, CANDLE_WAX, DECOR)
to_object("candle_flames", bm_flame, FLAME, DECOR)

# ---------------- picture lights stay (softer, warm), small discreet fixtures ----------------
bm_fix = bmesh.new()
for o in LIGHTS.objects:
    if o.name.startswith(("light_frame", "light_collage")):
        o.data.color = PICTURE
        o.data.energy = 150 if "collage" in o.name else 70
        o.data.spot_size = math.radians(55 if "collage" in o.name else 36); o.data.spot_blend = 0.85
        c = o.location
        cyl(bm_fix, Vector((c.x, c.y, H - 0.012)), 0.04, 0.024, 12)
to_object("ceiling_light_fixtures", bm_fix, BRASS)

# ---------------- soft warm uplight (like hidden cove light) so ceilings glow gently ----------------
for name, (x0, y0, x1, y1), e in [("foyer", (0, 0, 11, 10), 160), ("story", (0, 10, 11, 21), 170),
                                  ("heart", (11, 1.5, 23, 21), 320), ("right_top", (23, 13, 38, 21), 220),
                                  ("right_strip", (23, 1.5, 26.5, 13), 90), ("screen", (26.5, 1.5, 38, 13), 45)]:
    light(f"light_cove_{name}", "AREA", ((x0 + x1) / 2, (y0 + y1) / 2, 3.3), e, FILL,
          rot=(math.pi, 0, 0), size=(x1 - x0 - 1.0, y1 - y0 - 1.0))

bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
for img in bpy.data.images:
    if "textures" in img.filepath:
        img.filepath = "//textures/" + img.filepath.replace("\\", "/").split("textures/")[-1]
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True, relative_remap=False)
print("faces", len(faces), "sconces", len(sconce_spots), "lights", len(LIGHTS.objects))
