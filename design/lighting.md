# Lighting — baked, identical on every device

Mood: **bright and romantic.** Blush-ivory walls, warm cream ceilings, honey wood, soft rosy fill light, warm-white spotlights that make each photo the focal point, and a pink-violet twilight sky over the garden.

All museum light is calculated once in Blender (Cycles) and stored in **lightmaps**. The web draws that stored light; it never calculates lights.

Result: the same look on phone, tablet and desktop; no lag, no heat.

## Rules (do not break)

1. **No real-time lights** in the web: no SpotLight, PointLight, DirectionalLight, HemisphereLight, no shadows. Lights exported in museum.glb (if any) are removed on load.
2. **Identical everywhere.** No quality tiers that change lights, materials or effects. The only thing allowed to adapt is render resolution (pixel ratio), to keep the frame rate.
3. Tone mapping: `AgXToneMapping`, exposure 1.0, output sRGB. Compare against `design/lighting-reference/baked-*.png` (those images were rendered from the lightmaps only, exactly as the web should draw them).

## Files

- `web/public/models/museum.glb`: static meshes have **two UV sets**. `TEXCOORD_0` is for surface textures (1 unit = 1 m) and `TEXCOORD_1` is the lightmap UV.
- Each static mesh has the extra (custom property) `lightmap_group`: `walls`, `floors`, `ceilings`, `garden_walls` or `trim`.
- `web/public/models/lightmaps/lm_<group>.png`: one lightmap per group (sRGB, 8-bit).
- `web/public/models/lightmaps/lightmaps.json`:
  ```json
  { "intensity": 0.29, "maps": { "walls": { "file": "lm_walls.png", "objects": ["walls"] }, ... } }
  ```

## How to draw a static mesh

```
final colour = albedo × lightmap_linear × intensity
```

- Material: `MeshBasicMaterial` (cheapest, no light maths).
  - `color` / `map` = the glTF base colour / base colour texture (albedo).
  - `lightMap` = lm_<group>.png with `colorSpace = SRGBColorSpace`, `flipY = false`, `channel = 1` (TEXCOORD_1).
  - `lightMapIntensity` = `intensity`. Check how your three.js version's MeshBasicMaterial applies the lightmap: if it multiplies by `RECIPROCAL_PI`, use `intensity × Math.PI`.
- Lightmap textures: linear filtering, mipmaps on, anisotropy 4.
- Emissive meshes (`ceiling_light_glow`): `MeshBasicMaterial` with the emissive colour.

## Photos and frames (built in code)

**The couple's photos are never changed.** Every photo is shown exactly as uploaded: same colours, brightness and contrast, in every room and on every device.

- Photo: `MeshBasicMaterial`, `map` = photo (`colorSpace = SRGBColorSpace`), `color` = white, **`toneMapped = false`**, no fog, no post-processing on it, no light tint. This keeps the pixels 1:1 with the original file.
- Photo texture quality: mipmaps on, anisotropy 8, never compressed below the uploaded quality.

Every slot in the glb has the extra `light_rgb` = the light (linear RGB) falling on that spot of the wall. It is used **only for the frame around the photo**, so frames sit naturally in the room:

- Mat (white border): `MeshBasicMaterial`, colour white × `light_rgb`.
- Gold moulding: `MeshMatcapMaterial` with a warm gold matcap generated in code (canvas gradient, no downloaded file), `color` = `light_rgb` normalised so the brightest slot = 1. It looks metallic with no lights.
- The collage board's frame and backing use the same `light_rgb` rule; the collage photos follow the photo rule (exact colours).
- Screen slideshow: the same photo rule (exact colours, `toneMapped = false`).

## Characters

Sample the floor lightmap under the player's feet (read `lm_floors.png` once into an ImageData, look up the TEXCOORD_1 of the floor point under the player) and tint the character's `MeshBasicMaterial`/matcap with it, smoothed over ~0.3 s. Walking from a dark doorway into a lit room then feels natural.

## Changing the lighting

Only in Blender: change the lights in the `lights` collection, then re-bake. The bake scripts write new lightmaps and `light_rgb` values; the web picks them up with no code change.
