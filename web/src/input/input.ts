import { CAMERA, CONTROLS } from '../config/gameFeel'
import { damp } from '../lib/smoothing'

/**
 * Shared input state. Written by touch/mouse/keyboard handlers, read by the
 * player (physics step) and camera (render frame). A plain object on purpose:
 * no re-renders.
 *
 * `yaw`/`pitch` are look *targets*; the camera follows them with lag.
 * yaw 0 = looking north (−Z); pitch positive = looking down.
 */
export const input = {
  joyX: 0, // analog −1…1 after deadzone: right
  joyY: 0, // analog −1…1 after deadzone: forward
  keys: new Set<string>(),
  yaw: 0,
  pitch: CAMERA.pitchDefault,
  yawSpeed: 0, // look inertia (rad/s)
  pitchSpeed: 0,
  dragging: false,
  lastLookAt: -Infinity, // performance.now() of the last look input
}

export function addLook(dYaw: number, dPitch: number) {
  input.yaw += dYaw
  input.pitch = Math.min(CAMERA.pitchMaxDown, Math.max(-CAMERA.pitchMaxUp, input.pitch + dPitch))
  input.lastLookAt = performance.now()
}

/** Keeps turning a little after a swipe ends, slowing smoothly. */
export function applyLookInertia(dt: number) {
  if (input.dragging || (input.yawSpeed === 0 && input.pitchSpeed === 0)) return
  addLook(input.yawSpeed * dt, input.pitchSpeed * dt)
  const keep = 1 - damp(CONTROLS.inertiaTime, dt)
  input.yawSpeed *= keep
  input.pitchSpeed *= keep
  if (Math.abs(input.yawSpeed) + Math.abs(input.pitchSpeed) < 1e-3) stopLookInertia()
}

export function stopLookInertia() {
  input.yawSpeed = 0
  input.pitchSpeed = 0
}

export function resetLook() {
  input.yaw = 0
  input.pitch = CAMERA.pitchDefault
  input.lastLookAt = -Infinity
  stopLookInertia()
}

/** Joystick + WASD/arrows as one analog vector (length ≤ 1). */
export function readMove(): { x: number; y: number; run: boolean } {
  const k = input.keys
  const kx = (k.has('KeyD') || k.has('ArrowRight') ? 1 : 0) - (k.has('KeyA') || k.has('ArrowLeft') ? 1 : 0)
  const ky = (k.has('KeyW') || k.has('ArrowUp') ? 1 : 0) - (k.has('KeyS') || k.has('ArrowDown') ? 1 : 0)
  let x = input.joyX + kx
  let y = input.joyY + ky
  const length = Math.hypot(x, y)
  if (length > 1) {
    x /= length
    y /= length
  }
  return { x, y, run: k.has('ShiftLeft') || k.has('ShiftRight') }
}
