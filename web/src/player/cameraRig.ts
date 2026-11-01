import { PerspectiveCamera, Vector3, type Camera } from 'three'
import type { useRapier } from '@react-three/rapier'
import { CAMERA } from '../config/gameFeel'
import { applyLookInertia, input } from '../input/input'
import { damp, dampAngle } from '../lib/smoothing'

type Rapier = ReturnType<typeof useRapier>
type CastShape = Rapier['world']['castShape']
type Collider = Parameters<CastShape>[9]
type RigidBody = Parameters<CastShape>[10]

export type Motion = { vx: number; vz: number; speed: number; running: boolean }

const DEG = Math.PI / 180
const NO_ROTATION = { x: 0, y: 0, z: 0, w: 1 }

const rig = {
  yaw: 0,
  pitch: CAMERA.pitchDefault,
  arm: CAMERA.armWalk, // wanted arm length (walk/run)
  length: CAMERA.armWalk, // actual arm length after walls
  fov: CAMERA.fovWalk,
  follow: new Vector3(),
  ahead: new Vector3(),
  snap: true,
}
const pivot = new Vector3()

/** Camera yaw: "forward" for movement is where the camera looks. */
export const cameraYaw = () => rig.yaw

export function resetRig() {
  rig.yaw = input.yaw
  rig.pitch = input.pitch
  rig.arm = rig.length = CAMERA.armWalk
  rig.fov = CAMERA.fovWalk
  rig.ahead.set(0, 0, 0)
  rig.snap = true
}

/**
 * Design FOV on landscape screens. Portrait phones are widened to keep a
 * usable horizontal view (55° vertical would show only ~27° across).
 */
function screenFov(designFov: number, aspect: number): number {
  const keepWidth = (2 * Math.atan(Math.tan((CAMERA.portraitKeepWidth / 2) * DEG) / aspect)) / DEG
  return Math.max(CAMERA.fovWalk, Math.min(CAMERA.portraitMaxFov, keepWidth)) + (designFov - CAMERA.fovWalk)
}

/** Auto recentre: after moving a while without touching look, swing behind the player. */
function recentre(motion: Motion, dt: number) {
  const idleLook = performance.now() - input.lastLookAt > CAMERA.recentreAfter * 1000
  if (motion.speed < CAMERA.movingAbove || input.dragging || !idleLook) return
  const heading = Math.atan2(-motion.vx, -motion.vz)
  const off = Math.atan2(Math.sin(heading - input.yaw), Math.cos(heading - input.yaw))
  if (Math.abs(off) < CAMERA.recentreMaxAngle) input.yaw = dampAngle(input.yaw, heading, CAMERA.recentreTime, dt)
}

/**
 * Spring-arm camera. Runs every render frame after the physics step, with
 * `feet` = the player's interpolated visual position. Returns the distance
 * from the pivot to the camera (used to fade the player).
 */
export function updateCamera(
  camera: Camera,
  feet: Vector3,
  motion: Motion,
  walkSpeed: number,
  { world, rapier }: Rapier,
  ignoreCollider: Collider,
  ignoreBody: RigidBody,
  aspect: number,
  dt: number,
): number {
  applyLookInertia(dt)
  recentre(motion, dt)

  // Rotation lag
  rig.yaw = rig.snap ? input.yaw : dampAngle(rig.yaw, input.yaw, CAMERA.rotationLagTime, dt)
  rig.pitch = rig.snap ? input.pitch : rig.pitch + (input.pitch - rig.pitch) * damp(CAMERA.rotationLagTime, dt)

  // Position damping + look-ahead
  const moving = motion.speed > CAMERA.movingAbove
  const ahead = moving ? (CAMERA.lookAhead * Math.min(1, motion.speed / walkSpeed)) / motion.speed : 0
  if (rig.snap) {
    rig.follow.copy(feet)
    rig.ahead.set(motion.vx * ahead, 0, motion.vz * ahead)
  } else {
    const a = damp(CAMERA.followTime, dt)
    rig.follow.lerp(feet, a)
    rig.ahead.x += (motion.vx * ahead - rig.ahead.x) * a
    rig.ahead.z += (motion.vz * ahead - rig.ahead.z) * a
  }
  pivot.set(rig.follow.x + rig.ahead.x, rig.follow.y + CAMERA.pivotHeight, rig.follow.z + rig.ahead.z)

  // Arm length (walk/run), then walls: a sphere cast from the pivot.
  rig.arm += ((motion.running ? CAMERA.armRun : CAMERA.armWalk) - rig.arm) * damp(CAMERA.armTime, dt)
  const cp = Math.cos(rig.pitch)
  const dir = { x: Math.sin(rig.yaw) * cp, y: Math.sin(rig.pitch), z: Math.cos(rig.yaw) * cp }
  const probe = new rapier.Ball(CAMERA.wallProbeRadius)
  const hit = world.castShape(pivot, NO_ROTATION, dir, probe, 0, rig.arm, true, undefined, undefined, ignoreCollider, ignoreBody)
  const free = hit ? Math.max(CAMERA.wallMinArm, hit.time_of_impact) : rig.arm
  if (rig.snap) rig.length = free
  else rig.length += (free - rig.length) * damp(free < rig.length ? CAMERA.wallInTime : CAMERA.wallOutTime, dt)
  rig.length = Math.min(rig.length, free + CAMERA.wallSafeOvershoot) // never inside a wall

  camera.position.set(pivot.x + dir.x * rig.length, pivot.y + dir.y * rig.length, pivot.z + dir.z * rig.length)
  camera.lookAt(pivot)

  // Field of view
  rig.fov += ((motion.running ? CAMERA.fovRun : CAMERA.fovWalk) - rig.fov) * damp(CAMERA.fovTime, dt)
  if (camera instanceof PerspectiveCamera) {
    const fov = screenFov(rig.fov, aspect)
    if (Math.abs(camera.fov - fov) > 0.01) {
      camera.fov = fov
      camera.updateProjectionMatrix()
    }
  }

  rig.snap = false
  return rig.length
}
