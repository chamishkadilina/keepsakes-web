"""Her skeleton (game-engine bone names), skin weights and motion-captured idle + walk (Microsoft Rocketbox, MIT).
python -I rig.py -- prep.blend rocketbox_repo out.blend"""
import sys, os, json
import bpy
import numpy as np
from mathutils import Matrix, Vector

src, repo, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
scene = bpy.context.scene
scene.render.fps = 30
girl = bpy.data.objects["Girl"]
OUT = os.path.dirname(os.path.abspath(dst))

# her joints, measured on her (metres; she faces -y, her left is +x)
C = {"pelvis": (0, -0.02, 0.86), "spine_01": (0, -0.015, 0.95), "spine_02": (0, -0.015, 1.05), "spine_03": (0, -0.02, 1.16),
     "neck_01": (0, -0.025, 1.355), "head": (0, -0.025, 1.43), "head_end": (0, -0.02, 1.62)}
SIDE = {"clavicle": (0.02, -0.03, 1.33), "upperarm": (0.15, -0.025, 1.31), "lowerarm": (0.33, -0.025, 1.262),
        "hand": (0.49, -0.03, 1.215), "hand_end": (0.6, -0.035, 1.19), "thigh": (0.08, -0.02, 0.81),
        "calf": (0.055, -0.025, 0.45), "foot": (0.045, -0.015, 0.125), "ball": (0.045, -0.095, 0.025),
        "ball_end": (0.045, -0.14, 0.012)}
SLEEVE_X = (0.25, 0.38, 0.51)
BONES = [("Root", (0, 0, 0), (0, 0, 0.1), None), ("pelvis", C["pelvis"], C["spine_01"], "Root"),
         ("spine_01", C["spine_01"], C["spine_02"], "pelvis"), ("spine_02", C["spine_02"], C["spine_03"], "spine_01"),
         ("spine_03", C["spine_03"], C["neck_01"], "spine_02"), ("neck_01", C["neck_01"], C["head"], "spine_03"),
         ("head", C["head"], C["head_end"], "neck_01")]
for s, sg in (("l", 1), ("r", -1)):
    P = {k: (v[0] * sg, v[1], v[2]) for k, v in SIDE.items()}
    BONES += [(f"clavicle_{s}", P["clavicle"], P["upperarm"], "spine_03"), (f"upperarm_{s}", P["upperarm"], P["lowerarm"], f"clavicle_{s}"),
              (f"lowerarm_{s}", P["lowerarm"], P["hand"], f"upperarm_{s}"), (f"hand_{s}", P["hand"], P["hand_end"], f"lowerarm_{s}"),
              (f"thigh_{s}", P["thigh"], P["calf"], "pelvis"), (f"calf_{s}", P["calf"], P["foot"], f"thigh_{s}"),
              (f"foot_{s}", P["foot"], P["ball"], f"calf_{s}"), (f"ball_{s}", P["ball"], P["ball_end"], f"foot_{s}")]
    for k, sx in enumerate(SLEEVE_X):                             # her hanging sleeves: chains along her forearm
        top = 1.31 - (sx - 0.15) * 0.267 - 0.03
        parent = f"upperarm_{s}" if sx < 0.33 else f"lowerarm_{s}"
        BONES += [(f"sleeve_{k}_1_{s}", (sx * sg, -0.02, top), (sx * sg, -0.02, top - 0.2), parent),
                  (f"sleeve_{k}_2_{s}", (sx * sg, -0.02, top - 0.2), (sx * sg, -0.02, top - 0.42), f"sleeve_{k}_1_{s}")]
arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for name, h, t, parent in BONES:
    eb = arm_data.edit_bones.new(name)
    eb.head, eb.tail = h, t
    if name.startswith(("thigh", "calf", "foot", "ball", "pelvis", "spine", "neck", "head")):
        eb.align_roll(Vector((0, -1, 0)))
    if parent:
        eb.parent = arm_data.edit_bones[parent]
bpy.ops.object.mode_set(mode="OBJECT")

# ------------------------------------------------------------------------------------------------ weights
import bmesh                                       # the simplified mesh joins her two boot toes: part them
bm = bmesh.new(); bm.from_mesh(girl.data)
bridge = [f for f in bm.faces if max(v.co.z for v in f.verts) < 0.13 and max(abs(v.co.x) for v in f.verts) < 0.01]
bmesh.ops.delete(bm, geom=bridge, context="FACES")
bm.to_mesh(girl.data); bm.free()
print("parted", len(bridge), "faces between her boots")
co = np.empty(len(girl.data.vertices) * 3); girl.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
segs = {name: (np.array(h, float), np.array(t, float)) for name, h, t, p in BONES if name != "Root"}


def dist(name):
    a, b = segs[name]
    ab = b - a
    t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(co - (a + t[:, None] * ab), axis=1)


names = list(segs)
D = np.stack([dist(n) for n in names], 1)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
ax = np.abs(x)
allow = np.ones_like(D, bool)
for j, n in enumerate(names):
    if n.startswith(("clavicle", "upperarm", "lowerarm", "hand")):
        allow[:, j] = ((z > 0.95) | (ax > 0.2) & (z > 0.6)) & (np.sign(x) == (1 if n.endswith("_l") else -1))
        if n.startswith(("upperarm", "lowerarm", "hand")):
            allow[:, j] &= ax > 0.13
    if n.startswith("sleeve"):
        allow[:, j] = False
    if n.startswith(("thigh", "calf", "foot", "ball")):
        allow[:, j] = (z < 0.9) & (np.sign(x) == (1 if n.endswith("_l") else -1))
sleeve = (ax > 0.2) & (z < 1.25) & ((z > 0.9) | (ax > 0.29))   # her hanging sleeves (not her dress's sides)
for j, n in enumerate(names):
    if sleeve.any() and not n.startswith(("upperarm", "lowerarm", "hand")):
        allow[sleeve, j] = False
hair = ((z > 1.36) & (ax < 0.17)) | ((y > 0.045) & (z > 1.0) & (ax < 0.17))   # her hair beside and behind her
for j, n in enumerate(names):
    if hair.any() and n not in ("spine_02", "spine_03", "neck_01", "head"):
        allow[hair, j] = False
D = np.where(allow, D, 9.0)
W = 1.0 / np.maximum(D, 0.008) ** 4
W[~allow] = 0
# her dress: away from her legs it hangs from her hips and only follows her thighs a little
def leg_gap(s):
    """How far outside her leg's own surface (thigh, calf, boot) each vertex is."""
    best = np.full(len(co), 9.0)
    for bone, r0, r1 in ((f"thigh_{s}", 0.075, 0.055), (f"calf_{s}", 0.055, 0.045), (f"foot_{s}", 0.045, 0.035), (f"ball_{s}", 0.035, 0.03)):
        a, b = segs[bone]
        ab = b - a
        t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(co - (a + t[:, None] * ab), axis=1) - (r0 + (r1 - r0) * t)
        best = np.minimum(best, d)
    return best
gap = np.minimum(leg_gap("l"), leg_gap("r"))
skirt = np.clip((gap - 0.006) / 0.02, 0, 1) * (z < 0.86)
boots = (z < 0.17) & (ax < 0.09) & (y > -0.16) & (y < 0.07)        # her boots, heels and soles are hers, not the dress's
skirt[boots] = 0
pel = names.index("pelvis")
legs = [j for j, n in enumerate(names) if n.startswith(("thigh", "calf", "foot", "ball"))]
W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
for sd, sg in (("l", 1), ("r", -1)):                            # the drape hangs on its chains
    arm_z = 1.31 - (ax - 0.15) * 0.267                          # her arm's axis along its length
    hang = np.clip((arm_z - 0.045 - z) / 0.1, 0, 1) * sleeve * (np.sign(x) == sg)
    W *= (1 - hang)[:, None]
    xs = np.array(SLEEVE_X)
    f = np.clip(np.interp(ax, xs, np.arange(len(xs))), 0, len(xs) - 1)
    k0 = np.floor(f).astype(int); k1 = np.minimum(k0 + 1, len(xs) - 1); a1 = f - k0
    top = 1.31 - (ax - 0.15) * 0.267 - 0.03
    down = np.clip((top - z - 0.12) / 0.16, 0, 1)
    for k in range(len(xs)):
        wk = np.where(k0 == k, 1 - a1, 0) + np.where(k1 == k, a1, 0) * (k1 != k0)
        W[:, names.index(f"sleeve_{k}_1_{sd}")] += hang * wk * (1 - down)
        W[:, names.index(f"sleeve_{k}_2_{sd}")] += hang * wk * down
before = W[:, legs].sum(1)
for j in legs:                                     # her dress follows her thighs a little, never her calves or feet
    W[:, j] *= 1 - skirt * (0.75 if names[j].startswith("thigh") else 1.0)
W[:, pel] += before - W[:, legs].sum(1)
W = W / W.sum(1, keepdims=True)
# smooth along the mesh so seams and folds bend together
edges = np.array([e.vertices[:] for e in girl.data.edges])
for _ in range(3):
    acc = np.zeros_like(W); cnt = np.zeros(len(W))
    np.add.at(acc, edges[:, 0], W[edges[:, 1]]); np.add.at(acc, edges[:, 1], W[edges[:, 0]])
    np.add.at(cnt, edges[:, 0], 1); np.add.at(cnt, edges[:, 1], 1)
    W = np.where(cnt[:, None] > 0, 0.5 * W + 0.5 * acc / np.maximum(cnt, 1)[:, None], W)
# keep the four strongest
idx = np.argsort(-W, 1)[:, :4]
keep = np.zeros_like(W, bool); np.put_along_axis(keep, idx, True, 1)
W = np.where(keep & (W > 0.01), W, 0); W = W / W.sum(1, keepdims=True)
for j, n in enumerate(names):
    g = girl.vertex_groups.new(name=n)
    nz = np.where(W[:, j] > 0)[0]
    for i in nz:
        g.add([int(i)], float(W[i, j]), "REPLACE")
girl.parent = arm
mod = girl.modifiers.new("Armature", "ARMATURE"); mod.object = arm

# ------------------------------------------------------------------------------------------------ motion
MAP = {"Bip01 Pelvis": "pelvis", "Bip01 Spine": "spine_01", "Bip01 Spine1": "spine_02", "Bip01 Spine2": "spine_03",
       "Bip01 Neck": "neck_01", "Bip01 Head": "head"}
for s, t in (("L", "l"), ("R", "r")):
    MAP.update({f"Bip01 {s} Clavicle": f"clavicle_{t}", f"Bip01 {s} UpperArm": f"upperarm_{t}",
                f"Bip01 {s} Forearm": f"lowerarm_{t}", f"Bip01 {s} Hand": f"hand_{t}", f"Bip01 {s} Thigh": f"thigh_{t}",
                f"Bip01 {s} Calf": f"calf_{t}", f"Bip01 {s} Foot": f"foot_{t}", f"Bip01 {s} Toe0": f"ball_{t}"})
    for fi, fname in enumerate(("thumb", "index", "middle", "ring", "pinky")):
        for j, suffix in enumerate(("", "1", "2")):
            MAP[f"Bip01 {s} Finger{fi}{suffix}"] = f"{fname}_0{j + 1}_{t}"
INV = {v: k for k, v in MAP.items() if v in arm.data.bones}
ANIMS = os.path.join(repo, "Assets/Animations")
CLIPS = {"Idle": ("static", "f_idle_neutral_01"), "Walk": ("xy", "f_walk_stroll_01")}

rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
order = []


def walk_tree(b):
    order.append(b)
    for c in b.children:
        walk_tree(c)


for b in arm.data.bones:
    if b.parent is None:
        walk_tree(b)
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"


def first_child(bones, name):
    return next((c for c in bones[name].children), None)


def align(a, b):
    """The smallest rotation taking direction a onto b."""
    return a.normalized().rotation_difference(b.normalized()).to_matrix()


def use(act):
    arm.animation_data_create()
    arm.animation_data.action = act
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]


def bring(name, folder, clip):
    """Her motion from a Rocketbox clip: each of her bones turns as its counterpart does, from a rest in which it is
    first lined up with that counterpart (the two skeletons rest in different poses)."""
    before = set(bpy.data.objects)
    bpy.ops.wm.fbx_import(filepath=os.path.join(ANIMS, f"all_animations_max_motextr_{folder}", clip + ".max.fbx"))
    new = [o for o in bpy.data.objects if o not in before]
    srco = next(o for o in new if o.type == "ARMATURE")
    took = srco.animation_data.action
    sbones = srco.data.bones
    scene.frame_set(int(took.frame_range[0]))
    raw = {b.name: (srco.matrix_world @ b.matrix_local) for b in sbones}
    across = raw["Bip01 L Thigh"].translation - raw["Bip01 R Thigh"].translation      # her right to left: +x
    turn = Matrix.Rotation(-np.arctan2(across.y, across.x), 4, "Z")                    # face the clip her way
    srest = {n: turn @ m for n, m in raw.items()}
    # rest directions (to each bone's first child) of both skeletons, and the lining-up turn per bone
    line = {}
    for tname, sname in INV.items():
        tb = arm.data.bones[tname]
        if tname.startswith(("pelvis", "spine", "neck", "head", "clavicle", "foot", "ball")):
            line[tname] = Matrix.Identity(3)                        # her trunk rests upright like the clip's
            continue
        dt = tb.tail_local - tb.head_local                          # her limbs point at the next joint
        nxt = next((c for c in arm.data.bones if c.name in INV and (c.head_local - tb.tail_local).length < 2e-3), None)
        if nxt is not None:
            send = srest[INV[nxt.name]].translation
        else:                                                       # ends: the clip's "Nub" marks the tip
            nub = next((c for c in sbones[sname].children if c.name.endswith("Nub")), None)
            if nub is None:
                line[tname] = Matrix.Identity(3)
                continue
            send = srest[nub.name].translation
        line[tname] = align(dt, send - srest[sname].translation)
    hip_t = rest["pelvis"].translation.z
    hip_s = srest["Bip01 Pelvis"].translation.z
    k = hip_t / hip_s
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    use(act)
    f0, f1 = (int(round(v)) for v in took.frame_range)
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        pose = {}
        for b in order:
            base = pose[b.parent.name] @ rest[b.parent.name].inverted() @ rest[b.name] if b.parent else rest[b.name]
            sname = INV.get(b.name)
            if sname:
                sw = turn @ srco.matrix_world @ srco.pose.bones[sname].matrix
                delta = sw.to_3x3().normalized() @ srest[sname].to_3x3().normalized().inverted()
                rot = delta @ line[b.name] @ rest[b.name].to_3x3()
                head = base.translation
                if b.name == "pelvis":
                    p = sw.translation
                    head = Vector((p.x * k, p.y * k, p.z * k))
                pose[b.name] = Matrix.Translation(head) @ rot.to_4x4()
            elif b.name.startswith("sleeve_"):                    # keeps hanging as it rests
                q = base.to_quaternion().slerp(rest[b.name].to_quaternion(), 0.9)
                pose[b.name] = Matrix.Translation(base.translation) @ q.to_matrix().to_4x4()
            else:
                pose[b.name] = base
            if b.name.startswith("skirt_"):
                continue
            basis = base.inverted() @ pose[b.name]
            pb = arm.pose.bones[b.name]
            pb.rotation_quaternion = basis.to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=f - f0)
            if b.name == "pelvis":
                pb.location = basis.translation
                pb.keyframe_insert("location", frame=f - f0)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.actions.remove(took)
    return act


acts = {n: bring(n, *spec) for n, spec in CLIPS.items()}

walk = acts["Walk"]
use(walk)
pel = arm.pose.bones["pelvis"]
fr = [int(v) for v in walk.frame_range]
scene.frame_set(fr[0]); start = (arm.matrix_world @ pel.head).copy()
scene.frame_set(fr[1]); travel = (arm.matrix_world @ pel.head) - start
for f in range(fr[0], fr[1] + 1):                                # in place: take out her travel forwards
    scene.frame_set(f)
    t = (f - fr[0]) / max(1, fr[1] - fr[0])
    m = pel.matrix.copy(); m.translation -= Vector((travel.x * t, travel.y * t, 0)); pel.matrix = m
    pel.keyframe_insert("location", frame=f)
speed = travel.length / ((fr[1] - fr[0]) / 30)
print(f"walk speed {speed:.3f} m/s")
json.dump({"walk_speed": speed}, open(os.path.join(OUT, "motion.json"), "w"))
use(acts["Idle"])
bpy.data.objects.remove(bpy.data.objects["High"], do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=dst)
