# Look and lighting — final gallery

Target: the owner's final reference video (`design/reference-final/*.png`, frames from it), lit like a real gallery at night:

- warm cream-beige plain walls, tall cream skirting, thin gold panel lines on the gallery walls
- cream tray ceilings with a small cornice and gold lines, a few recessed downlights
- black track rails with white spot heads: every photo sits in its own soft pool of light, brightest just above the frame
- every photo in a slim modern rose-gold frame with a wide warm-white mat and a fine rose-gold bevel (fresh and romantic, not antique); the frame casts a soft shadow on the wall below it (no picture-light bars)
- the heart room's back wall: a softly backlit niche (its back wall the same warm beige as the walls) with the collage: a centred mosaic of mixed sizes in exactly the same frames, equal gaps everywhere
- glossy dark walnut-cherry floor with soft reflections of the lights; red and blush-pink rose petals and a few roses along the path that scatter when you walk through them
- no plants (the owner will add real assets later), no fairy lights, no sconces, no picture lights

**The web must look like `design/web-reference/*.png`.** Those screenshots were rendered in a real browser (three.js r170) with the drop-in code below.

## The museum file

`web/public/models/museum.glb` and `web/public/models/lightmaps/` are shipped **ready-made and browser-tested**. Do not re-export from Blender unless the model changes.

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
addCeilingLights(gltf.scene);                                 // lighting/ceilingLights.ts
const petals = createRosePetals(path);                        // decor/rosePetals.ts
scene.add(petals);
useFrame(({ camera }, delta) => petals.update(camera.position, delta));   // petals move around the visitor's feet

// photos in the single frames (slot_frame_*)
const size = new THREE.Box3().setFromObject(slot).getSize(new THREE.Vector3());          // slot size in metres
const { width, height } = photoSizeForSlot(photo.image.width / photo.image.height, Math.max(size.x, size.y, size.z));
const frame = createPhotoFrame({ photo, width, height, light: slot.userData.light_rgb });  // frames/photoFrame.ts
// the frame faces +Z with its back at z = 0: put it where the slot is, facing out of the wall

// the collage niche: all collage photos, any number. 5.28 m × 3.04 m = the niche opening
const collage = createCollageWall({ photos, width: 5.28, height: 3.04 });                // frames/collageWall.ts
// faces +Z, centred on collage_board. The placeholders (slot_*, collage_board) are hidden by applyBakedLighting.

const floors: THREE.Mesh[] = [];
gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh && o.name.startsWith("floor_") && o.name !== "floor_6_garden") floors.push(o as THREE.Mesh); });
const reflection = createFloorReflection(gl, scene, floors);  // lighting/floorReflection.ts
useFrame(({ camera }) => reflection.update(camera));          // runs before R3F renders the frame
```

- `bakedLighting.ts`: walls / floors / ceilings (albedo × lightmap, uv1, intensity × π), mouldings, tray cornices, the niche and the gold lines (vertex colours: lit like the room around them), spot lenses and niche LEDs (warm glow), track lights (shaded in their colour). Removes any exported lights. Logs an error if nothing got light (wrong path).
- `ceilingLights.ts`: recessed downlights (gold trim, deep reflector, hot lens) over the plain discs in the model, and a soft glare on every downlight and spot lens that grows when you look into the beam, like real lamps. Also glints in the floor reflection. 3 draw calls in total.
- `floorReflection.ts`: soft glossy reflections on the wood floor (`strength`, `roughness`). One extra low-resolution render of the (unlit, cheap) scene per frame. Objects with `userData.noReflection = true` are skipped (petals).
- `matcaps.ts`: polished gold (lamp trims), satin rose gold (photo frames) and a soft neutral shading, drawn in code.
- `photoFrame.ts`: slim rose-gold metal frame (flat face, softly rounded edges, 2.5–3.75 cm wide), wide warm-white mat (shown as it is, like the photo, so it stays clean white) with a fine rose-gold bevel, and the soft shadow the frame casts under the ceiling spot. 4 draw calls per frame.
- `collageWall.ts`: mosaic of mixed sizes, every photo in exactly the same frame as the single photos (a little slimmer, as they are smaller): the same gap between every two frames (`gap`, 5 cm), the same margin to the niche on all four sides (`margin`, ~10 cm), centred, the largest photo near the middle. Photos keep their aspect ratio. The same photos always give the same layout (`seed` gives another arrangement). Laid out once when it is created (well under 0.1 s); no cast shadows in the lit niche, so the gaps show the clean warm wall; 2 draw calls for all frames and mats plus one per photo.
- `rosePetals.ts`: `path` = floor points along the walking route (`[x, z]`, three.js coordinates). ~300 petals + 14 roses for the whole museum. `update()` each frame: petals within ~45 cm of the visitor's feet are swept aside, hop a few centimetres, spin and settle flat again; roses roll a little. Only nearby petals move (~0.03 ms per frame), and none drift more than 80 cm from where they were laid.

## Performance (measured)

Busiest view: ~130 draw calls and ~120k triangles including the reflection pass (phone portrait views: 45–60 draw calls). Everything is unlit (baked / matcap), so phones stay cool. If a phone struggles: `createFloorReflection(..., { resolution: 0.25 })` first, then `dpr={[1, 1.5]}`.

## Remove from earlier versions

- `createPhotoFrame`'s `pictureLight` option is gone (no picture lights anywhere): remove it from every call.
- `createCollageWall`: use the niche opening size above (`width: 5.28, height: 3.04`), not the old 4.9 × 2.9.
- `web/src/decor/fairyLights.ts`, `web/src/lighting/moods.ts`, `web/src/lighting/lightGlows.ts`, `web/src/lighting/goldMatcap.ts` (now `matcaps.ts`), `web/public/models/fairy_lights.json`, `web/public/models/moods.json`, and every use of them.
- In `tools/bake/`: `design_v20.py`, `grade_textures_v20.py`, `regrade_light.py` (replaced by `design.py`, `grade_textures.py`, `floor_tone.py`).
