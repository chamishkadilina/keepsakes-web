import type { MeshStandardMaterial } from 'three'
import { CAMERA } from '../config/gameFeel'
import { damp } from '../lib/smoothing'

/** Next player opacity for a given camera distance. */
export function fadeOpacity(current: number, cameraDistance: number, dt: number): number {
  const target = Math.min(1, Math.max(0, (cameraDistance - CAMERA.fadeEnd) / (CAMERA.fadeStart - CAMERA.fadeEnd)))
  return current + (target - current) * damp(CAMERA.fadeTime, dt)
}

/** Applies opacity; switches to transparent rendering only while faded. */
export function setOpacity(materials: MeshStandardMaterial[], opacity: number) {
  const solid = opacity > 0.99
  for (const m of materials) {
    m.opacity = opacity
    if (m.transparent === solid) {
      m.transparent = !solid
      m.depthWrite = solid
      m.needsUpdate = true
    }
  }
}
