import * as THREE from "three";

/**
 * Floor footprints of the furniture, exhibits and decor (the footprint_* markers in museum.glb), so the visitor walks
 * round every piece instead of through it. Each covers what stands on the floor up to head height (a tree's lower
 * branches too): round pieces (trees, urns, topiaries, side tables) have a circle, the rest a box turned with the piece.
 * Rugs are walkable. The rose petals use them too, so none lie under a sofa or on a rug.
 *
 *   const footprints = getFootprints(gltf.scene);
 *   const petals = createRosePetals(path, { avoid: (x, z) => isOnFootprint(footprints, x, z) });
 *   // every frame, after moving the camera:
 *   keepOffFootprints(camera.position, 0.3, footprints);
 */
export interface Footprint {
  name: string;
  walkable: boolean;                 // rugs
  radius: number | null;             // round pieces: a circle round the marker (halfWidth/halfDepth are its box)
  halfWidth: number;                 // along the marker's local x
  halfDepth: number;                 // along the marker's local z
  toLocal: THREE.Matrix4;            // world -> marker
  toWorld: THREE.Matrix4;
}

export function getFootprints(root: THREE.Object3D): Footprint[] {
  root.updateMatrixWorld(true);
  const found: Footprint[] = [];
  root.traverse((o) => {
    const half = o.userData.footprint as [number, number] | undefined;
    if (!o.name.startsWith("footprint_") || !half) return;
    found.push({
      name: o.name.slice("footprint_".length), walkable: !!o.userData.walkable, radius: (o.userData.radius as number | undefined) ?? null,
      halfWidth: half[0], halfDepth: half[1], toLocal: o.matrixWorld.clone().invert(), toWorld: o.matrixWorld.clone(),
    });
  });
  return found;
}

const p = new THREE.Vector3();

/** True if the floor point (x, z) lies on a footprint, or within `margin` metres of one. */
export function isOnFootprint(footprints: Footprint[], x: number, z: number, margin = 0.05): boolean {
  return footprints.some((f) => {
    p.set(x, 0, z).applyMatrix4(f.toLocal);
    if (f.radius !== null) return p.x * p.x + p.z * p.z < (f.radius + margin) ** 2;
    return Math.abs(p.x) < f.halfWidth + margin && Math.abs(p.z) < f.halfDepth + margin;
  });
}

/** Moves `position` (the visitor) out of every solid footprint, keeping `radius` metres clear. Height is kept. */
export function keepOffFootprints(position: THREE.Vector3, radius: number, footprints: Footprint[]): void {
  for (const f of footprints) {
    if (f.walkable) continue;
    p.copy(position).applyMatrix4(f.toLocal);
    p.y = 0;
    if (f.radius !== null) {                                                    // round: out along the radius
      const reach = f.radius + radius, d = Math.hypot(p.x, p.z);
      if (d >= reach) continue;
      if (d < 1e-6) p.set(reach, 0, 0); else p.multiplyScalar(reach / d);
    } else {
      const hx = f.halfWidth + radius, hz = f.halfDepth + radius;
      const dx = hx - Math.abs(p.x), dz = hz - Math.abs(p.z);
      if (dx <= 0 || dz <= 0) continue;
      if (dx < dz) p.x = Math.sign(p.x || 1) * hx;                             // out through the nearest side
      else p.z = Math.sign(p.z || 1) * hz;
    }
    const y = position.y;
    position.copy(p.applyMatrix4(f.toWorld));
    position.y = y;
  }
}
