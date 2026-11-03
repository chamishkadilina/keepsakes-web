# Museum bake pipeline

Mechanical tools: they never change the approved room layout. `pipeline.sh` runs everything (see its header).

| Step | Script | What it does |
|---|---|---|
| textures | `grade_textures.py`, `floor_synth.py`, `plank_variation.py`, `floor_tone.py` | grade the Poly Haven textures (cream-beige paint), rebuild the floor as random-length boards (2k, 2.2 m tile), tone it dark walnut-cherry. Already done: the results are in `assets-src/blender/textures/` |
| look | `design.py` | palette, tray ceilings with cornice + gold lines, a few downlights, track spots sized to every photo, collage niche with LEDs, gold wall panels, soft wall wash. Light colours and levels at the top (`WARM_WHITE`, `LEVEL`) |
| bake | `bake_lightmaps.py` | Cycles bake of walls, floors, ceilings, garden walls (light only, no colour) |
| encode | `finish_lightmaps.py` | denoise, PNG lightmaps + `lightmaps.json`, `light_rgb` on every photo slot |
| trim | `bake_trim_vertex.py`, `smooth_trim_light.py` | light for mouldings, cornices and the niche, baked into vertex colours |
| check | `check_lightmaps.py` | quick render of the baked result |
| export | `export_glb.py` | museum.glb (custom properties on, lights off, vertex colours on) |

If you change the layout in Blender, edit `assets-src/blender/museum_base.blend` and run the pipeline again (~20 min on 2 CPU cores).
