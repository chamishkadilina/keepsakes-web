"""After baking: denoise + encode lightmaps for the web, and store the light falling on each photo slot.
Usage: python finish_lightmaps.py <uv.blend> <exr_dir> <out_dir> <out.blend>
Writes <out_dir>/lightmaps/lm_<group>.png (sRGB 8-bit), <out_dir>/lightmaps/lightmaps.json
and saves <out.blend> with custom property light_rgb on every slot."""
import bpy, sys, os, json, glob
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc

src, exr_dir, out_dir, out_blend = sys.argv[1:5]
lm_dir = os.path.join(out_dir, "lightmaps"); os.makedirs(lm_dir, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=src)

def load_exr(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    return a  # row 0 = bottom (Blender convention)

def denoise(a):
    """Light, coverage-aware smoothing: never pulls in empty (black) texels.
    Isolated black texels inside lit areas (no light sample hit them) are filled from their neighbours."""
    mask = (a.max(axis=2) > 1e-6).astype(np.float32)
    num = np.stack([gaussian_filter(a[..., c] * mask, 1.8) for c in range(3)], axis=2)
    den = gaussian_filter(mask, 1.8)[..., None]
    out = np.where(den > 1e-4, num / np.maximum(den, 1e-4), 0)
    keep = np.maximum(mask, (den[..., 0] > 0.3).astype(np.float32))[..., None]   # lit texels + filled speckles
    return out * keep + a * (1 - keep)

maps = {Path: load_exr(Path) for Path in sorted(glob.glob(os.path.join(exr_dir, "lm_*.exr")))}
maps = {os.path.basename(k)[3:-4]: denoise(v) for k, v in maps.items()}

# one shared scale for all maps: the brightest 0.1 % of texels map to ~0.95
lum = np.concatenate([(m @ np.array([0.2126, 0.7152, 0.0722], np.float32)).ravel() for m in maps.values()])
lum = lum[lum > 1e-6]
intensity = float(np.percentile(lum, 99.9) / 0.95)

def fill_empty(a):
    """Gives every texel outside the UV islands the colour of the nearest island (push-pull), so the mipmaps
    never pull black into lit surfaces seen from a distance (dark seams along edges)."""
    mask = (a.max(axis=2) > 1e-6).astype(np.float32)
    pyramid, c, m = [], a * mask[..., None], mask
    while True:
        pyramid.append((c, m))
        if min(c.shape[:2]) < 2:
            break
        h, w = c.shape[0] // 2, c.shape[1] // 2
        c = c[:h * 2, :w * 2].reshape(h, 2, w, 2, 3).sum((1, 3))
        m = m[:h * 2, :w * 2].reshape(h, 2, w, 2).sum((1, 3))
    colour = pyramid[-1][0] / np.maximum(pyramid[-1][1], 1e-6)[..., None]
    for c, m in reversed(pyramid[:-1]):
        up = np.repeat(np.repeat(colour, 2, axis=0), 2, axis=1)[:c.shape[0], :c.shape[1]]
        colour = np.where((m > 0)[..., None], c / np.maximum(m, 1e-6)[..., None], up)
    return colour

def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)

groups = {}
for o in bpy.data.objects:
    g = o.get("lightmap_group")
    if g:
        groups.setdefault(g, []).append(o.name)

manifest = {"intensity": round(intensity, 4), "uv": "lightmap (TEXCOORD_1)", "colorSpace": "srgb", "flipY": False, "maps": {}}
for g, a in maps.items():
    png = (to_srgb(fill_empty(a) / intensity) * 255 + 0.5).astype(np.uint8)[::-1]  # flip: PNG row 0 = top (glTF UV convention)
    Image.fromarray(png, "RGB").save(os.path.join(lm_dir, f"lm_{g}.png"), optimize=True)
    manifest["maps"][g] = {"file": f"lm_{g}.png", "size": a.shape[0], "objects": sorted(groups.get(g, []))}
json.dump(manifest, open(os.path.join(lm_dir, "lightmaps.json"), "w"), indent=1)

# light on each photo: sample the wall lightmap right behind the slot centre
walls = bpy.data.objects["walls"]
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(walls, dg)
me = walls.data; uvl = me.uv_layers["lightmap"].data
wall_map = maps["walls"]; H, W = wall_map.shape[:2]

def sample(u, v):
    x, y = u * (W - 1), v * (H - 1)
    x0, y0 = int(np.floor(x)), int(np.floor(y)); fx, fy = x - x0, y - y0
    x1, y1 = min(x0 + 1, W - 1), min(y0 + 1, H - 1)
    return (wall_map[y0, x0] * (1 - fx) * (1 - fy) + wall_map[y0, x1] * fx * (1 - fy)
            + wall_map[y1, x0] * (1 - fx) * fy + wall_map[y1, x1] * fx * fy)

levels = []
for ob in bpy.data.collections["frames_slots"].objects:
    n = (ob.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    origin = ob.matrix_world.translation + n * 0.2
    hit, _, face, _ = bvh.ray_cast(origin, -n, 1.0)
    if hit is None:
        print("no wall behind", ob.name); continue
    poly = me.polygons[face]
    w = poly_3d_calc([me.vertices[i].co for i in poly.vertices], hit)
    uv = sum((Vector(uvl[li].uv) * wi for li, wi in zip(poly.loop_indices, w)), Vector((0, 0)))
    rgb = sample(uv.x, uv.y)
    ob["light_rgb"] = [round(float(c), 4) for c in rgb]
    levels.append((ob.name, float(rgb @ np.array([0.2126, 0.7152, 0.0722]))))

# collage photos: one even light level (average), so the whole board reads as one lit piece
col = [o for o in bpy.data.collections["frames_slots"].objects if o.name.startswith("slot_collage_") and "light_rgb" in o]
if col:
    avg = [round(sum(o["light_rgb"][c] for o in col) / len(col), 4) for c in range(3)]
    for o in col:
        o["light_rgb"] = avg

bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
lv = sorted(l for _, l in levels)
print("intensity", round(intensity, 3), "slots", len(levels), "light min/median/max",
      round(lv[0], 3), round(lv[len(lv) // 2], 3), round(lv[-1], 3))
for name, l in sorted(levels, key=lambda t: t[1])[:4]:
    print("darkest", name, round(l, 3))
