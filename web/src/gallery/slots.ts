import * as THREE from 'three'
import { ASSIGN } from '../config/frames'

/**
 * Where a frame hangs: on the wall behind its slot plane, facing into the room
 * (+Z of `quaternion`), the way frames/photoFrame.ts and frames/collageWall.ts expect.
 */
export type Placement = {
  position: THREE.Vector3
  quaternion: THREE.Quaternion
}

export type FrameSlot = Placement & {
  name: string
  number: number // NN from the name (route order)
  priority: number
  size: number // largest side of the square slot, metres
  light?: [number, number, number] // baked light on this spot (`light_rgb`)
}

export type MuseumSlots = {
  frames: FrameSlot[] // route order
  collage: Placement | null // centre of `collage_board`
  planes: THREE.Object3D[] // every slot plane, to hide
}

// Blender planes export with their front along local +Y and photo-up along local −Z.
const PLANE_TO_FRAME = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2)
const WALLS = ['walls', 'garden_walls']

/** The plane's centre, facing out of the wall. */
function placementOf(plane: THREE.Object3D): Placement {
  return {
    position: plane.getWorldPosition(new THREE.Vector3()),
    quaternion: plane.getWorldQuaternion(new THREE.Quaternion()).multiply(PLANE_TO_FRAME),
  }
}

/** Slot planes float a few cm in front of the wall; a frame's back goes on the wall itself. */
function onWall({ position, quaternion }: Placement, walls: THREE.Object3D[]): Placement {
  const back = new THREE.Vector3(0, 0, -1).applyQuaternion(quaternion)
  const hit = new THREE.Raycaster(position, back).intersectObjects(walls, false)[0]
  return { position: hit ? hit.point : position, quaternion }
}

/** Finds the slot planes by name (BUILD_SPEC §4). */
export function findSlots(scene: THREE.Object3D): MuseumSlots {
  scene.updateMatrixWorld(true)
  const walls = WALLS.map((name) => scene.getObjectByName(name)).filter((wall) => wall !== undefined)
  const found: MuseumSlots = { frames: [], collage: null, planes: [] }
  let missingPriority = 0

  scene.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh)) return
    const frame = obj.name.match(/^slot_frame_(\d+)$/)
    if (frame) {
      if (obj.userData.priority === undefined) missingPriority++
      const size = new THREE.Box3().setFromObject(obj).getSize(new THREE.Vector3())
      found.frames.push({
        ...onWall(placementOf(obj), walls),
        name: obj.name,
        number: Number(frame[1]),
        priority: Number(obj.userData.priority ?? ASSIGN.defaultPriority),
        size: Math.max(size.x, size.y, size.z),
        light: obj.userData.light_rgb,
      })
    }
    if (obj.name === 'collage_board') found.collage = placementOf(obj)
    // The collage lays itself out, so the slot_collage_* placeholders are only hidden.
    if (obj.name.startsWith('slot_')) found.planes.push(obj)
  })

  if (missingPriority > 0) {
    console.warn(
      `museum.glb: ${missingPriority} frame slots have no "priority" (export with Include → Custom Properties). Using ${ASSIGN.defaultPriority}.`,
    )
  }
  found.frames.sort((a, b) => a.number - b.number)
  return found
}
