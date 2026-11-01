import { useRef, type PointerEvent } from 'react'
import { CONTROLS } from '../config/gameFeel'
import { damp } from '../lib/smoothing'
import { addLook, input, stopLookInertia } from './input'
import { joystickFromOffset } from './joystick'
import { usePointerLock } from './usePointerLock'

type Drag = {
  mode: 'joystick' | 'look'
  mouse: boolean
  startX: number
  startY: number
  lastX: number
  lastY: number
  lastTime: number
  travelled: number
}

/**
 * Full-screen input layer.
 * Phone: left half = floating analog joystick (fades in/out),
 *        right half = drag to look with slight inertia.
 * Desktop: drag to look, or click to lock the pointer (Esc releases).
 */
export function Controls() {
  const drags = useRef(new Map<number, Drag>())
  const layer = useRef<HTMLDivElement>(null)
  const ring = useRef<HTMLDivElement>(null)
  const knob = useRef<HTMLDivElement>(null)
  const lockPointer = usePointerLock(layer)

  const drawJoystick = (x: number, y: number, knobX: number, knobY: number) => {
    if (ring.current) Object.assign(ring.current.style, { left: `${x}px`, top: `${y}px` })
    if (knob.current) Object.assign(knob.current.style, { left: `${x + knobX}px`, top: `${y + knobY}px` })
  }
  const showJoystick = (on: boolean) => {
    ring.current?.classList.toggle('on', on)
    knob.current?.classList.toggle('on', on)
  }

  const onDown = (e: PointerEvent<HTMLDivElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId)
    const mouse = e.pointerType === 'mouse'
    const joystickInUse = [...drags.current.values()].some((d) => d.mode === 'joystick')
    const mode = !mouse && e.clientX < window.innerWidth / 2 && !joystickInUse ? 'joystick' : 'look'
    drags.current.set(e.pointerId, {
      mode, mouse, startX: e.clientX, startY: e.clientY, lastX: e.clientX, lastY: e.clientY, lastTime: e.timeStamp, travelled: 0,
    })
    if (mode === 'joystick') {
      drawJoystick(e.clientX, e.clientY, 0, 0)
      showJoystick(true)
    } else {
      input.dragging = true
      stopLookInertia()
    }
  }

  const onMove = (e: PointerEvent<HTMLDivElement>) => {
    const d = drags.current.get(e.pointerId)
    if (!d || document.pointerLockElement) return
    const dx = e.clientX - d.lastX
    const dy = e.clientY - d.lastY
    d.travelled += Math.hypot(dx, dy)

    if (d.mode === 'look') {
      const perPx = d.mouse
        ? CONTROLS.mouseDragLook
        : CONTROLS.touchTurnPerShortSide / Math.min(window.innerWidth, window.innerHeight)
      const dYaw = -dx * perPx
      const dPitch = dy * perPx
      addLook(dYaw, dPitch)
      if (!d.mouse) {
        // Track swipe speed (rad/s) for inertia.
        const dt = Math.max(1, e.timeStamp - d.lastTime) / 1000
        const a = damp(CONTROLS.swipeSmoothingTime, dt)
        input.yawSpeed += (dYaw / dt - input.yawSpeed) * a
        input.pitchSpeed += (dPitch / dt - input.pitchSpeed) * a
      }
    } else {
      const stick = joystickFromOffset(e.clientX - d.startX, e.clientY - d.startY)
      input.joyX = stick.x
      input.joyY = stick.y
      drawJoystick(d.startX, d.startY, stick.knobX, stick.knobY)
    }
    d.lastX = e.clientX
    d.lastY = e.clientY
    d.lastTime = e.timeStamp
  }

  const onUp = (e: PointerEvent<HTMLDivElement>) => {
    const d = drags.current.get(e.pointerId)
    drags.current.delete(e.pointerId)
    if (!d) return
    if (d.mode === 'joystick') {
      input.joyX = 0
      input.joyY = 0
      drawJoystick(d.startX, d.startY, 0, 0)
      showJoystick(false)
      return
    }
    input.dragging = false
    if (d.mouse || e.timeStamp - d.lastTime > CONTROLS.inertiaStopAfterHold) stopLookInertia()
    if (d.mouse && d.travelled < CONTROLS.clickSlop) lockPointer()
  }

  return (
    <div
      ref={layer}
      className="controls"
      onPointerDown={onDown}
      onPointerMove={onMove}
      onPointerUp={onUp}
      onPointerCancel={onUp}
      onContextMenu={(e) => e.preventDefault()}
    >
      <div ref={ring} className="joystick-ring" />
      <div ref={knob} className="joystick-knob" />
    </div>
  )
}
