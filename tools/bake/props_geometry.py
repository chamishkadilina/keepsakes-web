"""Geometry helpers for the museum's props: one bmesh per material (Parts), rounded boxes, surfaces of revolution,
tubes, grids with UVs. Units: metres, Blender axes (z up)."""
import bmesh, math
from mathutils import Vector, Matrix

TAU = 2 * math.pi
UP = Vector((0, 0, 1))


def srgb(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1)


class Parts(dict):
    """One bmesh per material, made on first use: a piece builds into these, add() places and merges them.
    flames: candle flame points (the web lights them); fairies: the little lights behind the foyer's sheer curtains (the
    web lights them); notes: where the love notes hang ((card middle, ribbon top height); the web hangs them); lights:
    accent lights for the bake (dicts: pos, colour, watts, kind POINT, AREA or SPOT, for AREA size and normal, for SPOT
    normal and cone); markers: named points for the web, {name: (position, extras)} (an "aim" extra is a direction)."""
    def __init__(self):
        super().__init__()
        self.flames, self.fairies, self.notes, self.lights, self.markers = [], [], [], [], {}

    def __missing__(self, name):
        bm = self[name] = bmesh.new()
        return bm


def track(bm):
    """Verts created after this call: `done()` returns them (to place one part of a piece)."""
    before = set(bm.verts)
    return lambda: [v for v in bm.verts if v not in before]


def rbox(bm, size, radius, segments=3, at=(0, 0, 0)):
    """Box with rounded edges and corners, centred at `at` (size = full extents)."""
    done = track(bm)
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    edges = list({e for v in r["verts"] for e in v.link_edges})
    bmesh.ops.bevel(bm, geom=r["verts"] + edges, offset=min(radius, min(size) / 2 - 1e-4), offset_type="OFFSET",
                    segments=segments, profile=0.5, affect="EDGES", clamp_overlap=True)
    verts = done()
    bmesh.ops.translate(bm, verts=verts, vec=Vector(at))
    return verts


def cuts(bm, verts, axis, lo, hi, step):
    """Extra vertex rings across a part every `step` along an axis, so the baked vertex light has room to vary.
    Returns all the part's verts (the new ones included)."""
    done = track(bm)
    geom = list(set(verts) | {e for v in verts for e in v.link_edges} | {f for v in verts for f in v.link_faces})
    k = lo + step
    while k < hi - 1e-4:
        co, no = [0, 0, 0], [0, 0, 0]
        co[axis], no[axis] = k, 1
        geom = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)["geom"]
        k += step
    return list(verts) + done()


def board(bm, size, at, step=0.1, radius=0.003):
    """Flat panel (shelf, side, back) with vertex rings every `step` along its two long sides."""
    verts = rbox(bm, size, radius, 1, at=at)
    for axis in sorted(range(3), key=lambda a: size[a])[1:]:
        verts = cuts(bm, verts, axis, at[axis] - size[axis] / 2, at[axis] + size[axis] / 2, step)
    return verts


def cushion(bm, size, radius, at, face, puff, steps=(0.06, 0.06, 0.06)):
    """Upholstered block: a rounded box whose `face` side (axis index, sign) is softly domed by `puff` metres."""
    verts = rbox(bm, size, radius, 4, at=at)
    for axis in range(3):
        if axis != face[0]:
            verts = cuts(bm, verts, axis, at[axis] - size[axis] / 2, at[axis] + size[axis] / 2, steps[axis])
    a, sign = face
    others = [k for k in range(3) if k != a]
    for v in verts:
        d = (v.co[a] - at[a]) * sign
        if d <= 0:
            continue
        bump = 1.0
        for k in others:
            x = min(1.0, abs(v.co[k] - at[k]) / (size[k] / 2))
            bump *= math.cos(math.pi / 2 * x) ** 1.5
        v.co[a] += sign * puff * bump * min(1.0, d / (size[a] / 2))
    return verts


def lathe(bm, profile, seg=32, at=(0, 0, 0)):
    """Surface of revolution around z from [(radius, z), ...]; radius 0 makes a pole. Upwards = outward faces."""
    done = track(bm)
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(TAU * k / seg), r * math.sin(TAU * k / seg), z)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            if len(a) == 1 and len(b) == 1:
                break
            if len(a) == 1:
                bm.faces.new((a[0], b[(k + 1) % seg], b[k]))
            elif len(b) == 1:
                bm.faces.new((a[k], a[(k + 1) % seg], b[0]))
            else:
                bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    verts = done()
    bmesh.ops.translate(bm, verts=verts, vec=Vector(at))
    return verts


def tube(bm, pts, radius, seg=12, closed=False, plane_normal=None):
    """Round tube along a path; `radius` is one value or one per point (tapering branches). The cross-section is
    carried along without twisting (planar loops may pass their plane's normal instead)."""
    done = track(bm)
    n = len(pts)
    radii = list(radius) if isinstance(radius, (list, tuple)) else [radius] * n
    tangents = []
    for i in range(n):
        a = pts[i - 1] if (i > 0 or closed) else pts[i]
        b = pts[(i + 1) % n] if (i < n - 1 or closed) else pts[i]
        tangents.append((b - a).normalized())
    side = plane_normal.normalized() if plane_normal is not None else tangents[0].cross(UP)
    if side.length < 1e-3:
        side = tangents[0].cross(Vector((1, 0, 0)))
    side.normalize()
    rings = []
    for p, t, r in zip(pts, tangents, radii):
        if plane_normal is None:
            side = (side - t * side.dot(t)).normalized()                       # parallel transport: no twist
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(p + (side * math.cos(TAU * k / seg) + up * math.sin(TAU * k / seg)) * r) for k in range(seg)])
    for i in range(n if closed else n - 1):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(seg):
            bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k]))
    if not closed:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    verts = done()
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in verts for f in v.link_faces}))
    return verts


def rounded_rect(u0, u1, v0, v1, r, arc=5):
    """Closed rounded-rectangle path as (u, v) points, counter-clockwise."""
    pts = []
    for cu, cv, a0 in ((u1 - r, v0 + r, -90), (u1 - r, v1 - r, 0), (u0 + r, v1 - r, 90), (u0 + r, v0 + r, 180)):
        for k in range(arc + 1):
            a = math.radians(a0 + 90 * k / arc)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def place(bm, verts, yaw=0.0, at=(0, 0, 0), tilt=None):
    """Turns a built part (yaw in degrees around z; optional tilt (degrees, pivot) around x first) and moves it."""
    m = Matrix.Translation(Vector(at)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    if tilt:
        deg, pivot = tilt
        m = m @ Matrix.Translation(Vector(pivot)) @ Matrix.Rotation(math.radians(deg), 4, "X") @ Matrix.Translation(-Vector(pivot))
    bmesh.ops.transform(bm, matrix=m, verts=verts)


def aim(axis, spin=0.0):
    """Rotation turning +z towards `axis`, spun around it by `spin` radians."""
    return axis.to_track_quat("Z", "Y").to_matrix().to_4x4() @ Matrix.Rotation(spin, 4, "Z")


def along(pts, t):
    """Point at parameter t (0 ... 1) along a polyline (evenly by segment)."""
    k = min(len(pts) - 2, int(t * (len(pts) - 1)))
    return pts[k].lerp(pts[k + 1], t * (len(pts) - 1) - k)


def uv_layer(bm, name="UVMap"):
    """A named UV layer (made if missing). UVMap: textures; bob: balloon motion on the web."""
    return bm.loops.layers.uv.get(name) or bm.loops.layers.uv.new(name)


def set_uv(bm, faces, fn, layer="UVMap"):
    """UVs from a function of each corner's position."""
    layer = uv_layer(bm, layer)
    for f in faces:
        for loop in f.loops:
            loop[layer].uv = fn(loop.vert.co)


def in_rect(rect, a, b):
    """Point (a, b) in 0 ... 1 inside a UV rectangle."""
    u0, v0, u1, v1 = rect
    return (u0 + (u1 - u0) * a, v0 + (v1 - v0) * b)


def grid(bm, x0, x1, y0, y1, z, step=0.1, uv=None):
    """Flat grid facing up with vertices every ~`step`; uv(co) gives UVs."""
    done = track(bm)
    nx, ny = max(1, math.ceil((x1 - x0) / step)), max(1, math.ceil((y1 - y0) / step))
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, z)) for i in range(nx + 1)] for j in range(ny + 1)]
    faces = [bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i])) for j in range(ny) for i in range(nx)]
    if uv:
        set_uv(bm, faces, uv)
    return done()


def polar_grid(bm, radius, z, step=0.1, seg=48, uv=None, down=False):
    """Flat disc at height z with rings every ~`step` (a fan in the middle); faces up (or down). uv(co) gives UVs.
    Returns its verts and its outer ring."""
    done = track(bm)
    nr = max(1, math.ceil(radius / step))
    centre = bm.verts.new((0, 0, z))
    rings = [[bm.verts.new((radius * j / nr * math.cos(TAU * k / seg), radius * j / nr * math.sin(TAU * k / seg), z))
              for k in range(seg)] for j in range(1, nr + 1)]
    faces = [bm.faces.new((centre, rings[0][k], rings[0][(k + 1) % seg])) for k in range(seg)]
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[k], b[k], b[(k + 1) % seg], a[(k + 1) % seg])) for k in range(seg)]
    if down:
        bmesh.ops.reverse_faces(bm, faces=faces)
    if uv:
        set_uv(bm, faces, uv)
    return done(), rings[-1]


def uv_box(bm, size, at, uv):
    """Box (full extents `size`, centred at `at`) whose faces each get a UV rectangle: uv["+x"], uv["-z"], ...
    Each rectangle maps with v up the face (towards +z, or +y on the top and bottom), seen from outside."""
    layer = uv_layer(bm)
    axes, half, verts = (Vector((1, 0, 0)), Vector((0, 1, 0)), UP), [s / 2 for s in size], {}

    def vert(p):
        key = tuple(round(c, 6) for c in p)
        if key not in verts:
            verts[key] = bm.verts.new(Vector(at) + Vector(key))
        return verts[key]
    for a in range(3):
        for sign in (1, -1):
            n = axes[a] * sign
            up = axes[1] if a == 2 else axes[2]
            right = up.cross(n)
            ra, ua = (max(range(3), key=lambda i: abs(v[i])) for v in (right, up))
            corners = [(ru, rv) for ru, rv in ((0, 0), (1, 0), (1, 1), (0, 1))]
            f = bm.faces.new([vert(n * half[a] + right * ((ru - 0.5) * 2 * half[ra]) + up * ((rv - 0.5) * 2 * half[ua]))
                              for ru, rv in corners])
            rect = uv[("+" if sign > 0 else "-") + "xyz"[a]]
            for loop, (ru, rv) in zip(f.loops, corners):
                loop[layer].uv = in_rect(rect, ru, rv)
    return list(verts.values())

