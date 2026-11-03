# Materials — final gallery

| Surface | Material | Texture | Colour |
|---|---|---|---|
| All floors | `mat_floor_wood` | Poly Haven laminate_floor_02, graded + rebuilt as random-length boards (2k, 1 tile = 2.2 m) | glossy dark walnut-cherry |
| Walls | `mat_wall_plaster` | Poly Haven beige_wall_001, graded | warm cream-beige |
| Skirting, door frames, collage niche | `trim_cream` | none | cream |
| Crown moulding | `crown_cream` | none | cream |
| Ceiling band, tray, cornice | `ceiling` | none | warm white |
| Gold panel lines (walls, ceilings) | `gold_trim` | none | gilt gold, lit like the mouldings (vertex light) |
| Track rails / spot heads | `track_black` / `track_white` | none | matte black / white |
| Spot lenses, niche LED strips | `led_glow` | none | warm white glow (unlit on the web) |
| Downlight trims | `brass_soft` | none | brass (gold matcap on the web) |

Textures: `assets-src/blender/textures/<id>/<id>_albedo_*.jpg`. The web uses albedo (TEXCOORD_0) × lightmap.

Photo frames (web only, `web/src/frames/`): satin rose-gold metal, warm-white mat with a fine rose-gold bevel. The same frames in the collage.

Light (baked): warm 2400 K white for the downlights, photo spots and wall wash, a soft warmer LED glow in the collage niche (the niche's back wall stays the same warm beige as the walls), a warm dusk sky through the doors. Levels and colours: `tools/bake/design.py` (`LEVEL`, `WARM_WHITE`).
