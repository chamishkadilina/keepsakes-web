# BUILD_SPEC.md — Keepsakes · The Museum of Us (experience build)

> Brand: Keepsakes · Domain: keepsakes.gift · Repo: `keepsakes-web` (private)
>
> **Scope: only the experience.** No sign-in, payments, database or editor yet. All gift content comes from local demo files.
>
> Use with Claude Code one step at a time: *"Read CLAUDE.md and BUILD_SPEC.md. Do step B1 only. Show me and stop."*
>
> **OWNER:** = done by Chamishka (Blender work, phone tests, tester feedback).

---

## 0. Goal and definition of done

A private 3D museum of a couple's story that opens in any phone browser. They walk through it alone, or together on two phones, see their photos in a warm, beautiful place, and end in a twilight garden, sitting side by side in front of their biggest photo, reading the final words.

- [ ] 4 of 5 outside testers say "wow" or "I'd send this to my partner".
- [ ] Nobody gets lost between the entrance and the garden.
- [ ] Walkable in < 6 s on a mid-range phone (4G); ≥ 30 fps on iPhone 11 / Pixel 6a.
- [ ] Two phones see each other in Together mode within 2 s.
- [ ] Works with 6 photos and with 30 photos, never looks empty.

## 1. Phases

| Phase | Who | What |
|---|---|---|
| **A. Museum in Blender** | OWNER (by hand) | Polish `museum.blend` → export `museum.glb`. Guide: `assets-src/blender/BLENDER_GUIDE.md`. |
| **B. Walkable experience** | Claude Code | The web page: walking, photos, the 7 moments, music, polish, speed. |
| **C. Together mode** | Claude Code | Two people in the museum at the same time. |
| **T. Tester loop** | OWNER + Claude Code | After B and after C: test with real people, fix, repeat. |

A and B run side by side: every time the owner exports a new `museum.glb`, the web page shows it.

---

## 2. The museum (approved layout — do not change)

Source: `assets-src/blender/museum.blend`. Route and doors: `design/route.md`. Look: `design/museum-reference.png`.

Units metres, Blender Z up (glTF exports Y up). Origin = foyer south-west corner. x = east, y = north.

| Room | Marker | Floor area (x, y) |
|---|---|---|
| 1 Foyer | `room_1_foyer` | 0–11, 0–10 |
| 2 Story gallery (with partition wall) | `room_2_story_gallery` | 0–11, 10–21 |
| 3 Heart room | `room_3_heart_room` | 11–23, 1.5–21 |
| 4 Right gallery (L-shape) | `room_4_right_gallery` | 23–38, 13–21 + 23–26.5, 1.5–13 |
| 5 Screen room | `room_5_screen_room` | 26.5–38, 1.5–13 |
| 6 Garden (enclosed) | `room_6_garden` | 38–52, 0–16 |

Walls 4 m high (outer 0.4 m, inner 0.25 m). Doors 3 m wide × 3 m high (entrance 3.2 m). Windows sill 1.0 m, top 3.2 m. Garden walls 2.4 m. Arched garden door.

---

## 3. Phase A — museum in Blender (OWNER)

Follow `assets-src/blender/BLENDER_GUIDE.md`. Order:

| Step | What | Then |
|---|---|---|
| **A1** | Export the walls-only `museum.glb` now | Claude Code does **B1**: walk test on your phone. Don't polish until the size and pacing feel right. |
| **A2** | Structure details: ceilings, skirting, door and window trims, glass | export → check in browser |
| **A3** | Materials (CC0 textures, 1K) | export → check |
| **A4** | Frames and photo slots | export → Claude Code does **B2** |
| **A5** | Furniture and decor (rose arch, welcome wall, benches, screen, easel, plants) | export → check |
| **A6** | Garden (grass, roses, path, trees, string lights) | export → check |
| **A7** | Lighting + route markers (doors, path dots) | export → Claude Code does **B3** |
| **A8** | Bake lighting, final export | Claude Code optimises the file (B5) |

Characters: Quaternius CC0 (2 looks for her, 2 for him; idle, walk, sit, wave) → `web/public/models/characters.glb`. Claude Code may prepare this in B1 with a placeholder capsule first.

---

## 4. Names the web code depends on

Keep these names exactly. Anything not listed is free to name as you like.

| Name | Type | Meaning |
|---|---|---|
| `room_1_foyer` … `room_6_garden` | empty | Room centres (music, lighting, triggers) |
| `spawn_her`, `spawn_him` | empty | Start points at the entrance, facing into the foyer |
| `slot_centrepiece` | plane | Photo #1 on the garden easel (largest) |
| `slot_heart_01` … `06` | plane | Photos #2–#7 on the heart wall |
| `slot_frame_01` … `23` | plane | Remaining photos, numbered in route order |
| `deco_swap_frame_01` … `23` | any | Shown instead of a frame when there are fewer photos |
| `frame_01` … `23` | mesh | The frame around each slot (hidden together with its slot) |
| `screen_surface` | plane | Slideshow screen in the screen room |
| `seat_screen_1/2`, `seat_garden_1/2` | empty | Where avatars sit, facing forward (−Y in Blender) |
| `welcome_wall_text` | plane | Area for the "For {name}" welcome text |
| `door_01` … `06` | empty | Centre of each doorway in route order |
| `path_000` … `path_NNN` | empty | Route trail points on the floor, in order |
| `col_*` | mesh | Invisible collision boxes for furniture (walls and floors collide automatically) |
| `rt_light_*` | light | Lights that stay live in the browser (everything else is baked) |

Slot planes: front faces into the room, origin in the centre, size = the largest photo area inside the frame. The web fits each photo inside it by aspect ratio.

---

## 5. Demo content

`web/public/demo/demo-gift-6.json` and `demo-gift-30.json`, switch with `?demo=6` / `?demo=30`.

```json
{
  "theirName": "Maya",
  "yourName": "Ethan",
  "dedication": "Every photo in here is a moment I never want to forget. This place is yours.",
  "finalWords": "Of all the places I've been, my favourite is next to you.",
  "music": "piano",
  "photos": [
    { "src": "/demo/photos/01.webp", "thumb": "/demo/photos/01_t.webp", "w": 1600, "h": 1067, "caption": "Where it all began" }
  ],
  "roomKey": "demo-room-local"
}
```
Demo photos: Pixabay License, listed in `ASSETS.md`.

---

## 6. Phase B — walkable experience (Claude Code)

**B1 — Walk test.** Vite app in `web/`. Load `museum.glb`, capsule (or character) at `spawn_her`, third-person camera that never clips walls, joystick + drag-to-look on phone, WASD + mouse on desktop, collisions from walls, floors and `col_*`. On-screen timer from entrance to garden. Run with `npm run dev -- --host` and explain how to open it on a phone on the same Wi-Fi.
**OWNER:** walk it on your phone. Judge room sizes, doors, pacing, walk time. Report changes before polishing in Blender.

**B2 — Photos.** Fill slots from the demo file: thumbnails first, full size within 4 m. Empty slots → hide `slot_frame_NN` + `frame_NN`, show `deco_swap_frame_NN`. Tap a photo → full screen with caption, swipe next/previous.

**B3 — The 7 moments.**
1. Intro card: dedication typed line by line → "Open your gift" (starts music, fades in over 3 s).
2. Welcome wall text from data.
3. Wayfinding: glowing petal/gold trail along `path_*`, the next door is the brightest point, backtrack hint after 10 s, "Take me to the garden" after the screen room or after 8 minutes.
4. Heart wall glows as you enter the heart room.
5. Screen room slideshow with crossfades; sit on the bench to watch.
6. Garden: sitting shows the final words; lights dim slightly; hearts drift up.
7. End: "Made with Keepsakes · keepsakes.gift", small and quiet.

**B4 — Polish.** Tone mapping, subtle bloom, vignette, soft footsteps, smooth camera, quality tiers by GPU, 2D slideshow fallback if WebGL fails, `prefers-reduced-motion`, mute button always visible.

**B5 — Speed.** Optimise `museum.glb` with gltf-transform (meshopt, KTX2/WebP ≤ 1K, 2K only for hero surfaces). Meet §8 on a real mid-range Android and an iPhone 11-class phone.

---

## 7. Phase C — Together mode (Claude Code)

- "Who are you?": **"I'm Maya" / "I'm Ethan"** (+ "Just looking"). Picks name tag and look.
- Supabase Realtime only (free project, no tables): channel `gift:{roomKey}`. Presence `{ who, name, look, joinedAt, seated }`. First 2 by `joinedAt` are players; others watch invisibly.
- Broadcast: `move {p, ry, anim}` ≤ 8×/s only while moving; `say {id}` preset messages ("I love you", "Come here", "Look at this one", "Remember this?", "❤️") ≤ 1/s; `emote {wave|heart|hug|sit}`; `look {slotId}` makes that photo glow for the partner.
- Partner ~100 ms behind with interpolation; arrival chime + "{name} is here 🤍"; edge arrow when off-screen.
- Both seated on the garden bench → the shared ending plays for both. Alone, sitting still shows it.
- Auto-reconnect; solo always works. Unit tests for `roomRules.ts`.
- **OWNER:** create a free Supabase project, put URL + anon key in `web/.env.local`, test two phones on different networks for 15 minutes.

---

## 8. Quality targets

| Metric | Target |
|---|---|
| Loading screen visible (mid Android, 4G) | < 1.5 s |
| Walkable | < 6 s |
| `museum.glb` (without photos) | ≤ 8 MB |
| Draw calls | ≤ 150 |
| Frame rate | ≥ 30 fps iPhone 11 / Pixel 6a; 60 desktop |
| Together: partner appears | < 2 s |

---

## 9. Assets (free for commercial use)

| Need | Source | License |
|---|---|---|
| Textures, HDRI sky | Poly Haven, ambientCG | CC0 |
| Plants, roses, trees, props | Poly Haven, Quaternius, Kenney | CC0 |
| Characters | Quaternius | CC0 |
| Demo photos | Pixabay | Pixabay License |
| Music | Pixabay Music, FreePD | Pixabay License / CC0 |
| Footsteps, chime, UI sounds | Kenney | CC0 |
| Fonts | Cormorant Garamond, Inter, Caveat | SIL OFL (self-hosted) |

---

## 10. Tester loop (T)

1. **OWNER:** send the test link to 5 people (ideally couples). Watch at least 2 use it without helping.
2. Ask: What did you feel? Where were you confused? What did you love? Would you send this to your partner?
3. Paste answers into `design/feedback/round-N.md`.
4. Claude Code proposes the top 5 fixes by impact; the owner picks; implement.
5. Repeat until §0 is met.

## 11. Later (separate spec)

Sign-in (Google/Apple), editor, photo upload, payments (Lemon Squeezy), share link + QR, My gifts, database + security rules, legal pages, launch, more museum designs.
