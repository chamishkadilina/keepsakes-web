"""The museum's furniture, exhibits and romantic decor, modelled in code so they share the building's palette and bake
with its light. design.py calls add(): it builds every piece of LAYOUT where it belongs, merges them into one mesh per
material in each part of the museum (prop_<zone>_<material>: a few draw calls, and the rooms you can't see are culled),
marks each piece's floor footprint (footprint_<name>: a box or a circle the visitor walks round), where every candle
flame burns (candle_flames), the little lights behind the foyer's sheers (fairy_lights), the projector's lens
(projector_lens) and the dimmer switch (dimmer_switch), and returns the exhibit spotlights and the accent lights
(candles, lanterns, the sheers' little lights, the neon, the uplights by the screen) for the bake.

  - the velvet sofas with cream cushions, rugs, marble tables and consoles with roses and candles
  - exhibits in their own spotlights: the big title wall facing you as you come in (foyer), the quote board on its
    easel and a grand dome of roses beside the collage
  - each chapter's title on a smaller board straight ahead as you come into its room (story gallery, right gallery)
  - the foyer's round rug with their initials; the heart room's dance floor in a pool of light, under the web's disco
    ball; love notes hanging over the right gallery (one per reason); popcorn, drinks and a "Now Showing"
    poster in the cinema
  - romance: ivory sheers with little lights glowing through them along the foyer's side walls, velvet curtains framing
    the door where the story begins, candles (their flames burn on the web), heart foil balloons
    that float, golden light strings along the heart room's walls and a gold dimmer by its door, a rose garland round
    the collage, candles round the rose-petal heart in front of it, flower stands and urns, a neon
  - green house trees: kentia palms, weeping figs, olive trees and fiddle-leaf figs; rose topiaries (props_trees.py)
  - the screen room's cinema: a projector, the screen in its black-and-gold frame on a little velvet stage between
    red velvet curtains, velvet curtains on the garden door (props_cinema.py), rose topiaries washed by warm floor
    lights either side of the stage
  - the way in (props_entrance.py), like a wedding: the entrance's ivory doorway with its deep red doors wide open in
    a garland of roses, a red carpet into the foyer lined with gold flower stands, roses and balloons by the door (the
    clearing: entrance.py; the wood round it and the little lights over it: garden.py)

Pieces: props_romance.py, props_flowers.py, props_trees.py, props_cinema.py, props_entrance.py (the garden: garden.py); helpers:
props_geometry.py; texture: props_atlas.py. Every piece is lit by its own baked vertex light (bake_vertex). Units:
metres, Blender axes (z up); a piece's front faces local +y."""
import bmesh, math, random
from mathutils import Vector, Matrix
from props_geometry import (TAU, UP, Parts, track, rbox, cuts, cushion, lathe, tube, place, set_uv, in_rect, grid, polar_grid,
                            uv_box)
from props_flowers import leaf, bloom, roses, rose_leaves, vase_of_roses, flower_urn
from props_romance import (plinth, candle_cluster, candle_tray, lantern, heart_point, balloon_bunch, light_string,
                           sheer_drape, dimmer_switch, velvet_ropes, neon_sign, floral_stand, niche_garland, love_notes)
from props_trees import olive_tree, fig_tree, kentia_palm, weeping_fig, rose_topiary
from props_cinema import projector, curtain_panel, pelmet, cinema_screen, poster, popcorn_box, drink_cup
from props_entrance import portal, jamb, door_leaf, runner
from props_atlas import RUGS, MARBLE_RECT, uv_rect

PALETTE = {                                   # material name: sRGB colour (the web reads the names)
    "velvet_rose": (152, 80, 112),            # dusty-rose velvet
    "velvet_cream": (236, 226, 212),          # cushions, white roses
    "curtain_velvet": (118, 16, 34),          # deep red velvet: the curtains, pelmets and the little stage
    "gold_metal": (226, 192, 140),            # champagne gold, like the downlight trims and spot heads
    "ribbon_red": (150, 22, 40),              # the topiaries' satin bows
    "quote_board": (246, 240, 228),           # the quote board's face (the web writes the quote on it)
    "welcome_board": (246, 240, 228),         # the title wall's face (the web writes the welcome on it)
    "chapter_story": (246, 240, 228),         # the story gallery's chapter board (the web writes its title on it)
    "chapter_reasons": (246, 240, 228),       # the right gallery's chapter board (the web writes its title on it)
    "monogram_rug": (244, 238, 228),          # the foyer's round rug (the web weaves their initials into it)
    "poster_face": (240, 236, 230),           # the cinema poster's lit face (the web draws their poster; not baked)
    "popcorn": (246, 226, 170),               # buttery popcorn
    "sheer_ivory": (248, 242, 234),           # the foyer's sheer curtains (see-through on the web, not baked)
    "screen_white": (240, 240, 238),          # the cinema screen (softly lit on the web, not baked)
    "rose_petal": (150, 12, 30),              # deep red roses, velvet ropes
    "rose_blush": (226, 150, 160),            # blush-pink roses
    "rose_leaf": (78, 128, 60),               # rose leaves and stems
    "ficus_leaf": (62, 110, 46),              # the weeping figs' small glossy leaves
    "olive_leaf": (118, 134, 96),             # silvery olive green
    "fig_leaf": (42, 80, 36),                 # deep fiddle-leaf green, the foliage between roses
    "bark": (98, 86, 72),                     # trunks and branches
    "soil": (54, 40, 30),                     # potting soil, candle wicks
    "decor_atlas": (255, 255, 255),           # rugs, marble, gift wrap (props_atlas.py)
    "balloon_foil": (255, 255, 255),          # heart balloons and their ribbons (colours from the atlas)
    "projector_white": (236, 234, 230),       # the projector's body: satin white, so it reads on the ceiling
    "projector_black": (36, 34, 34),          # its mount, vents and lens barrel
    "lens_glow": (255, 244, 225),             # the projector's lens (lit on the web, not baked)
    "bulb_glow": (255, 214, 150),             # the bulbs of the light strings (lit on the web, not baked)
    "glass": (255, 255, 255),                 # lantern panes, the neon's panel (shaded on the web, not baked)
    "neon_text": (255, 120, 180),             # where the web writes the neon words (not baked)
}
# trim_cream (plinths, planters, urns, vases, candles, the letters' faces) is the building's own cream (design.py)
UNBAKED = ("glass", "neon_text", "lens_glow", "bulb_glow", "sheer_ivory", "screen_white", "poster_face")
DOUBLE_SIDED = ("rose_petal", "rose_blush", "rose_leaf", "olive_leaf", "fig_leaf", "ficus_leaf", "velvet_cream", "curtain_velvet",
                "sheer_ivory")                    # thin surfaces (the web draws both sides)
NO_REFLECTION = ("rose_petal", "rose_blush", "rose_leaf", "olive_leaf", "fig_leaf", "ficus_leaf", "velvet_cream", "bark", "soil",
                 "decor_atlas", "glass", "ribbon_red", "neon_text", "lens_glow", "bulb_glow", "sheer_ivory", "monogram_rug",
                 "popcorn")


# ---------------------------------------------------------------- seating

def pillow(bm, w, h, t, n=8):
    """Square cushion: two domed faces sewn together at a seam, corners pinched in a little; faces +y."""
    done = track(bm)
    rows = []
    for j in range(n + 1):
        v = j / n * 2 - 1
        rows.append([(u * w / 2 * (1 - 0.08 * v * v), t / 2 * (max(0.0, 1 - u * u) * max(0.0, 1 - v * v)) ** 0.45,
                      v * h / 2 * (1 - 0.08 * u * u)) for u in (i / n * 2 - 1 for i in range(n + 1))])
    front = [[bm.verts.new(p) for p in row] for row in rows]
    back = [[front[j][i] if i in (0, n) or j in (0, n) else bm.verts.new((p[0], -p[1], p[2])) for i, p in enumerate(row)]
            for j, row in enumerate(rows)]
    for j in range(n):
        for i in range(n):
            bm.faces.new((front[j][i], front[j + 1][i], front[j + 1][i + 1], front[j][i + 1]))
            bm.faces.new((back[j][i], back[j][i + 1], back[j + 1][i + 1], back[j + 1][i]))
    return done()


def sofa(parts, rng, width=1.7, depth=0.84):
    """Velvet sofa (the screen room's loveseat; wider in the heart room): channel-tufted back, rounded arms, one deep
    bench cushion, tapered gold legs and two cream velvet cushions."""
    v, g, cr = parts["velvet_rose"], parts["gold_metal"], parts["velvet_cream"]
    arm, back = 0.17, 0.2
    cuts(v, rbox(v, (width, depth, 0.22), 0.03, 3, at=(0, 0, 0.22)), 0, -width / 2, width / 2, 0.2)
    seat_w, seat_d = width - 2 * arm, depth - back
    cushion(v, (seat_w + 0.01, seat_d, 0.13), 0.05, (0, depth / 2 - seat_d / 2, 0.385), (2, 1), 0.018, (0.1, 0.1, 0.1))
    for s in (-1, 1):                                                                    # arms
        cuts(v, rbox(v, (arm, depth, 0.36), 0.06, 4, at=(s * (width / 2 - arm / 2), 0, 0.47)), 1, -depth / 2, depth / 2, 0.2)
    n = max(6, round(seat_w / 0.227))
    cw = seat_w / n
    for i in range(n):                                                                   # channel-tufted back
        x = -seat_w / 2 + cw * (i + 0.5)
        c = cushion(v, (cw + 0.02, back - 0.04, 0.56), 0.05, (x, -depth / 2 + back / 2, 0.61), (1, 1), 0.02, (0.06, 0.1, 0.08))
        place(v, c, tilt=(9, (0, -depth / 2 + 0.03, 0.33)))                              # leans back
    rbox(v, (seat_w + 0.02, 0.05, 0.5), 0.02, 3, at=(0, -depth / 2 + 0.025, 0.58))      # back panel
    for sx in (-1, 1):                                                                   # legs
        for sy in (-1, 1):
            lathe(g, [(0, 0.0), (0.013, 0.0), (0.013, 0.004), (0.022, 0.11), (0, 0.11)], 16,
                  at=(sx * (width / 2 - 0.08), sy * (depth / 2 - 0.08), 0))
    for s in (-1, 1):                                                                    # cushions against the back, by the arms
        p = pillow(cr, 0.44, 0.44, 0.16)
        place(cr, p, tilt=(16, (0, 0, -0.22)))
        place(cr, p, yaw=-s * rng.uniform(6, 12), at=(s * (seat_w / 2 - 0.25), -depth / 2 + back + 0.1, 0.69))


# ---------------------------------------------------------------- exhibits

def rose_display(parts, rng, plinth_h=0.62, scale=1.2):
    """The grand roses: a full dome of 112 red and blush roses with leaves, in a cream urn with gold bands on a round
    cream plinth. Returns where its spotlight aims."""
    plinth(parts, plinth_h, 0.3)
    c, g = parts["trim_cream"], parts["gold_metal"]
    urn = [(0, 0), (0.12, 0), (0.125, 0.006), (0.125, 0.024), (0.112, 0.032), (0.08, 0.044), (0.06, 0.07), (0.055, 0.1),
           (0.06, 0.12), (0.078, 0.132), (0.062, 0.148), (0.09, 0.168), (0.135, 0.2), (0.17, 0.24), (0.19, 0.28),
           (0.2, 0.31), (0.208, 0.33), (0.222, 0.345), (0.226, 0.356), (0.214, 0.362), (0.2, 0.356), (0, 0.33)]
    lathe(c, [(r * scale, z * scale) for r, z in urn], 48, at=(0, 0, plinth_h))
    for r, z0, z1 in ((0.1262, 0.008, 0.022), (0.0792, 0.126, 0.138), (0.2275, 0.346, 0.357)):   # gold bands
        r, z0, z1 = r * scale, plinth_h + z0 * scale, plinth_h + z1 * scale
        lathe(g, [(r - 0.002, z0), (r, z0 + 0.001), (r, z1 - 0.001), (r - 0.002, z1)], 48)
    rim, radius, base = plinth_h + 0.356 * scale, 0.36, math.radians(100)
    centre = Vector((0, 0, rim - 0.03 - radius * math.cos(base)))                       # the lowest roses rest on the rim
    core = [(0.3 * math.sin(math.radians(a)), centre.z - 0.3 * math.cos(math.radians(a))) for a in range(0, 181, 20)]
    lathe(parts["fig_leaf"], [(0, core[0][1])] + core[1:-1] + [(0, core[-1][1])], 16)   # dark foliage between the roses
    roses(parts, rng, centre, radius, 112, base, 1.2)
    rose_leaves(parts, rng, centre, radius, 30, (1.65, 1.95), (0.1, 0.13))
    return Vector((0, 0, rim + 0.12))


def framed_board(parts, rng, board, board_w, board_h, f=0.035, posy=None):
    """A board in a slim gold frame (`f` wide) with a posy of roses on two corners (`posy`: their size, by default
    grown with the board), in its own frame: x across, y out of its face, z up from its bottom edge. `board` is its
    face's material, with UVs across it (the web writes on it)."""
    g, b, c = parts["gold_metal"], parts[board], parts["trim_cream"]
    x0, x1, z0, z1 = -board_w / 2 + f, board_w / 2 - f, f, board_h - f
    nx, nz = max(9, round(13 * board_w / board_h)), 13
    vs = [[b.verts.new((x0 + (x1 - x0) * i / nx, 0.012, z0 + (z1 - z0) * j / nz)) for i in range(nx + 1)] for j in range(nz + 1)]
    face = [b.faces.new((vs[j][i], vs[j + 1][i], vs[j + 1][i + 1], vs[j][i + 1])) for j in range(nz) for i in range(nx)]
    set_uv(b, face, lambda co: ((x1 - co.x) / (x1 - x0), (co.z - z0) / (z1 - z0)))     # read from the front: u runs to -x
    rbox(c, (board_w - 0.01, 0.02, board_h - 0.01), 0.004, 1, at=(0, 0, board_h / 2))  # backing board
    for (sx, sz, w, h) in ((0, f / 2, board_w, f), (0, board_h - f / 2, board_w, f),  # slim gold frame
                           (-board_w / 2 + f / 2, board_h / 2, f, board_h), (board_w / 2 - f / 2, board_h / 2, f, board_h)):
        cuts(g, rbox(g, (w, 0.03, h), 0.008, 2, at=(sx, 0.008, sz)), 0 if w > h else 2, -2, 2, 0.15)
    corner_posies(parts, rng, board_w, board_h, posy or board_h / 1.36)


def title_wall(parts, rng, width=4.2, height=2.4, bottom=0.8, board="welcome_board", frame=0.06, posy=2.1):
    """A board in a slim gold frame hung flat on the wall, roses on two corners; the web writes on its face (`board`):
    the foyer's big title wall, straight ahead as she comes in (welcome_board: "The Museum of Us", their names, the date,
    his note), and, smaller, a chapter's title straight ahead as you come into its room (chapter_story,
    chapter_reasons). The wall is local y = 0, the room +y. Returns the board's centre (for its spotlight)."""
    done = {name: track(parts[name]) for name in (board, "trim_cream", "gold_metal", "rose_petal", "rose_blush", "rose_leaf")}
    framed_board(parts, rng, board, width, height, f=frame, posy=posy)
    m = Matrix.Translation((0, 0.012, bottom))
    for name, fn in done.items():
        bmesh.ops.transform(parts[name], matrix=m, verts=fn())
    return Vector((0, 0.03, bottom + height / 2))


def easel_sign(parts, rng, board="quote_board", board_w=1.0, board_h=1.36, lean=12, ledge_z=0.78):
    """Gold display easel holding a board in a slim gold frame (`board` = its material, with UVs: the web writes on it:
    quote_board), a posy of roses on two corners; the easel grows with the board. Returns the board's centre (for its
    spotlight)."""
    g = parts["gold_metal"]
    ledge_y, k = 0.04, board_h / 1.36
    cos, sin = math.cos(math.radians(lean)), math.sin(math.radians(lean))
    to_easel = Matrix.Translation((0, ledge_y, ledge_z)) @ Matrix.Rotation(math.radians(lean), 4, "X")   # board frame -> easel
    done = {name: track(parts[name]) for name in (board, "trim_cream", "gold_metal", "rose_petal", "rose_blush", "rose_leaf")}
    framed_board(parts, rng, board, board_w, board_h)
    for name, fn in done.items():
        bmesh.ops.transform(parts[name], matrix=to_easel, verts=fn())

    def leg(x, z):                                                                       # a point on a front leg, just behind the board
        zb = (z - ledge_z + 0.025 * sin) / cos
        return Vector((x, ledge_y - 0.025 * cos - zb * sin, z))
    peak, spread, back = ledge_z + 0.87 * board_h * cos, 0.4 * board_w, 0.64 * k
    for s in (-1, 1):                                                                    # two splayed front legs with little feet
        tube(g, [leg(s * (spread - 0.35 * board_w * t), peak * t) for t in (0, 0.25, 0.5, 0.75, 1)], 0.011 * k, 12)
        lathe(g, [(0, 0), (0.016, 0), (0.016, 0.012), (0, 0.016)], 12, at=leg(s * spread, 0))
    top = leg(0, peak)
    rbox(g, (0.12, 0.04, 0.05), 0.012, 2, at=top + Vector((0, -0.01, 0)))                # hinge cap
    foot = Vector((0, -back, 0.008))
    tube(g, [(top + Vector((0, -0.03, -0.01))).lerp(foot, i / 6) for i in range(7)], 0.01 * k, 12)   # back leg
    lathe(g, [(0, 0), (0.015, 0), (0.015, 0.012), (0, 0.016)], 12, at=(0, -back, 0))
    rbox(g, (0.66 * board_w, 0.09, 0.024), 0.008, 2, at=(0, ledge_y + 0.002, ledge_z - 0.012))   # the ledge the board stands on
    rbox(g, (0.66 * board_w, 0.012, 0.03), 0.004, 2, at=(0, ledge_y + 0.046, ledge_z + 0.004))   # its front lip
    return to_easel @ Vector((0, 0.012, board_h / 2))


def corner_posies(parts, rng, w, h, k=1.0):
    """A swag of roses and leaves hugging a board's top-left and bottom-right corners as you face it (board frame: x
    across, y out of the board, z up): big blooms in the corner, smaller ones along both edges (`k`: their size)."""
    for (cx, cz, sx, sz, reach) in ((w / 2, h, -1, -1, 0.46 * k), (-w / 2, 0, 1, 1, 0.34 * k)):
        corner = Vector((cx + sx * 0.05, 0, cz + sz * 0.05))
        arms = ((Vector((sx, 0, 0)), Vector((0, 0, sz))), (Vector((0, 0, sz)), Vector((sx, 0, 0))))   # (along, inwards)
        blooms = [(corner, 1.35 * k, Vector((0, 0, 0)))]
        for along_edge, inwards in arms:
            n = round(reach / 0.07)
            for i in range(1, n + 1):
                t = i / n
                blooms.append((corner + along_edge * (reach * t) + inwards * rng.uniform(-0.01, 0.035) * (1 - t), (1.3 - 0.6 * t) * k, along_edge * t))
            for t in (0.35, 0.7, 1.08):                                                  # leaves peeking out over the frame
                d = (along_edge * (0.6 + 0.6 * (t > 1)) - inwards * 0.8 + Vector((0, 0.15, 0))).normalized()
                length = rng.uniform(0.08, 0.11)
                leaf(parts["rose_leaf"], corner + along_edge * (reach * min(t, 1.0)) + Vector((0, 0.024, 0)), d, length, length * 0.42, 0.008)
        for i in range(3):                                                               # an inner row filling the corner
            a = (i + 1) / 4 * math.pi / 2
            blooms.append((corner + Vector((sx * math.cos(a), 0, sz * math.sin(a))) * 0.13 * k, 1.05 * k, Vector((0, 0, 0))))
        for p, k, tilt in blooms:
            axis = (Vector((0, 1, 0)) + tilt * 0.3 + Vector((rng.uniform(-0.1, 0.1), 0, rng.uniform(-0.1, 0.1)))).normalized()
            bloom(parts["rose_blush" if rng.random() < 0.3 else "rose_petal"], p + Vector((0, 0.03 + rng.uniform(0, 0.012), 0)), axis,
                  k * rng.uniform(0.92, 1.05), rng.uniform(0, TAU), 10)


def rug(parts, rng, design="heart", step=0.1, thickness=0.012):
    """A rug lying on the floor: decor_atlas design `design` at its real size, a thin edge all round."""
    bm = parts["decor_atlas"]
    W, D = RUGS[design]["size"]
    rect = uv_rect(RUGS[design]["rect"], 2)
    uv = lambda co: in_rect(rect, co.x / W + 0.5, co.y / D + 0.5)
    grid(bm, -W / 2, W / 2, -D / 2, D / 2, thickness, step, uv)
    corners = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    edge = []
    for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
        edge.append(bm.faces.new([bm.verts.new(p) for p in ((ax, ay, 0), (bx, by, 0), (bx, by, thickness), (ax, ay, thickness))]))
    set_uv(bm, edge, lambda co: uv(co * 0.995))                                           # the edge shows the binding


def monogram_rug(parts, rng, radius=1.3, thickness=0.012):
    """A round ivory rug in the foyer's open middle: the web weaves the couple's initials into it (monogram_rug: UVs
    across the disc, read from the entrance). A thin edge all round; you walk over it."""
    bm = parts["monogram_rug"]
    uv = lambda co: (0.5 + co.x / (2 * radius), 0.5 + co.y / (2 * radius))
    _, ring = polar_grid(bm, radius, thickness, 0.1, 72, uv)
    low = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in ring]
    n = len(ring)
    edge = [bm.faces.new((low[k], low[(k + 1) % n], ring[(k + 1) % n], ring[k])) for k in range(n)]
    set_uv(bm, edge, lambda co: uv(co * 0.995))                                           # the edge shows the binding


def dance_floor(parts, rng, radius=1.25, thickness=0.015, ceiling=4.32):
    """A round dance floor in the heart room: white marble with a gold rim, a fine gold ring and a little gold heart in
    its middle (its tip towards local +y), in a soft pool of light from the ceiling (a spot, baked). Marked for the web
    (dance_floor: its middle and "radius"): the web's disco ball hangs over it. You walk over it."""
    bm, g = parts["decor_atlas"], parts["gold_metal"]
    rect = uv_rect(MARBLE_RECT, 2)
    polar_grid(bm, radius, thickness, 0.12, 72, lambda co: in_rect(rect, 0.5 + co.x / (2.1 * radius), 0.5 + co.y / (2.1 * radius)))
    lathe(g, [(radius + 0.014, 0.0), (radius + 0.014, thickness - 0.004), (radius + 0.01, thickness + 0.001),
              (radius - 0.004, thickness + 0.001)], 96)                                   # the gold rim
    lathe(g, [(0.84 * radius + 0.012, thickness + 0.0008), (0.84 * radius, thickness + 0.0008)], 96)   # a fine ring
    t = thickness + 0.001
    centre = g.verts.new((0, 0, t))
    edge = [g.verts.new((0.19 * x, -0.19 * y, t)) for x, y in (heart_point(TAU * k / 48) for k in range(48))]
    for k in range(48):
        f = g.faces.new((centre, edge[k], edge[(k + 1) % 48]))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    parts.lights.append(dict(kind="SPOT", pos=Vector((0, 0, ceiling - 0.08)), normal=Vector((0, 0, -1)),
                             cone=2 * math.atan((radius + 0.35) / (ceiling - 0.08)), colour=(1.0, 0.86, 0.68), watts=1200.0))
    parts.markers["dance_floor"] = (Vector((0, 0, thickness)), {"radius": radius})


# ---------------------------------------------------------------- tables

def marble_top(parts, radius, z, thickness=0.025, seg=48):
    """Round white-marble table top (decor_atlas), its surface at z."""
    bm = parts["decor_atlas"]
    rect = uv_rect(MARBLE_RECT, 2)
    uv = lambda co: in_rect(rect, 0.5 + co.x / (2.1 * radius), 0.5 + co.y / (2.1 * radius))
    _, ring = polar_grid(bm, radius, z, 0.1, seg, uv)
    _, low = polar_grid(bm, radius, z - thickness, 0.5, seg, uv, down=True)
    faces = [bm.faces.new((low[k], low[(k + 1) % seg], ring[(k + 1) % seg], ring[k])) for k in range(seg)]
    set_uv(bm, faces, lambda co: in_rect(rect, 0.05 + 0.9 * abs(math.atan2(co.y, co.x)) / math.pi, 0.5 + (co.z - z) * 4))


def side_table(parts, rng, radius=0.23, height=0.56, treat=None):
    """Small round marble side table on a slim gold stem, a little vase of roses and a candle on it (by the cinema's
    loveseat, `treat` instead of the roses: "popcorn" or "drinks")."""
    g = parts["gold_metal"]
    stem = [(0.016, 0.04 + (height - 0.1) * k / 5) for k in range(6)]
    lathe(g, [(0, 0), (0.16, 0), (0.165, 0.004), (0.165, 0.01), (0.15, 0.014), (0.03, 0.02)] + stem +
          [(0.03, height - 0.04), (0.08, height - 0.028), (0.08, height - 0.024), (0, height - 0.024)], 32)
    marble_top(parts, radius, height, 0.024)
    if treat == "popcorn":
        popcorn_box(parts, rng, (-0.05, 0.05, height))
    elif treat == "drinks":
        for x, y in ((-0.1, 0.03), (-0.01, 0.11)):
            drink_cup(parts, rng, (x, y, height))
    else:
        vase_of_roses(parts, rng, (-0.05, 0.04, height), 5, 0.17)
    candle_cluster(parts, rng, (0.1, -0.07, height), 1, 0.6)


def coffee_table(parts, rng, radius=0.45, height=0.42):
    """Round marble coffee table on a gold cage base (two rings and slim rods), candles and roses on it."""
    g = parts["gold_metal"]
    ring = lambda z: [Vector(((radius - 0.07) * math.cos(TAU * k / 48), (radius - 0.07) * math.sin(TAU * k / 48), z)) for k in range(48)]
    tube(g, ring(0.012), 0.011, 10, closed=True, plane_normal=UP)
    tube(g, ring(height - 0.039), 0.009, 10, closed=True, plane_normal=UP)
    for k in range(12):
        a = TAU * k / 12
        x, y = (radius - 0.07) * math.cos(a), (radius - 0.07) * math.sin(a)
        tube(g, [Vector((x, y, 0.012 + (height - 0.051) * k / 5)) for k in range(6)], 0.006, 8)
    marble_top(parts, radius, height, 0.03, 64)
    candle_tray(parts, rng, (-0.16, 0.08, height))
    vase_of_roses(parts, rng, (0.17, -0.06, height), 9, 0.2)


def console(parts, rng, width=1.2, depth=0.38, height=0.8):
    """Marble-topped console on a slim gold frame, roses and candles on it (stands against a wall, back at -y)."""
    g = parts["gold_metal"]
    rect = uv_rect(MARBLE_RECT, 2)
    long = in_rect(rect, 0.05, 0.3) + in_rect(rect, 0.95, 0.6)                          # a wide strip of the marble
    top = uv_box(parts["decor_atlas"], (width, depth, 0.03), (0, 0, height - 0.015),
                 {"+z": long, "-z": long, "+x": rect, "-x": rect, "+y": long, "-y": long})
    cuts(parts["decor_atlas"], top, 0, -width / 2, width / 2, 0.15)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts(g, rbox(g, (0.022, 0.022, height - 0.03), 0.004, 1, at=(sx * (width / 2 - 0.04), sy * (depth / 2 - 0.04), (height - 0.03) / 2)),
                 2, 0, height - 0.03, 0.12)
        rbox(g, (0.018, depth - 0.08, 0.018), 0.004, 1, at=(sx * (width / 2 - 0.04), 0, 0.12))
    for sy in (-1, 1):
        rbox(g, (width - 0.08, 0.018, 0.018), 0.004, 1, at=(0, sy * (depth / 2 - 0.04), 0.12))
        rbox(g, (width - 0.08, 0.018, 0.04), 0.004, 1, at=(0, sy * (depth / 2 - 0.04), height - 0.05))
    vase_of_roses(parts, rng, (-0.27 * width, 0.0, height), 11, 0.26)
    candle_tray(parts, rng, (0.24 * width, 0.0, height))




# ---------------------------------------------------------------- the museum's pieces

HEART_AT = (17.0, 18.6)                                   # the rose-petal heart in front of the collage (web: rosePetals.ts)
HEART_WIDTH = 1.9


def heart_ring(at, width, gap=1.0, count=16):
    """Spots for little groups of candles all round the rose-petal heart, open at its tip (towards the sofa) so you
    can step in."""
    out = []
    for i in range(count):
        t = TAU * i / count
        if abs(t - math.pi) < gap / 2:
            continue
        x, y = heart_point(t)
        o = Vector((x, y + 0.15)).normalized()
        out.append((at[0] + x * width / 2 + o.x * 0.2, at[1] + y * width / 2 + o.y * 0.2))
    return out


# (name, piece, yaw, (x, y), options). Placed off the photos, doors and walking routes; exhibits name the rail point and
# the wall (normal into the room) their spotlight hangs from: "spot": ((x, y), (nx, ny), pool radius).
LAYOUT = [
    # foyer, the invitation: the big title wall facing you as you come in, in its own spotlight between two rose
    # topiaries, heart balloons on gold weights either side of it; ivory sheers with little lights behind them along
    # both side walls; the door where the story begins framed by velvet curtains hanging straight either side under a
    # pelmet (it is in the corner: the right one's hook is on the side wall), its way kept clear; green trees in the
    # corners, urns of roses in front of the sheers
    ("welcome", title_wall, 180, (4.45, 9.875), {"spot": ((4.45, 8.745), (0, -1), 2.4)}),
    ("topiary_foyer_w", rose_topiary, 0, (1.95, 9.35), {}),
    ("topiary_foyer_e", rose_topiary, 0, (6.95, 9.35), {}),
    ("balloons_foyer_w", balloon_bunch, 0, (1.9, 8.55), {"count": 5, "weight": True}),
    ("balloons_foyer_e", balloon_bunch, 0, (7.0, 8.55), {"count": 5, "weight": True}),
    ("rug_foyer", monogram_rug, 0, (4.45, 5.6), {}),
    ("sheers_foyer_w", sheer_drape, -90, (0.2, 9.6), {"length": 9.3}),
    ("sheers_foyer_e", sheer_drape, 90, (10.875, 1.85), {"length": 7.75}),
    ("curtain_foyer_w", curtain_panel, 180, (9.16, 9.875), {"side": 1, "opening": 2.74, "beyond": 0.34, "rod": 3.88, "top_inner": 1.08}),
    ("curtain_foyer_e", curtain_panel, 180, (9.16, 9.875), {"side": -1, "opening": 2.74, "beyond": 0.34, "rod": 3.88, "top_inner": 1.08,
                                                           "hook": "side"}),
    ("pelmet_foyer", pelmet, 180, (9.135, 9.875), {"width": 3.47, "height": 0.45, "top": 4.31}),
    ("ficus_foyer_sw", weeping_fig, 75, (1.35, 1.15), {}),
    ("urn_foyer_w", flower_urn, 0, (0.72, 3.0), {}),
    ("urn_foyer_e", flower_urn, 0, (10.35, 3.0), {}),
    ("olive_foyer", olive_tree, 20, (0.95, 9.1), {}),
    ("fig_foyer", fig_tree, 0, (10.1, 0.95), {}),
    ("curtain_entrance_w", curtain_panel, 0, (5.5, 0.2), {"side": -1, "opening": 2.74, "beyond": 0.34, "rod": 3.88, "top_inner": 1.08}),
    ("curtain_entrance_e", curtain_panel, 0, (5.5, 0.2), {"side": 1, "opening": 2.74, "beyond": 0.34, "rod": 3.88, "top_inner": 1.08}),
    ("pelmet_entrance", pelmet, 0, (5.5, 0.2), {"width": 3.47, "height": 0.45, "top": 3.99}),   # under the roof line
    # outside, the way in, like a wedding: the ivory doorway with its red doors opened right back to the wall and a
    # garland of roses round it, rose topiaries and balloons either side, a wide red carpet for the two of them from
    # the far end of the clearing into the foyer, lined with gold flower stands (the wood round the clearing and the little lights over it: garden.py; its ground: entrance.py)
    ("portal", portal, 180, (5.5, -0.2), {}),
    ("garland_entrance", niche_garland, 180, (5.5, -0.28), {"half_width": 1.55, "z_top": 3.48, "z_low": 1.4}),   # on the architrave
    ("jamb_w", jamb, 180, (5.5, -0.2), {"side": 1}),
    ("jamb_e", jamb, 180, (5.5, -0.2), {"side": -1}),
    ("door_w", door_leaf, 180, (5.5, -0.2), {"side": 1}),
    ("door_e", door_leaf, 180, (5.5, -0.2), {"side": -1}),
    ("runner_entrance", runner, 0, (5.5, -13.8), {"length": 15.6, "width": 1.8}),
    ("topiary_entrance_w", rose_topiary, 0, (2.95, -0.75), {}),
    ("topiary_entrance_e", rose_topiary, 0, (8.05, -0.75), {}),
    ("balloons_entrance_w", balloon_bunch, 0, (1.9, -1.0), {"count": 5, "weight": True}),
    ("balloons_entrance_e", balloon_bunch, 0, (9.1, -1.0), {"count": 5, "weight": True}),
] + [(f"stand_entrance_{i}", floral_stand, 0, (x, y), {"height": 1.2}) for i, (x, y) in
     enumerate((x, y) for y in (-13.0, -10.4, -7.8, -5.4) for x in (3.85, 7.15))] + [
    # story gallery (how it began): its chapter board straight ahead as you come in, between balloons and a flower
    # stand; roses by the doorway and in a corner, consoles, a weeping fig in the far corner
    ("topiary_story_e", rose_topiary, 0, (10.45, 14.5), {}),
    ("topiary_story_sw", rose_topiary, 0, (0.75, 10.75), {}),
    ("console_story_1", console, -90, (0.39, 13.85), {"width": 0.9, "depth": 0.32}),
    ("console_story_2", console, -90, (0.39, 17.15), {"width": 0.9, "depth": 0.32}),
    ("ficus_story_nw", weeping_fig, 140, (1.0, 20.0), {}),
    ("stand_story_ne", floral_stand, 0, (10.25, 20.2), {}),
    ("chapter_story", title_wall, 180, (8.7, 20.8), {"board": "chapter_story", "width": 2.6, "height": 1.55, "bottom": 1.0,
                                                    "frame": 0.05, "posy": 1.45, "spot": ((8.7, 19.67), (0, -1), 1.55)}),
    ("balloons_story", balloon_bunch, 0, (6.8, 20.2), {"count": 5, "weight": True}),
    # heart room (us, now): the sofa facing the collage with balloons either side, the quote board and the roses either
    # side of it, the rose-petal heart ringed by candles in front of it, a garland round it; in its south half the dance
    # floor in a pool of light under the web's disco ball, balloons beside it; rose topiaries along the south wall, kentia
    # palms either side of the room, golden light strings along the walls, a gold dimmer on the wall by the door
    ("sofa_heart", sofa, 0, (17.0, 14.3), {"width": 2.3}),
    ("rug_heart", rug, 0, (17.0, 15.55), {"design": "heart"}),
    ("coffee_table_heart", coffee_table, 0, (17.0, 15.75), {}),
    ("side_table_heart_w", side_table, 0, (15.5, 14.35), {}),
    ("side_table_heart_e", side_table, 0, (18.5, 14.35), {}),
    ("balloons_sofa", balloon_bunch, 0, (18.5, 14.35), {"count": 5, "anchor": (0.14, 0.1, 0.56)}),
    ("balloons_sofa_w", balloon_bunch, 0, (15.5, 14.35), {"count": 5, "anchor": (-0.14, 0.1, 0.56)}),
    ("quote_board", easel_sign, 200, (13.35, 18.65), {"board_w": 1.2, "board_h": 1.63, "spot": ((12.255, 17.3), (1, 0), 0.9)}),
    ("roses", rose_display, 0, (20.6, 18.55), {"spot": ((21.745, 17.3), (-1, 0), 0.5)}),
    ("ropes_roses", velvet_ropes, 0, (20.6, 18.55), {"posts": [(-0.8, -0.3), (0.0, -0.85), (0.8, -0.3)]}),
    ("garland", niche_garland, 180, (17.0, 20.63), {}),
    ("fig_heart_w", fig_tree, 0, (11.75, 14.3), {}),
    ("fig_heart_e", fig_tree, 0, (22.25, 14.3), {}),
    ("palm_heart_w", kentia_palm, 200, (12.05, 9.3), {}),
    ("palm_heart_e", kentia_palm, 20, (21.95, 9.3), {}),
    ("lights_heart_ws", light_string, -90, (11.15, 10.0), {"length": 8.0}),
    ("lights_heart_wn", light_string, -90, (11.15, 20.4), {"length": 6.0}),
    ("lights_heart_es", light_string, 90, (22.84, 2.0), {"length": 8.0}),
    ("lights_heart_en", light_string, 90, (22.84, 14.4), {"length": 6.0}),
    ("lights_heart_s", light_string, 0, (11.6, 1.73), {"length": 10.8}),
    ("dimmer_heart", dimmer_switch, -90, (11.125, 13.7), {}),
    ("dance_floor", dance_floor, 0, (17.0, 6.2), {}),
    ("balloons_dance", balloon_bunch, 0, (14.95, 6.2), {"count": 5, "weight": True}),
    ("topiary_heart_sw", rose_topiary, 0, (15.4, 2.25), {}),
    ("topiary_heart_se", rose_topiary, 0, (18.6, 2.25), {}),
    ("olive_heart_sw", olive_tree, 30, (11.9, 2.4), {}),
    ("olive_heart_se", olive_tree, -40, (22.1, 2.4), {}),
    # corridor: the console under the neon sign, between two lanterns
    ("console_corridor", console, 0, (24.75, 1.92), {}),
    ("neon", neon_sign, 0, (24.75, 1.73), {}),
    ("lantern_corridor_w", lantern, 0, (23.9, 2.0), {}),
    ("lantern_corridor_e", lantern, 0, (25.6, 2.0), {}),
    # right gallery (reasons I love you): its chapter board straight ahead as you come in, balloons beside it, the love
    # notes hanging over its open middle, a kentia palm between stands, flower stands and trees in the corners
    ("chapter_reasons", title_wall, 180, (26.5, 20.8), {"board": "chapter_reasons", "width": 2.6, "height": 1.55, "bottom": 1.0,
                                                       "frame": 0.05, "posy": 1.45, "spot": ((26.5, 19.67), (0, -1), 1.55)}),
    ("balloons_reasons", balloon_bunch, 0, (28.3, 20.25), {"count": 5, "weight": True}),
    ("love_notes", love_notes, 0, (30.4, 17.0), {}),
    ("palm_right", kentia_palm, 20, (24.15, 17.2), {}),
    ("stand_right_1", floral_stand, 0, (23.55, 15.9), {}),
    ("stand_right_2", floral_stand, 0, (23.55, 18.5), {}),
    ("olive_right_nw", olive_tree, 0, (23.95, 20.05), {}),
    ("olive_right_ne", olive_tree, 0, (36.95, 20.0), {}),
    ("fig_right_se", fig_tree, 0, (37.05, 13.95), {}),
    ("stand_right_e1", floral_stand, 0, (37.2, 15.55), {}),
    ("stand_right_e2", floral_stand, 0, (37.2, 18.45), {}),
    # screen room: the loveseat on the seat markers facing the screen with popcorn and drinks beside it, the projector
    # behind it, the screen in its frame on a little stage between velvet curtains, the "Now Showing" poster by the way
    # in, curtains on the garden door, rose topiaries either side of the stage, each washed by a little floor light
    ("loveseat_screen", sofa, 0, (32.25, 7.11), {}),
    ("rug_screen", rug, 0, (32.25, 8.0), {"design": "screen"}),
    ("side_table_screen_w", side_table, 0, (31.12, 7.15), {"treat": "popcorn"}),
    ("side_table_screen_e", side_table, 0, (33.38, 7.15), {"treat": "drinks"}),
    ("poster", poster, 0, (28.2, 1.7), {}),
    ("balloons_loveseat", balloon_bunch, 0, (33.0, 7.11), {"count": 3, "anchor": (0, 0, 0.65)}),
    ("projector", projector, 0, (32.25, 5.0), {"drop": 0.72, "scale": 1.5, "aim": (0.0, 7.45, -1.45)}),
    ("curtain_s", curtain_panel, 90, (37.77, 6.475), {"side": -1}),
    ("curtain_n", curtain_panel, 90, (37.77, 6.475), {"side": 1}),
    ("pelmet", pelmet, 90, (37.77, 6.475), {}),
    ("screen", cinema_screen, 180, (32.25, 12.875), {}),
    ("curtain_screen_w", curtain_panel, 180, (32.25, 12.875), {"side": 1, "opening": 6.0, "rod": 3.84, "top_inner": 2.62}),
    ("curtain_screen_e", curtain_panel, 180, (32.25, 12.875), {"side": -1, "opening": 6.0, "rod": 3.84, "top_inner": 2.62}),
    ("pelmet_screen", pelmet, 180, (32.25, 12.875), {"width": 7.1, "height": 0.48, "top": 4.3}),
    ("olive_screen_s", olive_tree, 0, (37.15, 2.15), {}),
    ("olive_screen_n", olive_tree, 0, (37.15, 12.35), {}),
    ("topiary_screen_w", rose_topiary, 0, (28.3, 12.3), {"uplight": True}),
    ("topiary_screen_e", rose_topiary, 0, (36.2, 12.3), {"uplight": True}),
] + [(f"candles_heart_{i}", candle_cluster, 0, at, {"count": (2, 1, 3, 2)[i % 4], "size": 0.9, "light": i % 2 == 0})
       for i, at in enumerate(heart_ring(HEART_AT, HEART_WIDTH))]

WALKABLE = {rug, monogram_rug, dance_floor, runner}             # pieces you walk over


def zone(x, y):
    """The part of the museum a piece stands in: its meshes merge per zone, so the parts out of sight are culled."""
    if x > 38:
        return "garden"
    if y < 0:
        return "entrance"
    if x < 11:
        return "foyer" if y < 10 else "story"
    if x < 23:
        return "heart" if y > 11 else "heartsouth"
    return "right" if y > 13 else "screen"                # the corridor goes with the screen room


def footprint(points):
    """Where a piece stands, from its points below head height (local x, y): the middle, the half size and, for a round
    piece (planters, plinths, round tables), the radius of the circle it fills."""
    lo = Vector((min(p.x for p in points), min(p.y for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points)))
    middle, half = (lo + hi) / 2, (hi - lo) / 2
    reach = max((Vector((p.x, p.y)) - middle).length for p in points)
    round_ = abs(half.x - half.y) < 0.15 * max(half.x, half.y) and reach < 1.12 * max(half.x, half.y)
    return middle, half, (reach if round_ else None)


def build(name, piece, yaw, at, opts):
    """One piece of LAYOUT, placed: its parts per material, its footprint (world middle, half size, radius or None; None
    for what does not stand on the floor: wall pieces, balloons) and its spot target."""
    parts = Parts()
    target = piece(parts, random.Random(name), **opts)
    local = [v.co.copy() for bm in parts.values() for v in bm.verts]
    m = Matrix.Translation((at[0], at[1], 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    for bm in parts.values():
        bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
        pivot = bm.loops.layers.uv.get("pivot")
        if pivot:                                         # balloon middles to world (x, 1 + y: the glTF export flips v)
            for f in bm.faces:
                for loop in f.loops:
                    w = m @ Vector((loop[pivot].uv.x, loop[pivot].uv.y, 0))
                    loop[pivot].uv = (w.x, 1 + w.y)
    parts.flames = [m @ p for p in parts.flames]
    parts.fairies = [m @ p for p in parts.fairies]
    parts.notes = [(m @ p, top) for p, top in parts.notes]
    for light in parts.lights:
        light["pos"] = m @ light["pos"]
        if "normal" in light:
            light["normal"] = m.to_3x3() @ light["normal"]
    parts.markers = {k: (m @ pos, {e: ([round(c, 4) for c in m.to_3x3() @ Vector(v)] if e == "aim" else v) for e, v in extras.items()})
                     for k, (pos, extras) in parts.markers.items()}
    stands = [p for p in local if p.z < 1.9] if any(p.z < 0.05 for p in local) else []
    place_ = None
    if stands:
        middle, half, radius = footprint(stands)
        place_ = (m @ Vector((middle.x, middle.y, 0)), half, radius)
    return parts, place_, (m @ target if target is not None else None)


def add(collection, material, atlas_path):
    """Builds LAYOUT into `collection`: one mesh per material in each zone (prop_<zone>_<material>, custom property
    "prop" = the material; material(name, rgb) makes the materials), an empty per piece standing on the floor marking
    its footprint (footprint_<name>: "footprint" = half width, half depth, turned by the empty's rotation, and "radius"
    for a round one; "walkable" for rugs), one empty listing every candle flame (candle_flames: "flames" = x, y, z, ...;
    the web lights them), one listing the little lights behind the sheers (fairy_lights: "fairies" = x, y, z, ...), one
    listing where the love notes hang (love_notes: "notes" = x, y, z of a card's middle, its ribbon's top height, ...) and
    the pieces' named markers (projector_lens, dimmer_switch: "aim"; dance_floor: "radius").
    Returns (exhibit spotlights: (name, rail point, target, wall normal, radius), accent lights: Parts.lights dicts)."""
    import bpy
    mats = {name: material(name, rgb) for name, rgb in PALETTE.items()}
    mats["trim_cream"] = bpy.data.materials["trim_cream"]
    image = bpy.data.images.load(atlas_path)
    image.pack()
    for name in ("decor_atlas", "balloon_foil"):
        nt = mats[name].node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    merged, flames, fairies, notes, spots, lights = {}, [], [], [], [], []

    def empty(name, at, rotation=0.0, **props):
        ob = bpy.data.objects.new(name, None)
        ob.location = at; ob.rotation_euler = (0, 0, rotation)
        for k, v in props.items():
            ob[k] = v
        collection.objects.link(ob)

    for name, piece, yaw, at, opts in LAYOUT:
        opts = dict(opts)
        spot = opts.pop("spot", None)
        parts, place_, target = build(name, piece, yaw, at, opts)
        z = zone(*at)
        for mat_name, bm in parts.items():
            if not bm.verts:
                bm.free(); continue
            for f in bm.faces:
                f.smooth = True
            for e in bm.edges:
                if e.is_manifold and e.calc_face_angle(0) > math.radians(50):
                    e.smooth = False
            me = bpy.data.meshes.new("_piece"); bm.to_mesh(me); bm.free()
            if (z, mat_name) not in merged:
                merged[z, mat_name] = bmesh.new()
            merged[z, mat_name].from_mesh(me)
            bpy.data.meshes.remove(me)
        flames += parts.flames
        fairies += parts.fairies
        notes += parts.notes
        lights += parts.lights
        for marker, (pos, extras) in parts.markers.items():
            empty(marker, pos, **extras)
        if place_:
            middle, half, radius = place_
            props = {"footprint": [round(half.x, 3), round(half.y, 3)]}
            if radius:
                props["radius"] = round(radius, 3)
            if piece in WALKABLE:
                props["walkable"] = True
            empty(f"footprint_{name}", (middle.x, middle.y, 0), math.radians(yaw), **props)
        if spot:
            rail, wall, radius = spot
            spots.append((name, Vector(rail), target, Vector((*wall, 0)), radius))
    empty("candle_flames", (0, 0, 0), flames=[round(c, 4) for p in flames for c in p])
    empty("fairy_lights", (0, 0, 0), fairies=[round(c, 3) for p in fairies for c in p])
    empty("love_notes", (0, 0, 0), notes=[round(c, 3) for p, top in notes for c in (*p, top)])
    for (z, mat_name), bm in merged.items():
        me = bpy.data.meshes.new(f"prop_{z}_{mat_name}"); bm.to_mesh(me); bm.free(); me.materials.append(mats[mat_name])
        ob = bpy.data.objects.new(me.name, me); collection.objects.link(ob)
        ob["prop"] = mat_name
        if mat_name in UNBAKED:
            ob.hide_render = True                        # drawn by the web only, never in the bake
        else:
            ob["bake_vertex"] = True
        if mat_name in NO_REFLECTION:
            ob["noReflection"] = True                    # left out of the web's floor reflection (floorReflection.ts)
    return spots, lights
