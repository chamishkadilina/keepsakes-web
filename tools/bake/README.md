# Museum bake pipeline

Mechanical tools: they never change the approved room layout. `pipeline.sh` runs everything (see its header).

| Step | Script | What it does |
|---|---|---|
| textures | `grade_textures.py`, `floor_synth.py`, `plank_variation.py`, `floor_tone.py`, `props_atlas.py` | grade the Poly Haven textures (cream-beige paint), rebuild the floor as random-length boards (2k, 2.2 m tile), tone it dark walnut-cherry; paint the one texture for the rugs, marble, gift wrap, boxwood and the balloon colours (`decor/decor_atlas.jpg`). Already done: the results are in `assets-src/blender/textures/` |
| look | `design.py` | palette, tray ceilings with cornice + gold lines, a few downlights, track spots sized to every photo and exhibit, collage niche with LEDs, gold wall panels, soft wall wash, a dimmer screen room (like a little cinema), and the warm glow of every candle, lantern and the neon (accent lights). Light colours and levels at the top (`WARM_WHITE`, `LEVEL`) |
| furniture and decor | `props.py` (used by `design.py`) with `props_romance.py`, `props_flowers.py`, `props_trees.py`, `props_cinema.py`, `props_garden.py`, `props_geometry.py` | everything in the rooms and the garden, modelled in code and merged into one mesh per material in each part of the museum. Where everything stands: `LAYOUT` in `props.py` (each exhibit also names the rail its own spot hangs from); colours: `PALETTE`. Every piece gets a `footprint_<name>` marker for walking and the petals (a circle for round pieces, else a box, covering what stands on the floor up to head height); the `candle_flames` marker lists where the web lights a flame, `projector_lens` where the projector's beam starts |
| bake | `bake_lightmaps.py` | Cycles bake of walls, floors, ceilings, garden walls (light only, no colour) |
| encode | `finish_lightmaps.py` | denoise, PNG lightmaps + `lightmaps.json`, `light_rgb` on every photo slot |
| trim | `bake_trim_vertex.py`, `smooth_trim_light.py` | light for mouldings, cornices, the niche and all the furniture and decor, baked into vertex colours |
| check | `check_lightmaps.py` | quick render of the baked result |
| export | `export_glb.py` | museum.glb (custom properties on, lights off, vertex colours on) |

If you change the layout in Blender, edit `assets-src/blender/museum_base.blend` and run the pipeline again (~1 h on 2 CPU cores). To move or add furniture and decor, edit `LAYOUT` in `props.py` and run the pipeline.
