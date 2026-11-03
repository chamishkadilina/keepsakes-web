import bpy, sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
bpy.ops.export_scene.gltf(filepath=sys.argv[2], export_format="GLB", use_visible=False, export_extras=True,
    export_lights=False, export_cameras=False, export_yup=True, export_apply=True, export_vertex_color="ACTIVE",
    export_all_vertex_colors=False, export_animations=False, export_draco_mesh_compression_enable=False)
print("exported")
