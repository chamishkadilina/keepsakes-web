import * as THREE from 'three'
import { ASSIGN } from '../config/frames'

/**
 * A photo area from museum.glb. Its "frame space" is the space the gallery
 * builds in: centred on the slot, x right, y up (the photo's up), z out of the
 * wall into the room. `matrix` takes frame space to world space.
 */
export type Slot = {
  name: string
  number: number // NN from the name (route order)
  priority: number
  width: number
  height: number
  matrix: THREE.Matrix4
}

export type MuseumSlots = {
  frames: Slot[] // route order
  collage: Slot[] // slot_collage_01 … in order
  collageBoard: Slot | null
  centrepiece: Slot | null
  planes: THREE.Object3D[] // every slot plane, to hide
}

// Blender planes export with their front along local +Y and photo-up along local −Z.
const PLANE_TO_FRAME_SPACE = new THREE.Matrix4().makeRotationX(-Math.PI / 2)

function toSlot(mesh: THREE.Mesh, number: number): Slot {
  mesh.geometry.computeBoundingBox()
  const size = mesh.geometry.boundingBox!.getSize(new THREE.Vector3())
  const priority = Number(mesh.userData.priority ?? ASSIGN.defaultPriority)
  return {
    name: mesh.name,
    number,
    priority,
    width: size.x,
    height: size.z,
    matrix: mesh.matrixWorld.clone().multiply(PLANE_TO_FRAME_SPACE),
  }
}

const byNumber = (a: Slot, b: Slot) => a.number - b.number

/** Finds the slot planes by name (BUILD_SPEC §4). */
export function findSlots(scene: THREE.Object3D): MuseumSlots {
  scene.updateMatrixWorld(true)
  const found: MuseumSlots = { frames: [], collage: [], collageBoard: null, centrepiece: null, planes: [] }
  let missingPriority = 0

  scene.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh)) return
    const frame = obj.name.match(/^slot_frame_(\d+)$/)
    const collage = obj.name.match(/^slot_collage_(\d+)$/)
    if (frame) {
      if (obj.userData.priority === undefined) missingPriority++
      found.frames.push(toSlot(obj, Number(frame[1])))
    } else if (collage) found.collage.push(toSlot(obj, Number(collage[1])))
    else if (obj.name === 'slot_centrepiece') found.centrepiece = toSlot(obj, 0)
    else if (obj.name === 'collage_board') found.collageBoard = toSlot(obj, 0)
    else return
    if (obj.name.startsWith('slot_')) found.planes.push(obj)
  })

  if (missingPriority > 0) {
    console.warn(
      `museum.glb: ${missingPriority} frame slots have no "priority" (export with Include → Custom Properties). Using ${ASSIGN.defaultPriority}.`,
    )
  }
  found.frames.sort(byNumber)
  found.collage.sort(byNumber)
  return found
}
