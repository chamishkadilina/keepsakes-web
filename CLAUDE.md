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

Blender (for read-only tools): `/Applications/Blender.app/Contents/MacOS/Blender --background --python <script>` (5.2.3 LTS).
