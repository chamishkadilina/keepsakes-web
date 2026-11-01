import * as THREE from 'three'
import { FRAME } from '../config/frames'

/**
 * Pieces of a frame in frame space (x right, y up, z into the room, photo at z = 0).
 * All return non-indexed geometry with position + normal only, ready to merge.
 */

/**
 * Gold moulding swept around an opening of halfW × halfH. Each profile point is a
 * rectangle grown outward by its offset, so the four corners meet in clean mitres.
 */
export function mouldingGeometry(halfW: number, halfH: number): THREE.BufferGeometry {
  const back = -FRAME.wallGap
  const rings = FRAME.profile.map(([across, up]) => {
    const d = across * FRAME.mouldingWidth
    const z = back + up * FRAME.mouldingDepth
    const w = halfW + d
    const h = halfH + d
    // Counter-clockwise seen from the room.
    return [
      new THREE.Vector3(-w, -h, z),
      new THREE.Vector3(w, -h, z),
      new THREE.Vector3(w, h, z),
      new THREE.Vector3(-w, h, z),
    ]
  })

  const positions: number[] = []
  for (let k = 0; k < rings.length - 1; k++) {
    const a = rings[k]
    const b = rings[k + 1]
    for (let i = 0; i < 4; i++) {
      const j = (i + 1) % 4
      for (const v of [a[i], b[i], b[j], a[i], b[j], a[j]]) positions.push(v.x, v.y, v.z)
    }
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  geometry.computeVertexNormals() // non-indexed → flat faces, crisp mitres
  return geometry
}

/** A flat rectangle facing the room (or away from it with `facingBack`). */
export function quadGeometry(
  width: number,
  height: number,
  centre: THREE.Vector3Like,
  facingBack = false,
): THREE.BufferGeometry {
  const geometry = new THREE.PlaneGeometry(width, height)
  if (facingBack) geometry.rotateY(Math.PI)
  geometry.translate(centre.x, centre.y, centre.z)
  geometry.deleteAttribute('uv')
  return geometry.toNonIndexed()
}
