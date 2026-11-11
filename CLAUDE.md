# CLAUDE.md — rules for Claude Code in keepsakes-web

Keepsakes (keepsakes.gift): a couple's photos become a private 3D "Museum of Us" they walk through in the browser, alone or together on two phones.

Read `BUILD_SPEC.md` before any task. Do one step, show the result, update `PROGRESS.md`, then stop.

## Who does what
- **The owner makes the museum by hand in Blender.** `assets-src/blender/museum.blend` is the only source of the 3D world.
- **Claude Code builds the web experience** in `web/` around the exported `web/public/models/museum.glb`.
- Never edit, regenerate or "fix" `museum.blend` or write scripts that rebuild the museum. If something in the model is wrong, tell the owner exactly what to change in Blender.
- Read-only Blender scripts (check names, report sizes, render a preview) are allowed. Put them in `tools/`.
- When the owner asks, helper scripts for mechanical work (lightmap UVs, baking, export) are allowed. They work on a copy and never change the design.

## Rules
1. Scope now: the experience only. No sign-in, payments, database or editor.
2. Web code never builds rooms. It loads the `.glb`, finds objects by name (BUILD_SPEC §4), fills photo slots from `web/public/demo/demo-gift-*.json`, and adds interaction.
3. Stack: Vite + React 18 + TypeScript (strict), three.js + @react-three/fiber + drei, @react-three/rapier, @react-three/postprocessing, Zustand.
4. Small, readable files (< 250 lines), clear names, no clever abstractions.
5. Mobile first: check at 390×844. Must meet the targets in BUILD_SPEC §8.
6. Assets: only CC0, Pixabay License, SIL OFL, MIT/ISC. Add every asset to `ASSETS.md`. No Mixamo, no "personal use only", nothing copied from other gift sites.
7. Never commit secrets. `.env.local` stays out of git. Never invent API keys.
8. If a request would hurt quality, speed or clarity, say so and suggest a better option first.
9. Make `design/game-feel.md` the movement standard: player movement, camera and controls must match it. Its values live only in `web/src/config/gameFeel.ts`.
10. The owner tests every step manually and says "passed". Never build debug overlays, test harnesses, trace scripts or measurement tools unless the owner asks.
11. Clean, simple, maintainable code: small focused files, clear names, no dead code, no hacks, tuning values only in config files.
12. Work efficiently: read only the files needed, don't run the dev server or browser tests, short summaries.
13. **No real-time lights.** All light is baked in Blender (`design/lighting.md`). The web never adds SpotLight, PointLight, DirectionalLight, HemisphereLight, AmbientLight or shadows; lights in the `.glb` are removed on load. Materials are unlit (`MeshBasicMaterial` + lightmap, or `light_rgb`; matcap for gold). Tuning lives in `web/src/config/lighting.ts`. One exception: the characters (bride) are lit by their own `addCharacterLights` (`web/src/characters/character.ts`: hemisphere, two directional, room reflections). Only their lit materials use it; nothing in the museum may use a lit material.
14. **Identical on every device.** No quality tiers that change lights, materials or effects. Only the render resolution (pixel ratio) may adapt, to keep the frame rate.
15. **Never change the couple's photos.** Every photo (frames, collage, screen, garden board, full-screen viewer) shows its exact original colours: `MeshBasicMaterial`, white colour, `toneMapped = false`, no tint, no filters, no post-processing. Only the frame around it takes the room's `light_rgb`.

Blender (for read-only tools): `/Applications/Blender.app/Contents/MacOS/Blender --background --python <script>` (5.2.3 LTS).
