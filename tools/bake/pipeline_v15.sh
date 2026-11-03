#!/bin/bash
set -e
PY="/tmp/claude-0/-home-claude/dafdcac3-3e14-5613-9f35-9d766d9c05cb/scratchpad/bpyenv/bin/python -I -u"; SC=/tmp/claude-0/-home-claude/dafdcac3-3e14-5613-9f35-9d766d9c05cb/scratchpad/scripts; V=/tmp/claude-0/-home-claude/dafdcac3-3e14-5613-9f35-9d766d9c05cb/scratchpad/v15
cd /tmp

$PY $SC/bake_lightmaps.py $V/uv2.blend $V/lm 160 1.0 walls,floors,ceilings,garden_walls 2>&1 | grep -E "baked|done|rror"
$PY $SC/finish_lightmaps.py $V/uv2.blend $V/lm $V/out $V/final.blend 2>&1 | grep -E "intensity|rror"
$PY $SC/bake_trim_vertex.py $V/final.blend $V/out/lightmaps/lightmaps.json 160 2>&1 | grep -E "saved|rror"
$PY $SC/smooth_trim_light.py $V/final.blend 6 2>&1 | grep -E "saved|rror"
$PY $SC/regrade_light.py $V/out/lightmaps $V/final.blend 1.7 ceilings=0.372 2>&1 | grep -E "intensity|rror"
$PY $SC/set_ceiling_colour.py $V/final.blend 2>&1 | grep -E "ceiling material|rror"
$PY $SC/export_glb.py $V/final.blend $V/museum.glb 2>&1 | grep -E "exported|rror"
echo PIPELINE_DONE
