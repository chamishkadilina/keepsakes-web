# Blender guide — polishing museum.blend

`museum.blend` is the one source of the museum. You polish it by hand; the web loads what you export.

## Golden rules (break these and the web breaks)

1. **Never move or resize the walls, doors or rooms.** The layout is approved.
2. **Keep the names in BUILD_SPEC §4 exactly** (`slot_frame_01`, `spawn_her`, `door_01`, …).
3. **Metres, real sizes.** Type exact numbers in the N panel. Snap increment 0.05 m.
4. **Apply transforms before export:** select all → Ctrl+A → All Transforms.
5. **Materials: Principled BSDF only** (Base Color, Roughness, Metallic, Normal Map, Emission, Alpha). Other nodes don't export to the web.
6. **Textures outside the .blend:** put them in `assets-src/blender/textures/`, then File → External Data → Make Paths Relative. Don't pack them. Max 1K, 2K only for the floor or the hero wall.
7. **Budget:** ≤ 200k triangles in total (Overlays → Statistics), ≤ 25 materials. Fewer = faster on phones.
8. Every downloaded asset gets a line in `ASSETS.md` (file, URL, author, license). CC0 only.

## Collections (already created)

| Collection | Put in it |
|---|---|
| `structure` | walls, garden walls, ceilings, trims, glass |
| `floors` | floors |
| `frames_slots` | `frame_NN`, `slot_*`, `screen_surface`, `welcome_wall_text`, `deco_swap_frame_NN` |
| `decor` | rose arch, benches, easel, plants, garden |
| `lights` | lights (`rt_light_*` = stays live on the web) |
| `colliders` | `col_*` invisible boxes around furniture |
| `route` | `door_01…06`, `path_000…` empties |
| `markers` | rooms and spawns (don't touch) |

## Export (every time)

File → Export → glTF 2.0:
- Format: **glTF Binary (.glb)**
- Include: Visible Objects, Punctual Lights ✓
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
- Door trims: 10 cm wide around each doorway. Window frames + glass (`glass` material: Alpha 0.15, Roughness 0.05).

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

**A4 — Frames and slots.**
- Gallery frame: photo area **1.2 × 0.9 m**, gold frame 8 cm wide, white mat 8 cm, 5 cm deep. Centre at **1.6 m** high. Centres ≥ 2.5 m apart, 2 m clear floor in front.
- Slot plane = the photo area, 1 cm in front of the mat, front facing into the room.
- Make one frame + slot, then Shift+D duplicate and rename. Number in route order.
- Suggested spread (23 total): story gallery 9 (incl. both sides of the partition), heart room 5, right gallery 9. Plus `slot_heart_01…06` on the heart room north wall and `slot_centrepiece` (1.6 × 1.2 m) on the garden easel.
- For each frame, place a small `deco_swap_frame_NN` (plant, lamp or small art) in the same spot — shown when there are fewer photos.

**A5 — Furniture and decor.** Rose arch at the entrance, welcome wall in the foyer, screen + bench in the screen room, side tables with small frames in the heart room, a few plants. Add a `col_*` box for anything solid. Nothing blocks a doorway or hides a photo.

**A6 — Garden.** Grass, pink/white rose bushes along the walls, stone path from the arch to the bench, 2 small trees, string lights, easel + bench for two facing it. Add `seat_garden_1/2` empties on the bench.

**A7 — Lighting and route.**
- Warm spot per frame, string lights in the heart room, screen glow, twilight sky (Poly Haven HDRI) over the garden.
- **The next door is always the brightest point** in each room.
- `door_01…06` empties in doorway centres; `path_000…` empties every ~1.5 m on the floor along `design/route.md`.

**A8 — Bake and final export.** Baked light is what makes it look real on phones. When you reach this step, ask Claude Code for a bake helper script (it runs on a copy of the file, never changes the design).

## Save

Ctrl+S often. `.blend1` backup files are ignored by git.
