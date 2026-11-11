import * as THREE from 'three'
import type { Placement } from './slots'

/** A framed photo's centre and the way it faces (into the room). */
type PhotoSpot = { centre: THREE.Vector3; facing: THREE.Vector3 }

/** The framed photos on the walls, set by Gallery. Not in the store: Player reads them every frame. */
const spots: PhotoSpot[] = []
const toFeet = new THREE.Vector3()

export function setPhotoSpots(frames: Placement[]) {
  spots.length = 0
  for (const { position, quaternion } of frames) {
    spots.push({ centre: position, facing: new THREE.Vector3(0, 0, 1).applyQuaternion(quaternion) })
  }
}

/** The centre of the nearest photo within `reach` (over the floor) that faces her, or null. */
export function nearestPhoto(feet: THREE.Vector3, reach: number): THREE.Vector3 | null {
  let best: THREE.Vector3 | null = null
  let bestDistance = reach
  for (const { centre, facing } of spots) {
    toFeet.subVectors(feet, centre)
    if (toFeet.dot(facing) <= 0) continue // behind the wall it hangs on
    const distance = Math.hypot(toFeet.x, toFeet.z)
    if (distance <= bestDistance) {
      best = centre
      bestDistance = distance
    }
  }
  return best
}
