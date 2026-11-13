"""The clearing outside the foyer's south door, where the couple start, side by side in front of the door: a wide
stone path to it across a lawn in a clearing of a little wood, under the same night sky. The lawn runs on under the
trees, which garden.py plants (garden_layout.ENTRANCE: the clearing's size, its wood and the little lights strung over
it). The doorway, its doors, the carpet, the flower stands and the roses are props.LAYOUT pieces (props_entrance.py).
Textures at their real size: the garden's grass (garden_layout.py) and Precast Stone Paving (Poly Haven, CC0). Lit by
its baked vertex light, like the furniture. Also its walkable ground (col_floor_*: invisible, the web walks on it) and
the invisible walls round the clearing (col_entrance_wall_*), and it moves the couple's start (spawn_her, spawn_him)
here.

  entrance.add(collection)      # in design.py, after props.add (it moves the spawn markers)
"""
import bpy, bmesh, math, os
from mathutils import Vector
import garden_layout as L

C = L.ENTRANCE["clearing"]
X0, X1, Y0, NW = C["x0"], C["x1"], C["y0"], C["north_west"]   # m: the clearing you walk in; north: the museum
FRONT = -0.2                          # m: the museum's front wall (outer face)
CORNER = (11.2, 1.3)                  # the corner east of the foyer, up to the heart room's south wall
DOOR, PATH = (4.0, 7.0), (3.5, 7.5)   # x: the doorway; the path, wider
WOOD = 12.0                           # m: the lawn runs on this far beyond the edges, under the trees
STEP, WOOD_STEP = 0.35, 1.2           # m between vertices, for the baked light: in the clearing, under the trees
WALL_H, WALL_T = 2.4, 0.35            # m: the invisible walls round the clearing
SPAWN = {"spawn_her": (5.0, -3.2), "spawn_him": (6.0, -3.2)}
PAVING = ("entrance_paving", "../entrance/entrance_paving.jpg", 2.24)   # material, file (from the garden's folder), tile m


def textured(name, file, folder):
    m = bpy.data.materials.new(name); nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.normpath(os.path.join(folder, file)), check_existing=True); tex.image.pack()
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    return m


def ground(bm, x0, x1, y0, y1, tile, step=STEP, z=0.0):
    """A flat grid facing up over x0-x1, y0-y1, its UVs the world position over the texture's size."""
    nu, nv = max(1, math.ceil((x1 - x0) / step)), max(1, math.ceil((y1 - y0) / step))
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nu, y0 + (y1 - y0) * j / nv, z)) for i in range(nu + 1)] for j in range(nv + 1)]
    uv = bm.loops.layers.uv.verify()
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
            for loop in f.loops:
                loop[uv].uv = (loop.vert.co.x / tile, loop.vert.co.y / tile)


def collider(collection, name, lo, hi):
    """An invisible box the web collides with (col_*; col_floor_*: ground it walks on)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(hi) - Vector(lo), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(Vector(lo) + Vector(hi)) / 2, verts=bm.verts)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.hide_render = True; collection.objects.link(ob)


def finish(collection, name, bm, mat):
    me = bpy.data.meshes.new(f"prop_entrance_{name}"); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new(me.name, me); collection.objects.link(ob)
    ob["prop"] = mat.name; ob["bake_vertex"] = True; ob["noReflection"] = True


def add(collection):
    folder = os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), L.FOLDER)
    grass, paving = textured("entrance_grass", L.SURFACES["floor_6_garden"][1], folder), textured(PAVING[0], PAVING[1], folder)
    lawn, path = bmesh.new(), bmesh.new()
    (cx, cy), (p0, p1), w, t = CORNER, PATH, WOOD, L.TILE
    ground(lawn, X0, p0, Y0, FRONT, t); ground(lawn, p1, X1, Y0, FRONT, t)   # the clearing, either side of the path
    ground(lawn, X0, FRONT, FRONT, NW, t)                                     # by the story gallery
    ground(lawn, cx, X1, FRONT, cy, t)                                        # by the heart room
    ground(lawn, X0 - w, X1 + w, Y0 - w, Y0, t, WOOD_STEP)                    # under the trees: south,
    ground(lawn, X0 - w, X0, Y0, NW + w, t, WOOD_STEP)                        # west,
    ground(lawn, X0, FRONT, NW, NW + w, t, WOOD_STEP)                         # north of the strip by the story gallery
    ground(lawn, X1, X1 + w, Y0, cy, t, WOOD_STEP)                            # and east
    ground(path, p0, p1, Y0, FRONT, PAVING[2], z=0.004)
    ground(path, DOOR[0], DOOR[1], FRONT, 0.0, PAVING[2], z=0.004)            # under the door, up to the foyer's floor
    for name, bm, mat in (("lawn", lawn, grass), ("path", path, paving)):
        finish(collection, name, bm, mat)
    collider(collection, "col_floor_entrance", (X0, Y0, -0.1), (X1, FRONT, 0))
    collider(collection, "col_floor_entrance_door", (DOOR[0], FRONT, -0.1), (DOOR[1], 0, 0))
    collider(collection, "col_floor_entrance_west", (X0, FRONT, -0.1), (FRONT, NW, 0))
    collider(collection, "col_floor_entrance_east", (cx, FRONT, -0.1), (X1, cy, 0))
    collider(collection, "col_entrance_wall_n", (X0 - WALL_T, NW, 0), (FRONT, NW + WALL_T, WALL_H))
    collider(collection, "col_entrance_wall_w", (X0 - WALL_T, Y0 - WALL_T, 0), (X0, NW + WALL_T, WALL_H))
    collider(collection, "col_entrance_wall_s", (X0 - WALL_T, Y0 - WALL_T, 0), (X1 + WALL_T, Y0, WALL_H))
    collider(collection, "col_entrance_wall_e", (X1, Y0 - WALL_T, 0), (X1 + WALL_T, cy, WALL_H))
    for name, (x, y) in SPAWN.items():
        bpy.data.objects[name].location = (x, y, 0)
