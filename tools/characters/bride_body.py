"""The bride's body: the Universal Base Characters female with her long hair (dark brown), refined eyebrows, a soft
smile, slimmer arms and shoulders, and soft bridal makeup painted into her skin texture (rose lips, a warm blush, a
touch of eyeshadow). Imported by bride_build.py."""
import math

import bpy
import numpy as np
from mathutils import Vector

HAIR_TINT = (0.2, 0.13, 0.09)                                                       # dark brown
MOUTH = Vector((0.0, -0.09, 1.585))                                                  # her mouth at rest (this model)


def import_gltf(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def load(body_path, hair_path):
    new = import_gltf(body_path)
    arm = next(o for o in new if o.type == "ARMATURE")
    for o in import_gltf(hair_path):
        if o.type == "MESH" and o.name.startswith("Hair"):
            o.parent = arm
            o.modifiers[0].object = arm
    for o in list(bpy.data.objects):
        if o.name.startswith("Icosphere") or (o.type == "ARMATURE" and o is not arm):
            bpy.data.objects.remove(o, do_unlink=True)
    arm.name = "Bride"
    return arm, bpy.data.objects["Superhero_Female"]


def pixels(img):
    a = np.empty(img.size[0] * img.size[1] * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)


def store(img, a):
    img.pixels.foreach_set(a.ravel())
    img.update()


def tint_hair():
    for img in bpy.data.images:
        if img.name.startswith("T_Hair_2_BaseColor") and img.size[0]:
            a = pixels(img)
            a[..., :3] *= np.array(HAIR_TINT, np.float32)
            store(img, a)


def weights(ob, v):
    names = {g.index: g.name for g in ob.vertex_groups}
    return {names[g.group]: g.weight for g in v.groups}


def slim_arms(body, arm, amount=0.2):
    """Draw her arms (and a little of her shoulders) in towards their bones."""
    bones = arm.data.bones
    segs = {n: (bones[n].head_local, bones[n].tail_local) for n in bones.keys() if n.startswith(("upperarm", "lowerarm"))}
    for v in body.data.vertices:
        w = weights(body, v)
        for name, (a, b) in segs.items():
            k = w.get(name, 0.0)
            if k < 0.05:
                continue
            ab = b - a
            t = max(0.0, min(1.0, (v.co - a).dot(ab) / ab.length_squared))
            near = a + ab * t
            taper = amount * (0.55 if name.startswith("upperarm") and t < 0.25 else 1.0)  # gentler at the shoulder
            v.co = v.co.lerp(near, taper * k)


def soft_smile(body, lift=0.0045):
    """Lift the corners of her mouth a little."""
    for v in body.data.vertices:
        for side in (-1, 1):
            corner = Vector((side * 0.024, -0.079, 1.585))
            d = (v.co - corner).length
            if d < 0.018 and v.co.y < -0.06:
                f = (1 - d / 0.018) ** 2
                v.co.z += lift * f
                v.co.y += 0.0008 * f


def islands(me):
    """Groups of connected vertex indices."""
    links = {v.index: set() for v in me.vertices}
    for e in me.edges:
        a, b = e.vertices
        links[a].add(b)
        links[b].add(a)
    seen, out = set(), []
    for start in links:
        if start in seen:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            i = stack.pop()
            group.append(i)
            for j in links[i] - seen:
                seen.add(j)
                stack.append(j)
        out.append(group)
    return out


def refine_brows(ob, thin=0.6):
    """Thinner, gently arched eyebrows (the eyelashes in the same mesh stay as they are)."""
    V = ob.data.vertices
    for group in islands(ob.data):
        if min(V[i].co.z for i in group) < 1.665:                                       # eyelashes
            continue
        xs = [abs(V[i].co.x) for i in group]
        x0, x1 = min(xs), max(xs)
        bins = {}
        for i in group:
            bins.setdefault(round(abs(V[i].co.x) * 300), []).append(V[i].co.z)
        centre = {k: sum(z) / len(z) for k, z in bins.items()}
        for i in group:
            v = V[i]
            mid = centre[round(abs(v.co.x) * 300)]
            t = (abs(v.co.x) - x0) / max(x1 - x0, 1e-6)                                 # 0 inner end, 1 outer end
            v.co.z = mid + (v.co.z - mid) * thin * (1 - 0.3 * t) + 0.0018 * math.sin(math.pi * min(1.0, t * 1.2))


def face_mask(body, img, pick, blur=6):
    """A soft mask over the texture where her faces chosen by pick(vertex position) -> weight are painted."""
    from PIL import Image, ImageDraw, ImageFilter
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    uv = body.data.uv_layers.active.data
    V = body.data.vertices
    for poly in body.data.polygons:
        k = sum(pick(V[i].co) for i in poly.vertices) / len(poly.vertices)
        if k <= 0.01:
            continue
        pts = [(uv[li].uv.x * w, (1 - uv[li].uv.y) * h) for li in poly.loop_indices]
        draw.polygon(pts, fill=int(255 * min(1.0, k)))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return np.flipud(np.asarray(mask, np.float32) / 255)                             # Blender's pixel rows go bottom-up


def makeup(body):
    img = next(i for i in bpy.data.images if i.name.startswith("T_Superhero_Female") and "BaseColor" in i.name)
    a = pixels(img)
    rgb = a[..., :3]

    def blend(mask, colour, strength):
        m = (mask * strength)[..., None]
        lum = rgb.mean(axis=2, keepdims=True)
        target = np.array(colour, np.float32) * (0.6 + 0.8 * lum)                      # keeps the texture's shading
        rgb[:] = rgb * (1 - m) + target * m

    def lips(co):
        if co.y > -0.072:
            return 0.0
        e = (co.x / 0.025) ** 2 + ((co.z - MOUTH.z) / 0.012) ** 2
        return max(0.0, 1 - e) ** 0.5

    def cheeks(co):
        if co.y > -0.03:
            return 0.0
        d = min((co - Vector((s * 0.046, -0.07, 1.612))).length for s in (-1, 1))
        return max(0.0, 1 - d / 0.024) ** 1.5

    def lids(co):
        if co.y > -0.05:
            return 0.0
        d = min(((co.x - s * 0.034) / 0.022) ** 2 + ((co.z - 1.672) / 0.007) ** 2 for s in (-1, 1))
        return max(0.0, 1 - d)

    blend(face_mask(body, img, lips, 3), (0.62, 0.2, 0.26), 0.55)
    blend(face_mask(body, img, cheeks, 14), (0.78, 0.42, 0.42), 0.18)
    blend(face_mask(body, img, lids, 5), (0.42, 0.27, 0.24), 0.3)
    store(img, a)


def prepare(body_path, hair_path):
    arm, body = load(body_path, hair_path)
    tint_hair()
    slim_arms(body, arm)
    soft_smile(body)
    refine_brows(bpy.data.objects["Eyebrows"])
    makeup(body)
    return arm, body
