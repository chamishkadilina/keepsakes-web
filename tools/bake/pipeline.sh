#!/bin/bash
# Rebuilds the museum look and its baked lighting. Run from the repo root.
#   tools/bake/pipeline.sh <blender-python> [samples=320] [scale=1.0]
# <blender-python>: a Python with the `bpy` 5.2 module (pip install bpy) + numpy scipy pillow.
# Input:  assets-src/blender/museum_base.blend (the owner's approved layout, before the look is applied)
# Output: assets-src/blender/museum.blend, web/public/models/museum.glb, web/public/models/lightmaps/
set -e
PY="$1 -I -u"; N=${2:-320}; R=${3:-1.0}
T=tools/bake; A=assets-src/blender; WORK=$(mktemp -d)
ln -s "$PWD/$A/textures" "$WORK/textures"
$PY $T/design.py $A/museum_base.blend $WORK/uv.blend
$PY $T/bake_lightmaps.py $WORK/uv.blend $WORK $N $R walls,floors,ceilings,garden_walls
$PY $T/finish_lightmaps.py $WORK/uv.blend $WORK $WORK/out $WORK/final.blend
$PY $T/bake_trim_vertex.py $WORK/final.blend $WORK/out/lightmaps/lightmaps.json $N
$PY $T/smooth_trim_light.py $WORK/final.blend 6
cp $WORK/final.blend $A/museum.blend
$PY $T/export_glb.py $A/museum.blend web/public/models/museum.glb
rm -rf web/public/models/lightmaps && cp -r $WORK/out/lightmaps web/public/models/lightmaps
echo "done: museum.blend, museum.glb, lightmaps"
