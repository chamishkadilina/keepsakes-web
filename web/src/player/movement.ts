import type { Collider, KinematicCharacterController, RigidBody, World } from '@dimforge/rapier3d-compat'
import type { useRapier } from '@react-three/rapier'
import { Vector3 } from 'three'
import { MOVEMENT, PLAYER } from '../config/gameFeel'
import { keepOffFootprints, type Footprint } from '../decor/footprints'
import { readMove } from '../input/input'
import { spring } from '../lib/smoothing'
import { GROUND_RAY_GROUPS } from '../world/useMuseumColliders'
import type { Motion } from './cameraRig'

type RapierApi = ReturnType<typeof useRapier>['rapier']

export const CAPSULE_CENTER = PLAYER.halfHeight + PLAYER.radius // feet → capsule centre

/** Everything the movement step remembers between physics steps. */
export type MoveState = {
  motion: Motion
  accelX: number // spring rate of the velocity (m/s²)
  accelZ: number
  fallSpeed: number
  grounded: boolean
  heading: number // direction the player wants to face (yaw)
  moved: boolean // true once the player has given any input
}

export const newMoveState = (): MoveState => ({
  motion: { vx: 0, vz: 0, speed: 0, running: false },
  accelX: 0,
  accelZ: 0,
  fallSpeed: 0,
  grounded: false,
  heading: 0,
  moved: false,
})

export function createController(world: World): KinematicCharacterController {
  const c = world.createCharacterController(MOVEMENT.skin)
  c.enableAutostep(MOVEMENT.stepHeight, MOVEMENT.stepMinWidth, false)
  c.setMaxSlopeClimbAngle(MOVEMENT.maxSlope)
  c.setSlideEnabled(true)
  return c
}

/** Eased, camera-relative velocity from the current input. */
function updateVelocity(s: MoveState, cameraYaw: number, dt: number) {
  const move = readMove() // analog, length ≤ 1
  const push = Math.hypot(move.x, move.y)
  const top = move.run ? MOVEMENT.runSpeed : MOVEMENT.walkSpeed
  const sin = Math.sin(cameraYaw)
  const cos = Math.cos(cameraYaw)
  const tx = (-sin * move.y + cos * move.x) * top
  const tz = (-cos * move.y - sin * move.x) * top
  if (push > 0) {
    s.moved = true
    s.heading = Math.atan2(-tx, -tz)
  }

  const m = s.motion
  const ease = Math.hypot(tx, tz) >= m.speed ? MOVEMENT.speedUpTime : MOVEMENT.slowDownTime
  ;[m.vx, s.accelX] = spring(m.vx, s.accelX, tx, ease, dt)
  ;[m.vz, s.accelZ] = spring(m.vz, s.accelZ, tz, ease, dt)
  m.speed = Math.hypot(m.vx, m.vz)
  if (push === 0 && m.speed < MOVEMENT.stopBelowSpeed) {
    m.vx = m.vz = m.speed = s.accelX = s.accelZ = 0
  }
  m.running = move.run && push > MOVEMENT.runMinPush
}

/**
 * One physics step. The controller handles walls (slide) and steps
 * (autostep); height comes from a ground ray so the player stays exactly on
 * the floor (the controller's own grounded flag flickers on flat floors). The
 * ray sees only `floor_*` meshes (and the invisible `col_floor_*` ground). Furniture has no colliders: its footprints
 * push the capsule back out.
 * Returns the next body position.
 */
export function stepMovement(
  s: MoveState,
  controller: KinematicCharacterController,
  world: World,
  rapier: RapierApi,
  collider: Collider,
  body: RigidBody,
  cameraYaw: number,
  footprints: Footprint[],
  dt: number,
) {
  updateVelocity(s, cameraYaw, dt)

  s.fallSpeed = s.grounded ? 0 : Math.min(s.fallSpeed + MOVEMENT.gravity * dt, MOVEMENT.maxFallSpeed)
  controller.computeColliderMovement(collider, { x: s.motion.vx * dt, y: -s.fallSpeed * dt, z: s.motion.vz * dt })
  const d = controller.computedMovement()
  const p = body.translation()
  const next = new Vector3(p.x + d.x, p.y + d.y, p.z + d.z)
  keepOffFootprints(next, PLAYER.radius, footprints)

  const down = new rapier.Ray(next, { x: 0, y: -1, z: 0 })
  const ground = world.castRay(down, CAPSULE_CENTER + MOVEMENT.groundSnap, true, undefined, GROUND_RAY_GROUPS, collider, body)
  s.grounded = ground !== null
  if (ground) next.y += CAPSULE_CENTER + MOVEMENT.skin - ground.timeOfImpact
  return next
}
