# Lighting bake (helper scripts)

Mechanical tools that turn the lights in `museum.blend` into web lightmaps. They never change the design.

`romantic.py in.blend out.blend 50 160` sets the romantic palette and light levels (ambient W, spot W).

Run order (Blender 5.2 Python + numpy, scipy, pillow):
1. `lightmap_uvs.py in.blend uv.blend`: second UV map "lightmap" for walls, floors, ceilings, garden walls, trim
2. `fix_trim_uv.py uv.blend uv2.blend`: splits skirting/jambs so their lightmap islands are not too thin
3. `bake_lightmaps.py uv2.blend lm/ 192`: Cycles bake → `lm/lm_<group>.exr`
4. `finish_lightmaps.py uv2.blend lm/ web/public/models out.blend`: denoise, encode PNGs + `lightmaps.json`, store `light_rgb` on every slot
5. `check_lightmaps.py out.blend web/public/models/lightmaps design/lighting-reference`: renders with lightmaps only (how the web should look)

Re-bake after any change to walls, lights or static assets.
