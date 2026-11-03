"""Re-UV only the trim group (skirting, door jambs): cut long strips into <= 2.5 m pieces so
their lightmap islands are not paper-thin. Other groups' UVs are untouched."""
import bpy, bmesh, sys, math
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
objs = [bpy.data.objects[n] for n in ("skirting", "door_jambs", "chair_rail", "crown_moulding", "boiserie") if n in bpy.data.objects]
for o in objs:
    bm = bmesh.new(); bm.from_mesh(o.data)
    for axis in (0, 1):
        for k in range(1, 22):
            co = [0, 0, 0]; co[axis] = k * 2.5
            no = [0, 0, 0]; no[axis] = 1
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co, plane_no=no)
    if o.name == "boiserie":   # short strips already: skip vertical cuts
        bm.to_mesh(o.data); bm.free(); continue
    for k in (1.0, 2.0, 3.0):   # jambs are 4 m tall
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, k), plane_no=(0, 0, 1))
    bm.to_mesh(o.data); bm.free()
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True); o.data.uv_layers.active = o.data.uv_layers["lightmap"]
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
# many small faces: Blender's lightmap packer keeps every face usable (smart project + pack collapsed them)
bpy.ops.uv.lightmap_pack(PREF_CONTEXT="ALL_FACES", PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_BOX_DIV=48, PREF_MARGIN_DIV=0.2)
bpy.ops.object.mode_set(mode="OBJECT")
# make sure every island sits inside the 0..1 square (packing can spill over with many islands)
import numpy as np
allp = np.concatenate([np.array([d.uv[:] for d in o.data.uv_layers["lightmap"].data]) for o in objs])
lo, hi = allp.min(0), allp.max(0); k = 0.996 / max(hi - lo)
for o in objs:
    for d in o.data.uv_layers["lightmap"].data:
        d.uv = ((d.uv[0] - lo[0]) * k + 0.002, (d.uv[1] - lo[1]) * k + 0.002)
print("trim uv span before", (hi - lo).round(3))
for o in objs:
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
bpy.ops.wm.save_as_mainfile(filepath=sys.argv[2], compress=True)
print("trim faces", [len(o.data.polygons) for o in objs])
