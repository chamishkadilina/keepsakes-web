"""Smooths baked vertex light on trim: averages corners that share a position and facing direction,
then blurs across neighbouring faces that face the same way (hard edges between moulding faces stay).
Usage: python smooth_trim_light.py <final.blend> [iterations]"""
import bpy, sys
import numpy as np
path = sys.argv[1]; iters = int(sys.argv[2]) if len(sys.argv) > 2 else 6
bpy.ops.wm.open_mainfile(filepath=path)
for o in [o for o in bpy.data.objects if o.get("light_vertex")]:
    me = o.data; attr = me.color_attributes["light"].data
    col = np.empty(len(attr) * 4, np.float32); attr.foreach_get("color", col); col = col.reshape(-1, 4)
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", lv)
    fn = np.empty(len(me.polygons) * 3, np.float32); me.polygons.foreach_get("normal", fn); fn = fn.reshape(-1, 3)
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get("loop_start", ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get("loop_total", lt)
    face_of_loop = np.repeat(np.arange(len(me.polygons)), lt)
    nq = np.round(fn[face_of_loop] * 4).astype(np.int32)                 # facing direction, quantised
    pq = np.round(co[lv] * 500).astype(np.int64)                          # position, 2 mm grid
    keys = np.concatenate([pq, nq], axis=1)
    _, key_id = np.unique(keys, axis=0, return_inverse=True); key_id = key_id.ravel()
    c = col[:, :3].astype(np.float64)
    nk = key_id.max() + 1
    for _ in range(iters):
        ksum = np.zeros((nk, 3)); np.add.at(ksum, key_id, c)
        kcnt = np.bincount(key_id, minlength=nk)[:, None]
        c = (ksum / kcnt)[key_id]                                          # corners sharing a key agree
        fsum = np.zeros((len(me.polygons), 3)); np.add.at(fsum, face_of_loop, c)
        fmean = fsum / lt[:, None]
        ksum = np.zeros((nk, 3)); np.add.at(ksum, key_id, fmean[face_of_loop])
        c = 0.5 * c + 0.5 * (ksum / kcnt)[key_id]                          # blur over same-facing neighbours
    col[:, :3] = c.astype(np.float32)
    attr.foreach_set("color", col.ravel())
    print(o.name, "smoothed", len(attr))
bpy.ops.wm.save_as_mainfile(filepath=path, compress=True, relative_remap=False)
print("saved")
