"""Prepares the garden's CC0 models (Poly Haven, ASSETS.md) for the museum, once: real-world size, far fewer triangles,
small colour textures, one clean material each. Run again only to change an asset's preparation.
Usage: blender --background --python tools/bake/garden_assets.py -- <downloads> <out dir>
  <downloads>: one folder per Poly Haven id with its 1k glTF (.gltf, .bin, *_diff_1k.jpg), or for a surface its
               *_diff_1k.jpg only (SURFACES: the grass and the garden walls); the jacaranda: its 1k .blend and
               colour textures (TREE_BLEND)
  <out dir>:   assets-src/blender/textures/garden (garden_assets.blend + <material>.jpg; the bake pipeline reads them)
Each asset becomes a collection of variants (one mesh each, its base centred on the origin, front towards local +y).
The jacaranda is grown by its own geometry nodes (Poly Haven's .blend), twice (TREES: the big one and a smaller one): its whole
branch structure, a little simplified, with fewer of its own leaf clusters, each still on its twig, and its lighter trunk. Below
CANOPY_FROM only leaves and twig tips are cut, so you walk under the canopy and no branch goes missing.
The bench and the firewood are made in code (garden_wood.py), from <downloads>/teak_veneer and bark_brown_02."""
import bpy, bmesh, sys, os, glob
import numpy as np
from mathutils import Matrix, Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import garden_wood

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(out, exist_ok=True)
TREE_BLEND = "jacaranda_blend/jacaranda_tree_1k.blend"
CANOPY_FROM = 2.4                            # m: below this only the trunk (you walk under the canopy)
# name: height (m), share of the leaf clusters' density, decimate ratios of the branches and the trunk
TREES = {"jacaranda_tree": (11.0, 0.1, 0.15, 0.5), "jacaranda_small": (7.5, 0.07, 0.08, 0.3)}
LEAF_SIZE = 1.7                              # each leaf cluster this much larger: a full canopy from fewer clusters
# id: scale, decimate ratio, texture size, options (join: one variant from all parts; keep: these variants only;
# glass: materials drawn as the museum's glass; darken: its texture's brightness). What you see up close (by the bench and
# the fire) keeps most detail.
ASSETS = {
    "stone_fire_pit": (1.0, 1.0, 512, {"darken": 0.5}),                # sooty stones, not pale ones in the firelight
    "dry_branches_medium_01": (1.0, 0.5, 256, {}),
    "wicker_basket_02": (1.0, 0.6, 512, {"join": True}),
    "wine_bottles_01": (1.0, 0.8, 256, {"keep": ("champagne",)}),
    "wooden_lantern_01": (1.3, 0.4, 512, {"join": True, "glass": ("wooden_lantern_01_glass",)}),
    "wooden_candlestick": (1.0, 0.02, 256, {}),
    "pachira_aquatica_01": (1.4, 0.15, 512, {}),
    "wild_rooibos_bush": (1.6, 0.5, 256, {}),
    "fern_02": (1.0, 1.0, 256, {}),
    "shrub_04": (1.6, 0.4, 256, {}),
    "periwinkle_plant": (1.0, 0.3, 256, {}),
    "dandelion_01": (1.0, 0.2, 256, {}),
    "flower_gazania": (1.0, 0.5, 256, {}),
    "rock_moss_set_01": (0.5, 0.2, 512, {}),
}
# id: texture size, brightness, (tint colour, strength): the grass and the garden walls (garden.py)
SURFACES = {"leafy_grass": (1024, 0.6, ((0.32, 0.55, 0.22), 0.7)), "mossy_stone_wall": (512, 0.45, None)}


def read(coll, attr, n, dtype, width=1):
    a = np.zeros(n * width, dtype); coll.foreach_get(attr, a)
    return a.reshape(-1, width) if width > 1 else a


def import_asset(asset_id):
    """Imports the glTF into its own collection; returns its mesh objects with their transforms applied."""
    coll = bpy.data.collections.new(asset_id); bpy.context.scene.collection.children.link(coll)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glob.glob(f"{src}/{asset_id}/*.gltf")[0])
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    for o in meshes:
        o.data.transform(o.matrix_world); o.parent = None; o.matrix_world = Matrix()
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    for o in new:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
    return coll, meshes


def to_base(o, scale=1.0, at=None):
    """Scales the mesh and moves it so its base (or `at`) sits on the origin."""
    co = read(o.data.vertices, "co", len(o.data.vertices), np.float32, 3) * scale
    base = at * scale if at is not None else np.array([(co[:, 0].min() + co[:, 0].max()) / 2, (co[:, 1].min() + co[:, 1].max()) / 2, co[:, 2].min()])
    o.data.vertices.foreach_set("co", (co - base).ravel()); o.data.update()


def decimate(o, ratio):
    if ratio >= 1.0:
        return
    m = o.modifiers.new("decimate", "DECIMATE"); m.ratio = ratio
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    o.modifiers.clear(); old = o.data; o.data = me; bpy.data.meshes.remove(old)


def build_tree(coll, name, height, leaves, branches, trunk_ratio):
    """A jacaranda from its own geometry nodes, at real size (trunk base on the origin), split into its trunk,
    branches and leaves (<name>_<part>)."""
    with bpy.data.libraries.load(os.path.join(src, TREE_BLEND), link=False) as (lib, dst):
        dst.objects = ["jacaranda_tree_geometry_nodes", "jacaranda_tree_trunk_LOD1"]
    grow, trunk = dst.objects
    for img in bpy.data.images:                                    # its textures, from the download folder
        img.filepath = os.path.join(src, os.path.dirname(TREE_BLEND), "textures", os.path.basename(img.filepath))
    bpy.context.scene.collection.objects.link(grow)
    ng = grow.modifiers[0].node_group
    scatter = ng.nodes["Distribute Points on Faces"]
    fewer = ng.nodes.new("ShaderNodeMath"); fewer.operation = "MULTIPLY"; fewer.inputs[1].default_value = leaves
    ng.links.new(scatter.inputs["Density"].links[0].from_socket, fewer.inputs[0]); ng.links.new(fewer.outputs[0], scatter.inputs["Density"])
    next(n for n in ng.nodes if n.bl_idname == "GeometryNodeObjectInfo").inputs["Object"].default_value = trunk
    size = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeRandomValue"   # the clusters' random size
                and any(l.from_socket.name == "random size min" for i in n.inputs for l in i.links))
    out = next(o for o in size.outputs if o.enabled and o.links)
    larger = ng.nodes.new("ShaderNodeMath"); larger.operation = "MULTIPLY"; larger.inputs[1].default_value = LEAF_SIZE
    for link in list(out.links):
        ng.links.new(larger.outputs[0], link.to_socket)
    ng.links.new(out, larger.inputs[0])
    simpler = grow.modifiers.new("simpler", "DECIMATE"); simpler.ratio = branches
    grow.modifiers.move(len(grow.modifiers) - 1, 0)               # the branches simplified before the leaves grow on them
    me = bpy.data.meshes.new_from_object(grow.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    me.transform(grow.matrix_world); bpy.data.objects.remove(grow)
    co = read(me.vertices, "co", len(me.vertices), np.float64, 3)
    s = height / (co[:, 2].max() - co[:, 2].min())
    base = co[co[:, 2] < co[:, 2].min() + 0.3].mean(0); base[2] = co[:, 2].min()
    me.vertices.foreach_set("co", ((co - base) * s).astype(np.float32).ravel()); me.update()
    for i, mat in enumerate(me.materials):
        part = next(k for k in ("leaves", "branches", "trunk") if k in mat.name)
        bm = bmesh.new(); bm.from_mesh(me)
        low = [f for f in bm.faces if f.material_index != i or (part != "trunk" and max(v.co.z for v in f.verts) < CANOPY_FROM)]
        bmesh.ops.delete(bm, geom=low, context="FACES")
        for f in bm.faces:
            f.material_index = 0
        part_me = bpy.data.meshes.new(f"{name}_{part}"); bm.to_mesh(part_me); bm.free()
        part_me.materials.append(clean_material(mat, 512, ()))
        ob = bpy.data.objects.new(part_me.name, part_me); ob["garden_asset"] = name; coll.objects.link(ob)
        if part == "trunk":
            decimate(ob, trunk_ratio)
    bpy.data.meshes.remove(me)
    for helper in [c for c in bpy.data.collections if c.name.startswith("jacaranda_tree_leaves")]:   # its leaf templates
        for o in list(helper.objects):
            bpy.data.objects.remove(o)
        bpy.data.collections.remove(helper)
    bpy.data.objects.remove(trunk)


def colour_image(socket):
    """The image texture feeding a colour input, through any mix or colour nodes in between."""
    for link in socket.links:
        node = link.from_node
        if node.type == "TEX_IMAGE" and node.image:
            return node.image
        found = next((img for s in node.inputs if (img := colour_image(s))), None)
        if found:
            return found
    return None


def save_8bit(image, path, with_alpha):
    """Saves a texture as 8-bit JPEG (or PNG with alpha), whatever its source format, with its colours unchanged."""
    scene = bpy.context.scene; scene.view_settings.view_transform = "Standard"
    f = scene.render.image_settings
    f.file_format, f.color_mode, f.color_depth = ("PNG", "RGBA", "8") if with_alpha else ("JPEG", "RGB", "8")
    f.quality = 85
    image.save_render(filepath=path)


def find_image(mat, word):
    """A texture of the material by its kind ("diff", "alpha"), wherever it sits in the material's nodes."""
    nodes = mat.node_tree.nodes if mat.node_tree else []
    return next((n.image for n in nodes if n.type == "TEX_IMAGE" and n.image and word in n.image.name), None)


def clean_material(mat, size, glass, darken=1.0):
    """One plain material per surface: its colour texture (resized, saved next to the .blend) or its colour. A cut-out
    surface (leaf cards with an alpha map) keeps its shape: colour and alpha in one PNG, exported as alpha MASK."""
    if mat.name in glass:
        return bpy.data.materials.get("glass") or bpy.data.materials.new("glass")
    name = "garden_" + mat.name.split(".")[0]                       # one material for both trees' copies
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    nodes = mat.node_tree.nodes if mat.node_tree else []
    bsdf = next((nd for nd in nodes if nd.type == "BSDF_PRINCIPLED"), None)
    image = (colour_image(bsdf.inputs["Base Color"]) if bsdf else None) or find_image(mat, "diff")
    alpha = find_image(mat, "alpha")
    if alpha is image or (alpha and not os.path.exists(bpy.path.abspath(alpha.filepath))):
        alpha = None                                               # no mask of its own (leaves shaped in the mesh)
    if alpha:
        alpha.colorspace_settings.name = "Non-Color"              # a mask: its raw values, not converted as colour
    new = bpy.data.materials.new(name)
    nt = new.node_tree; p = nt.nodes["Principled BSDF"]
    if image:
        image.scale(size, size)
        if darken != 1.0:
            px = np.zeros(size * size * 4, np.float32); image.pixels.foreach_get(px)
            px.reshape(-1, 4)[:, :3] *= darken; image.pixels.foreach_set(px)
        if alpha:
            alpha.scale(size, size)
            px, cut = np.zeros(size * size * 4, np.float32), np.zeros(size * size * 4, np.float32)
            image.pixels.foreach_get(px); alpha.pixels.foreach_get(cut)
            px[3::4] = cut[0::4]; image.pixels.foreach_set(px)
        path = os.path.join(out, name + (".png" if alpha else ".jpg"))
        save_8bit(image, path, alpha is not None)
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(path)
        tex.image.filepath = "//" + os.path.basename(path)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        if alpha:                                                  # alpha clip: the glTF exporter writes alphaMode MASK
            clip = nt.nodes.new("ShaderNodeMath"); clip.operation = "ROUND"
            nt.links.new(tex.outputs["Alpha"], clip.inputs[0]); nt.links.new(clip.outputs[0], p.inputs["Alpha"])
    elif bsdf:
        p.inputs["Base Color"].default_value = bsdf.inputs["Base Color"].default_value
    return new


bpy.ops.wm.read_factory_settings(use_empty=True)
for tree_name, params in TREES.items():
    tree = bpy.data.collections.new(tree_name); bpy.context.scene.collection.children.link(tree)
    build_tree(tree, tree_name, *params)
garden_wood.build(src, out)
for asset_id, (scale, ratio, size, opts) in ASSETS.items():
    coll, objs = import_asset(asset_id)
    if "keep" in opts:
        for o in [o for o in objs if not o.name.endswith(opts["keep"])]:
            objs.remove(o); bpy.data.objects.remove(o)
    if opts.get("join") and len(objs) > 1:
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs):
            bpy.ops.object.join()
        objs = [objs[0]]
    for o in objs:
        to_base(o, scale)
        decimate(o, ratio)
        for i, mat in enumerate(o.data.materials):
            o.data.materials[i] = clean_material(mat, size, opts.get("glass", ()), opts.get("darken", 1.0))
        o.name = o.data.name = o.name.replace("_LOD0", "")
        o["garden_asset"] = asset_id
for c in bpy.data.collections:
    for o in c.objects:
        o["triangles"] = sum(len(p.vertices) - 2 for p in o.data.polygons)
        print(f"ASSET {c.name:22s} {o.name:34s} {o['triangles']:7d} tris  {[m.name for m in o.data.materials]}")
bpy.data.orphans_purge(do_recursive=True)
for img in bpy.data.images:
    img.filepath = "//" + os.path.basename(img.filepath)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "garden_assets.blend"), compress=True, relative_remap=False)
print("saved", os.path.join(out, "garden_assets.blend"))
for surface_id, (size, brightness, tint) in SURFACES.items():   # the grass and the walls: tiling colour textures
    img = bpy.data.images.load(glob.glob(f"{src}/{surface_id}/*_diff_1k.jpg")[0]); img.scale(size, size)
    px = np.zeros(size * size * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(-1, 4)
    if tint:                                                    # its detail kept, its colour moved towards the tint
        colour, strength = tint
        lum = px[:, :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        px[:, :3] += (lum[:, None] * np.array(colour, np.float32) * 2.0 - px[:, :3]) * strength
    px[:, :3] *= brightness; img.pixels.foreach_set(px.ravel())
    img.save(filepath=os.path.join(out, f"garden_{surface_id}.jpg"), quality=85)
    print("saved", f"garden_{surface_id}.jpg")
