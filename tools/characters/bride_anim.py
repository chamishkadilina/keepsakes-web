"""Animates the bride (bride_build.py's glb) and saves bride.blend:

  Idle, Walk, Sit_Down, Sit_Idle, Sit_Up   her body from the Universal Animation Libraries (CC0), holding her bouquet
                                            in both hands at her waist (in her lap when seated, the gown draped)
  Wave, Blow_Kiss, Twirl, Curtsy,           the emotes, made here on her skeleton (the bouquet stays in her left hand)
  Smell_Flowers, Slow_Dance (loops)

The skirt and veil bones are left to the web (it swings them), so they are not keyed, except the skirt's when she
sits (how the gown lies on her lap; the web swings it from there).

  python -I bride_anim.py -- <bride_base.glb> <UAL1_Standard.glb> <UAL2_Standard.glb> <out.blend>
"""
import math
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

CHAR, UAL1, UAL2, OUT = sys.argv[sys.argv.index("--") + 1:]
FPS = 30
KEEP = {"Idle_Loop": "_Idle", "Walk_Formal_Loop": "_Walk", "Sitting_Enter": "_Sit_Down", "Sitting_Idle_Loop": "_Sit_Idle",
        "Sitting_Exit": "_Sit_Up"}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = FPS


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


for path in (UAL1, UAL2):                                                          # the libraries: keep the actions we use
    for o in import_glb(path):
        bpy.data.objects.remove(o, do_unlink=True)
for act in list(bpy.data.actions):
    if act.name in KEEP:
        act.name = KEEP[act.name]
    else:
        bpy.data.actions.remove(act)

objs = import_glb(CHAR)
arm = next(o for o in objs if o.type == "ARMATURE")
for o in objs:
    if o.type == "MESH":
        o.hide_viewport = True                                                      # faster pose updates
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "QUATERNION"
if arm.animation_data is None:
    arm.animation_data_create()
FREE = {b.name for b in pb if b.name.startswith(("skirt_", "veil_"))}             # swung by the web, not keyed
REST = {b.name: b.matrix_local.copy() for b in arm.data.bones}


def use(action):
    arm.animation_data.action = action
    if action and action.slots:
        arm.animation_data.action_slot = action.slots[0]


def sample(action, frames):
    """Each bone's local transform at each frame of `action` (looped)."""
    use(action)
    start, end = (int(round(v)) for v in action.frame_range)
    out = []
    for f in frames:
        scene.frame_set(start + f % max(1, end - start))
        out.append({b.name: (b.location.copy(), b.rotation_quaternion.copy()) for b in pb})
    use(None)
    return out


def length_of(action):
    start, end = action.frame_range
    return int(round(end - start))


def apply(pose):
    for name, (loc, rot) in pose.items():
        pb[name].location, pb[name].rotation_quaternion = loc, rot
    bpy.context.view_layer.update()


def head(name):
    return pb[name].head.copy()


def tail(name):
    return pb[name].tail.copy()


def set_matrix(name, m):
    pb[name].matrix = m
    bpy.context.view_layer.update()


def rotate_world(name, axis, angle):
    """Turn a bone about its head by `angle` round the world `axis`."""
    m = pb[name].matrix
    pivot = m.translation
    set_matrix(name, Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, Vector(axis).normalized()) @ Matrix.Translation(-pivot) @ m)


def move_world(name, offset):
    m = pb[name].matrix.copy()
    m.translation += Vector(offset)
    set_matrix(name, m)


def aim(name, direction):
    """Turn a bone (the least) so that it points along `direction`."""
    m = pb[name].matrix
    q = Vector(m.col[1][:3]).rotation_difference(Vector(direction).normalized())
    pivot = m.translation
    set_matrix(name, Matrix.Translation(pivot) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ m)


def two_bone(upper, lower, target, pole):
    """Turn `upper` and `lower` so that the end of `lower` reaches `target`, bending towards `pole`."""
    s = head(upper)
    a, b = (tail(upper) - s).length, (tail(lower) - head(lower)).length
    t = Vector(target)
    d = min(max((t - s).length, 1e-3), a + b - 1e-4)
    u = (t - s).normalized()
    cos_a = (a * a + d * d - b * b) / (2 * a * d)
    p = Vector(pole) - s
    v = (p - p.project(u)).normalized()
    joint = s + u * (a * cos_a) + v * (a * math.sqrt(max(0.0, 1 - cos_a * cos_a)))
    aim(upper, joint - s)
    aim(lower, s + u * d - joint)


def frame_of(fingers, palm):
    f = Vector(fingers).normalized()
    n = (Vector(palm) - Vector(palm).project(f)).normalized()
    return Matrix((f, n, f.cross(n))).transposed()


def arm_ik(side, wrist, pole, fingers, palm):
    """The wrist to `wrist`, the elbow towards `pole`, the hand's fingers along `fingers` and its palm facing `palm`."""
    low, hand = f"lowerarm_{side}", f"hand_{side}"
    two_bone(f"upperarm_{side}", low, wrist, pole)
    rest = REST[hand].to_3x3()
    want = frame_of(fingers, palm) @ frame_of(rest.col[1], (0, 0, -1)).transposed() @ rest
    twist = (pb[low].matrix.to_3x3().inverted() @ want).to_quaternion().to_swing_twist("Y")[1]
    m = pb[low].matrix                                                                # the forearm shares the hand's turn
    pivot, axis = m.translation, Vector(m.col[1][:3])
    set_matrix(low, Matrix.Translation(pivot) @ Matrix.Rotation(twist * 0.5, 4, axis) @ Matrix.Translation(-pivot) @ m)
    set_matrix(hand, Matrix.Translation(tail(low)) @ want.to_4x4())


FINGERS = ("index", "middle", "ring", "pinky")


def curl_axis(side):
    m = arm.data.bones[f"index_02_{side}"].matrix_local.to_3x3()
    best = None
    for axis in ("X", "Z"):
        for sign in (1, -1):
            tip = m @ Matrix.Rotation(sign * 0.5, 3, axis) @ Vector((0, 1, 0))
            if best is None or -tip.z > best[0]:
                best = (-tip.z, axis, sign)
    return best[1], best[2]


AXES = {s: curl_axis(s) for s in ("l", "r")}


def fingers(side, curls, thumb=None, spread=0.0):
    """Bend the fingers: curls = (index, middle, ring, pinky) in radians-ish; `thumb` = (bend, out)."""
    axis, sign = AXES[side]
    bend_axis = Vector((1, 0, 0)) if axis == "X" else Vector((0, 0, 1))
    fan_axis = Vector((0, 0, 1)) if axis == "X" else Vector((1, 0, 0))
    for name, c in zip(FINGERS, curls):
        for j, k in ((1, 0.8), (2, 1.2), (3, 0.9)):
            q = Quaternion(bend_axis, sign * c * k)
            if j == 1 and spread:
                fan = {"index": -1, "middle": -0.3, "ring": 0.4, "pinky": 1}[name]
                q = Quaternion(fan_axis, spread * fan * (1 if side == "l" else -1)) @ q
            pb[f"{name}_0{j}_{side}"].rotation_quaternion = q
    if thumb is not None:
        bend, out = thumb
        for j in (1, 2, 3):
            q = Quaternion(bend_axis, sign * bend * (0.4 if j == 1 else 0.7))
            if j == 1:
                q = Quaternion(fan_axis, out * (1 if side == "l" else -1)) @ q
            pb[f"thumb_0{j}_{side}"].rotation_quaternion = q
    bpy.context.view_layer.update()


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease(t, keys):
    """Smooth interpolation through (time, value) keys; values may be tuples."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            k = smooth((t - t0) / (t1 - t0))
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * k for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * k
    return keys[-1][1]


# -------------------------------------------------------------------------------- places on her, as at rest
SH = REST["upperarm_l"].translation.z                                              # her shoulders' height at rest
MOUTH = Vector((0.0, -0.105, REST["Head"].translation.z + 0.035))
WAIST = Vector((0.0, -0.27, 1.0))                                                  # where she holds her bouquet


def turn_of(bone):
    """How `bone` is turned from its rest. "body": her chest's place and the way it faces, kept upright."""
    if bone == "body":
        ahead = turn_of("spine_03") @ Vector((0, -1, 0))
        return Matrix.Rotation(math.atan2(ahead.x, -ahead.y), 3, "Z")
    return pb[bone].matrix.to_3x3() @ REST[bone].to_3x3().inverted()


def on(bone, point):
    """A point given at rest, carried along by `bone` as posed now."""
    b = "spine_03" if bone == "body" else bone
    return pb[b].head + turn_of(bone) @ (Vector(point) - REST[b].translation)


def along(bone, direction):
    return turn_of(bone) @ Vector(direction)


def reach(side, bone, wrist, pole, fingers_dir, palm):
    w = on(bone, wrist)
    arm_ik(side, w, w + along(bone, pole), along(bone, fingers_dir), along(bone, palm))


GRIP = (1.0, 1.08, 1.15, 1.22)                                                     # fingers round the stem


def hold(side, grip, up, inward):
    """One hand round the bouquet's stem at `grip` (world), the stem along `up`, the fingers reaching `inward`."""
    u = up.normalized()
    f = (inward - inward.project(u)).normalized()
    palm = f.cross(u) if side == "l" else u.cross(f)
    wrist = grip - palm * 0.03 - f * 0.078
    out = Vector((1 if side == "l" else -1, 0.35, -0.7))
    arm_ik(side, wrist, wrist + along("body", out), f, palm)
    fingers(side, GRIP, (0.5, 0.25))


def bouquet(at, up=(0, -0.25, 1), both=True, bone="body"):
    """Holding the bouquet: the left hand round its stem at `at` (given at rest, relative to `bone`), the right hand
    just below it (or free)."""
    g, u = on(bone, at), along(bone, up).normalized()
    hold("l", g, u, along("body", (-1, -0.3, 0)))
    if both:
        hold("r", g - u * 0.085, u, along("body", (1, -0.3, 0)))


def bouquet_left(at=(0.07, -0.25, 1.02)):
    """The bouquet in her left hand only, a little to her left (her right hand free)."""
    g, u = on("body", at), along("body", (0.12, -0.3, 1)).normalized()
    hold("l", g, u, along("body", (-1, -0.45, 0)))


def plant_feet(feet):
    """Keep her feet where they were (after moving her hips): knees bend forward."""
    for side, (ankle, rot) in feet.items():
        two_bone(f"thigh_{side}", f"calf_{side}", ankle, ankle + along("body", (0, -1, 0.6)) + Vector((0, 0, 0.3)))
        m = rot.copy()
        m.translation = tail(f"calf_{side}")
        set_matrix(f"foot_{side}", m)


def feet_now():
    return {s: (head(f"foot_{s}"), pb[f"foot_{s}"].matrix.copy()) for s in ("l", "r")}


# -------------------------------------------------------------------------------- the emotes
def wave(t, T):
    sway = 0.07 * math.sin((t - 0.5) * 2 * math.pi * 1.5) * smooth((t - 0.45) / 0.3) * smooth((T - 0.45 - t) / 0.3)
    rotate_world("spine_03", (0, 1, 0), 0.04)
    rotate_world("Head", (0, 1, 0), 0.1)
    bouquet_left()
    reach("r", "body", (-0.29 + sway, -0.12, SH + 0.15), (-0.4, 0.3, -0.6), (-0.15 + 0.4 * sway, 0, 1), (0, -1, 0))
    fingers("r", (0.05, 0.05, 0.08, 0.12), (0.1, 0.2), spread=0.1)


def blow_kiss(t, T):
    k = ease(t, [(0.0, 0.0), (1.1, 0.0), (1.5, 1.0)])
    rotate_world("spine_02", (1, 0, 0), -0.07 * (1 - k) + 0.05 * k)
    rotate_world("Head", (1, 0, 0), -0.1 * (1 - k))
    rotate_world("Head", (0, 1, 0), 0.08)
    bouquet_left()
    near = on("Head", MOUTH + Vector((0.0, -0.08, -0.16)))
    far = on("body", Vector((-0.34, -0.5, MOUTH.z - 0.08)))
    w = near.lerp(far, k)
    fing = along("Head", Vector((0.25, 0.25, 1))).lerp(along("body", Vector((-0.5, -1, 0.3))), k)
    palm = along("Head", Vector((0, 1, -0.2))).lerp(along("body", Vector((0, -0.3, 1))), k)
    arm_ik("r", w, w + along("body", Vector((-0.5, 0.4, -0.5))), fing, palm)
    c = 0.45 * (1 - k)
    fingers("r", (c, c, c + 0.1, c + 0.15), (0.35 * (1 - k), 0.3), spread=0.15 * k)


def twirl(t, T):
    """One slow turn on the spot, her right arm lifting gracefully, the gown swinging out."""
    spin = ease(t, [(0.3, 0.0), (2.3, 1.0)])
    rotate_world("root", (0, 0, 1), -2 * math.pi * spin)
    lift = math.sin(math.pi * min(1.0, max(0.0, (t - 0.25) / (T - 0.6))))
    rotate_world("spine_03", (0, 1, 0), 0.08 * lift)
    rotate_world("Head", (1, 0, 0), -0.12 * lift)
    bouquet(WAIST + Vector((0.06, 0.0, 0.18)), (0.1, -0.2, 1), both=False)
    reach("r", "body", (-0.32 - 0.12 * lift, -0.1, SH - 0.05 + 0.3 * lift), (-0.6, 0.2, -0.3),
          (-0.6, -0.1, 0.4 + 0.6 * lift), (0, -0.4, -1))
    fingers("r", (0.15, 0.22, 0.3, 0.38), (0.15, 0.25), spread=0.08)


def curtsy(t, T):
    """A bride's curtsy: knees bend, a little bow of her body and head, her right hand lifting her skirt aside."""
    dip = ease(t, [(0.3, 0.0), (1.1, 1.0), (1.8, 1.0), (2.5, 0.0)])
    feet = feet_now()
    move_world("pelvis", (0, 0, -0.11 * dip))
    plant_feet(feet)
    rotate_world("spine_02", along("body", (1, 0, 0)), -0.16 * dip)
    rotate_world("Head", along("body", (1, 0, 0)), -0.25 * dip)
    bouquet_left()
    reach("r", "body", (-0.3, -0.12 - 0.05 * dip, 0.98 + 0.06 * dip), (-0.6, 0.3, -0.2), (-0.1, -0.5, -1), (1, -0.2, 0))
    fingers("r", (0.7, 0.75, 0.8, 0.85), (0.4, 0.2))


def smell_flowers(t, T):
    """She lifts the bouquet to her face, breathes the roses in, and lowers it again."""
    k = ease(t, [(0.25, 0.0), (1.0, 1.0), (2.3, 1.0), (3.0, 0.0)])
    rotate_world("Head", along("body", (1, 0, 0)), -0.14 * k)
    rotate_world("spine_03", along("body", (1, 0, 0)), -0.05 * k + 0.02 * k * math.sin(max(0.0, t - 1.1) * 2.2))
    at = WAIST.lerp(Vector((0.0, -0.25, 1.4)), k)
    up = Vector((0, -0.25, 1)).lerp(Vector((0, 0.35, 1)), k)
    bouquet(at, tuple(up))


def slow_dance(t, T):
    """A slow, swaying dance on the spot, turning a little this way and that, the bouquet held close (loops)."""
    w = 2 * math.pi * t / T
    rotate_world("root", (0, 0, 1), 0.4 * math.sin(w))
    feet = feet_now()
    move_world("pelvis", along("body", (0.035 * math.sin(2 * w), 0, -0.012 * (1 - math.cos(4 * w)) / 2)))
    plant_feet(feet)
    rotate_world("spine_02", along("body", (0, 1, 0)), -0.06 * math.sin(2 * w))
    rotate_world("Head", along("body", (0, 1, 0)), 0.1 * math.sin(2 * w + 0.6))
    bouquet(WAIST + Vector((0.0, 0.03, 0.2)), (0, -0.1, 1))


EMOTES = {"Wave": (wave, 2.6), "Blow_Kiss": (blow_kiss, 2.8), "Twirl": (twirl, 2.8), "Curtsy": (curtsy, 2.8),
          "Smell_Flowers": (smell_flowers, 3.2)}
LOOPS = {"Slow_Dance": (slow_dance, 4.0)}
FADE_IN, FADE_OUT = 0.35, 0.45


# -------------------------------------------------------------------------------- making the actions
def key(name, poses, free=FREE):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    use(act)
    last = {}
    for f, pose in enumerate(poses):
        for b in pb:
            if b.name in free:
                continue
            loc, rot = pose[b.name]
            if b.name in last and last[b.name].dot(rot) < 0:                       # no flips between frames
                rot = -rot
            last[b.name] = rot
            b.location, b.rotation_quaternion = loc, rot
            b.keyframe_insert("location", frame=f)
            b.keyframe_insert("rotation_quaternion", frame=f)
    use(None)
    print("action", name, len(poses), "frames")


def snapshot():
    return {b.name: (b.location.copy(), b.rotation_quaternion.copy()) for b in pb}


def blend(a, b, w):
    return {n: (a[n][0].lerp(b[n][0], w), a[n][1].slerp(b[n][1], w)) for n in a}


STANDING = REST["pelvis"].translation.z
CHAINS = sum(1 for b in pb if b.name.startswith("skirt_") and b.name.endswith("_1"))


def drape_skirt():
    """Seated, the gown lies over her lap and knees and falls to the floor in front of her and at her sides (behind
    her it goes into the seat): the skirt bones are keyed for sitting, and the web swings them from there."""
    seated = smooth((STANDING - 0.05 - head("pelvis").z) / 0.25)                     # 0 standing ... 1 seated
    if seated <= 0:
        return
    up, fwd = Vector((0, 0, 1)), along("body", (0, -1, 0))
    for k in range(CHAINS):
        a = 2 * math.pi * k / CHAINS
        d = along("body", (math.cos(a), math.sin(a), 0))                              # out, on this chain's side
        ff = max(0.0, -math.sin(a))                                                   # 1 at her front
        knee = head("calf_l" if math.cos(a) > 0 else "calf_r") + up * 0.1 + d * 0.06
        side = (d - up * 0.15).normalized()                                          # over the seat, then down
        lap = (knee + d * 0.12 * (1 - ff) - head(f"skirt_{k}_1")).normalized()        # over her thigh to the knee
        dirs = (side.lerp(lap, ff).normalized(),
                (d * 0.25 * (1 - ff) + fwd * 0.15 * ff - up).normalized(),            # falling past her shins
                (d * 0.8 - up * 0.6).normalized())                                    # and out over the floor
        for i, direction in enumerate(dirs, 1):
            name = f"skirt_{k}_{i}"
            rest = pb[name].rotation_quaternion.copy()
            aim(name, direction)
            pb[name].rotation_quaternion = rest.slerp(pb[name].rotation_quaternion.copy(), seated)
            bpy.context.view_layer.update()


def held(base_poses, at=WAIST, lap=False):
    """The base poses with her holding the bouquet (at her waist, or in her lap, the gown draped over it)."""
    out = []
    for pose in base_poses:
        apply(pose)
        if lap:
            knees = (head("calf_l") + head("calf_r")) / 2
            hips = (head("thigh_l") + head("thigh_r")) / 2
            g = hips.lerp(knees, 0.55) + Vector((0, 0, 0.12))
            u = (along("body", (0, -0.5, 1))).normalized()
            hold("l", g, u, along("body", (-1, -0.3, 0)))
            hold("r", g - u * 0.085, u, along("body", (1, -0.3, 0)))
            drape_skirt()
        else:
            bouquet(at)
        out.append(snapshot())
    return out


idle_src = bpy.data.actions["_Idle"]
idle_len = length_of(idle_src)
key("Idle", held(sample(idle_src, range(idle_len))))
walk_src = bpy.data.actions["_Walk"]
key("Walk", held(sample(walk_src, range(length_of(walk_src)))))
for name in ("Sit_Down", "Sit_Idle", "Sit_Up"):
    src = bpy.data.actions["_" + name]
    key(name, held(sample(src, range(length_of(src) + (0 if name == "Sit_Idle" else 1))), lap=True),
        free={b for b in FREE if b.startswith("veil_")})

idle_held = None
for name, (fn, T) in EMOTES.items():
    n = int(round(T * FPS)) + 1
    base = held(sample(idle_src, range(n)))
    poses = []
    for f in range(n):
        t = f / FPS
        apply(base[f])
        fn(t, T)
        w = smooth(t / FADE_IN) * smooth((T - t) / FADE_OUT)
        poses.append(blend(base[f], snapshot(), w))
    key(name, poses)
for name, (fn, T) in LOOPS.items():
    n = int(round(T * FPS))
    base = held(sample(idle_src, [0]))[0]
    poses = []
    for f in range(n):
        apply(base)
        fn(f / FPS, T)
        poses.append(snapshot())
    key(name, poses)

for act in [a for a in bpy.data.actions if a.name.startswith("_")]:
    bpy.data.actions.remove(act)
use(bpy.data.actions["Idle"])
for o in objs:
    o.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("ok", sorted(a.name for a in bpy.data.actions))
