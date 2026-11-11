import type { Material } from 'three'
import { CAMERA } from '../config/gameFeel'
import { damp } from '../lib/smoothing'

/** Next player opacity for a given camera distance. */
export function fadeOpacity(current: number, cameraDistance: number, dt: number): number {
  const target = Math.min(1, Math.max(0, (cameraDistance - CAMERA.fadeEnd) / (CAMERA.fadeStart - CAMERA.fadeEnd)))
  return current + (target - current) * damp(CAMERA.fadeTime, dt)
}

type Look = { opacity: number; transparent: boolean; depthWrite: boolean }
const looks = new WeakMap<Material, Look>() // each material as it was made (some are see-through by design)

/** Applies opacity; switches to transparent rendering only while faded. */
export function setOpacity(materials: Material[], opacity: number) {
  const faded = opacity <= 0.99
  for (const m of materials) {
    let look = looks.get(m)
    if (!look) looks.set(m, (look = { opacity: m.opacity, transparent: m.transparent, depthWrite: m.depthWrite }))
    m.opacity = look.opacity * opacity
    const transparent = look.transparent || faded
    if (m.transparent !== transparent) {
      m.transparent = transparent
      m.depthWrite = faded ? false : look.depthWrite
      m.needsUpdate = true
    }
  }
}
