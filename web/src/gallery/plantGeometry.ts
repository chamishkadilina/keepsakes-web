import * as THREE from 'three'
import { PLANT } from '../config/frames'

/** Pot and leaves of the small placeholder plant, standing at the origin. */
export type PlantParts = { pot: THREE.BufferGeometry; leaves: THREE.BufferGeometry[] }

function clean(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
  geometry.deleteAttribute('uv')
  return geometry.index ? geometry.toNonIndexed() : geometry
}

/** `turn` rotates the leaves so neighbouring plants don't look identical. */
export function plantParts(turn: number): PlantParts {
  const pot = new THREE.CylinderGeometry(PLANT.potRadiusTop, PLANT.potRadiusBottom, PLANT.potHeight, 16)
  pot.translate(0, PLANT.potHeight / 2, 0)

  const leaves: THREE.BufferGeometry[] = []
  for (let i = 0; i < PLANT.leafCount; i++) {
    const leaf = new THREE.SphereGeometry(1, 8, 6)
    leaf.scale(PLANT.leafWidth / 2, PLANT.leafLength / 2, PLANT.leafWidth / 5)
    leaf.translate(0, PLANT.leafLength / 2, 0) // base of the leaf at the origin
    const tilt = PLANT.leafTilt * (i % 2 === 0 ? 1 : 0.6)
    leaf.rotateX(tilt)
    leaf.rotateY(turn + (i / PLANT.leafCount) * Math.PI * 2)
    leaf.translate(0, PLANT.potHeight * 0.9, 0)
    leaves.push(clean(leaf))
  }
  return { pot: clean(pot), leaves }
}
