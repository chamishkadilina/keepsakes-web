"""Where everything in the night garden stands (garden.py places it). Blender metres: x east, y north, z up.
The garden: x 38-52, y 0-16; its door in the west wall, y 5-8 (kept clear from y 4.4 to 8.6).
The bench stands by the door, its back to the house, looking across the lawn: the fire in front of it, the lit
jacaranda ahead on the left, the moon ahead on the right (MOON in design.py, LIGHTING.nightSky in the web).
The lawn itself stays open and clean: plants grow in the border, round the tree and in flower beds along the border."""

FOLDER = "textures/garden"                       # next to the input .blend: garden_assets.py's models and textures
SURFACES = {"floor_6_garden": ("grass", "garden_leafy_grass.jpg"), "garden_walls": ("garden_wall", "garden_mossy_stone_wall.jpg")}
TILE = 2.0                                       # m: both textures' real size
DOOR = (38.3, 6.5)
TREE = (46.8, 9.8)
SMALL_TREE = (50.4, 14.2, 140)                   # a younger jacaranda in the far corner (x, y, yaw): a little wood
BENCH, BENCH_YAW = (39.7, 3.5), 115.0            # a teak garden bench for two (garden_wood.py), near the door; faces
                                                 # local -y (north-east): the tree ahead on the left, the moon on the right
BENCH_OPEN = 4.0                                 # m: no tall trees this near the bench, so the sky stays open behind it
SEATS = {"seat_garden_1": (-0.36, -0.05, 0.52), "seat_garden_2": (0.36, -0.05, 0.52)}   # in the bench's frame, on its cushion
FIRE = (0, -3.6)                                 # in the bench's frame: the fire pit out on the lawn before it
FIRE_SINK = 0.12                                 # m: the pit sits this deep in its burnt earth (its outer stones touch the ground)
TEEPEE = dict(logs=("firewood_a", "firewood_b", "firewood_c"), count=5, radius=0.24, lean=(22, 30))   # m, degrees
FALLEN = [("firewood_c", (0.38, -0.12), 10, 80), ("firewood_a", (-0.34, 0.22), 170, 82)]   # logs lying in the embers: (x, y) from the fire, yaw, lean
KINDLING = [("dry_branches_medium_01_b", 20), ("dry_branches_medium_01_c", 110)]   # (variant, yaw): twigs under them
FIRE_LIGHT = dict(colour=(1.0, 0.42, 0.12), watts=70.0, height=1.0, radius=0.3)   # its warm light, baked: above the logs, so the stones glow, not glare
BY_BENCH = [  # (asset variant, (x, y) in the bench's frame, extra yaw, scale): a lantern either side
    ("wooden_lantern_01", (-1.0, -0.15), 15, 1.0),
    ("wooden_lantern_01", (0.95, -0.55), -20, 0.8),
]
PACHIRA = ("pachira_aquatica_01_bark_d", "pachira_aquatica_01_leaves_d")
FEATURES = [  # (asset variant or variants, (x, y), yaw, scale)
    (PACHIRA, (39.1, 9.8), 200, 1.5),                                        # north of the door
    ("wild_rooibos_bush_b", (39.7, 9.1), 90, 1.2),
    ("wooden_lantern_01", (43.4, 8.0), -30, 1.0),                            # on the way from the door to the tree
    ("wooden_lantern_01", (45.7, 8.7), 50, 0.9),                             # at the tree's foot
    ("rock_moss_set_01_rock05", (48.1, 9.0), 25, 0.9),                       # mossy stones and ferns round the tree's foot
    ("rock_moss_set_01_rock02", (45.6, 10.8), 140, 0.8),
    ("fern_02_b", (45.2, 9.7), 0, 1.1), ("fern_02_c", (46.0, 11.3), 70, 1.0), ("fern_02_a", (47.5, 11.3), 20, 1.0),
    ("fern_02_d", (48.4, 10.4), 140, 1.0), ("fern_02_b", (47.7, 8.4), 200, 0.9), ("fern_02_c", (46.5, 8.3), 90, 0.9),
    ("rock_moss_set_01_rock04", (41.4, 13.4), 60, 1.0),                      # stones at the front of the border
    ("rock_moss_set_01_rock06", (49.9, 3.2), 10, 0.9),
]
TALL = [PACHIRA] * 2 + [("pachira_aquatica_01_bark_c", "pachira_aquatica_01_leaves_c")]
FRONT = ["wild_rooibos_bush_a", "wild_rooibos_bush_b", "wild_rooibos_bush_c", "fern_02_b", "shrub_04"]
BORDER = {"tall": 0.9, "front": 1.8, "spacing": (1.5, 0.9)}    # m from the walls, m between plants
TALL_SCALE = (1.6, 2.2)                         # the trees round the edge: about 3.5-5 m, a little wood
WALLS = [((38.15, 0.15), (51.85, 0.15)), ((51.85, 0.15), (51.85, 15.85)), ((51.85, 15.85), (38.15, 15.85)),
         ((38.15, 15.85), (38.15, 8.6)), ((38.15, 4.4), (38.15, 0.15))]   # the walls' inner faces, the door left clear
FLOWERS = ["flower_gazania_" + k for k in "cde"] + ["periwinkle_plant_0" + k for k in "56"]   # the lighter variants
BEDS = dict(distance=2.6, step=1.7, keep=0.65, count=(4, 6), size=(0.6, 0.3))   # flower beds before the border: m from the
                                                # wall, m apart, share planted, flowers in each, half length and depth (m)
STRANDS, STRAND_LIGHTS, STRAND_STEP = 70, (3, 7), 0.2   # strings of little lights hanging from the canopy (m apart)
LIGHTS_LOWEST, TREE_GLOWS = 2.3, 8              # m: no light lower (above her head); warm pools they cast (bake only)
SWAGS = [(38.2, 2.2, 3.5), (38.2, 11.0, 3.5), (38.2, 14.0, 3.5), (44.5, 0.2, 2.4), (51.8, 3.0, 2.4)]   # wall ends
SWAG_STEP, SWAG_SAG = 0.3, 0.6                  # strings of lights draped from the tree to the walls: m apart, sag
SWAYING = ("jacaranda", "pachira", "wild_rooibos", "fern", "shrub", "flower_", "periwinkle")   # what the breeze moves (web wind.ts)

# The clearing outside the entrance, where the couple start (entrance.py builds its ground): x CLEARING x0-x1, y y0 up
# to the museum, and a strip west of the museum up to y north_west. No walls: a little wood round it, tall trees in
# rows outwards from its edges hiding everything beyond, bushes in front and between them; warm little lights strung
# over the clearing in two zigzags from the museum's front to the trees, and swagged across the front over the door.
# Placed by garden.py (Garden.entrance).
UNDERGROWTH = ["wild_rooibos_bush_b", "wild_rooibos_bush_c", "wild_rooibos_bush_d"]
ENTRANCE = dict(
    clearing=dict(x0=-4.0, x1=16.0, y0=-14.0, north_west=3.5),
    edges=[((-0.2, 3.5), (-4.0, 3.5)), ((-4.0, 3.5), (-4.0, -14.0)), ((-4.0, -14.0), (16.0, -14.0)),
           ((16.0, -14.0), (16.0, 1.0))],       # outwards: their right
    rows=[  # (m outwards from the edge, m apart, scale range, choices); negative: inside the clearing, walked round
        (-0.8, 1.0, (1.1, 1.45), UNDERGROWTH),
        (0.2, 1.5, (2.4, 3.1), TALL),
        (1.1, 1.0, (1.8, 2.5), UNDERGROWTH),     # between the trunks, up to eye level
        (2.0, 1.7, (2.9, 3.6), TALL),
        (3.8, 1.9, (3.6, 4.4), TALL),            # taller outwards: their crowns close over the long view
        (5.8, 2.2, (4.4, 5.4), TALL),            # up to about 12 m
    ],
    path=(3.0, 8.0),                             # x: no bushes across the path's end
    museum=[(-0.2, 11.2, -0.2, 21.2), (11.2, 38.2, 1.3, 21.2)],   # its outer walls (x0, x1, y0, y1): nothing grows into them
    margin=(2.8, 0.7),                           # m kept from them: trees (their crowns), bushes
    room=(0.2, 0.35),                            # each one's room on the ground, as a share of its width: trees, bushes
    strings=[[(-1.0, -0.4, 3.8), (15.0, -4.6, 3.6), (-3.0, -9.0, 3.6), (15.0, -13.3, 3.4)],
             [(12.0, -0.4, 3.8), (-3.0, -4.6, 3.6), (15.0, -9.0, 3.6), (-3.0, -13.3, 3.4)],
             [(0.6, -0.28, 3.85), (5.5, -0.42, 4.05), (10.4, -0.28, 3.85)]],   # swagged across the front, over the door
    sag=0.55, step=0.3,                          # m: the strings' sag, the lights' spacing
    glow=(1.0, 0.62, 0.3), watts=14.0,           # their warm light on the clearing (bake only): one per string's span,
    glow_clear=0.8,                              # m: no nearer the museum's front than this (no hot spots on the doors)
)
