import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { createGoldMaterial, createSatinBlackMatcap } from "./matcaps";

/**
 * Gallery track lights over the plain rails and spots in museum.glb, in satin black and champagne gold (like the
 * building's gold lines and the downlight trims): a slim black rail with soft rounded edges and gold end caps and, on
 * it, a designer spot for every photo: black adapter, swivel and U-yoke with gold knobs, a gold cylinder head with a
 * fine black band and bezel, and the warm lens set deep in a gold reflector, so you only see the light when you look
 * into the beam (like a real anti-glare gallery spot). Every spot keeps the aim of its baked light.
 * 8 draw calls for all of them.
 */
export interface Lamp { p: THREE.Vector3; axis: THREE.Vector3 }   // lens centre and beam direction (world)

const RAIL_W = 0.032, RAIL_H = 0.026;   // rail profile
const R = 0.036;                         // head radius
const BACK = -0.072, LENS = 0.062, FRONT = 0.09;   // back of the head, lens and front of the bezel, from the pivot along the beam
const YOKE = Math.hypot(BACK, R) + 0.005;          // pivot to the yoke bar: the head tilts freely under it
const DROP = YOKE + 0.046;                         // rail underside to the pivot: adapter 26 mm, swivel 14 mm, yoke bar 6 mm
const UP = new THREE.Vector3(0, 1, 0);

/** World boxes of the separate pieces of a merged mesh (vertices at the same place belong together). */
function pieces(mesh: THREE.Mesh): THREE.Box3[] {
  const { position } = mesh.geometry.attributes, index = mesh.geometry.index;
  const parent = Array.from({ length: position.count }, (_, i) => i);
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])));
  const join = (a: number, b: number) => { parent[find(a)] = find(b); };
  const seen = new Map<string, number>();
  for (let i = 0; i < position.count; i++) {
    const key = [position.getX(i), position.getY(i), position.getZ(i)].map((v) => v.toFixed(4)).join();
    const first = seen.get(key);
    if (first === undefined) seen.set(key, i); else join(i, first);
  }
  if (index) for (let i = 0; i < index.count; i += 3) { join(index.getX(i), index.getX(i + 1)); join(index.getX(i), index.getX(i + 2)); }
  const boxes = new Map<number, THREE.Box3>(), v = new THREE.Vector3();
  for (let i = 0; i < position.count; i++) {
    const root = find(i);
    if (!boxes.has(root)) boxes.set(root, new THREE.Box3());
    boxes.get(root)!.expandByPoint(v.fromBufferAttribute(position, i).applyMatrix4(mesh.matrixWorld));
  }
  return [...boxes.values()];
}

/** Merges parts into one geometry (rounded boxes come without an index, so none keeps one). */
const merge = (parts: THREE.BufferGeometry[], groups = false) => mergeGeometries(parts.map((g) => (g.index ? g.toNonIndexed() : g)), groups);

/** Turned part around the beam (+Z) from [radius, z] points; a repeated point makes a crisp edge. */
const lathe = (points: number[][]) => new THREE.LatheGeometry(points.map(([r, z]) => new THREE.Vector2(r, z)), 24).rotateX(Math.PI / 2);

/** One rail per piece of the model's rails, flush with the ceiling. Groups: paint, gold end caps. */
function railGeometry(rails: THREE.Box3[]): THREE.BufferGeometry {
  const bodies: THREE.BufferGeometry[] = [], caps: THREE.BufferGeometry[] = [];
  for (const rail of rails) {
    const size = rail.getSize(new THREE.Vector3()), c = rail.getCenter(new THREE.Vector3()), length = Math.max(size.x, size.z);
    const place = (g: THREE.BufferGeometry) => g.rotateY(size.x > size.z ? 0 : Math.PI / 2).translate(c.x, rail.max.y - RAIL_H / 2, c.z);
    bodies.push(place(new RoundedBoxGeometry(length - 0.008, RAIL_H, RAIL_W, 1, 0.005)));
    for (const s of [-1, 1]) caps.push(place(new THREE.BoxGeometry(0.008, RAIL_H, RAIL_W + 0.001).translate(s * (length / 2 - 0.004), 0, 0)));
  }
  return merge([merge(bodies), merge(caps)], true);
}

/** Adapter, swivel and U-yoke around the pivot (origin), the yoke across the beam (X). Groups: paint, gold knobs. */
function mountGeometry(): THREE.BufferGeometry {
  const paint = merge([
    new RoundedBoxGeometry(0.085, 0.026, 0.03, 1, 0.006).translate(0, DROP - 0.013, 0),                       // adapter
    new THREE.CylinderGeometry(0.011, 0.011, 0.014, 12, 1, true).translate(0, DROP - 0.033, 0),                 // swivel
    new THREE.BoxGeometry(2 * R + 0.022, 0.006, 0.016).translate(0, YOKE + 0.003, 0),                           // yoke
    ...[-1, 1].map((s) => new THREE.BoxGeometry(0.005, YOKE + 0.012, 0.016).translate(s * (R + 0.0085), (YOKE - 0.012) / 2, 0)),
  ]);
  const knobs = merge([-1, 1].map((s) => new THREE.CylinderGeometry(0.009, 0.009, 0.005, 12).rotateZ(Math.PI / 2).translate(s * (R + 0.0135), 0, 0)));
  return merge([paint, knobs], true);
}

/** Cylinder head around the pivot (origin), shining along +Z. Groups: body, band and bezel, reflector, lens. */
function headGeometry(): THREE.BufferGeometry {
  const body = lathe([[0, BACK], [R - 0.006, BACK], [R - 0.0015, BACK + 0.0025], [R, BACK + 0.007], [R, FRONT - 0.0115]]);
  const trim = merge([
    lathe([[R + 0.0004, BACK + 0.015], [R + 0.0004, BACK + 0.021]]),                                          // fine band
    lathe([[R + 0.0004, FRONT - 0.0125], [R + 0.0004, FRONT - 0.003], [R - 0.0018, FRONT], [R - 0.0052, FRONT]]),   // bezel
  ]);
  const reflector = lathe([[R - 0.0052, FRONT], [0.0185, LENS]]);
  const lens = new THREE.CircleGeometry(0.0188, 16).translate(0, 0, LENS + 0.0002);
  return merge([body, trim, reflector, lens], true);
}

/** Inside the head: drawn a little behind, so seen edge-on from the side it never shows through the body. */
const recessed = (material: THREE.Material) => Object.assign(material.clone(), { polygonOffset: true, polygonOffsetFactor: 4, polygonOffsetUnits: 4 });

/**
 * Removes the plain track rails and spot heads and builds the detailed ones. `lenses`: the spot lenses of the model.
 * Returns the group and the new lens positions (for the glare).
 */
export function createTrackLights(root: THREE.Object3D, lenses: Lamp[], lensMaterial: THREE.Material): { group: THREE.Group; lenses: Lamp[] } {
  const group = new THREE.Group();
  const railMesh = root.getObjectByName("track_rails") as THREE.Mesh | undefined;
  if (!railMesh) return { group, lenses };
  const rails = pieces(railMesh).filter((b) => Math.max(b.max.x - b.min.x, b.max.z - b.min.z) > 0.3);   // the rest are old stems
  for (const name of ["track_rails", "track_heads"]) root.getObjectByName(name)?.removeFromParent();

  const mounts: THREE.Matrix4[] = [], heads: THREE.Matrix4[] = [], placed: Lamp[] = [];
  for (const { p, axis } of lenses) {
    const rail = rails.find((b) => p.x > b.min.x - 0.1 && p.x < b.max.x + 0.1 && p.z > b.min.z - 0.1 && p.z < b.max.z + 0.1);
    if (!rail) continue;
    const c = rail.getCenter(new THREE.Vector3()), alongX = rail.max.x - rail.min.x > rail.max.z - rail.min.z;
    const pivot = new THREE.Vector3(alongX ? p.x : c.x, rail.max.y - RAIL_H - DROP, alongX ? c.z : p.z);     // under the rail's centre line
    const facing = new THREE.Vector3(axis.x, 0, axis.z).normalize();                                          // the head turns towards its photo ...
    const side = new THREE.Vector3().crossVectors(UP, facing).normalize();
    mounts.push(new THREE.Matrix4().makeBasis(side, UP, facing).setPosition(pivot));
    heads.push(new THREE.Matrix4().makeBasis(side, new THREE.Vector3().crossVectors(axis, side), axis).setPosition(pivot));   // ... and tilts down to it
    placed.push({ p: pivot.clone().addScaledVector(axis, LENS), axis });
  }

  const paint = new THREE.MeshMatcapMaterial({ matcap: createSatinBlackMatcap(), toneMapped: false });
  const gold = createGoldMaterial({ color: 0xf2dfc0 });                                                     // champagne, like the downlight trims
  group.add(new THREE.Mesh(railGeometry(rails), [paint, gold]));
  for (const [geometry, materials, matrices] of [
    [mountGeometry(), [paint, gold], mounts], [headGeometry(), [gold, paint, recessed(gold), recessed(lensMaterial)], heads],
  ] as const) {
    const mesh = new THREE.InstancedMesh(geometry, [...materials], matrices.length);
    matrices.forEach((m, i) => mesh.setMatrixAt(i, m));
    mesh.frustumCulled = false;
    group.add(mesh);
  }
  return { group, lenses: placed };
}
