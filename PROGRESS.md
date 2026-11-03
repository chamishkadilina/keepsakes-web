# PROGRESS

| Step | Status | Notes |
|---|---|---|
| Layout (walls, doors, windows, garden) | ✅ Approved | `assets-src/blender/museum.blend`; approved again after the B1 phone walk, 2026-11-01 |
| A1 Export walls-only `museum.glb` | ✅ Done | 43 KB. `walls` and `garden_walls` have no material (web shows a matte placeholder until A3) |
| B1 Walk test on phone | ✅ Done 2026-11-01 | `web/`: capsule at `spawn_her`, joystick + drag-to-look, WASD + mouse, trimesh collisions, wall-safe 3rd-person camera, timer (first step → garden) + room name + Restart |
| B1 Owner phone walk | ✅ Done | Layout approved. Camera fixes applied (see below) |
| B1 Game feel (`design/game-feel.md` §1–3, §5) | ✅ Built 2026-11-01 | Spring-eased movement, spring-arm camera, floating joystick, pointer lock. Tuning in `web/src/config/gameFeel.ts`. Owner: test on Mac 120 Hz + phone |
| Museum update | ✅ Done 2026-11-01 | No windows, full-height doorways (garden arch kept), garden empty. Slots: 43 frames (priority 1/2/3), collage board + 12 slots, screen, 4 seats |
| B2 Photos + frames | ✅ Built 2026-11-01 | `web/src/gallery/`: collage = first 12, then frames by priority → route order; contain fit, 9:16–16:9 crop; mat + gold mitred moulding, polaroids, board moulding, plant for empty frames; thumbnails → full within 4 m. Tuning: `web/src/config/frames.ts`. Demo: `?demo=6` / `?demo=30` (default 30). Owner: test |
| Look = `design/web-reference` (final gallery) | ✅ Built 2026-11-03, lighting kit v5 (collage without cast shadows; shipped `museum.glb` + lightmaps with a softer collage niche, loaded as-is; rose-gold frames; collage without a `light` option) | `design/lighting.md` followed as-is (spot pools, no picture lights, `lm_trim` lightmap) on the shipped `museum.glb` (not re-exported): `lighting/bakedLighting.ts`, `lighting/ceilingLights.ts`, `lighting/floorReflection.ts` (wood floors), `decor/rosePetals.ts` (300 petals + 14 roses on `config/route.ts`, swept aside around the visitor every frame). Every frame photo: `photoSizeForSlot` + `createPhotoFrame`, hung on the wall behind its slot, photo's own aspect ratio (no crop). Heart room: `createCollageWall` (5.28 × 3.04 m, the niche opening) centred on `collage_board`, `slot_collage_*` hidden. Every frame is filled (photos repeat from #1 when they run out); no placeholder plants. Removed: fairy lights, moods, goldMatcap (→ `matcaps.ts`), `fairy_lights.json`, `moods.json`, old frame/polaroid/plant code, `pictureLight` option, `tools/bake/design_v20.py`, `grade_textures_v20.py`, `regrade_light.py`. AgX, antialias, no composer, CSS vignette per spec. Owner: compare with `design/web-reference/*.png`, check phone frame rate |
| Baked lighting (`design/lighting.md`) | ✅ Built 2026-11-02 (bright romantic re-bake) | No real-time lights. Static meshes: `MeshBasicMaterial` + lightmap per `lightmap_group` (intensity × π, three divides by π). Photos: exact original colours (white, `toneMapped = false`, anisotropy 8). Mats/plants/board frame: slot `light_rgb`; gold: code-generated matcap, light normalised to brightest slot. Capsule tinted by the floor lightmap (0.3 s). AgX, exposure 1. Tuning: `web/src/config/lighting.ts`. Owner: compare with `design/lighting-reference/baked-*.png` |
| Textured floors + walls (`design/materials.md`) | ✅ Built 2026-11-02 | glTF base colour texture (sRGB, mipmaps, repeat, anisotropy 8) × lightmap. 4 Poly Haven CC0 textures in `ASSETS.md`. Owner: compare with `design/lighting-reference/baked-*.png` (incl. foyer) |
| B2b Photo viewer (tap → full screen) | ⏳ Next | |
| A2 Structure details | ⏳ | Owner (ceilings, skirting, door trims) |

## B1 tuning values (easy to change)
- Walk speed 2.2 m/s (Shift = 4.0 m/s on desktop): `web/src/player/Player.tsx`
- Capsule 1.8 m tall, 0.3 m radius: `web/src/player/Player.tsx`
- Camera 3.2 m behind, 2.2 m high, looking slightly down at the head (1.6 m): `web/src/player/cameraRig.ts`
- Wall in the way: camera eases in (no snap), hard stop 8 cm before the wall surface so it never clips
- Capsule fades out when the camera is closer than 1 m (fully transparent at 0.5 m)
