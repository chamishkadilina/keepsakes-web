import * as THREE from "three";

/** Frame cross-sections: swept around a rectangle to build mouldings and mats. */
export type Band = "lip" | "face" | "side";   // inner edge / front / outer side
/** Cross-section point: d = distance outward from the inner edge, z = height off the wall, band of the next face. */
export type P = [d: number, z: number, band: Band, crease?: boolean];

/** Slim modern metal frame: flat face with softly rounded edges, 3 cm wide and 3 cm deep at scale 1. */
export const FRAME_WIDTH = 0.03;
export const FRAME_DEPTH = 0.03;
export const FRAME_PROFILE: P[] = [
  [0.0, 0.012, "lip", true], [0.0, 0.024, "lip"], [0.0025, 0.0285, "face"], [0.006, FRAME_DEPTH, "face"],   // inner edge
  [0.024, FRAME_DEPTH, "face"], [0.0275, 0.0285, "face"], [FRAME_WIDTH, 0.025, "side", true],               // face, outer edge
  [FRAME_WIDTH, 0.0, "side", true],                                                                         // side to the wall
];
/** Tone of each band (multiplies the frame colour): the face full, the inner and outer sides a little darker. */
export const FRAME_TONE: Record<Band, [number, number, number]> = { lip: [0.84, 0.8, 0.76], face: [1, 1, 1], side: [0.66, 0.6, 0.54] };

/** Sweeps a cross-section around a rectangle (mitred corners, smooth or creased normals, a tone per band). */
export function sweep(halfW: number, halfH: number, profile: P[], tone: (band: Band) => [number, number, number]) {
  const pos: number[] = [], nor: number[] = [], col: number[] = [];
  const seg = profile.slice(0, -1).map(([d0, z0], i) => {
    const [d1, z1] = profile[i + 1], l = Math.hypot(d1 - d0, z1 - z0);
    return [-(z1 - z0) / l, (d1 - d0) / l];                          // (outward, up) normal of this face
  });
  const normalAt = (i: number, s: number) => {
    if (profile[i][3] || i === 0 || i === profile.length - 1) return seg[s];
    const a = seg[i - 1], b = seg[i], l = Math.hypot(a[0] + b[0], a[1] + b[1]);
    return [(a[0] + b[0]) / l, (a[1] + b[1]) / l];
  };
  const sides = [[0, 1], [1, 0], [0, -1], [-1, 0]];                   // top, right, bottom, left
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  for (let side = 0; side < 4; side++) {
    const [nx, ny] = sides[side], [tx, ty] = [ny, -nx];
    const half = (d: number) => (nx === 0 ? halfW : halfH) + d;
    for (let s = 0; s < seg.length; s++) {
      const col3 = tone(profile[s][2]);
      const quad = ([[s, 0], [s, 1], [s + 1, 1], [s + 1, 0]] as const).map(([i, end]) => {
        const d = profile[i][0], sign = end ? 1 : -1;
        const x = nx * (halfW + d) + tx * sign * half(d), y = ny * (halfH + d) + ty * sign * half(d);
        const [nd, nz] = normalAt(i, s);
        return { p: [x, y, profile[i][1]], n: [nx * nd, ny * nd, nz] };
      });
      for (const tri of [[0, 1, 2], [0, 2, 3]]) {
        const [p0, p1, p2] = tri.map((k) => quad[k]);
        a.fromArray(p1.p).sub(c.fromArray(p0.p)); b.fromArray(p2.p).sub(c);
        const flip = a.cross(b).dot(c.fromArray(p0.n)) < 0;          // keep faces pointing along their normals
        for (const q of flip ? [p0, p2, p1] : [p0, p1, p2]) {
          pos.push(...q.p); nor.push(...q.n); col.push(...col3);
        }
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  return g;
}
