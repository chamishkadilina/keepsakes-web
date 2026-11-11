"""Builds the bride and saves her as one glb (no animations; bride_anim.py adds them):

  her body (bride_body.py: hair, brows, smile, makeup), a white ball gown (a lace bodice with a sweetheart neckline,
  a blush satin sash with a pearl brooch, a full satin skirt to the floor with soft folds, a short train and a lace hem),
  a long tulle veil from a pearl tiara, a pearl necklace and a bouquet of white and blush roses in her left hand.

The skirt hangs from 16 chains of 3 bones (skirt_<k>_<1..3>, from the waist round to the hem, then skirt_<k>_end
marking the hem) and the veil from 3 chains (veil_<l|c|r>_<1..3>, veil_<l|c|r>_end): the web swings them (gravity,
inertia, her legs pushing the skirt).

  python -I bride_build.py -- <Superhero_Female_FullBody.gltf> <Hair_Long.gltf> <out.glb>
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(HERE, "..", "bake"))                                  # the museum's props (roses), after the standard library

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import bride_body
import lace
from props_flowers import bloom, leaf

BODY, HAIR, OUT = sys.argv[sys.argv.index("--") + 1:]
TEX = os.path.join(os.path.dirname(os.path.abspath(OUT)), "tex")
rng = random.Random(7)
TAU = 2 * math.pi
CY = 0.03                                                                            # the skirt's middle (y), a little back

bpy.ops.wm.read_factory_settings(use_empty=True)
arm, body = bride_body.prepare(BODY, HAIR)
os.makedirs(TEX, exist_ok=True)
lace.lace(TEX)
lace.trim(TEX)
lace.tulle(TEX)


# ------------------------------------------------------------------------------------------------ materials
def material(name, colour, roughness=0.5, metallic=0.0, texture=None, normal=None, alpha=False, double=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    b = nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*colour, 1)
    b.inputs["Roughness"].default_value = roughness
    b.inputs["Metallic"].default_value = metallic
    if texture:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(TEX, texture))
        links.new(t.outputs["Color"], b.inputs["Base Color"])
        if alpha:
            links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    if normal:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(TEX, normal))
        t.image.colorspace_settings.name = "Non-Color"
        n = nodes.new("ShaderNodeNormalMap")
        links.new(t.outputs["Color"], n.inputs["Color"])
        links.new(n.outputs["Normal"], b.inputs["Normal"])
    if alpha:
        m.surface_render_method = "BLENDED"
    m.use_backface_culling = not double
    return m


MAT = {
    "Lace": material("Lace", (1, 1, 1), 0.55, texture="lace_albedo.png", normal="lace_normal.png"),
    "Satin": material("Satin", (0.78, 0.76, 0.73), 0.36, double=True),
    "LaceTrim": material("LaceTrim", (1, 1, 1), 0.6, texture="lace_trim.png", alpha=True, double=True),
    "Tulle": material("Tulle", (1, 1, 1), 0.6, texture="tulle.png", alpha=True, double=True),
    "Sash": material("Sash", (0.8, 0.55, 0.53), 0.32),
    "Pearl": material("Pearl", (0.92, 0.89, 0.85), 0.22),
    "Gold": material("Gold", (0.83, 0.64, 0.33), 0.3, metallic=1.0),
    "RoseWhite": material("RoseWhite", (0.8, 0.77, 0.72), 0.55, double=True),
    "RoseBlush": material("RoseBlush", (0.72, 0.33, 0.38), 0.55, double=True),
    "Leaf": material("Leaf", (0.055, 0.12, 0.08), 0.85, double=True),
    "Ribbon": material("Ribbon", (0.9, 0.87, 0.82), 0.38),
}

# ------------------------------------------------------------------------------------------------ helpers
V = body.data.vertices
GROUPS = {g.index: g.name for g in body.vertex_groups}


def weights_of(v):
    return {GROUPS[g.group]: g.weight for g in v.groups if g.weight > 0.001}


def make(name, bm, weights, mat, smooth=True):
    """A mesh skinned to her skeleton: weights[i] = {bone: weight} for vertex i."""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = arm
    ob.modifiers.new("Armature", "ARMATURE").object = arm
    for i, w in enumerate(weights):
        total = sum(w.values()) or 1
        for bone, value in w.items():
            if value > 1e-4:
                (ob.vertex_groups.get(bone) or ob.vertex_groups.new(name=bone)).add([i], value / total, "REPLACE")
    me.materials.append(MAT[mat] if isinstance(mat, str) else mat)
    for p in me.polygons:
        p.use_smooth = smooth
    return ob


def arm_weight(poly):
    return max(sum(w for b, w in weights_of(V[i]).items() if b.startswith(("upperarm", "lowerarm", "hand", "clavicle")))
               for i in poly.vertices)


def neckline(x, y):
    """The top of the bodice: a sweetheart dip at the front middle, a little lower at the back."""
    return 1.405 - (0.03 * math.exp(-(x / 0.04) ** 2) if y < 0 else 0.022)


def radii(z0, z1, n, cy=CY, verts=None):
    """How far her body reaches from the skirt's middle, round her, between two heights (n directions)."""
    out = [0.0] * n
    for v in verts or V:
        co = v.co if hasattr(v, "co") else v
        if z0 <= co.z <= z1:
            dx, dy = co.x, co.y - cy
            k = int((math.atan2(dy, dx) % TAU) / TAU * n) % n
            out[k] = max(out[k], math.hypot(dx, dy))
    for _ in range(4):
        out = [max(out[k], 0.5 * (out[k - 1] + out[(k + 1) % n])) for k in range(n)]
    return out


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------ bodice
def bodice():
    """Her torso from the waist to the neckline, a little out from her and softened (lace)."""
    faces = [p for p in body.data.polygons if min(V[i].co.z for i in p.vertices) > 1.0
             and min(V[i].co.z - neckline(V[i].co.x, V[i].co.y) for i in p.vertices) < 0
             and arm_weight(p) < 0.85 and abs(sum(V[i].co.x for i in p.vertices) / len(p.vertices)) < 0.185]
    bm, index, wts = bmesh.new(), {}, []
    for p in faces:
        for vi in p.vertices:
            if vi not in index:
                v = V[vi]
                index[vi] = bm.verts.new(v.co + v.normal * 0.011)
                wts.append(weights_of(v))
    for p in faces:
        try:
            bm.faces.new([index[vi] for vi in p.vertices])
        except ValueError:
            pass
    bm.verts.ensure_lookup_table()
    inner = [v for v in bm.verts if not v.is_boundary]
    for _ in range(5):                                                                # soften the muscles away
        bmesh.ops.smooth_vert(bm, verts=inner, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    for v in bm.verts:                                                                # but never closer to her than 9 mm
        loc, normal, _, _ = TORSO.find_nearest(v.co)
        if loc is not None and (v.co - loc).dot(normal) < 0.009:
            v.co = loc + normal * 0.009
    for v in bm.verts:
        if v.is_boundary and v.co.z > 1.2:
            v.co.z = neckline(v.co.x, v.co.y)
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:                                                                # lace wrapped round her
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = ((math.atan2(co.x, -(co.y - 0.01)) / TAU + 0.5) * 6, co.z * 9)
    bm.verts.index_update()
    return make("Bodice", bm, wts, "Lace")


# ------------------------------------------------------------------------------------------------ skirt
N, LEVELS, TOP = 96, 22, 1.075
CHAINS, JOINTS = 16, (0.0, 0.3, 0.65, 1.0)                                           # skirt bones: where along it they meet


def back(a):
    """1 straight behind her, falling to 0 at her sides."""
    return max(0.0, math.cos(a - math.pi / 2)) ** 3


def skirt_point(a, s, hugs=None, j=None, folds=True):
    """A point on the skirt: a round her (0 = her left, pi/2 = behind her), s from the waist (0) to the hem (1)."""
    k = int(a / TAU * N) % N
    waist = WAIST[k] + 0.012
    hem = 0.6 + 0.02 * math.cos(2 * a) ** 2
    bell = 0.55 * (1 - (1 - s) ** 2.2) + 0.45 * s
    r = waist + (hem - waist) * bell
    z = TOP - s * (TOP - 0.03)
    if hugs is not None:
        r = max(r, hugs[j][k] + 0.035)
    t = smoothstep(0.55, 1.0, s) * back(a)                                           # the train: further back, along the floor
    r += 0.55 * t
    z = max(0.012, z - 0.22 * t * 1.6)
    if folds:
        r *= 1 + 0.032 * s ** 1.4 * math.sin(14 * a + 0.7 * math.sin(3 * a))
    return Vector((r * math.cos(a), CY + r * math.sin(a), z))


WAIST = radii(TOP - 0.02, TOP + 0.02, N)


def skirt_weights(a, s):
    """Pelvis at the waist, then the chain bones on either side of this direction, joint by joint."""
    f = a / TAU * CHAINS
    k0 = int(math.floor(f)) % CHAINS
    k1, t = (k0 + 1) % CHAINS, f - math.floor(f)
    mids = [(JOINTS[i] + JOINTS[i + 1]) / 2 for i in range(3)]
    hats = []
    for i in range(3):
        left = mids[i - 1] if i else 0.0
        right = mids[i + 1] if i < 2 else 2.0
        if s <= mids[i]:
            hats.append(smoothstep(left, mids[i], s) if i else min(1.0, s / mids[0]))
        else:
            hats.append(1 - smoothstep(mids[i], right, s) if i < 2 else 1.0)
    pelvis = max(0.0, 1 - s / mids[0])
    w = {"pelvis": pelvis}
    for i, h in enumerate(hats):
        w[f"skirt_{k0}_{i + 1}"] = w.get(f"skirt_{k0}_{i + 1}", 0) + h * (1 - t)
        w[f"skirt_{k1}_{i + 1}"] = w.get(f"skirt_{k1}_{i + 1}", 0) + h * t
    return w


def skirt():
    heights = [TOP - (j / LEVELS) * (TOP - 0.03) for j in range(LEVELS + 1)]
    hugs = [radii(z - 0.03, z + 0.03, N) if z > 0.06 else [0.0] * N for z in heights]
    bm, wts, rings = bmesh.new(), [], []
    uv = bm.loops.layers.uv.new()
    for j in range(LEVELS + 1):
        s = j / LEVELS
        ring = []
        for k in range(N + 1):                                                        # a seam vertex for the UVs
            a = TAU * (k % N) / N
            ring.append(bm.verts.new(skirt_point(a, s, hugs, j)))
            wts.append(skirt_weights(a, s))
        rings.append(ring)
    for j in range(LEVELS):
        for k in range(N):
            f = bm.faces.new((rings[j][k], rings[j + 1][k], rings[j + 1][k + 1], rings[j][k + 1]))
            for loop, (kk, jj) in zip(f.loops, ((k, j), (k, j + 1), (k + 1, j + 1), (k + 1, j))):
                loop[uv].uv = (kk / N * 8, 1 - jj / LEVELS)
    bm.verts.index_update()
    ob = make("Skirt", bm, wts, "Satin")
    # a lace band round the hem, just outside the satin
    bm, wts, rings = bmesh.new(), [], []
    uv = bm.loops.layers.uv.new()
    band = (0.84, 0.92, 1.0)
    for s in band:
        j = s * LEVELS
        ring = []
        for k in range(N + 1):
            a = TAU * (k % N) / N
            p = skirt_point(a, s, hugs, min(int(round(j)), LEVELS))
            d = Vector((p.x, p.y - CY, 0)).normalized()
            ring.append(bm.verts.new(p + d * 0.004))
            wts.append(skirt_weights(a, s))
        rings.append(ring)
    for j in range(len(band) - 1):
        for k in range(N):
            f = bm.faces.new((rings[j][k], rings[j + 1][k], rings[j + 1][k + 1], rings[j][k + 1]))
            for loop, (kk, jj) in zip(f.loops, ((k, j), (k, j + 1), (k + 1, j + 1), (k + 1, j))):
                loop[uv].uv = (kk / N * 12, 1 - jj / (len(band) - 1))
    bm.verts.index_update()
    make("LaceHem", bm, wts, "LaceTrim")
    return ob


# ------------------------------------------------------------------------------------------------ sash and brooch
def sash():
    bm, wts, loops = bmesh.new(), [], []
    for z in (1.052, 1.102):
        r = radii(z - 0.012, z + 0.012, 64, cy=0.01)
        loops.append([bm.verts.new(((r[k] + 0.014) * math.cos(TAU * (k + 0.5) / 64),
                                    0.01 + (r[k] + 0.014) * math.sin(TAU * (k + 0.5) / 64), z)) for k in range(64)])
        wts += [{"spine_01": 0.5, "pelvis": 0.5}] * 64
    for k in range(64):
        bm.faces.new((loops[0][k], loops[0][(k + 1) % 64], loops[1][(k + 1) % 64], loops[1][k]))
    bm.verts.index_update()
    make("Sash", bm, wts, "Sash")
    front = min((v.co for v in loops_front()), key=lambda c: c.y)
    pearls([front + Vector((math.cos(a) * 0.012, -0.021, math.sin(a) * 0.012)) for a in [i * TAU / 7 for i in range(7)]]
           + [front + Vector((0, -0.025, 0))], 0.0055, "Brooch", {"spine_01": 0.5, "pelvis": 0.5})


def loops_front():
    return [v for v in V if abs(v.co.z - 1.078) < 0.01 and abs(v.co.x) < 0.01 and v.co.y < 0]


# ------------------------------------------------------------------------------------------------ pearls
def pearls(points, radius, name, weight):
    """Pearls at `points`, each moving with weight (a dict, or a function of its position)."""
    bm, wts = bmesh.new(), []
    for p in points:
        verts = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)["verts"]
        w = weight(p) if callable(weight) else weight
        for v in verts:
            v.co += p
            wts.append(w)
    bm.verts.index_update()
    return make(name, bm, wts, "Pearl")


def snap(tree, origin, direction, lift):
    hit = tree.ray_cast(origin, direction.normalized())
    return None if hit[0] is None else hit[0] - direction.normalized() * lift


def bvh_of(objects, keep=lambda p: True):
    verts, polys = [], []
    for ob in objects:
        base = len(verts)
        verts += [v.co.copy() for v in ob.data.vertices]
        polys += [[base + i for i in p.vertices] for p in ob.data.polygons if ob is not body or keep(p)]
    return BVHTree.FromPolygons(verts, polys)


def nearest_weights(p):
    best = min(V, key=lambda v: (v.co - p).length_squared)
    return weights_of(best)


def necklace(tree):
    """A strand of pearls lying round the base of her neck, lower at the front."""
    path = []
    for i in range(240):
        f = TAU * i / 240
        d = Vector((math.sin(f), -math.cos(f), 0))
        z = 1.495 - 0.06 * max(0.0, math.cos(f)) ** 1.5                                # lowest at the front
        hit = tree.ray_cast(Vector((0, 0.012, z)), d)                                  # out from inside her neck
        p = hit[0] + d * 0.0062 if hit[0] is not None else None
        if p:
            path.append(p)
    points, run = [path[0]], 0.0
    for a, b in zip(path, path[1:] + path[:1]):
        run += (b - a).length
        if run >= 0.0098:
            points.append(b)
            run = 0.0
    pearls(points, 0.0046, "Necklace", nearest_weights)


def tiara(tree):
    """A fine arc of pearls on a gold band over the top of her head, from ear to ear."""
    centre = Vector((0, 0.01, 1.66))
    path = []
    for i in range(41):
        f = math.radians(-72 + 144 * i / 40)
        d = Vector((math.sin(f), -0.12, math.cos(f))).normalized()
        p = snap(tree, centre + d * 0.4, -d, 0.004)
        if p:
            path.append(p)
    pearls([p for i, p in enumerate(path) if i % 2 == 0], 0.0042, "Tiara", {"Head": 1.0})
    bm = bmesh.new()
    for a, b in zip(path, path[1:]):
        verts = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=0.0015, radius2=0.0015, depth=(b - a).length)["verts"]
        rot = Vector((0, 0, 1)).rotation_difference(b - a).to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ rot, verts=verts)
    bm.verts.index_update()
    make("TiaraBand", bm, [{"Head": 1.0}] * len(bm.verts), "Gold")


# ------------------------------------------------------------------------------------------------ veil
VEIL_ROWS, VEIL_COLS, VEIL_TOP, VEIL_BOTTOM = 26, 15, 1.735, 0.56
VEIL_CHAINS, VEIL_JOINTS = (("l", 0.7), ("c", 0.0), ("r", -0.7)), (0.08, 0.38, 0.68, 1.0)


def veil(tree):
    """A sheet of tulle from the back of her crown, over her hair and back, down over the gown's back."""
    grid = []
    for j in range(VEIL_ROWS + 1):
        v = j / VEIL_ROWS
        z = VEIL_TOP - v * (VEIL_TOP - VEIL_BOTTOM)
        width = 0.13 + 0.62 * v ** 0.85
        row = []
        for i in range(VEIL_COLS + 1):
            u = i / VEIL_COLS * 2 - 1
            x = u * width / 2
            p = snap(tree, Vector((x, 1.2, z)), Vector((0, -1, 0)), 0.012)
            y = p.y if p else 0.12
            row.append(Vector((x, y, z)))
        grid.append(row)
    for _ in range(6):                                                              # let it fall smoothly: no tight wrapping
        for j in range(1, VEIL_ROWS + 1):
            for i in range(VEIL_COLS + 1):
                up = grid[j - 1][i].y
                grid[j][i].y = max(grid[j][i].y, up - 0.05 * (VEIL_TOP - VEIL_BOTTOM) / VEIL_ROWS * 10)
        for j in range(VEIL_ROWS + 1):
            ys = [p.y for p in grid[j]]
            for i in range(1, VEIL_COLS):
                grid[j][i].y = max(grid[j][i].y, (ys[i - 1] + ys[i] + ys[i + 1]) / 3)
    bm, wts = bmesh.new(), []
    uv = bm.loops.layers.uv.new()
    verts = [[None] * (VEIL_COLS + 1) for _ in range(VEIL_ROWS + 1)]
    for j in range(VEIL_ROWS + 1):
        for i in range(VEIL_COLS + 1):
            verts[j][i] = bm.verts.new(grid[j][i])
            wts.append(veil_weights(i / VEIL_COLS * 2 - 1, j / VEIL_ROWS))
    for j in range(VEIL_ROWS):
        for i in range(VEIL_COLS):
            f = bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
            for loop, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                loop[uv].uv = (ii / VEIL_COLS, 1 - jj / VEIL_ROWS)
    bm.verts.index_update()
    make("Veil", bm, wts, "Tulle")
    return grid


def veil_weights(u, v):
    w = {"Head": max(0.0, 1 - v / VEIL_JOINTS[0])}
    mids = [(VEIL_JOINTS[i] + VEIL_JOINTS[i + 1]) / 2 for i in range(3)]
    for name, cu in VEIL_CHAINS:
        across = max(0.0, 1 - abs(u - cu) / 0.7)
        for i in range(3):
            lo = mids[i - 1] if i else VEIL_JOINTS[0]
            hi = mids[i + 1] if i < 2 else 9.0
            if v <= mids[i]:
                h = smoothstep(lo, mids[i], v) if i else smoothstep(VEIL_JOINTS[0] * 0.5, mids[0], v)
            else:
                h = 1 - smoothstep(mids[i], hi, v) if i < 2 else 1.0
            w[f"veil_{name}_{i + 1}"] = w.get(f"veil_{name}_{i + 1}", 0) + h * across * (1 - w["Head"])
    return w


# ------------------------------------------------------------------------------------------------ bones
def add_bones(veil_grid):
    """The skirt's and the veil's chains of bones."""
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    for k in range(CHAINS):
        a = TAU * k / CHAINS
        pts = [skirt_point(a, s, folds=False) for s in JOINTS]
        parent = eb["pelvis"]
        for i in range(3):
            b = eb.new(f"skirt_{k}_{i + 1}")
            b.head, b.tail = pts[i], pts[i + 1]
            b.parent, b.use_connect = parent, i > 0
            parent = b
        end(eb, f"skirt_{k}_end", parent)
    for name, cu in VEIL_CHAINS:
        i = int(round((cu + 1) / 2 * VEIL_COLS))
        pts = [veil_grid[int(round(v * VEIL_ROWS))][i] for v in VEIL_JOINTS]
        parent = eb["Head"]
        for n in range(3):
            b = eb.new(f"veil_{name}_{n + 1}")
            b.head, b.tail = pts[n], pts[n + 1]
            b.parent, b.use_connect = parent, n > 0
            parent = b
        end(eb, f"veil_{name}_end", parent)
    bpy.ops.object.mode_set(mode="OBJECT")


def end(eb, name, parent):
    """A small bone at the end of a chain, marking where its last bone ends (the web swings each bone towards the
    next one's start)."""
    b = eb.new(name)
    b.head = parent.tail
    b.tail = parent.tail + (parent.tail - parent.head).normalized() * 0.02
    b.parent, b.use_connect = parent, True


# ------------------------------------------------------------------------------------------------ bouquet
def bouquet():
    """White and blush roses with leaves and baby's breath over a stem wrapped in ivory ribbon, held in her left hand.
    Built along +z (the stem from 0 to 0.2, the flowers above), then put in her hand."""
    bms = {name: bmesh.new() for name in ("RoseWhite", "RoseBlush", "Leaf", "Ribbon", "Pearl")}
    centre, radius = Vector((0, 0, 0.27)), 0.085
    golden = math.pi * (3 - math.sqrt(5))
    count = 15
    for i in range(count):                                                           # a dome of roses
        cz = 1 - (i + 0.5) / count * 0.78
        sz = math.sqrt(1 - cz * cz)
        d = Vector((sz * math.cos(i * golden), sz * math.sin(i * golden), cz))
        bloom(bms["RoseBlush" if i % 3 == 1 else "RoseWhite"], centre + d * radius, (d + Vector((0, 0, 0.3))).normalized(),
              0.62 * rng.uniform(0.92, 1.06), rng.uniform(0, TAU), 9, (4, 4))
    for i in range(12):                                                               # leaves round its edge
        a = TAU * i / 12 + rng.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), -0.15)).normalized()
        leaf(bms["Leaf"], centre + d * radius * 0.85, (d + Vector((0, 0, -0.35))).normalized(), 0.07, 0.03, 0.015)
    for i in range(36):                                                               # baby's breath
        a, cz = rng.uniform(0, TAU), rng.uniform(0.15, 0.95)
        d = Vector((math.sqrt(1 - cz * cz) * math.cos(a), math.sqrt(1 - cz * cz) * math.sin(a), cz))
        for v in bmesh.ops.create_icosphere(bms["Pearl"], subdivisions=1, radius=0.0035)["verts"]:
            v.co += centre + d * (radius + 0.03)
    rib = bms["Ribbon"]                                                              # the ribbon-wrapped stem and a bow
    for v in bmesh.ops.create_cone(rib, cap_ends=True, segments=12, radius1=0.018, radius2=0.021, depth=0.19)["verts"]:
        v.co += Vector((0, 0, 0.1))
    for side in (-1, 1):
        verts = bmesh.ops.create_icosphere(rib, subdivisions=2, radius=0.022)["verts"]
        for v in verts:
            v.co = Vector((v.co.x * 1.3, v.co.y * 0.35, v.co.z * 0.75)) + Vector((side * 0.03, -0.022, 0.17))
        verts = bmesh.ops.create_cone(rib, cap_ends=True, segments=6, radius1=0.006, radius2=0.004, depth=0.14)["verts"]
        for v in verts:
            v.co = Matrix.Rotation(side * 0.25, 3, "Y") @ v.co + Vector((side * 0.02, -0.024, 0.1))
    obs = []
    for name, bm in bms.items():
        me = bpy.data.meshes.new("Bouquet_" + name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MAT[name])
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new("Bouquet_" + name, me)
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "Bouquet"
    # in her left hand: the stem across her palm (the hand's z: towards her thumb), gripped 9 cm up the stem
    hand = arm.data.bones["hand_l"]
    rest = arm.matrix_world @ hand.matrix_local
    grip = Matrix(((1, 0, 0, 0.03), (0, 1, 0, 0.078), (0, 0, 1, 0.0), (0, 0, 0, 1)))  # in the hand: palm side, mid-palm
    local = grip @ Matrix.Translation((0, 0, -0.09))                                   # its z = the hand's z (the stem)
    ob.parent = arm
    ob.parent_type = "BONE"
    ob.parent_bone = "hand_l"
    bpy.context.view_layer.update()
    ob.matrix_world = rest @ local
    return ob


# ------------------------------------------------------------------------------------------------ build
TORSO = bvh_of([body], keep=lambda p: arm_weight(p) < 0.85)
bodice()
skirt()
sash()
head_tree = bvh_of([body, bpy.data.objects["Hair_Long"]], keep=lambda p: arm_weight(p) < 0.3)
necklace(bvh_of([body]))
tiara(bvh_of([bpy.data.objects["Hair_Long"]]))
back_tree = bvh_of([body, bpy.data.objects["Hair_Long"], bpy.data.objects["Skirt"], bpy.data.objects["Bodice"]],
                   keep=lambda p: arm_weight(p) < 0.3)
grid = veil(back_tree)
add_bones(grid)
bouquet()

for mat in bpy.data.materials:                                                       # drop textures whose files are missing
    if mat.node_tree:
        for node in [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and (not n.image or not n.image.size[0])]:
            mat.node_tree.nodes.remove(node)
for img in bpy.data.images:                                                          # phone-sized textures; eyes opaque
    if img.name.startswith("T_Eye_Brown") and img.size[0]:
        px = bride_body.pixels(img)
        px[..., 3] = 1.0
        bride_body.store(img, px)
    if img.size[0] > 1024 and not ("BaseColor" in img.name and "Superhero" in img.name):
        img.scale(1024, 1024)
    if img.size[0]:
        img.pack()

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_animations=False, export_skins=True, export_morph=False,
                          export_yup=True, use_visible=False, export_image_format="WEBP", export_image_quality=88)
print("ok", OUT, sorted((o.name, len(o.data.polygons)) for o in bpy.data.objects if o.type == "MESH"), len(arm.data.bones), "bones")
