# Blender guide — polishing museum.blend

`museum.blend` is the one source of the museum. You polish it by hand; the web loads what you export.

## Golden rules (break these and the web breaks)

1. **Never move or resize the walls, doors or rooms.** The layout is approved.
2. **Keep the names in BUILD_SPEC §4 exactly** (`slot_frame_01`, `spawn_her`, `door_01`, …).
3. **Metres, real sizes.** Type exact numbers in the N panel. Snap increment 0.05 m.
4. **Apply scale before export:** Ctrl+A → Scale. Apply All Transforms only to non-slot objects: `slot_*`, `collage_board` and `screen_surface` must keep their rotation (the web reads each slot's facing from it).
5. **Materials: Principled BSDF only** (Base Color, Roughness, Metallic, Normal Map, Emission, Alpha). Other nodes don't export to the web.
6. **Textures outside the .blend:** put them in `assets-src/blender/textures/`, then File → External Data → Make Paths Relative. Don't pack them. Max 1K, 2K only for the floor or the hero wall.
7. **Budget:** ≤ 200k triangles in total (Overlays → Statistics), ≤ 25 materials. Fewer = faster on phones.
8. Every downloaded asset gets a line in `ASSETS.md` (file, URL, author, license). CC0 only.

## Collections (already created)

| Collection | Put in it |
|---|---|
| `structure` | walls, garden walls, ceilings, trims, glass |
| `floors` | floors |
| `frames_slots` | `slot_*`, `collage_board`, `screen_surface`, `welcome_wall_text` |
| `decor` | rose arch, benches, easel, plants, garden |
| `lights` | lights (`rt_light_*` = stays live on the web) |
| `colliders` | `col_*` invisible boxes around furniture |
| `route` | `door_01…06`, `path_000…` empties |
| `markers` (seats) | `seat_screen_1/2`, `seat_garden_1/2` empties |
| `markers` | rooms and spawns (don't touch) |

## Export (every time)

File → Export → glTF 2.0:
- Format: **glTF Binary (.glb)**
- Include: Visible Objects, Punctual Lights ✓, **Custom Properties ✓** (carries frame `priority`)
- Transform: **+Y Up ✓**
- Mesh: Apply Modifiers ✓, UVs ✓, Normals ✓
- Compression: **off** (Claude Code optimises later)
- Animation: off
- Save to: `web/public/models/museum.glb` (overwrite)

Then refresh the web page. Commit `museum.blend` + `museum.glb` together.

## The steps

**A1 — Export now (walls only).** Before any polish. Claude Code builds the walk test (B1). Walk it on your phone: are rooms too big or small, doors clear, walk time 1.5–2 minutes? Fix the plan now; changes later are expensive.

**A2 — Structure details.**
- Ceilings: a plane per room at z = 4.0, named `ceiling_*`. Garden stays open to the sky.
- Skirting boards: 12 cm high, 2 cm deep, around each room.
- Door trims: 10 cm wide around each full-height doorway; the garden arch keeps its arch shape. No windows.

**A3 — Materials** (Poly Haven / ambientCG, 1K):

| Surface | Material |
|---|---|
| Foyer floor | light marble |
| Gallery and heart room floors | warm oak |
| Screen room floor + walls | dark matte |
| Walls | warm ivory plaster |
| Skirting, trims | dark wood |
| Outside walls | charcoal |
| Garden floor | grass + stone path |

**A4 — Photo slots (done).** Frames are **built in code**; in Blender you only place the photo areas.
- `slot_frame_01…43`: square planes 1.0–1.8 m (= the largest photo area), numbered in route order, custom property `priority` 1/2/3 (1 = hero frames, filled first). Centre ~1.6 m high, 3 cm in front of the wall, front facing into the room. Leave room around each box for the 8 cm mat + 6 cm moulding the web adds.
- `collage_board` (5.0 × 3.0 m) on the heart room north wall + `slot_collage_01…12` scattered on it, mixed sizes, slightly tilted, each a few mm in front of the board. Their tilt is kept.
- `screen_surface` (4.8 × 2.7 m) on the screen room north wall.
- Seats: `seat_screen_1/2`, `seat_garden_1/2` empties; local −Y = where the sitter looks.
- Every slot plane: origin in the centre, UV upright, rotation and position are kept by the web (don't apply rotation if it flips the photo).
- Don't model frames, mats or placeholder decor; the web builds them and puts a small plant under empty frames.

**A5 — Furniture and decor.** Rose arch at the entrance, welcome wall in the foyer, bench in the screen room, side tables in the heart room, a few plants. Garden easel with `slot_centrepiece` (optional): a plane whose bottom edge sits on the easel ledge; the web rests the photo there with a gold moulding. Add a `col_*` box for anything solid. Nothing blocks a doorway or hides a photo.

**A6 — Garden.** Grass, pink/white rose bushes along the walls, stone path from the arch to the bench, 2 small trees, string lights, easel + bench for two facing it. Add `seat_garden_1/2` empties on the bench.

**A7 — Lighting and route.**
- Warm spot per frame, string lights in the heart room, screen glow, twilight sky (Poly Haven HDRI) over the garden.
- **The next door is always the brightest point** in each room.
- `door_01…06` empties in doorway centres; `path_000…` empties every ~1.5 m on the floor along `design/route.md`.

**A8 — Bake and final export.** Baked light is what makes it look real on phones. When you reach this step, ask Claude Code for a bake helper script (it runs on a copy of the file, never changes the design).

## Save

Ctrl+S often. `.blend1` backup files are ignored by git.
