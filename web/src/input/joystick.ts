import { CONTROLS } from '../config/gameFeel'

/**
 * Turns a thumb offset from the joystick centre (px) into an analog move
 * vector with a deadzone, and the knob offset to draw (clamped to the ring).
 */
export function joystickFromOffset(dx: number, dy: number) {
  const r = CONTROLS.joystickRadius
  const length = Math.hypot(dx, dy)
  if (length === 0) return { x: 0, y: 0, knobX: 0, knobY: 0 }
  const reach = Math.min(length, r)
  const dirX = dx / length
  const dirY = dy / length
  const push = reach / r
  const dz = CONTROLS.joystickDeadzone
  const strength = push < dz ? 0 : (push - dz) / (1 - dz)
  return { x: dirX * strength, y: -dirY * strength, knobX: dirX * reach, knobY: dirY * reach }
}
