"""The garden at night, a place of their own (layout: garden_layout.py): a teak garden bench for two by the door looking
across the lawn, a log fire in a ring of stones before it, a big jacaranda with strings of little warm lights hanging
from it and draped to the walls, a picnic basket and champagne, lanterns, mossy stones and ferns round the tree, a clean
leafy lawn, and a layered border of trees, bushes and ferns before old mossy stone walls, with flower beds before it.
Also the little wood round the entrance courtyard and the little lights strung over it (Garden.entrance; entrance.py).
CC0 models from Poly Haven (ASSETS.md) and the bench and firewood made in code, prepared by garden_assets.py.

  accents += garden.add(collection)      # in design.py, after props.add (it extends that call's markers)
"""
import bpy, bmesh, math, os, random
from mathutils import Matrix, Vector
from props import footprint
from props_romance import CANDLE_LIGHT
import garden_layout as L


def rotate(v, yaw):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return Vector((v[0] * c - v[1] * s, v[0] * s + v[1] * c))


def by_bench(local):
    return Vector(L.BENCH) + rotate(local, L.BENCH_YAW)


class Garden:
    def __init__(self, collection):
        self.collection = collection
        self.merged, self.placed, self.accents, self.flames = {}, [], [], []
        self.rng = random.Random(14)
        self.breeze = random.Random(5)                                # each plant's own rhythm in the breeze

    def size(self, names, scale):
        vs = [v.co for n in names for v in bpy.data.objects[n].data.vertices]
        s = max(scale) if isinstance(scale, tuple) else scale
        return max(max(v.x for v in vs) - min(v.x for v in vs), max(v.y for v in vs) - min(v.y for v in vs)) * s / 2

    def free(self, at, radius, keep_out=()):
        """True when a piece this wide fits here: clear of what is placed and of the walking ways."""
        if any((Vector(at) - p).length < radius + r for p, r in self.placed):
            return False
        return not any(near(at) < radius + r for near, r in keep_out)

    def put(self, names, at, yaw, scale, name=None, walk_round=True, lift=0.0, lean=0.0, phase=None):
        """Places one piece (its variants' meshes) and merges its faces into the garden mesh of each material. Its
        footprint (what stands below head height) turns with it. `lean` tips its top towards local -x (degrees).
        A plant carries its own rhythm in the breeze and its height in a second UV set, `wind` (phase, height in m;
        glTF TEXCOORD_1, read by the web's wind.ts: a UV set survives the meshopt packing, a custom attribute does not)."""
        s = Matrix.Diagonal((*scale, 1)) if isinstance(scale, tuple) else Matrix.Scale(scale, 4)
        turn = Matrix.Translation((at[0], at[1], lift)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(-lean), 4, "Y")
        m, low = turn @ s, []
        sway = names[0].startswith(L.SWAYING)
        if sway:
            height = max((s @ v.co).z for n in names for v in bpy.data.objects[n].data.vertices) + lift
            wind = [self.breeze.random() if phase is None else phase, height]
        for n in names:
            me = bpy.data.objects[n].data.copy(); me.transform(s)
            low += [v.co.copy() for v in me.vertices if v.co.z + lift < 1.8]   # copies: the mesh is removed below
            me.transform(turn)
            if sway:                                                 # the wind always the second set (TEXCOORD_1)
                while len(me.uv_layers) > 1:
                    me.uv_layers.remove(me.uv_layers[-1])
                me.uv_layers.new(name="wind").data.foreach_set("uv", wind * len(me.loops))
            for i, mat in enumerate(me.materials):
                key = "glass" if mat.name.startswith("glass") else mat.name
                bm = bmesh.new(); bm.from_mesh(me)
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != i], context="FACES")
                for f in bm.faces:
                    f.material_index = 0
                tmp = bpy.data.meshes.new("_piece"); bm.to_mesh(tmp); bm.free()
                self.merged.setdefault(key, bmesh.new()).from_mesh(tmp); bpy.data.meshes.remove(tmp)
            bpy.data.meshes.remove(me)
        self.placed.append((Vector(at), self.size(names, scale)))
        if name and walk_round and low:
            middle, half, radius = footprint(low)
            ob = bpy.data.objects.new(f"footprint_garden_{name}", None)
            ob.location = (*(Vector(at) + rotate(middle, yaw)), 0); ob.rotation_euler = (0, 0, math.radians(yaw))
            ob["footprint"] = [round(half.x, 3), round(half.y, 3)]
            if radius:
                ob["radius"] = round(radius, 3)
            self.collection.objects.link(ob)
        return m

    def lights_of(self, asset, m):
        """A candle's or a lantern's flame (the web lights it) and its warm glow (baked)."""
        top = max(v.co.z for v in bpy.data.objects[asset].data.vertices)
        flame = m @ Vector((0, 0, top + 0.025 if asset == "wooden_candlestick" else top * 0.42))
        self.flames.append(flame)
        self.accents.append(dict(kind="POINT", pos=flame + Vector((0, 0, 0.03)), colour=CANDLE_LIGHT, watts=5.0 if asset == "wooden_candlestick" else 6.0))

    def tree(self):
        """The jacaranda; strings of little lights hang straight down from the underside of its canopy."""
        parts = [o.name for o in bpy.data.objects if o.get("garden_asset") == "jacaranda_tree"]
        m = self.put(parts, L.TREE, 0, 1.0, "jacaranda_trunk", phase=0.0)   # phase 0: its little lights sway with it
        self.placed[-1] = (Vector(L.TREE), 1.2)                   # only the trunk takes room on the ground
        twigs = [m @ v.co for v in bpy.data.objects["jacaranda_tree_branches"].data.vertices]
        self.twigs = [p for p in twigs if 2.9 < p.z < 4.6 and 1.0 < (p.xy - Vector(L.TREE)).length < 5.5]
        lights = []
        for top in self.rng.sample(self.twigs, L.STRANDS):
            for k in range(self.rng.randint(*L.STRAND_LIGHTS)):
                if top.z - 0.1 - k * L.STRAND_STEP >= L.LIGHTS_LOWEST:
                    lights.append(top - Vector((0, 0, 0.1 + k * L.STRAND_STEP)))
        for i in range(L.TREE_GLOWS):                             # their warm light under the canopy, for the bake
            group = lights[i::L.TREE_GLOWS]
            self.accents.append(dict(kind="POINT", pos=sum(group, Vector()) / len(group), colour=(1.0, 0.62, 0.3), watts=35.0))
        x, y, yaw = L.SMALL_TREE                                  # and a younger one in the far corner
        self.put([o.name for o in bpy.data.objects if o.get("garden_asset") == "jacaranda_small"], (x, y), yaw, 1.0, "jacaranda_small")
        self.placed[-1] = (Vector((x, y)), 0.9)
        return lights

    def swags(self):
        """Strings of little lights draped from the tree's lower branches to the walls, above head height."""
        lights = []
        for end in map(Vector, L.SWAGS):
            start = min(self.twigs, key=lambda p: (p - end).length)
            n = max(2, int((end - start).length / L.SWAG_STEP))
            for k in range(n + 1):
                t = k / n; p = start.lerp(end, t)
                p.z = max(L.LIGHTS_LOWEST, p.z - 4 * L.SWAG_SAG * t * (1 - t))
                lights.append(p)
        return lights

    def bench(self):
        self.put(["garden_bench", "bench_cushions"], by_bench((0, 0)), L.BENCH_YAW, 1.0, "bench")
        for i, (asset, local, yaw, scale) in enumerate(L.BY_BENCH):
            m = self.put([asset], by_bench(local), L.BENCH_YAW + yaw, scale, f"by_bench_{i}", walk_round=not asset.startswith("wine"))
            if asset in ("wooden_candlestick", "wooden_lantern_01"):
                self.lights_of(asset, m)
        for name, (x, y, z) in L.SEATS.items():                   # sitters look along local -Y, as the bench
            seat = bpy.data.objects[name]
            seat.location = (*by_bench((x, y)), z)
            seat.rotation_euler = (0, 0, math.radians(L.BENCH_YAW))

    def fire(self):
        """The fire pit, set into a patch of burnt earth: a teepee of firewood leaning in over kindling, two logs fallen
        into the embers; the web lights the fire at the `campfire` marker. Its warm light is baked."""
        at = by_bench(L.FIRE)
        self.put(["fire_ground"], at, self.rng.uniform(0, 360), 1.0)
        self.put(["stone_fire_pit"], at, 0, 1.0, "fire_pit", lift=-L.FIRE_SINK)
        for asset, yaw in L.KINDLING:
            self.put([asset], at, yaw, 0.55, lift=0.03)
        t = L.TEEPEE
        for k in range(t["count"]):                               # each log's foot out on the ring, its top leaning in
            yaw = 360 * k / t["count"] + self.rng.uniform(-10, 10)
            self.put([t["logs"][k % len(t["logs"])]], at + rotate((t["radius"], 0), yaw), yaw, 1.0, lift=0.02, lean=self.rng.uniform(*t["lean"]))
        for asset, offset, yaw, lean in L.FALLEN:
            self.put([asset], at + Vector(offset), yaw, 1.0, lift=0.06, lean=lean)
        self.placed.append((at, 0.8))
        ob = bpy.data.objects.new("campfire", None); ob.location = (at.x, at.y, 0.12); self.collection.objects.link(ob)
        f = L.FIRE_LIGHT
        self.accents.append(dict(kind="POINT", pos=Vector((at.x, at.y, f["height"])), colour=f["colour"], watts=f["watts"], radius=f["radius"]))

    def features(self):
        for i, (asset, at, yaw, scale) in enumerate(L.FEATURES):
            names = list(asset) if isinstance(asset, tuple) else [asset]
            if not self.free(at, self.size(names, scale) * 0.5):
                continue
            m = self.put(names, at, yaw, scale, f"feature_{i}", walk_round=not names[0].startswith("fern"))
            if asset == "wooden_lantern_01":
                self.lights_of(asset, m)

    def border(self):
        for layer, choices, step in (("tall", L.TALL, L.BORDER["spacing"][0]), ("front", L.FRONT, L.BORDER["spacing"][1])):
            for i, (a, b) in enumerate(L.WALLS):
                a, b = Vector(a), Vector(b); along = (b - a).normalized(); inward = Vector((-along.y, along.x))
                for k in range(int((b - a).length / step)):
                    at = a + along * (step * (k + 0.5) + self.rng.uniform(-0.2, 0.2)) + inward * (L.BORDER[layer] + self.rng.uniform(-0.15, 0.15))
                    names = list(self.rng.choice(choices)) if layer == "tall" else [self.rng.choice(choices)]
                    scale = self.rng.uniform(*L.TALL_SCALE) if layer == "tall" else self.rng.uniform(1.0, 1.25)
                    if layer == "tall" and (at - Vector(L.BENCH)).length < L.BENCH_OPEN:
                        continue                                  # the sky stays open behind the bench
                    if self.free(at, self.size(names, scale) * (0.25 if layer == "tall" else 0.5)):
                        self.put(names, at, self.rng.uniform(0, 360), scale, f"{layer}_{i}_{k}")

    def flower_beds(self):
        """Flower beds before the border, each one kind, along the walls with gaps between; clear of the way from the
        door to the bench and of the fire. The lawn in the middle stays open."""
        door, bench = Vector(L.DOOR), by_bench((0, -0.9))
        def to_path(p):
            d = bench - door; t = max(0.0, min(1.0, (Vector(p) - door).dot(d) / d.length_squared))
            return (Vector(p) - (door + d * t)).length
        keep_out = [(to_path, 0.8), (lambda p: (Vector(p) - by_bench(L.FIRE)).length, 1.6)]
        b = L.BEDS
        for a, z in L.WALLS:
            a, z = Vector(a), Vector(z); along = (z - a).normalized(); inward = Vector((-along.y, along.x))
            for k in range(int((z - a).length / b["step"])):
                if self.rng.random() > b["keep"]:
                    continue
                middle, kind = a + along * b["step"] * (k + 0.5) + inward * b["distance"], self.rng.choice(L.FLOWERS)
                for _ in range(self.rng.randint(*b["count"])):
                    at = middle + along * self.rng.uniform(-1, 1) * b["size"][0] + inward * self.rng.uniform(-1, 1) * b["size"][1]
                    scale = self.rng.uniform(1.0, 1.4)
                    if self.free(at, self.size([kind], scale) * 0.5, keep_out):
                        self.put([kind], at, self.rng.uniform(0, 360), scale)

    def entrance(self):
        """The wood round the entrance clearing (garden_layout.ENTRANCE): rows of tall trees outwards from its edges, bushes
        in front of and between them, none near the museum's walls; the little lights strung over the clearing and their
        warm glow (bake). Returns the lights."""
        e = L.ENTRANCE
        def museum(p):                                            # m from the museum's outer walls
            return min(math.hypot(max(x0 - p.x, 0, p.x - x1), max(y0 - p.y, 0, p.y - y1)) for x0, x1, y0, y1 in e["museum"])
        wood = []                                                 # (where, room): crowns may overlap, trunks and bushes not
        for row, (offset, step, scales, choices) in enumerate(e["rows"]):
            trees = isinstance(choices[0], tuple)
            for i, (a, b) in enumerate(e["edges"]):
                a, b = Vector(a), Vector(b); along = (b - a).normalized(); out = Vector((along.y, -along.x))
                for k in range(int((b - a).length / step) + 1):
                    at = a + along * (step * (k + 0.5 * (row % 2)) + self.rng.uniform(-0.3, 0.3)) + out * (offset + self.rng.uniform(-0.25, 0.25))
                    if offset < 0 and at.y < e["clearing"]["y0"] + 1.5 and e["path"][0] < at.x < e["path"][1]:
                        continue                                  # the path's end stays open
                    if museum(at) < e["margin"][0 if trees else 1]:
                        continue                                  # crowns would grow through its walls
                    names = list(self.rng.choice(choices)) if trees else [self.rng.choice(choices)]
                    scale = self.rng.uniform(*scales)
                    room = self.size(names, scale) * e["room"][0 if trees else 1]
                    if all((at - p).length >= room + r for p, r in wood):
                        wood.append((at, room))
                        self.put(names, at, self.rng.uniform(0, 360), scale, f"entrance_{row}_{i}_{k}" if offset < 0 else None)
        lights = []
        for string in e["strings"]:
            for start, end in zip(map(Vector, string), map(Vector, string[1:])):
                n = max(2, int((end - start).length / e["step"]))
                span = []
                for k in range(n + 1):
                    t = k / n; p = start.lerp(end, t)
                    p.z -= 4 * e["sag"] * t * (1 - t)
                    span.append(p)
                lights += span
                glow = span[n // 2] - Vector((0, 0, 0.2))
                glow.y = min(glow.y, -0.2 - e["glow_clear"])           # the museum's front is at y -0.2
                self.accents.append(dict(kind="POINT", pos=glow, colour=e["glow"], watts=e["watts"]))
        return lights

    def finish(self):
        """One mesh per material (prop_garden_<material>), lit by its own baked vertex light like every prop."""
        for key, bm in self.merged.items():
            me = bpy.data.meshes.new(f"prop_garden_{key.removeprefix('garden_')}"); bm.to_mesh(me); bm.free()
            me.materials.append(bpy.data.materials[key])           # "glass": the museum's own (props.py)
            ob = bpy.data.objects.new(me.name, me); self.collection.objects.link(ob)
            ob["prop"] = key; ob["noReflection"] = True
            if key == "glass":
                ob.hide_render = True                               # drawn by the web only (its glass material)
            else:
                ob["bake_vertex"] = True
            print(f"garden {me.name:44s} {len(me.polygons):7d} faces")


def surfaces(folder):
    """The grass and the garden walls: their colour textures, tiled at their real size on the first UV set (the second
    holds their baked light)."""
    for name, (mat_name, file) in L.SURFACES.items():
        ob = bpy.data.objects[name]; me = ob.data; uv = me.uv_layers["UVMap"].data
        for poly in me.polygons:
            n = poly.normal
            for li in poly.loop_indices:
                p = ob.matrix_world @ me.vertices[me.loops[li].vertex_index].co
                u, v = (p.x, p.y) if abs(n.z) > 0.7 else (p.y, p.z) if abs(n.x) > abs(n.y) else (p.x, p.z)
                uv[li].uv = (u / L.TILE, v / L.TILE)
        nt = bpy.data.materials[mat_name].node_tree; bsdf = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.path.join(folder, file)); tex.image.pack()
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])


def add(collection):
    """Builds the garden into `collection`. Extends the candle_flames marker (props.add), lists the tree's little lights
    in `garden_lights`; returns the accent lights for the bake (lanterns, the fire and the tree's little lights)."""
    folder = os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), L.FOLDER)
    with bpy.data.libraries.load(os.path.join(folder, "garden_assets.blend"), link=False) as (src, dst):
        dst.objects = list(src.objects)
    for img in bpy.data.images:
        if "garden_" in img.name and not img.packed_file:
            img.pack()
    g = Garden(collection)
    lights = g.tree(); g.bench(); g.fire(); g.features(); g.border(); g.flower_beds()
    lights += g.swags() + g.entrance(); g.finish()
    surfaces(folder)
    for ob in [o for o in bpy.data.objects if o.get("garden_asset")]:
        bpy.data.objects.remove(ob)
    flames = bpy.data.objects["candle_flames"]
    flames["flames"] = list(flames["flames"]) + [round(c, 4) for p in g.flames for c in p]
    garden_lights = bpy.data.objects.new("garden_lights", None)   # the web draws them larger than the foyer's
    garden_lights["fairies"] = [round(c, 3) for p in lights for c in p]; collection.objects.link(garden_lights)
    return g.accents
