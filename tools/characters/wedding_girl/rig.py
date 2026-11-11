"""Her skeleton (game-engine bone names), skin weights, the chains her dress, sleeves and hair swing on, relaxed fingers,
and her motion-captured idles and walks (Microsoft Rocketbox, MIT) retargeted onto her.
python -I rig.py -- prep.blend rocketbox_repo out.blend"""
import sys, os, json
import bpy, bmesh
import numpy as np
from mathutils import Matrix, Vector

src, repo, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
scene = bpy.context.scene
scene.render.fps = 30
girl = bpy.data.objects["Girl"]
OUT = os.path.dirname(os.path.abspath(dst))

# ------------------------------------------------------------------------------------------------ her joints
# measured on her (metres; she faces -y, her left is +x)
C = {"pelvis": (0, -0.02, 0.86), "spine_01": (0, -0.015, 0.95), "spine_02": (0, -0.015, 1.05), "spine_03": (0, -0.02, 1.16),
     "neck_01": (0, -0.025, 1.355), "head": (0, -0.025, 1.43), "head_end": (0, -0.02, 1.62)}
SIDE = {"clavicle": (0.02, -0.03, 1.33), "upperarm": (0.15, -0.025, 1.31), "lowerarm": (0.33, -0.025, 1.262),
        "hand": (0.49, -0.03, 1.215), "hand_end": (0.6, -0.035, 1.19), "thigh": (0.08, -0.02, 0.81),
        "calf": (0.055, -0.025, 0.45), "foot": (0.045, -0.015, 0.125), "ball": (0.045, -0.095, 0.025),
        "ball_end": (0.045, -0.14, 0.012),
        "knuckles": (0.540, -0.033, 1.205), "fingers_mid": (0.572, -0.033, 1.200), "fingers_end": (0.606, -0.035, 1.197)}
SLEEVE_X = (0.25, 0.38, 0.51)                                     # her hanging sleeves: chains along her forearm
HAIR_X = (-0.13, -0.065, 0.0, 0.065, 0.13)                        # her hair down her back: chains across it
HAIR_Z = (1.44, 1.33, 1.22, 1.11)
CURL = (24, 32)                                                   # relaxed fingers: degrees at the knuckles, then mid-finger
BONES = [("Root", (0, 0, 0), (0, 0, 0.1), None), ("pelvis", C["pelvis"], C["spine_01"], "Root"),
         ("spine_01", C["spine_01"], C["spine_02"], "pelvis"), ("spine_02", C["spine_02"], C["spine_03"], "spine_01"),
         ("spine_03", C["spine_03"], C["neck_01"], "spine_02"), ("neck_01", C["neck_01"], C["head"], "spine_03"),
         ("head", C["head"], C["head_end"], "neck_01")]
for s, sg in (("l", 1), ("r", -1)):
    P = {k: (v[0] * sg, v[1], v[2]) for k, v in SIDE.items()}
    BONES += [(f"clavicle_{s}", P["clavicle"], P["upperarm"], "spine_03"), (f"upperarm_{s}", P["upperarm"], P["lowerarm"], f"clavicle_{s}"),
              (f"lowerarm_{s}", P["lowerarm"], P["hand"], f"upperarm_{s}"), (f"hand_{s}", P["hand"], P["hand_end"], f"lowerarm_{s}"),
              (f"fingers_01_{s}", P["knuckles"], P["fingers_mid"], f"hand_{s}"),
              (f"fingers_02_{s}", P["fingers_mid"], P["fingers_end"], f"fingers_01_{s}"),
              (f"thigh_{s}", P["thigh"], P["calf"], "pelvis"), (f"calf_{s}", P["calf"], P["foot"], f"thigh_{s}"),
              (f"foot_{s}", P["foot"], P["ball"], f"calf_{s}"), (f"ball_{s}", P["ball"], P["ball_end"], f"foot_{s}")]
    for k, sx in enumerate(SLEEVE_X):
        top = 1.31 - (sx - 0.15) * 0.267 - 0.03
        parent = f"upperarm_{s}" if sx < 0.33 else f"lowerarm_{s}"
        BONES += [(f"sleeve_{k}_1_{s}", (sx * sg, -0.02, top), (sx * sg, -0.02, top - 0.2), parent),
                  (f"sleeve_{k}_2_{s}", (sx * sg, -0.02, top - 0.2), (sx * sg, -0.02, top - 0.42), f"sleeve_{k}_1_{s}"),
                  (f"sleeve_{k}_end_{s}", (sx * sg, -0.02, top - 0.42), (sx * sg, -0.02, top - 0.46), f"sleeve_{k}_2_{s}")]
BODY = [b[0] for b in BONES if b[0] != "Root" and not b[0].startswith(("sleeve", "fingers"))]

# ------------------------------------------------------------------------------------------------ her mesh
bm = bmesh.new()                                                  # the simplified mesh joins her two boot toes: part them
bm.from_mesh(girl.data)
bridge = [f for f in bm.faces if max(v.co.z for v in f.verts) < 0.13 and max(abs(v.co.x) for v in f.verts) < 0.01]
bmesh.ops.delete(bm, geom=bridge, context="FACES")
bm.to_mesh(girl.data)
bm.free()
co = np.empty(len(girl.data.vertices) * 3)
girl.data.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
ax = np.abs(x)
segs = {name: (np.array(h, float), np.array(t, float)) for name, h, t, p in BONES if name in BODY}


def leg_gap(s):
    """How far outside her leg's own surface (thigh, calf, boot) each vertex is."""
    best = np.full(len(co), 9.0)
    for bone, r0, r1 in ((f"thigh_{s}", 0.075, 0.055), (f"calf_{s}", 0.055, 0.045), (f"foot_{s}", 0.045, 0.035), (f"ball_{s}", 0.035, 0.03)):
        a, b = segs[bone]
        ab = b - a
        t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1)
        best = np.minimum(best, np.linalg.norm(co - (a + t[:, None] * ab), axis=1) - (r0 + (r1 - r0) * t))
    return best


# her dress: what is off her legs below her hips (her boots, heels and soles are hers)
skirt = np.clip((np.minimum(leg_gap("l"), leg_gap("r")) - 0.006) / 0.02, 0, 1) * (z < 0.86)
skirt[(z < 0.17) & (ax < 0.09) & (y > -0.16) & (y < 0.07)] = 0

# it hangs on chains of bones around her hips, swung in the web by a light cloth simulation
CH = 16
radial = np.hypot(x, y + 0.02)
around = np.arctan2(y + 0.02, x)
CHAINS = []                                                       # (index, angle, hem height)
for k in range(CH):
    a = 2 * np.pi * k / CH
    sel = (skirt > 0.5) & (np.abs(np.angle(np.exp(1j * (around - a)))) < np.pi / CH * 1.3)
    if sel.sum() < 30:
        continue
    hem = np.percentile(z[sel], 3)
    if 0.86 - hem < 0.12:
        continue
    pts, r = [], np.median(radial[sel & (z > 0.75)]) * 0.9
    for f in (0, 1 / 3, 2 / 3, 1):
        zt = 0.86 - f * (0.86 - hem)
        band = sel & (np.abs(z - zt) < 0.03)
        if band.sum() > 3:
            r = np.median(radial[band]) * 0.9
        pts.append(np.array((r * np.cos(a), -0.02 + r * np.sin(a), zt)))
    end = pts[3] + (pts[3] - pts[2]) / np.linalg.norm(pts[3] - pts[2]) * 0.03
    BONES += [(f"skirt_{k}_1", pts[0], pts[1], "pelvis"), (f"skirt_{k}_2", pts[1], pts[2], f"skirt_{k}_1"),
              (f"skirt_{k}_3", pts[2], pts[3], f"skirt_{k}_2"), (f"skirt_{k}_end", pts[3], end, f"skirt_{k}_3")]
    CHAINS.append((k, a, hem))

# her hair down her back: chains from the back of her head, just inside its surface
for k, hx in enumerate(HAIR_X):
    pts, hy = [], 0.08
    for hz in HAIR_Z:
        near = (np.abs(x - hx) < 0.035) & (np.abs(z - hz) < 0.025) & (y > 0.0)
        if near.sum() > 3:
            hy = y[near].max() - 0.02
        pts.append(np.array((hx, hy, hz)))
    end = pts[-1] + (0, 0, -0.04)
    names_k = [f"hair_{k}_1", f"hair_{k}_2", f"hair_{k}_3", f"hair_{k}_end"]
    for i, n in enumerate(names_k):
        BONES.append((n, pts[i], pts[i + 1] if i < 3 else end, "head" if i == 0 else names_k[i - 1]))
print("parted", len(bridge), "faces between her boots; dress chains", len(CHAINS), "hair chains", len(HAIR_X))

# ------------------------------------------------------------------------------------------------ her skeleton
arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for name, h, t, parent in BONES:
    eb = arm_data.edit_bones.new(name)
    eb.head, eb.tail = [float(v) for v in h], [float(v) for v in t]
    if name.startswith(("thigh", "calf", "foot", "ball", "pelvis", "spine", "neck", "head")):
        eb.align_roll(Vector((0, -1, 0)))
    if parent:
        eb.parent = arm_data.edit_bones[parent]
bpy.ops.object.mode_set(mode="OBJECT")

# ------------------------------------------------------------------------------------------------ weights


def dist(name):
    a, b = segs[name]
    ab = b - a
    t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(co - (a + t[:, None] * ab), axis=1)


names = [n for n, h, t, p in BONES if n != "Root"]
col = {n: j for j, n in enumerate(names)}
D = np.stack([dist(n) if n in segs else np.full(len(co), 9.0) for n in names], 1)
allow = np.zeros_like(D, bool)
sleeve = (ax > 0.2) & (z < 1.25) & ((z > 0.9) | (ax > 0.29))    # her hanging sleeves (not her dress's sides)
hair = ((z > 1.36) & (ax < 0.17)) | ((y > 0.045) & (z > 1.0) & (ax < 0.17))   # her hair beside and behind her
for n in BODY:
    ok = np.ones(len(co), bool)
    side = 1 if n.endswith("_l") else -1
    if n.startswith(("clavicle", "upperarm", "lowerarm", "hand")):
        ok = ((z > 0.95) | (ax > 0.2) & (z > 0.6)) & (np.sign(x) == side)
        if not n.startswith("clavicle"):
            ok &= ax > 0.13
    if n.startswith(("thigh", "calf", "foot", "ball")):
        ok = (z < 0.9) & (np.sign(x) == side)
    if not n.startswith(("upperarm", "lowerarm", "hand")):
        ok &= ~sleeve
    if n not in ("spine_02", "spine_03", "neck_01", "head"):
        ok &= ~hair
    allow[:, col[n]] = ok
W = np.where(allow, 1.0 / np.maximum(D, 0.008) ** 4, 0)
W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)


def give(amount, shares):
    """Moves `amount` (0..1 per vertex) of every vertex's weight onto bones: shares = {bone: fraction per vertex}."""
    global W
    W = W * (1 - amount)[:, None]
    for bone, share in shares.items():
        W[:, col[bone]] += amount * share


def segments(f, n):
    """Blend along a chain of n bones: f = 0 at its top .. 1 at its end."""
    w = np.stack([np.clip(1 - np.abs(f - (j + 0.5) / n) * n, 0, 1) for j in range(n)], 1)
    w[f < 0.5 / n, 0] = 1
    w[f > 1 - 0.5 / n, n - 1] = 1
    return w / w.sum(1, keepdims=True)


for sd, sg in (("l", 1), ("r", -1)):
    mine = np.sign(x) == sg
    # the drape of her sleeve hangs on its chains
    top = 1.31 - (ax - 0.15) * 0.267
    hang = np.clip((top - 0.045 - z) / 0.1, 0, 1) * sleeve * mine
    f = np.clip(np.interp(ax, SLEEVE_X, np.arange(len(SLEEVE_X))), 0, len(SLEEVE_X) - 1)
    down = np.clip((top - z - 0.15) / 0.16, 0, 1)
    shares = {}
    for k in range(len(SLEEVE_X)):
        wk = np.clip(1 - np.abs(f - k), 0, 1)
        shares[f"sleeve_{k}_1_{sd}"], shares[f"sleeve_{k}_2_{sd}"] = wk * (1 - down), wk * down
    give(hang, shares)
    # her fingers (not her thumb, which lies along them)
    fingers = mine & (z > 1.1) & ~((y < -0.064) & (ax < 0.558))
    f1 = np.clip((ax - 0.530) / 0.018, 0, 1) * fingers
    f2 = np.clip((ax - 0.563) / 0.016, 0, 1) * fingers
    f1, f2 = f1 * f1 * (3 - 2 * f1), f2 * f2 * (3 - 2 * f2)
    give(f1, {f"fingers_01_{sd}": 1 - f2 / np.maximum(f1, 1e-9), f"fingers_02_{sd}": f2 / np.maximum(f1, 1e-9)})

# her dress doesn't follow her legs: it hangs from her hips on its chains
legs = [col[n] for n in names if n.startswith(("thigh", "calf", "foot", "ball"))]
before = W[:, legs].sum(1)
W[:, legs] *= (1 - skirt)[:, None]
W[:, col["pelvis"]] += before - W[:, legs].sum(1)


def across(position, places, loop):
    """Share between the two neighbouring chains: returns per-chain fractions (n vertices x n chains)."""
    places = np.asarray(places, float)
    n = len(places)
    out = np.zeros((len(position), n))
    if loop:
        ext = np.r_[places, places[0] + 2 * np.pi]
        p = (position - places[0]) % (2 * np.pi) + places[0]
    else:
        ext, p = places, np.clip(position, places[0], places[-1])
    i0 = np.clip(np.searchsorted(ext, p, side="right") - 1, 0, len(ext) - 2)
    t = (p - ext[i0]) / (ext[i0 + 1] - ext[i0])
    np.add.at(out, (np.arange(len(p)), i0 % n), 1 - t)
    np.add.at(out, (np.arange(len(p)), (i0 + 1) % n), t)
    return out


order_c = np.argsort([c[1] for c in CHAINS])
share = across(around, [CHAINS[i][1] for i in order_c], True)
hem_v = share @ np.array([CHAINS[i][2] for i in order_c])
seg = segments(np.clip((0.86 - z) / np.maximum(0.86 - hem_v, 0.05), 0, 1), 3)
amount = W[:, col["pelvis"]] * skirt
give(amount, {f"skirt_{CHAINS[i][0]}_{j + 1}": share[:, c] * seg[:, j] for c, i in enumerate(order_c) for j in range(3)})

# her hair down her back swings on its chains, from the back of her head
amount = (np.clip((y - 0.03) / 0.025, 0, 1) * np.clip((0.19 - ax) / 0.04, 0, 1) * np.clip((z - 1.07) / 0.05, 0, 1)
          * np.clip((HAIR_Z[0] + 0.03 - z) / 0.06, 0, 1))
share = across(x, HAIR_X, False)
seg = segments(np.clip((HAIR_Z[0] - z) / (HAIR_Z[0] - HAIR_Z[-1]), 0, 1), 3)
give(amount, {f"hair_{k}_{j + 1}": share[:, k] * seg[:, j] for k in range(len(HAIR_X)) for j in range(3)})

W = W / W.sum(1, keepdims=True)
edges = np.array([e.vertices[:] for e in girl.data.edges])        # smoothed along the mesh, so seams and folds bend together
for _ in range(3):
    acc = np.zeros_like(W)
    cnt = np.zeros(len(W))
    np.add.at(acc, edges[:, 0], W[edges[:, 1]])
    np.add.at(acc, edges[:, 1], W[edges[:, 0]])
    np.add.at(cnt, edges[:, 0], 1)
    np.add.at(cnt, edges[:, 1], 1)
    W = np.where(cnt[:, None] > 0, 0.5 * W + 0.5 * acc / np.maximum(cnt, 1)[:, None], W)
idx = np.argsort(-W, 1)[:, :4]                                    # the four strongest
keep = np.zeros_like(W, bool)
np.put_along_axis(keep, idx, True, 1)
W = np.where(keep & (W > 0.01), W, 0)
W = W / W.sum(1, keepdims=True)
for n, j in col.items():
    nz = np.where(W[:, j] > 0)[0]
    if len(nz):
        g = girl.vertex_groups.new(name=n)
        for i in nz:
            g.add([int(i)], float(W[i, j]), "REPLACE")
girl.parent = arm
girl.modifiers.new("Armature", "ARMATURE").object = arm

# ------------------------------------------------------------------------------------------------ motion
MAP = {"Bip01 Pelvis": "pelvis", "Bip01 Spine": "spine_01", "Bip01 Spine1": "spine_02", "Bip01 Spine2": "spine_03",
       "Bip01 Neck": "neck_01", "Bip01 Head": "head"}
for s, t in (("L", "l"), ("R", "r")):
    MAP.update({f"Bip01 {s} Clavicle": f"clavicle_{t}", f"Bip01 {s} UpperArm": f"upperarm_{t}",
                f"Bip01 {s} Forearm": f"lowerarm_{t}", f"Bip01 {s} Hand": f"hand_{t}", f"Bip01 {s} Thigh": f"thigh_{t}",
                f"Bip01 {s} Calf": f"calf_{t}", f"Bip01 {s} Foot": f"foot_{t}", f"Bip01 {s} Toe0": f"ball_{t}"})
INV = {v: k for k, v in MAP.items()}
ANIMS = os.path.join(repo, "Assets/Animations")
CLIPS = {                                                         # name: (folder, Rocketbox clip, frame her left foot lands)
    "Idle": ("static", "f_idle_neutral_01", None), "Idle_Look": ("static", "f_idle_look_around_01", None),
    "Idle_Shift": ("static", "f_idle_move_01", None),
    "Walk_Slow": ("xy", "f_walk_stroll_01", 12), "Walk": ("xy", "f_walk_neutral_01", 9), "Walk_Fast": ("xy", "f_walk_fast_02", 8),
}
rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
order = []


def walk_tree(b):
    order.append(b)
    for c in b.children:
        walk_tree(c)


walk_tree(arm.data.bones["Root"])
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
CURLS = {}                                                        # her fingers' relaxed curl, in each bone's own axes
for s, sg in (("l", 1), ("r", -1)):
    for n, deg in zip((f"fingers_01_{s}", f"fingers_02_{s}"), CURL):
        r = rest[n].to_3x3()
        CURLS[n] = (r.inverted() @ Matrix.Rotation(np.radians(deg) * sg, 3, "Y") @ r).to_4x4()


def align(a, b):
    """The smallest rotation taking direction a onto b."""
    return a.normalized().rotation_difference(b.normalized()).to_matrix()


def use(act):
    arm.animation_data_create()
    arm.animation_data.action = act
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]


def bring(name, folder, clip, lands):
    """Her motion from a Rocketbox clip: each of her bones turns as its counterpart does, from a rest in which it is
    first lined up with that counterpart (the two skeletons rest in different poses). Walks are kept in place and start
    as her left foot lands, so they blend in step. Returns the action and how far a walk travels per loop."""
    before = set(bpy.data.objects)
    bpy.ops.wm.fbx_import(filepath=os.path.join(ANIMS, f"all_animations_max_motextr_{folder}", clip + ".max.fbx"))
    new = [o for o in bpy.data.objects if o not in before]
    srco = next(o for o in new if o.type == "ARMATURE")
    took = srco.animation_data.action
    sbones = srco.data.bones
    f0, f1 = (int(round(v)) for v in took.frame_range)
    count = f1 - f0
    scene.frame_set(f0)
    raw = {b.name: (srco.matrix_world @ b.matrix_local) for b in sbones}
    side = raw["Bip01 L Thigh"].translation - raw["Bip01 R Thigh"].translation        # her right to left: +x
    turn = Matrix.Rotation(-np.arctan2(side.y, side.x), 4, "Z")                        # face the clip her way
    srest = {n: turn @ m for n, m in raw.items()}
    line = {}                                                       # the lining-up turn per bone
    for tname, sname in INV.items():
        tb = arm.data.bones[tname]
        if tname.startswith(("pelvis", "spine", "neck", "head", "clavicle", "foot", "ball")):
            line[tname] = Matrix.Identity(3)                        # her trunk and feet rest like the clip's
            continue
        nxt = next((c for c in arm.data.bones if c.name in INV and (c.head_local - tb.tail_local).length < 2e-3), None)
        tip = sbones[INV[nxt.name]] if nxt else next(c for c in sbones[sname].children if c.name.endswith("Finger2"))
        line[tname] = align(tb.tail_local - tb.head_local, srest[tip.name].translation - srest[sname].translation)
    def leg(joints):                                                 # hip to knee to ankle
        return (joints[1] - joints[0]).length + (joints[2] - joints[1]).length

    k = (leg([rest[n].translation for n in ("thigh_l", "calf_l", "foot_l")])        # her legs against the clip's: how far
         / leg([srest[n].translation for n in ("Bip01 L Thigh", "Bip01 L Calf", "Bip01 L Foot")]))   # she really steps

    def pelvis_at(f):
        scene.frame_set(f)
        return (turn @ srco.matrix_world @ srco.pose.bones["Bip01 Pelvis"].matrix).translation.copy()

    path = [pelvis_at(f0 + i) for i in range(count + 1)]
    travel = (path[-1] - path[0]) if lands is not None else Vector()
    travel.z = 0
    still = [p - travel * (i / count) for i, p in enumerate(path)]
    centre = sum(still, Vector()) / len(still)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    use(act)
    for out in range(count + 1):
        i = (out + (lands or 0)) % count if lands is not None else out
        scene.frame_set(f0 + i)
        pose = {}
        for b in order:
            base = pose[b.parent.name] @ rest[b.parent.name].inverted() @ rest[b.name] if b.parent else rest[b.name]
            sname = INV.get(b.name)
            if sname:
                sw = turn @ srco.matrix_world @ srco.pose.bones[sname].matrix
                rot = sw.to_3x3().normalized() @ srest[sname].to_3x3().normalized().inverted() @ line[b.name] @ rest[b.name].to_3x3()
                head = base.translation
                if b.name == "pelvis":
                    head = rest["pelvis"].translation + (still[i] - Vector((centre.x, centre.y, srest["Bip01 Pelvis"].translation.z))) * k
                pose[b.name] = Matrix.Translation(head) @ rot.to_4x4()
            elif b.name in CURLS:
                pose[b.name] = base @ CURLS[b.name]
            elif b.name.startswith("sleeve_") and b.name[-4:-1] == "_1_":   # her sleeves keep hanging as they rest
                q = base.to_quaternion().slerp(rest[b.name].to_quaternion(), 0.9)
                pose[b.name] = Matrix.Translation(base.translation) @ q.to_matrix().to_4x4()
            elif b.name.startswith("hair_") and b.name.endswith("_1"):      # her hair lies on her back as her head turns
                on_back = (pose["spine_03"] @ rest["spine_03"].inverted() @ rest[b.name]).to_quaternion()
                q = base.to_quaternion().slerp(on_back, 0.7)
                pose[b.name] = Matrix.Translation(base.translation) @ q.to_matrix().to_4x4()
            else:
                pose[b.name] = base
                continue                                             # (follows its parent: no keys)
            basis = base.inverted() @ pose[b.name]
            pb = arm.pose.bones[b.name]
            pb.rotation_quaternion = basis.to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=out)
            if b.name == "pelvis":
                pb.location = basis.translation
                pb.keyframe_insert("location", frame=out)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.actions.remove(took)
    return act, travel.length * k, count / 30


info = {}
for n, (folder, clip, lands) in CLIPS.items():
    act, stride, seconds = bring(n, folder, clip, lands)
    info[n] = {"seconds": round(seconds, 4), "stride": round(stride, 4), "speed": round(stride / seconds, 4)}
    print(n, info[n])
json.dump(info, open(os.path.join(OUT, "motion.json"), "w"), indent=1)
use(bpy.data.actions["Idle"])
bpy.data.objects.remove(bpy.data.objects["High"], do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=dst)
