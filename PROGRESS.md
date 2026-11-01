# PROGRESS

| Step | Status | Notes |
|---|---|---|
| Layout (walls, doors, windows, garden) | ✅ Approved | `assets-src/blender/museum.blend`; approved again after the B1 phone walk, 2026-11-01 |
| A1 Export walls-only `museum.glb` | ✅ Done | 43 KB. `walls` and `garden_walls` have no material (web shows a matte placeholder until A3) |
| B1 Walk test on phone | ✅ Done 2026-11-01 | `web/`: capsule at `spawn_her`, joystick + drag-to-look, WASD + mouse, trimesh collisions, wall-safe 3rd-person camera, timer (first step → garden) + room name + Restart |
| B1 Owner phone walk | ✅ Done | Layout approved. Camera fixes applied (see below) |
| B1 Game feel (`design/game-feel.md` §1–3, §5) | ✅ Built 2026-11-01 | Spring-eased movement, spring-arm camera, floating joystick, pointer lock. Tuning in `web/src/config/gameFeel.ts`. Owner: test on Mac 120 Hz + phone |
| A2 Structure details | ⏳ Next | Owner (ceilings, skirting, trims, glass) |

## B1 tuning values (easy to change)
- Walk speed 2.2 m/s (Shift = 4.0 m/s on desktop): `web/src/player/Player.tsx`
- Capsule 1.8 m tall, 0.3 m radius: `web/src/player/Player.tsx`
- Camera 3.2 m behind, 2.2 m high, looking slightly down at the head (1.6 m): `web/src/player/cameraRig.ts`
- Wall in the way: camera eases in (no snap), hard stop 8 cm before the wall surface so it never clips
- Capsule fades out when the camera is closer than 1 m (fully transparent at 0.5 m)
