"""The garden's pieces made in code, because Poly Haven has none of them: a classic teak garden bench for two (its
cushions and throw: garden_cushions.py), round firewood logs, and the patch of burnt earth the fire pit sits in. CC0
textures from Poly Haven (ASSETS.md): Teak Veneer, Bark Brown 02, Burned Ground 01.
garden_assets.py calls build(); each piece becomes a garden asset like the downloaded models (base on the origin).
The bench faces local -y (the sitters look that way); a log stands up local +z from its foot."""
import bpy, bmesh, math, os, random
import numpy as np
from mathutils import Matrix, Vector
import garden_cushions

# id: (its real size in m, brightness): weathered teak, a touch darker than new; bark at half size (thin logs)
TEXTURES = {"teak_veneer": (1.0, 0.72), "bark_brown_02": (0.5, 0.85), "burned_ground_01": (1.0, 0.6)}
BENCH = dict(width=1.5, seat=0.45, tilt=14.0, slats=6, spindles=11)   # m, m, degrees back, counts
LOGS = {"firewood_a": (0.62, 0.050), "firewood_b": (0.70, 0.045), "firewood_c": (0.55, 0.056)}   # length, radius (m)
CHAR = (0.035, 0.028, 0.024)                      # the logs' cut ends, burnt
BEVEL = 0.004                                     # m: every edge of the bench softly rounded
GROUND = dict(radius=1.0, ragged=0.15, height=0.006)   # m: the burnt earth round the fire pit, its uneven edge, above the grass


def material(name, src, out, texture, size=512):
    """A plain material with its colour texture: resized, brightness set, saved next to garden_assets.blend."""
    img = bpy.data.images.load(os.path.join(src, texture, f"{texture}_diff_1k.jpg")); img.scale(size, size)
    px = np.zeros(size * size * 4, np.float32); img.pixels.foreach_get(px)
    px.reshape(-1, 4)[:, :3] *= TEXTURES[texture][1]; img.pixels.foreach_set(px)
    path = os.path.join(out, f"{name}.jpg"); img.save(filepath=path, quality=85); bpy.data.images.remove(img)
    m = bpy.data.materials.new(name); nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(path); tex.image.filepath = "//" + os.path.basename(path)
    nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def plain(name, colour):
    m = bpy.data.materials.new(name); m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*colour, 1)
    return m


def board(bm, size, matrix, tile, rng):
    """One rounded board: grain along its longest side, the texture shifted so no two boards match."""
    piece = bmesh.new(); bmesh.ops.create_cube(piece, size=1.0)
    for v in piece.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    puv = piece.loops.layers.uv.new("UVMap"); along = max(range(3), key=lambda i: size[i])
    shift = Vector((rng.random(), rng.random()))
    for f in piece.faces:
        n = max(range(3), key=lambda i: abs(f.normal[i])); a, b = [i for i in range(3) if i != n]
        if along in (a, b):
            a, b = along, b if a == along else a
        for loop in f.loops:
            loop[puv].uv = Vector((loop.vert.co[a], loop.vert.co[b])) / tile + shift
    bmesh.ops.bevel(piece, geom=piece.edges[:], offset=BEVEL, segments=2, affect="EDGES", profile=0.5)
    bmesh.ops.transform(piece, matrix=matrix, verts=piece.verts)
    me = bpy.data.meshes.new("_board"); piece.to_mesh(me); piece.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def bench(coll, mat):
    """Legs, arms, a slatted seat and a back of upright spindles leaning back, all teak."""
    b, rng, tile = BENCH, random.Random(3), TEXTURES["teak_veneer"][0]
    bm = bmesh.new(); bm.loops.layers.uv.new("UVMap")

    def put(size, at, frame=Matrix()):
        board(bm, size, frame @ Matrix.Translation(at), tile, rng)

    side, inner, seat = b["width"] / 2 - 0.05, b["width"] - 0.16, b["seat"]
    back = Matrix.Translation((0, 0.19, 0.42)) @ Matrix.Rotation(math.radians(-b["tilt"]), 4, "X")   # leaning back
    for x in (-side, side):
        put((0.055, 0.055, 0.64), (x, -0.2, 0.32))                     # front leg, up to the arm
        put((0.055, 0.06, 0.45), (x, 0.19, 0.225))                     # back leg
        put((0.055, 0.06, 0.52), (x, 0, 0.26), back)                   # back post
        put((0.07, 0.64, 0.03), (x, 0.0, 0.655))                       # arm, a little past the front leg
        put((0.03, 0.4, 0.07), (x * 0.985, 0, 0.385))                  # seat rail
        put((0.035, 0.4, 0.035), (x, 0, 0.12))                         # low rail
    put((inner, 0.025, 0.07), (0, -0.205, 0.385)); put((inner, 0.025, 0.07), (0, 0.19, 0.385))   # front and back rails
    put((0.03, 0.4, 0.05), (0, 0, 0.395)); put((inner, 0.035, 0.035), (0, 0, 0.12))            # middle support, stretcher
    width, gap = 0.062, 0.011
    for k in range(b["slats"]):                                        # the seat, its top at seat height
        put((inner + 0.02, width, 0.022), (0, -0.235 + width / 2 + k * (width + gap), seat - 0.011))
    put((inner, 0.03, 0.085), (0, 0, 0.47), back); put((inner, 0.025, 0.05), (0, 0, 0.11), back)   # back's top, bottom rail
    for k in range(b["spindles"]):
        x = (k / (b["spindles"] - 1) - 0.5) * (inner - 0.12)
        put((0.045, 0.016, 0.3), (x, 0, 0.285), back)
    me = bpy.data.meshes.new("garden_bench"); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new("garden_bench", me); ob["garden_asset"] = "garden_bench"; coll.objects.link(ob)


def log(coll, name, length, radius, bark, end, rng):
    """A round log, a little uneven and bent, bark all round, its cut ends burnt."""
    sides, rings = 12, max(4, int(length / 0.08))
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); tile = TEXTURES["bark_brown_02"][0]
    bend = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.03
    grid = []
    for r in range(rings + 1):
        t = r / rings; middle = bend * 4 * t * (1 - t) + Vector((0, 0, t * length))
        swell = radius * rng.uniform(0.93, 1.07)
        grid.append([bm.verts.new(middle + Vector((math.cos(a), math.sin(a), 0)) * swell * rng.uniform(0.95, 1.05))
                     for a in (2 * math.pi * k / sides for k in range(sides))])
    circ = 2 * math.pi * radius
    for r in range(rings):
        for k in range(sides):
            f = bm.faces.new((grid[r][k], grid[r][(k + 1) % sides], grid[r + 1][(k + 1) % sides], grid[r + 1][k]))
            for loop, (du, dv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                loop[uv].uv = ((k + du) / sides * circ / tile, (r + dv) / rings * length / tile)
    for ring, flip in ((grid[0], True), (grid[-1], False)):           # the cut ends
        f = bm.faces.new(list(reversed(ring)) if flip else ring); f.material_index = 1
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(bark); me.materials.append(end)
    ob = bpy.data.objects.new(name, me); ob["garden_asset"] = "firewood"; coll.objects.link(ob)


def fire_ground(coll, mat, rng):
    """A disc of burnt earth with a ragged edge, lying just on the grass; the fire pit sits in it."""
    g, sides = GROUND, 48
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    edge = [g["radius"] * (1 - g["ragged"] * (0.5 + 0.3 * math.sin(3 * a + 1) + 0.2 * math.sin(7 * a) + rng.uniform(-0.2, 0.2)))
            for a in (2 * math.pi * k / sides for k in range(sides))]
    rings = [[bm.verts.new((math.cos(2 * math.pi * k / sides) * edge[k] * t, math.sin(2 * math.pi * k / sides) * edge[k] * t, g["height"]))
              for k in range(sides)] for t in (0.35, 0.7, 1.0)]
    middle = bm.verts.new((0, 0, g["height"]))
    for k in range(sides):
        bm.faces.new((middle, rings[0][k], rings[0][(k + 1) % sides]))
        for inner, outer in zip(rings, rings[1:]):
            bm.faces.new((inner[k], outer[k], outer[(k + 1) % sides], inner[(k + 1) % sides]))
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = Vector(loop.vert.co.xy) / TEXTURES["burned_ground_01"][0]
    me = bpy.data.meshes.new("fire_ground"); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new("fire_ground", me); ob["garden_asset"] = "fire_ground"; coll.objects.link(ob)


def build(src, out):
    """The bench with its cushions, the logs and the burnt earth, each in its own collection of garden_assets.blend."""
    for asset in ("garden_bench", "firewood", "fire_ground"):
        coll = bpy.data.collections.new(asset); bpy.context.scene.collection.children.link(coll)
        if asset == "garden_bench":
            bench(coll, material("garden_bench_teak", src, out, "teak_veneer"))
            garden_cushions.build(coll)
        elif asset == "fire_ground":
            fire_ground(coll, material("garden_fire_ground", src, out, "burned_ground_01"), random.Random(4))
        else:
            bark, end, rng = material("garden_firewood_bark", src, out, "bark_brown_02"), plain("garden_firewood_end", CHAR), random.Random(8)
            for name, (length, radius) in LOGS.items():
                log(coll, name, length, radius, bark, end, rng)
