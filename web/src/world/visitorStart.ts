import * as THREE from 'three'
import { findProps } from '../decor/findProps'

export type VisitorStart = {
  position: [number, number, number]
  yaw: number
}

/** Where a visitor (`spawn_her`, `spawn_him`) starts: on their marker, turned to the middle of the title wall. */
export function visitorStart(scene: THREE.Object3D, spawnName: string): VisitorStart {
  const position = new THREE.Vector3()
  const spawn = scene.getObjectByName(spawnName)
  if (spawn) spawn.getWorldPosition(position)
  else console.warn(`museum.glb has no ${spawnName}; using origin`)

  const board = findProps(scene, 'welcome_board')[0]
  if (!board) console.warn('museum.glb has no welcome_board; facing north')
  const wall = board ? new THREE.Box3().setFromObject(board).getCenter(new THREE.Vector3()) : position
  const yaw = board ? Math.atan2(position.x - wall.x, position.z - wall.z) : 0
  return { position: [position.x, position.y, position.z], yaw }
}
