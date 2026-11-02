"""Re-UV only the trim group (skirting, door jambs): cut long strips into <= 2.5 m pieces so
their lightmap islands are not paper-thin. Other groups' UVs are untouched."""
import bpy, bmesh, sys, math
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
objs = [bpy.data.objects[n] for n in ("skirting", "door_jambs")]
for o in objs:
    bm = bmesh.new(); bm.from_mesh(o.data)
    for axis in (0, 1):
        for k in range(1, 22):
            co = [0, 0, 0]; co[axis] = k * 2.5
            no = [0, 0, 0]; no[axis] = 1
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co, plane_no=no)
    for k in (1.0, 2.0, 3.0):   # jambs are 4 m tall
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, k), plane_no=(0, 0, 1))
    bm.to_mesh(o.data); bm.free()
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True); o.data.uv_layers.active = o.data.uv_layers["lightmap"]
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.uv.select_all(action="SELECT")
bpy.ops.uv.pack_islands(rotate=True, margin_method="FRACTION", margin=0.006, shape_method="AABB")
bpy.ops.object.mode_set(mode="OBJECT")
for o in objs:
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
bpy.ops.wm.save_as_mainfile(filepath=sys.argv[2], compress=True)
print("trim faces", [len(o.data.polygons) for o in objs])
