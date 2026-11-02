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
| Owner: re-export `museum.glb` | ⏳ Needed | Turn on Include → Custom Properties; `priority` is in the .blend but not in the current export (all frames fall back to priority 3) |
| Baked lighting (`design/lighting.md`) | ✅ Built 2026-11-02 (bright romantic re-bake) | No real-time lights. Static meshes: `MeshBasicMaterial` + lightmap per `lightmap_group` (intensity × π, three divides by π). Photos: exact original colours (white, `toneMapped = false`, anisotropy 8). Mats/plants/board frame: slot `light_rgb`; gold: code-generated matcap, light normalised to brightest slot. Capsule tinted by the floor lightmap (0.3 s). AgX, exposure 1. Tuning: `web/src/config/lighting.ts`. Owner: compare with `design/lighting-reference/baked-*.png` |
| Owner: `ceiling_light_fixtures` | ⏳ Needed | Has no `lightmap_group` or `light_rgb`, so it is drawn unlit (base colour). Add it to a bake group, or give it `light_rgb` |
| B2b Photo viewer (tap → full screen) | ⏳ Next | |
| A2 Structure details | ⏳ | Owner (ceilings, skirting, door trims) |

## B1 tuning values (easy to change)
- Walk speed 2.2 m/s (Shift = 4.0 m/s on desktop): `web/src/player/Player.tsx`
- Capsule 1.8 m tall, 0.3 m radius: `web/src/player/Player.tsx`
- Camera 3.2 m behind, 2.2 m high, looking slightly down at the head (1.6 m): `web/src/player/cameraRig.ts`
- Wall in the way: camera eases in (no snap), hard stop 8 cm before the wall surface so it never clips
- Capsule fades out when the camera is closer than 1 m (fully transparent at 0.5 m)
