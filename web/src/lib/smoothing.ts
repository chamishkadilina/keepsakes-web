/**
 * Frame-rate-independent smoothing. All take `seconds` = time to get ~95% of
 * the way, so the same value feels the same at 30, 60 or 120 fps.
 */

/** Factor for `x += (target - x) * damp(seconds, dt)`, i.e. 1 − exp(−k·dt). */
export function damp(seconds: number, dt: number): number {
  return 1 - Math.exp((-3 / seconds) * dt)
}

/** Damps an angle toward a target along the shortest way round. */
export function dampAngle(from: number, to: number, seconds: number, dt: number): number {
  const diff = Math.atan2(Math.sin(to - from), Math.cos(to - from))
  return from + diff * damp(seconds, dt)
}

/** Like dampAngle, but never turning faster than `maxRate` rad/s. */
export function turnAngle(from: number, to: number, seconds: number, maxRate: number, dt: number): number {
  const diff = Math.atan2(Math.sin(to - from), Math.cos(to - from))
  const step = diff * damp(seconds, dt)
  return from + Math.max(-maxRate * dt, Math.min(maxRate * dt, step))
}

/**
 * Critically damped spring toward `target`, exact for any dt. Unlike `damp`
 * it starts gently (no jump in acceleration) and never overshoots.
 * Returns [value, rate].
 */
export function spring(value: number, rate: number, target: number, seconds: number, dt: number): [number, number] {
  const w = 4.74 / seconds // (1 + w·t)·e^(−w·t) = 0.05 at t = seconds
  const offset = value - target
  const c = rate + w * offset
  const e = Math.exp(-w * dt)
  return [target + (offset + c * dt) * e, (rate - w * c * dt) * e]
}
