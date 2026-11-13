# Look and lighting — final gallery

Target: the owner's final reference video (`design/reference-final/*.png`, frames from it), lit like a real gallery at night:

- warm cream-beige plain walls, tall cream skirting, thin gold panel lines on the gallery walls
- cream tray ceilings with a small cornice and gold lines, a few recessed downlights
- slim black track rails with champagne-gold spot heads (black yoke and bezel, the warm lens deep in a gold reflector): every photo sits in its own soft pool of light, brightest just above the frame
- every photo in a slim modern rose-gold frame with a wide warm-white mat and a fine rose-gold bevel (fresh and romantic, not antique); the frame casts a soft shadow on the wall below it (no picture-light bars)
- the heart room's back wall: a softly backlit niche (its back wall the same warm beige as the walls) with the collage: a relaxed, centred gallery wall of mixed sizes in exactly the same frames, equal gaps everywhere
- glossy dark walnut-cherry floor with soft reflections of the lights; red and blush-pink rose petals and a few roses along the paths through every room that scatter when you walk through them: to a heart of petals in front of the collage, ringed by candles, through the corridor and the screen room to the garden door, and into the right gallery
- a romantic museum, warm like a home: channel-tufted dusty-rose velvet sofas with cream cushions (a three-seater facing the collage on an ivory-and-rose rug with a marble coffee table and side tables; the loveseat facing the screen), big green house trees in cream planters with gold rims (kentia palms, weeping figs, olive trees, fiddle-leaf figs), marble tables and consoles with roses and candles
- flowers as at a wedding: rose topiaries tied with red satin bows, urns of roses spilling over tall cream pedestals
- the foyer is the invitation: the big title wall straight ahead as she comes in, in its own spotlight between two rose topiaries and two bunches of heart balloons on little gold weights; a round ivory rug in its open middle with their initials in gold; ivory sheers along both side walls with a curtain of little warm lights glowing through them; the door where the story begins framed by wine-red velvet curtains hanging straight either side under a pelmet, its way kept clear. It has no photos of its own
- candles and gold lanterns where they belong (on the consoles and tables, round the petal heart, in the corridor, by the garden's daybed and on its grass), their flames flickering and their warm glow on the floors and walls; heart foil balloons, half of them red, the rest blush and rose gold, that float, bob and slowly turn at eye level (tied to the sofa's side tables, or standing on little gold heart weights by the title wall, the chapter boards and the dance floor); tall gold flower stands; a garland of roses round the collage; a pink neon of their words in the corridor
- strings of round, bright golden bulbs draped in swags along the heart room's walls: only the bulbs glow, with no pools of light on the walls between them
- each chapter's title on a smaller board in the same style, straight ahead as you come into its room: "How It Began" (story gallery) and "Reasons I Love You" (right gallery), each with his line under it if he wrote one
- in the heart room's south half, a round marble dance floor with a gold rim and a little gold heart, in a soft pool of light, and beside it a gramophone on a cream plinth that plays their song while they stand on the dance floor (its record turns); petals round the floor's edge
- love notes hanging over the right gallery's open middle, one cream card for each of his reasons, on thin red and gold ribbons above head height, slowly turning
- a gold dimmer switch on the heart room's wall by its door (nothing to do yet: the `dimmer_switch` marker is there for a later feature)
- a few party balloons lying on the floors of the heart room and the right gallery that roll and bounce away when she walks into them
- in their own spotlights: the foyer's title wall ("Welcome to The Museum of Us", their names, the date and his note), the chapter boards, the couple's quote on a big ivory board on a gold easel and a grand dome of roses either side of the collage
- the screen room is a little cinema: a little dimmer, a white projector hanging from the ceiling whose soft beam (dust drifting through it) lands on a real cinema screen (matte white in a black frame with a fine gold edge, above a low velvet stage, between wine-red velvet stage curtains tied back under a pelmet), the same curtains tied back at the garden door, a "Now Showing" film poster of the two of them glowing in a lightbox by the way in, popcorn and drinks on the tables by the loveseat, rose topiaries either side of the stage, each washed by a warm floor light
- every photo can have a small museum label under it (title, date, a line of their story)
- the garden finale through the screen room, at night under the moon and the stars: a daybed for two by the door looking across the lawn to the moon, a fire crackling in a ring of stones out on the lawn before it, a big jacaranda (and a younger one in the far corner) with strings of little warm lights hanging from its branches and draped to the walls, a picnic basket and champagne by the daybed, a few lanterns on a dark leafy lawn, mossy stones and ferns, patches of wildflowers, fireflies, and a little wood of trees, bushes and ferns all round before old mossy stone walls (`tools/bake/garden.py`, layout in `garden_layout.py`)
- no sconces, no picture lights

**The web must look like `design/web-reference/*.png`.** Those screenshots were rendered in a real browser (three.js r170) with the drop-in code below (`web-arrival.png`: the foyer as she comes in; `web-welcome.png`: the title wall; `web-rug.png`: the monogram rug; `web-chapter-story.png`, `web-chapter-reasons.png`: the chapter boards; `web-dance.png`, `web-gramophone.png`: the dance floor and the gramophone; `web-notes.png`: the love notes; `web-poster.png`, `web-popcorn.png`: the cinema's poster and treats; `web-sheers.png`, `web-doorway.png`: the sheers with their little lights and the door into the story; `web-quote.png`: the quote board; `web-candles.png`: the petal heart; `web-neon.png`: the neon; `web-dimmer.png`: the dimmer switch; `web-heart-lights.png`, `web-floor-balloons.png`: the light strings and the balloons on the floor; `web-screen.png`, `web-beam.png`, `web-projector.png`, `web-curtains.png`: the screen room; `web-garden*.png`: the garden; the room views show the decor).

## The walk, room by room

Each room has one part to play, so that by the end she feels loved and wants to thank him (about half the walks will be the two of them together, live):

| Room | Its part | What carries it |
|---|---|---|
| Foyer | the invitation | the big title wall straight ahead with roses and balloons either side, sheers with little lights, velvet curtains framing the door where the story begins |
| Story gallery | how it began | its chapter board straight ahead as you come in, their first photos in order, each with its label |
| Heart room | us now, the peak | the collage in its niche, the quote board, the petal heart ringed by candles, the sofa for two, the golden light strings; the dance floor where the gramophone plays their song |
| Corridor | a pause | "forever us" in neon |
| Right gallery | reasons I love you | its chapter board straight ahead as you come in, the love notes hanging over its middle (one per reason), photos with their labels |
| Screen room | moments in motion | their videos on the cinema screen, the loveseat with popcorn, their "Now Showing" poster |
| Garden | forever, thank you | the daybed for two by the fire, looking across the garden to the lit jacaranda and the moon (the ending is designed next, with the walk for two) |

## The museum file

`web/public/models/museum.glb` and `web/public/models/lightmaps/` are shipped **ready-made and browser-tested**. Do not re-export from Blender unless the model changes.

`museum.glb` is meshopt-compressed (9.7 MB instead of 30.4 MB). Load it with the meshopt decoder: drei's `useGLTF` already does; with a plain `GLTFLoader`:

```ts
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";
const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync("/models/museum.glb");
```

## Rules

1. **No real-time lights or shadows.** All light is baked in Blender. Identical on every device; only the pixel ratio may adapt for speed.
2. **Never change the couple's photos.** Photo materials: `MeshBasicMaterial`, `map` = photo (sRGB), white colour, `toneMapped: false`. Never crop or stretch a photo: frames take the photo's own aspect ratio. No post-processing pass may touch photos.
3. **No post-processing composer.** Render the scene directly so tone mapping stays per-material (room = AgX, photos = untouched).

## Renderer

```ts
gl.outputColorSpace = THREE.SRGBColorSpace;
gl.toneMapping = THREE.AgXToneMapping;      // tested against Neutral: AgX matches the reference
gl.toneMappingExposure = 1;
// <Canvas gl={{ antialias: true }} dpr={[1, 2]}>  — antialiasing on, everywhere
```

Soft vignette overlay (absolutely positioned over the canvas, `pointer-events: none`):

```css
background: radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 55%, rgba(30,18,10,0.35) 100%);
```

## Drop-in code (tested, use as-is)

After loading `museum.glb`, in this order:

```ts
await applyBakedLighting(gltf.scene, "/models/lightmaps");   // lighting/bakedLighting.ts
addCeilingLights(gltf.scene);                                 // lighting/ceilingLights.ts (downlights, track lights, glare)
scene.add(createCandleFlames(gltf.scene));                    // lighting/candleFlames.ts: every candle and lantern burns
scene.add(createCurtainLights(gltf.scene));                   // lighting/curtainLights.ts: the little lights behind the foyer's sheers and in the garden's tree
scene.add(createFireflies());                                 // lighting/fireflies.ts: fireflies over the garden
const fire = createCampfire(gltf.scene); if (fire) scene.add(fire); // lighting/campfire/: the garden's fire (the `campfire` marker)
const sky = new NightSky(); scene.add(sky);                  // lighting/nightSky.ts: the night over the garden
useFrame((_, delta) => sky.update(delta));                    // twinkling stars, now and then a shooting star
const balloons = animateBalloons(gltf.scene);                 // decor/balloons.ts: the heart balloons float, turn and sway away from her
useFrame(({ camera }, delta) => balloons.update(camera.position, delta));   // a third-person camera: pass her feet instead
await createNeonSign(gltf.scene, { text: "forever us" });     // decor/neonSign.ts: their words in neon (corridor)
const footprints = getFootprints(gltf.scene);                 // decor/footprints.ts: where the furniture stands
const avoid = (x: number, z: number) => isOnFootprint(footprints, x, z);
const petals = [                                              // decor/rosePetals.ts
  createRosePetals(PETAL_PATH, { avoid }),                    // from the entrance to the heart
  createRosePetalHeart(HEART_CENTRE, HEART_WIDTH, { avoid }), // the heart of petals in front of the collage
  createRosePetals(EAST_PATH, { count: 280, roses: 10, seed: 5, avoid }),      // corridor and screen room to the garden door
  createRosePetals(RIGHT_PATH, { count: 100, roses: 4, seed: 9, avoid }),      // into the right gallery
  createRosePetals(DANCE_RING, { count: 140, roses: 6, seed: 11, avoid }),     // round the dance floor
];
scene.add(...petals);
useFrame(({ camera }, delta) => petals.forEach((p) => p.update(camera.position, delta)));   // petals move around her feet
// in your movement code, after moving the camera each frame: nobody walks through furniture (rugs are walkable)
keepOffFootprints(camera.position, 0.3, footprints);

// photos in the single frames (slot_frame_*)
const size = new THREE.Box3().setFromObject(slot).getSize(new THREE.Vector3());          // slot size in metres
const { width, height } = photoSizeForSlot(photo.image.width / photo.image.height, Math.max(size.x, size.y, size.z));
const frame = createPhotoFrame({ photo, width, height, light: slot.userData.light_rgb });  // frames/photoFrame.ts
// the frame faces +Z with its back at z = 0: put it where the slot is, facing out of the wall
if (caption) {                                                // the photo's label, if the gift has a caption for it
  const plaque = await createPhotoPlaque({ title, date, text, light: slot.userData.light_rgb });   // frames/photoPlaque.ts
  plaque.position.y = -(frame.userData.outerSize[1] / 2 + 0.08 + plaque.userData.height / 2);
  frame.add(plaque);
}

// the collage niche: all collage photos, any number. 5.28 m × 3.04 m = the niche opening
const collage = createCollageWall({ photos, width: 5.28, height: 3.04 });                // frames/collageWall.ts
// faces +Z, centred on collage_board. The placeholders (slot_*, collage_board) are hidden by applyBakedLighting.

// the title wall (foyer, straight ahead as she comes in): their names, the date and his words from the gift (note is optional)
await createWelcomeSign(gltf.scene, { names: "Kasun & Nethmi", date: "Since 3 June 2019", note });   // decor/welcomeSign.ts
// at the start of the walk, turn each visitor (spawn_her, spawn_him) to face it, level: it is then centred on a phone too
const titleWall = new THREE.Box3().setFromObject(findProps(gltf.scene, "welcome_board")[0]).getCenter(new THREE.Vector3());
camera.lookAt(titleWall.x, camera.position.y, titleWall.z);

// the cinema screen (screen room): play their video or slideshow on a plane in screen_surface's place (4.8 m × 2.7 m,
// 1.5 cm in front of the white screen), fitted inside it, never stretched or cropped; when nothing plays, the white screen shows

// party balloons on the floors that roll away when she walks into them
const floorBalloons = createFloorBalloons(FLOOR_BALLOON_AREAS, { footprints });   // decor/floorBalloons.ts
scene.add(floorBalloons);
useFrame(({ camera }, delta) => floorBalloons.update(camera.position, delta));

// the projector's beam (screen room): always on, whether the screen shows their photos or a clip
const beam = createProjectorBeam(gltf.scene);                 // lighting/projectorBeam.ts
if (beam) scene.add(beam);

// the quote board (heart room, left of the collage): their quote, names and date from the gift
await createQuoteBoard(gltf.scene, { quote, names: "Kasun & Nethmi", date: "14 February 2021" });   // decor/quoteBoard.ts

// their initials on the foyer's rug, and each chapter's title (his line under it is optional)
await createMonogramRug(gltf.scene, { names: "Kasun & Nethmi" });                // decor/monogramRug.ts
await createChapterBoards(gltf.scene, { story: { line: storyLine }, reasons: { line: reasonsLine } });   // decor/chapterBoards.ts

// the love notes over the right gallery: one card per reason he gave (4 to 10; the gift builder offers some to pick)
scene.add(await createLoveNotes(gltf.scene, reasons));                           // decor/loveNotes.ts

// the gramophone by the dance floor plays their song (or your default track) while they stand on the floor
const gramophone = await createGramophone(gltf.scene, { song: songUrl, title: songTitle });   // decor/gramophone.ts
enterButton.addEventListener("click", () => gramophone.unlock());               // browsers start sound only after a tap
useFrame(({ camera }, delta) => gramophone.update(camera.position, delta));      // and gramophone.dispose() on unmount

// the cinema's "Now Showing" poster: their names and one of their photos (shown whole), once the photos have loaded
await createMoviePoster(gltf.scene, { names: "Kasun & Nethmi", photo });         // decor/moviePoster.ts

const floors: THREE.Mesh[] = [];
gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh && o.name.startsWith("floor_") && o.name !== "floor_6_garden") floors.push(o as THREE.Mesh); });
const reflection = createFloorReflection(gl, scene, floors);  // lighting/floorReflection.ts
useFrame(({ camera }) => reflection.update(camera));          // runs before R3F renders the frame

// the cinema dims while a video plays: after the floor reflection (it replaces the floors' shader patch), before the photos are added
const cinema = createCinemaLights(gltf.scene, ...petals);     // lighting/cinemaLights.ts
useFrame((_, delta) => cinema.update(delta));
video.addEventListener("play", () => cinema.dim(true));
for (const stop of ["pause", "ended"]) video.addEventListener(stop, () => cinema.dim(false));
videoPlane.userData.cinemaScreen = true;                      // the video itself stays bright
```

- `bakedLighting.ts`: walls / floors / ceilings (albedo × lightmap, uv1, intensity × π), mouldings, tray cornices, the niche and the gold lines (vertex colours: lit like the room around them), the furniture, exhibits and decor (vertex colours; velvet (sofas, cushions, the curtains, the cinema's stage) and gold keep their sheen, the balloons their foil shine, the projector and the screen's frame their satin white and black, rugs and marble keep their texture, roses, leaves and curtains show both sides), the foyer's sheers (see-through ivory voile, `sheerMaterial.ts`, drawn after the little lights behind them), the cinema screen (softly lit white), glass (lanterns: it only adds its reflections), spot lenses, niche LEDs and the projector's lens (warm glow), the bulbs of the light strings (bright gold). Hides the neon's words until `createNeonSign` writes them. Removes any exported lights. Logs an error if nothing got light (wrong path).
- `candleFlames.ts`: a small flame on every candle and in every lantern (~60, listed by the model's `candle_flames` marker): upright, always turned towards you, each flickering in its own rhythm, with a soft halo; they show in the floor reflection too. Their warm glow on the floors, walls and furniture is baked. 1 draw call, animated on the GPU.
- `curtainLights.ts`: the curtain of ~1,300 little warm lights hanging behind the foyer's sheers (listed by the model's `fairy_lights` marker): tiny bright points in a small soft glow, no halos, each twinkling softly in its own slow rhythm, seen through the voile. Their warm glow on the wall behind is baked. 1 draw call, animated on the GPU; drawn just before the sheers and before everything else see-through. A second call (`createCurtainLights(scene, { marker: 'garden_lights', ...LIGHTING.gardenLights })`) draws the ~420 little warm lights of the garden's jacaranda, larger (17 cm glow): strings hanging from its branches and five draped to the walls, all above head height (2.3 m) and below the leaves (`garden.py` adds them to `fairy_lights`; their warm glow under the canopy is baked).
- `sheerMaterial.ts` (used by `applyBakedLighting`): the sheers' ivory voile: see-through where it faces you, denser where its folds turn away, so the folds read softly and the little lights and the warm wall behind glow through it. Both sides drawn; drawn just after the little lights.
- `nightSky.ts`: the night over the garden (and through its door): deep blue-black overhead, a soft violet glow and a last rose glow at the horizon, a faint Milky Way, softly twinkling stars, a big soft moon (east-south-east, 26° up, ahead of the daybed; the bake's moonlight comes from the same place: `MOON` in `tools/bake/design.py`) and, now and then (every 10–28 s), a shooting star with a soft glowing tail, crossing the sky ahead of the daybed in about a second and a half. Tuning: `LIGHTING.nightSky` in `config/lighting.ts`. A dome that travels with the camera (keep the camera's far plane above 100 m); call `update(delta)` every frame. 1 draw call.
- `fireflies.ts`: ~45 fireflies over the garden inside its border: soft yellow-green points wandering slowly round their spots, mostly faint and glowing up now and then, each in its own rhythm. Not a light. Tuning: `LIGHTING.fireflies`. 1 draw call, animated on the GPU.
- `foliage.ts` (used by `applyBakedLighting`): leaf cards cut out by their texture's alpha (glTF alpha MASK: the jacaranda's) keep their leaves at a distance: the alpha is raised by how small the texture is drawn, so the averaged far-away mipmaps don't fall below the cut-off (`LIGHTING.foliageMipScale`).
- `campfire/` (`createCampfire` in `campfire.ts`): the fire in the garden's ring of stones, a teepee of logs over kindling (`TEEPEE` in `tools/bake/garden_layout.py`): a bed of coals with glowing cracks that slowly pulse (`coals.ts`), five layered flame sheets that turn to face you (warped-noise tongues, a touch of blue at the foot, a white-yellow heart, orange-red tips) in a soft heat halo (`flames.ts`), the logs and kindling glowing where the fire licks them (their baked material patched: call before `createCinemaLights`), sparks rising and twinkling, soft smoke curling up (`embers.ts`), and a warm glow on the grass that flickers with the flames over its baked light (`FIRE_LIGHT`). Not a light. Tuning: `LIGHTING.campfire`. ~10 draw calls, animated on the GPU.
- `balloons.ts`: every heart balloon floats on its own rhythm: it bobs gently, drifts a little and slowly turns to and fro about its own middle (about every 11 s), so its foil catches the light; its ribbon follows (less towards the knot where it is tied); balloons at the ceiling only bob down from it. Within 0.8 m of the visitor a balloon sways away from her and springs back, its ribbon still tied at the weight: call `update(camera.position, delta)` every frame (one small spring per balloon, 41 in all, passed to the vertex shader). Floating runs on the GPU, no extra draw call.
- `floorBalloons.ts`: round latex party balloons (red, blush, ivory, gold) lying on the floor in loose groups (`FLOOR_BALLOON_AREAS`: each room's floor and where they gather). When she walks into them they roll and bounce away from her feet, harder the faster she walks, knock into each other, bounce off the furniture (`footprints`) and stay inside their room, rolling to a stop in about two seconds. `light` matches them to the rooms' brightness. 1 draw call; `update()` well under 0.1 ms per frame.
- `projectorBeam.ts`: the projector's beam, like in a film hall: a soft cone of warm light from the lens on the ceiling (the `projector_lens` marker) to the corners of `screen_surface`, brightest at the lens, with specks of dust drifting slowly through it. Additive, no real-time light; 2 draw calls, not in the floor reflection. Keep it on in the screen room (`beam.visible = false` hides it); `strength` makes it brighter or softer.
- `neonSign.ts`: their words in pink neon script (Dancing Script) on the corridor's acrylic panel: crisp glass tubes (a white-hot core with a pink rim) in a soft glow close round them, sharp up close and read at an angle; ~22 characters fit on its one line. It switches on with a little flicker the first time she comes within ~8 m (distance only: walls don't count) (`flicker: false`: on from the start); `colour` changes the neon's colour. Its glow on the wall is baked. No extra draw call.
- `cinemaLights.ts`: `createCinemaLights(scene, ...decor)` returns `{ dim(on), update(dt) }`. `dim(true)` fades the screen room's baked materials (MeshBasic and matcap) to about 0.3 over about 1.5 s, `dim(false)` brings them back; call `update(delta)` every frame. Not a light: an `onBeforeCompile` patch with a world-position varying and one shared dim value inside the room's box (three.js x 26.5 to 38, z -13 to -1.5), with a soft edge kept inside the walls. Left bright: ShaderMaterials (the beam, flames, sheers, lamp glare), `poster_face`, `lens_glow` and any mesh with `userData.cinemaScreen` (the video plane). The couple's photos and their frames are never dimmed: they are added after it. Tuning: `LIGHTING.cinema` in `config/lighting.ts`.
- `ceilingLights.ts`: recessed downlights (gold trim, deep reflector, hot lens) over the plain discs in the model, the track lights (`trackLights.ts`) over the plain rails and spot heads, and a soft glare on every lamp that grows when you look into the beam, like real lamps (a track spot only glows when you can see into it). Also glints in the floor reflection. 11 draw calls in total.
- `trackLights.ts` (used by `addCeilingLights`, no extra call): slim satin-black rails with gold end caps and, on them, a designer spot for every photo: black adapter, swivel and U-yoke with gold knobs, a champagne-gold cylinder head with a fine black band and bezel, and the warm lens deep in a gold reflector. Built from the rails and lenses in `museum.glb`, so every spot keeps the aim of its baked light. Instanced: 8 draw calls for all of them.
- `floorReflection.ts`: soft glossy reflections on the wood floor (`strength`, `roughness`). One extra low-resolution render of the (unlit, cheap) scene per frame. Objects with `userData.noReflection = true` are skipped: the petals, the projector's beam, and the fine detail of the furniture and decor (leaves, roses, rugs, glass, bulbs; set in `museum.glb`), which would only blur there.
- `matcaps.ts`: polished gold (lamp trims, spot heads, furniture), satin rose gold (photo frames), satin black (track lights, the projector), velvet (sofas, cushions, roses, curtains), mylar foil (balloons), latex (the floor balloons), a glowing golden bulb (the light strings), clear glass and a soft neutral shading, drawn in code.
- `photoFrame.ts`: slim rose-gold metal frame (flat face, softly rounded edges, 2.5–3.75 cm wide), wide warm-white mat (shown as it is, like the photo, so it stays clean white) with a fine rose-gold bevel, and the soft shadow the frame casts under the ceiling spot. 4 draw calls per frame.
- `collageWall.ts`: a gallery wall like a real home: frames of different sizes fitted together like a puzzle around the middle (no rows or columns, no big holes), the same small gap between neighbouring frames (`gap`, 5 cm), the whole wall centred in the niche with at least `margin` (10 cm) to the edge. Every photo in exactly the same frame as the single photos; no cast shadows in the lit niche. Photos keep their aspect ratio. The same photos always give the same layout (`seed` gives another arrangement). Laid out once when created (well under 0.2 s); 2 draw calls for all frames and mats plus one per photo.
- `photoPlaque.ts`: a museum label for a photo: the title in serif capitals, the date in gold, up to three lines of their story in handwriting, on a cream card with a fine gold edge and a soft shadow, as bright as the light on its wall. Hang it under the frame (see above); make one only where the photo has a caption. 1 draw call (not in the floor reflection).
- `findProps.ts`: `findProps(root, material)` returns the model's furniture meshes of one material (they are merged per material and part of the museum; `userData.prop` is the material).
- `welcomeSign.ts`: the welcome on the foyer's title wall (the `welcome_board` prop, 4.1 m × 2.3 m in a gold frame, straight ahead as she comes in, in its own spotlight): "Welcome to" in small spaced gold capitals, "The Museum of Us" in calligraphy (Great Vibes), their names in calligraphy, a gold rule with a little heart, the date in gold capitals, and `note` (his words, up to ~30 words) in handwriting (Dancing Script) under it; a fine gold double border. Everything sizes itself to fit the board; the writing keeps clear of the roses on two corners. `title` and `line` change "The Museum of Us" and "Welcome to". Replaces the board's material (no extra draw call).
- `quoteBoard.ts`: the couple's quote on the board (the `quote_board` prop): calligraphy (Great Vibes) as large as fits, a fine gold double border, a gold rule with a little heart, the names and the date in spaced capitals (Cormorant Garamond). `"\n"` in the quote starts a new line; up to ~45 words fit nicely. The writing keeps clear of the roses on two corners. Replaces the board's material (no extra draw call).
- `chapterBoards.ts`: each chapter's title on its board (the `chapter_story` and `chapter_reasons` props, 2.1 m × 1.2 m, straight ahead as you come into the story gallery and the right gallery, each in its spotlight): the title in calligraphy (Great Vibes; "How It Began" and "Reasons I Love You" unless you give others; a long title breaks into two lines, "\n" breaks it where you like), a gold rule with a little heart, and `line` (up to ~20 words) in handwriting under it if he wrote one. Replaces the boards' materials (no extra draw call).
- `monogramRug.ts`: their initials woven into the foyer's round ivory rug (the `monogram_rug` prop, 2.6 m across): the two first letters of `names` in gold calligraphy either side of a little red heart, inside a ring of tiny roses and a dusty-rose border with fine gold lines, read from the entrance. Replaces the rug's material (no extra draw call).
- `loveNotes.ts`: one cream card per reason (4 to 10, 36 cm × 50 cm) hanging over the right gallery's open middle on thin red and gold ribbons from the ceiling, above head height (2.2–2.75 m): the reason in handwriting on both sides, a little red heart and its number; each card slowly turns and sways. The model lists where they hang (the `love_notes` marker), in an order that spreads any number of cards over the room. Not baked (`light` matches them to the room); 2 draw calls, animated on the GPU; not in the floor reflection.
- `gramophone.ts`: the gramophone by the dance floor plays `song` (their song, or your default track) and its record turns (grooves, and a wine-red label with `title`): at full volume while the visitor stands on the dance floor (the `dance_floor` marker and its radius), fading in as they step on and out as they step off, softly up to 5 m from it (on iPhones, whose volume can't be faded, only on the floor); `play()` plays it everywhere, `stop()` goes back. Call `unlock()` from a tap (browsers' rule) and `update(camera.position, delta)` every frame. Each visitor hears it on their own device. No extra draw call.
- `moviePoster.ts`: the cinema's "Now Showing" poster, glowing in its lightbox (the `poster_face` prop, 0.9 m × 1.33 m, by the way into the screen room): one of their photos whole (never cropped or stretched, as it is, in a fine gold frame), "A Love Story" in calligraphy, "Starring" their names and a tagline, on deep wine red (`title` and `tagline` change the words). Shown as it is, untouched by tone mapping, like the photos. No extra draw call.
- `lettering.ts`: the paper, gold border, capitals, heart rule, fitting and the board material shared by the title wall, the chapter boards, the rug and the quote board.
- `fonts.ts`: the three fonts for the title wall, the quote board, the neon and the labels, loaded once from `web/public/fonts` (SIL Open Font License: free for commercial use; keep the OFL files next to them).
- `footprints.ts`: `getFootprints(root)` reads the `footprint_*` markers in `museum.glb`: every piece standing on the floor, sized to what stands there up to head height (a tree's lower branches too); round pieces (trees, urns, topiaries, side tables) have a circle, the rest a box turned with the piece; rugs are marked walkable. `keepOffFootprints(position, radius, footprints)` moves the visitor out of the solid ones (call it after your movement each frame; keep your wall collision as it is). `isOnFootprint(footprints, x, z)` keeps the petals off rugs and from under furniture.
- `rosePetals.ts`: `createRosePetals(path)`: petals along a walking route (`[x, z]` floor points, three.js coordinates), ~300 petals + 14 roses for the museum's path; `createRosePetalHeart(centre, width)`: a heart of ~520 petals with 10 roses along its edge (a dense outline, lightly filled), which slowly gathers itself again once she steps more than 2 m away. Options: `count`, `roses`, `seed`, `avoid` (floor spots to keep clear). `update()` each frame: petals within ~45 cm of the visitor's feet are swept aside, hop a few centimetres, spin and settle flat again; roses roll a little. Only nearby petals move (well under 0.1 ms per frame for all three sets), and none drift more than 80 cm from where they were laid.

## Furniture, exhibits and decor

They are part of `museum.glb`, modelled in `tools/bake/props.py` and baked with the room, so they cast soft shadows on the floor and are lit like it; the candles, lanterns and the neon also glow on the floors and walls around them. They are merged into one mesh per material in each part of the museum (`prop_<zone>_<material>`, zones: `foyer`, `story`, `heart`, `heartsouth`, `screen` (with the corridor), `right`, `garden`), so the parts you can't see are culled; `userData.prop` is the material (`findProps`). Each piece has an empty `footprint_<name>` marking where it stands (used by `footprints.ts`), the `candle_flames` empty lists every flame (used by `candleFlames.ts`), `fairy_lights` every little light behind the sheers (`curtainLights.ts`), `projector_lens` marks where the beam starts (`projectorBeam.ts`) and `dimmer_switch` the dimmer by the heart room's door (its middle, and `userData.aim`: the way it faces; for a later feature). Where they stand (Blender x, y; three.js x = x, z = −y):

| Piece | What | Room | Where |
|---|---|---|---|
| `welcome` | title wall (the welcome), in its spotlight | foyer | (4.45, 9.875) |
| `topiary_foyer_w` | rose topiary | foyer | (1.95, 9.35) |
| `topiary_foyer_e` | rose topiary | foyer | (6.95, 9.35) |
| `balloons_foyer_w` | heart balloons on a gold weight | foyer | (1.9, 8.55) |
| `balloons_foyer_e` | heart balloons on a gold weight | foyer | (7.0, 8.55) |
| `rug_foyer` | round rug with their initials | foyer | (4.45, 5.6) |
| `sheers_foyer_w` | ivory sheers, little lights behind them | foyer | (0.2, 9.6) |
| `sheers_foyer_e` | ivory sheers, little lights behind them | foyer | (10.875, 1.85) |
| `curtain_foyer_w` | velvet curtain, tied back | foyer | (9.16, 9.875) |
| `curtain_foyer_e` | velvet curtain, tied back | foyer | (9.16, 9.875) |
| `pelmet_foyer` | curtain pelmet | foyer | (9.135, 9.875) |
| `ficus_foyer_sw` | weeping fig | foyer | (1.35, 1.15) |
| `urn_foyer_w` | urn of roses on a pedestal | foyer | (0.72, 3.0) |
| `urn_foyer_e` | urn of roses on a pedestal | foyer | (10.35, 3.0) |
| `olive_foyer` | olive tree | foyer | (0.95, 9.1) |
| `fig_foyer` | fig tree | foyer | (10.1, 0.95) |
| `topiary_story_e` | rose topiary | story gallery | (10.45, 14.5) |
| `topiary_story_sw` | rose topiary | story gallery | (0.75, 10.75) |
| `console_story_1` | console with roses and candles | story gallery | (0.39, 13.85) |
| `console_story_2` | console with roses and candles | story gallery | (0.39, 17.15) |
| `ficus_story_nw` | weeping fig | story gallery | (1.0, 20.0) |
| `stand_story_ne` | flower stand | story gallery | (10.25, 20.2) |
| `chapter_story` | chapter board (chapter_story), in its spotlight | story gallery | (8.7, 20.8) |
| `balloons_story` | heart balloons on a gold weight | story gallery | (7.05, 20.2) |
| `sofa_heart` | sofa | heart room | (17.0, 14.3) |
| `rug_heart` | rug | heart room | (17.0, 15.55) |
| `coffee_table_heart` | coffee table | heart room | (17.0, 15.75) |
| `side_table_heart_w` | side table | heart room | (15.5, 14.35) |
| `side_table_heart_e` | side table | heart room | (18.5, 14.35) |
| `balloons_sofa` | balloons | heart room | (18.5, 14.35) |
| `balloons_sofa_w` | balloons | heart room | (15.5, 14.35) |
| `quote_board` | quote board on its easel | heart room | (13.35, 18.65) |
| `roses` | grand roses | heart room | (20.6, 18.55) |
| `ropes_roses` | velvet ropes | heart room | (20.6, 18.55) |
| `garland` | rose garland round the collage | heart room | (17.0, 20.63) |
| `fig_heart_w` | fig tree | heart room | (11.75, 14.3) |
| `fig_heart_e` | fig tree | heart room | (22.25, 14.3) |
| `palm_heart_w` | kentia palm | heart room | (12.05, 9.3) |
| `palm_heart_e` | kentia palm | heart room | (21.95, 9.3) |
| `lights_heart_ws` | string of golden bulbs | heart room | (11.15, 10.0) |
| `lights_heart_wn` | string of golden bulbs | heart room | (11.15, 20.4) |
| `lights_heart_es` | string of golden bulbs | heart room | (22.84, 2.0) |
| `lights_heart_en` | string of golden bulbs | heart room | (22.84, 14.4) |
| `lights_heart_s` | string of golden bulbs | heart room | (11.6, 1.73) |
| `dimmer_heart` | gold dimmer switch (marker `dimmer_switch`) | heart room | (11.125, 13.7) |
| `dance_floor` | dance floor in a pool of light (marker `dance_floor`) | heart room | (17.0, 6.2) |
| `gramophone` | gramophone on a plinth (marker `gramophone`) | heart room | (19.05, 6.2) |
| `balloons_dance` | heart balloons on a gold weight | heart room | (14.95, 6.2) |
| `topiary_heart_sw` | rose topiary | heart room | (15.4, 2.25) |
| `topiary_heart_se` | rose topiary | heart room | (18.6, 2.25) |
| `olive_heart_sw` | olive tree | heart room | (11.9, 2.4) |
| `olive_heart_se` | olive tree | heart room | (22.1, 2.4) |
| `console_corridor` | console with roses and candles | corridor | (24.75, 1.92) |
| `neon` | neon sign | corridor | (24.75, 1.73) |
| `lantern_corridor_w` | lantern | corridor | (23.9, 2.0) |
| `lantern_corridor_e` | lantern | corridor | (25.6, 2.0) |
| `chapter_reasons` | chapter board (chapter_reasons), in its spotlight | right gallery | (26.5, 20.8) |
| `balloons_reasons` | heart balloons on a gold weight | right gallery | (28.3, 20.25) |
| `love_notes` | where the love notes hang (marker `love_notes`) | right gallery | (30.4, 17.0) |
| `palm_right` | kentia palm | right gallery | (24.15, 17.2) |
| `stand_right_1` | flower stand | right gallery | (23.55, 15.9) |
| `stand_right_2` | flower stand | right gallery | (23.55, 18.5) |
| `olive_right_nw` | olive tree | right gallery | (23.95, 20.05) |
| `olive_right_ne` | olive tree | right gallery | (36.95, 20.0) |
| `fig_right_se` | fig tree | right gallery | (37.05, 13.95) |
| `stand_right_e1` | flower stand | right gallery | (37.2, 15.55) |
| `stand_right_e2` | flower stand | right gallery | (37.2, 18.45) |
| `loveseat_screen` | loveseat | screen room | (32.25, 7.11) |
| `rug_screen` | rug | screen room | (32.25, 8.0) |
| `side_table_screen_w` | side table with popcorn | screen room | (31.12, 7.15) |
| `side_table_screen_e` | side table with drinks | screen room | (33.38, 7.15) |
| `poster` | "Now Showing" poster in a lightbox | screen room | (28.2, 1.7) |
| `balloons_loveseat` | balloons | screen room | (33.0, 7.11) |
| `projector` | ceiling projector | screen room | (32.25, 5.0) |
| `curtain_s` | velvet curtain, tied back | screen room | (37.77, 6.475) |
| `curtain_n` | velvet curtain, tied back | screen room | (37.77, 6.475) |
| `pelmet` | curtain pelmet | screen room | (37.77, 6.475) |
| `screen` | cinema screen in its frame, on a little stage | screen room | (32.25, 12.875) |
| `curtain_screen_w` | velvet curtain, tied back | screen room | (32.25, 12.875) |
| `curtain_screen_e` | velvet curtain, tied back | screen room | (32.25, 12.875) |
| `pelmet_screen` | curtain pelmet | screen room | (32.25, 12.875) |
| `olive_screen_s` | olive tree | screen room | (37.15, 2.15) |
| `olive_screen_n` | olive tree | screen room | (37.15, 12.35) |
| `topiary_screen_w` | rose topiary | screen room | (28.3, 12.3) |
| `topiary_screen_e` | rose topiary | screen room | (36.2, 12.3) |
| `candles_heart_*` | 13 × candles | heart room | round the petal heart |

The petal paths and the heart (three.js `[x, z]`), clear of every piece: from the entrance across the foyer, through the story gallery and into the heart room up to the tip of the petal heart (its candles leave a gap there to step in); the heart in front of the collage; from the heart room through the corridor and the screen room to the garden door; from the corridor into the right gallery; a ring round the dance floor; in the garden from the door through the arch to the bench.

```ts
const PETAL_PATH: [number, number][] = [[5.5, -1.5], [5.5, -3.2], [6.7, -3.6], [7.6, -5.6], [8.6, -7.7], [9.3, -9.4], [9.4, -10.6],
  [8.3, -12.6], [7.6, -16.4], [6.6, -18.6], [5.0, -18.9], [3.9, -17.6], [3.9, -15.3], [4.0, -12.6], [6.2, -11.4], [9.4, -11.6],
  [11.0, -12.0], [12.6, -12.2], [14.2, -13.0], [14.35, -15.2], [14.6, -16.9], [15.8, -17.3], [17.0, -17.3]];
const HEART_CENTRE: [number, number] = [17.0, -18.6], HEART_WIDTH = 1.9;          // props.py HEART_AT, HEART_WIDTH
const EAST_PATH: [number, number][] = [[18.2, -12.0], [20.5, -12.3], [22.6, -12.3], [24.4, -12.1], [24.8, -10.2], [24.8, -7.6], [24.8, -5.2],
  [25.3, -3.5], [27.0, -3.1], [29.0, -3.5], [30.9, -4.4], [33.2, -4.9], [35.3, -5.6], [36.9, -6.3], [37.9, -6.5]];
const RIGHT_PATH: [number, number][] = [[24.8, -13.2], [26.1, -14.5], [28.0, -15.5], [30.4, -16.3]];
const DANCE_RING: [number, number][] = Array.from({ length: 25 }, (_, i) =>     // a ring just outside the dance floor's edge
  [17.0 + 1.55 * Math.cos((i / 24) * Math.PI * 2), -6.2 + 1.55 * Math.sin((i / 24) * Math.PI * 2)]);
const FLOOR_BALLOON_AREAS: FloorBalloonArea[] = [       // each room's floor (x0, z0, x1, z1) and where the balloons gather
  { rect: [11.4, -20.6, 22.6, -1.9], count: 8, groups: [[13.4, -12.8], [19.8, -4.6]] },         // heart room
  { rect: [23.4, -20.6, 37.6, -13.5], count: 6, groups: [[27.2, -15.4], [34.2, -15.8]] },       // right gallery
];
```

## Performance (measured)

Busiest views (1280 × 720, floor reflection pass included): from the foyer through the door into the story gallery ~470 draw calls / ~1.15M triangles (most of them the photo frames beyond the door), the heart room seen across its corner ~395 / ~1.02M, the foyer ~350 / ~890k, the dance floor ~330 / ~900k, the garden ~105 / ~590k. Phone portrait views: 60–210 draw calls, 380k–760k triangles. Most draw calls are the photo frames (4 each, plus 1 for a label); the furniture and decor are one mesh per material in each part of the museum (out-of-sight parts are culled) and their fine detail (leaves, roses, rugs, glass, the sheers, the love notes) stays out of the reflection pass. The candle flames, the little lights behind the sheers, the love notes, balloons, neon, projector beam and sky animate on the GPU and everything is unlit (baked / matcap), so phones stay cool. `museum.glb` is 9.7 MB (meshopt). If a phone struggles: `createFloorReflection(..., { resolution: 0.25 })` first, then `dpr={[1, 1.5]}`.

## What the gift asks for

The gift builder only needs three things; everything else is optional and has a default, so every couple's museum is complete:

- **Required:** both names, the date they met, and at least 25 photos (with fewer, repeat favourites rather than leave a frame empty).
- **Optional:** his note (title wall), a quote (quote board), photo captions (labels), a line for each chapter (`storyLine`, `reasonsLine`; none: just the title), 4 to 10 reasons (offer ready ones to tick and let him write his own; none: no notes), their song and its title (none: your default romantic track), the neon's words (default "forever us"), the poster's photo (default: their first photo), video clips (none: a slideshow of their photos).
- All default words say "you" and "us", so they fit any couple.

## Remove from earlier versions

- v17's photo places `slot_frame_12` (story gallery) and `slot_frame_27` (right gallery) are gone: the chapter boards hang there. If your app hands photos to slots by name, give those two photos to the collage. The balloons that were at the ceilings (story gallery, heart room, right gallery) now float at eye level, part of `museum.glb` (nothing to change).

- v16's welcome easel, the foyer's console and the foyer's three photo slots (`slot_frame_01`–`03`, with their spots) are gone: the title wall, the sheers and the velvet curtains at the door take their places, and `welcomeSign.ts` now writes the title wall. If your app hands photos to slots by name, give those three photos to the collage (or the next free slots). The foyer has no floor balloons any more: use the `FLOOR_BALLOON_AREAS` above (heart room and right gallery).
- v16's moon gate and the two urns beside it in the right gallery are gone (its middle is left open); the `RIGHT_PATH` petals still lead in.

- v15's presents in the foyer, the table for two and the light strings outside the heart room are gone, and so is `web/src/lighting/bulbLights.ts`: remove the `createBulbLights` call (the bulbs glow bright gold by themselves now, without halos) and the `HEART_SOUTH_PATH` petals.
- v14's cherry blossom trees and heart of roses with its two flower stands are gone (kentia palms, weeping figs and the table for two take their places), and so are the `blossom_pink` and `blossom_white` materials and the blossom texture.
- v13's LOVE letters, the gallery bench, the rose-gold heart sculpture and its velvet ropes are gone, and so is the `rose_gold` material. The projector's beam is on all the time now: drop any `clipPlaying` switching of `beam.visible`.
- v13's darker ceilings were a missing part of the bake; v14 has the v12 ceilings back.
- `web/src/decor/loveLetter.ts`, the `createLoveLetter` call and its `letter.update` (the lectern and its book are gone; the title wall greets her now). The vitrines, the gramophone and the lanterns in the middle of the foyer, the story gallery and along the heart room's south wall are gone too: remove any code that looked for `letter_pages`, `leather_wine`, `paper_ivory`, the gramophone or the vitrines.
- v12's footprints stood in the wrong places (the invisible blocks, e.g. by the foyer's door, and pieces you could walk through): the new `museum.glb` puts each one exactly under its piece. Keep calling `keepOffFootprints` every frame after your movement; it now also handles the round footprints.
- The bookcases, round rugs, centre tables and books are gone from `museum.glb` (a museum, not a house); the prop meshes are now merged per part of the museum (`prop_<zone>_<material>`, e.g. `prop_heart_quote_board`). Never look a prop up by its mesh name: use `findProps(root, "quote_board")` (the title wall and the quote board already do). Any code that looked for `prop_letter_pages`, `prop_quote_board`, `prop_bench_*`, `prop_lectern_*` or `prop_rose_exhibit_*` by name can go.
- The petal path now ends at the tip of the petal heart (`[17.0, -17.3]`), not in the middle of it: use the `PETAL_PATH` above.
- `createRosePetals(path, count, roses, seed)` takes an options object: `createRosePetals(path, { count, roses, seed, avoid })`.
- `createPhotoFrame`'s `pictureLight` option is gone (no picture lights anywhere): remove it from every call.
- `createCollageWall`: use the niche opening size above (`width: 5.28, height: 3.04`), not the old 4.9 × 2.9.
- The old `web/src/decor/fairyLights.ts`, `web/src/lighting/moods.ts`, `web/src/lighting/lightGlows.ts`, `web/src/lighting/goldMatcap.ts` (now `matcaps.ts`), `web/public/models/fairy_lights.json`, `web/public/models/moods.json`, and every use of them.
- In `tools/bake/`: `design_v20.py`, `grade_textures_v20.py`, `regrade_light.py` (replaced by `design.py`, `grade_textures.py`, `floor_tone.py`).
