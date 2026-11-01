"""Read-only: lists slot objects in museum.blend with size and custom properties.

Run: Blender --background assets-src/blender/museum.blend --python tools/report_slots.py
"""
import bpy

PREFIXES = ("slot_", "collage_board", "screen_surface", "seat_")

for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if not obj.name.startswith(PREFIXES):
        continue
    props = {k: obj[k] for k in obj.keys() if not k.startswith("_")}
    size = tuple(round(v, 3) for v in obj.dimensions)
    print(f"{obj.name:20} {obj.type:6} size={size} props={props}")
