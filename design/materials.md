# Materials — final gallery

| Surface | Material | Texture | Colour |
|---|---|---|---|
| All floors | `mat_floor_wood` | Poly Haven laminate_floor_02, graded + rebuilt as random-length boards (2k, 1 tile = 2.2 m) | glossy dark walnut-cherry |
| Walls | `mat_wall_plaster` | Poly Haven beige_wall_001, graded | warm cream-beige |
| Skirting, door frames, collage niche | `trim_cream` | none | cream |
| Crown moulding | `crown_cream` | none | cream |
| Ceiling band, tray, cornice | `ceiling` | none | warm white |
| Gold panel lines (walls, ceilings) | `gold_trim` | none | gilt gold, lit like the mouldings (vertex light) |
| Track rails / spot heads | `track_black` / `track_white` | none | plain shapes in the model; the web replaces them with satin-black rails and champagne-gold spots |
| Spot lenses, niche LED strips | `led_glow` | none | warm white glow (unlit on the web) |
| Downlight trims | `brass_soft` | none | brass (gold matcap on the web) |

Textures: `assets-src/blender/textures/<id>/<id>_albedo_*.jpg`. The web uses albedo (TEXCOORD_0) × lightmap.

Photo frames (web only, `web/src/frames/`): satin rose-gold metal, warm-white mat with a fine rose-gold bevel. The same frames in the collage.

Furniture, exhibits and decor (`tools/bake/props.py`, baked with the room; one mesh per material in each part of the museum, `prop_<zone>_<material>`):

| Piece | Material | Colour |
|---|---|---|
| Sofas, cushions | `velvet_rose`, `velvet_cream` | dusty-rose velvet with cream velvet cushions (soft sheen on the web) |
| Curtains, swag and pelmets (the foyer's door into the story, the cinema screen, the garden door), the cinema's little stage | `curtain_velvet` | deep wine-red velvet (soft sheen on the web, both sides drawn) |
| The foyer's sheers | `sheer_ivory` | ivory voile, see-through on the web so the little lights behind them glow through (not baked) |
| Legs, frames, easels, table bases, lanterns, flower stands, stanchions, tie-backs, curtain rods, the light strings' wire, the dimmer, rims and bands | `gold_metal` | champagne gold (gold matcap on the web) |
| Plinths, urns, pedestals, planters, vases, candles, the bench, the boards' backs, the dimmer's inset | `trim_cream` | cream, like the skirting |
| Heart balloons | `balloon_foil` | red (half of them), blush and rose-gold mylar (the colours are swatches in the decor texture; foil matcap on the web) |
| Lantern panes, the neon's panel | `glass` | clear (not baked; on the web it only adds its reflections) |
| The neon's words | `neon_text` | written by the web (`neonSign.ts`); not baked |
| The foyer's title wall | `welcome_board` | ivory; the web writes the welcome on it (`welcomeSign.ts`) |
| The cinema screen | `screen_white` | matte white, softly lit on the web (not baked); their videos play just in front of it |
| Quote board | `quote_board` | ivory; the web writes the couple's quote on it (`quoteBoard.ts`) |
| Rugs, marble tops, hedges and rose bushes | `decor_atlas` | one texture for all of them (`assets-src/blender/textures/decor/decor_atlas.jpg`, painted by `tools/bake/props_atlas.py`): ivory rugs with dusty-rose borders, gold lines and a rose medallion, a deep burgundy rug in the screen room, white marble, clipped boxwood, the balloon and ribbon colours |
| Roses, velvet ropes | `rose_petal`, `rose_blush`, `velvet_cream`, `rose_leaf` | deep red, blush-pink and white velvety petals, green leaves (both sides drawn) |
| The weeping figs' leaves | `ficus_leaf` | fresh glossy green (both sides drawn) |
| The light strings' bulbs | `bulb_glow` | bright golden glow (not baked; a glowing-bulb matcap on the web) |
| Trees and topiaries | `olive_leaf`, `fig_leaf`, `bark`, `soil` | silvery olive green, deep fiddle-leaf green (also the kentia palms' fronds and the foliage inside the rose topiaries), grey-brown bark, dark soil |
| Ribbons | `ribbon_red` | red satin (the topiaries' bows) |
| The ceiling projector, the screen's frame | `projector_white`, `projector_black`, `lens_glow` | satin white body with a black mount, vents and lens barrel (shaded on the web so its details show in the dim room), the cinema screen's deep black border; the lens glows warm white (not baked) |

Track lights (web only, `web/src/lighting/trackLights.ts`): satin-black rails, adapters and yokes; champagne-gold heads, knobs and rail end caps (the gold of the downlight trims); black band and bezel; gold reflector around a warm lens.

Light (baked): warm 2400 K white for the downlights, photo spots and wall wash, a soft warmer LED glow in the collage niche (the niche's back wall stays the same warm beige as the walls), a warm dusk sky through the doors and over the garden, orange candlelight round every candle and lantern, the golden glow of the heart room's light strings on its walls, the warm glow of the little lights behind the foyer's sheers on its side walls and the pink glow of the neon on its wall. The screen room is dimmer, like a little cinema (its downlights at under a third of the gallery level, no wall wash). Levels and colours: `tools/bake/design.py` (`LEVEL`, `WARM_WHITE`) and `props_romance.py` (`CANDLE_LIGHT`, `BULB_LIGHT`, `FAIRY_LIGHT`, `NEON_LIGHT`).
