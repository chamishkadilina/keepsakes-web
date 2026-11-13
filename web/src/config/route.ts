import type { FloorBalloonArea } from '../decor/floorBalloons'

/**
 * The rose petals (design/lighting.md) as floor points [x, z] in three.js
 * coordinates (Blender (x, y) → three.js (x, −y)), clear of every piece of furniture.
 * The main path: entrance → story gallery → heart room, up to the tip of the petal heart.
 */
export const PETAL_PATH: [number, number][] = [
  [5.5, -1.5], [5.5, -3.2], [6.7, -3.6], [7.6, -5.6], [8.6, -7.7], [9.3, -9.4], [9.4, -10.6],
  [8.3, -12.6], [7.6, -16.4], [6.6, -18.6], [5.0, -18.9], [3.9, -17.6], [3.9, -15.3], [4.0, -12.6], [6.2, -11.4], [9.4, -11.6],
  [11.0, -12.0], [12.6, -12.2], [14.2, -13.0], [14.35, -15.2], [14.6, -16.9], [15.8, -17.3], [17.0, -17.3],
]

/** Down the red carpet outside, from the courtyard's far end to the open doors: a wedding aisle. */
export const ENTRANCE_PATH: [number, number][] = [[5.5, 13.4], [5.5, 9.0], [5.5, 4.6], [5.5, 0.4]]
export const ENTRANCE_PETALS = { count: 260, roses: 12, seed: 3 }

/** The heart of petals in front of the collage (props.py HEART_AT, HEART_WIDTH). */
export const HEART_CENTRE: [number, number] = [17.0, -18.6]
export const HEART_WIDTH = 1.9

/** Through the corridor and the screen room to the garden door. */
export const EAST_PATH: [number, number][] = [
  [18.2, -12.0], [20.5, -12.3], [22.6, -12.3], [24.4, -12.1], [24.8, -10.2], [24.8, -7.6], [24.8, -5.2],
  [25.3, -3.5], [27.0, -3.1], [29.0, -3.5], [30.9, -4.4], [33.2, -4.9], [35.3, -5.6], [36.9, -6.3], [37.9, -6.5],
]
export const EAST_PETALS = { count: 280, roses: 10, seed: 5 }

/** Into the right gallery. */
export const RIGHT_PATH: [number, number][] = [[24.8, -13.2], [26.1, -14.5], [28.0, -15.5], [30.4, -16.3]]
export const RIGHT_PETALS = { count: 100, roses: 4, seed: 9 }

/** A ring just outside the dance floor's edge (floor radius 1.8, ring 0.4 beyond it). */
const DANCE_RING_RADIUS = 1.8 + 0.4
export const DANCE_RING: [number, number][] = Array.from({ length: 25 }, (_, i) => [
  17.0 + DANCE_RING_RADIUS * Math.cos((i / 24) * Math.PI * 2),
  -6.2 + DANCE_RING_RADIUS * Math.sin((i / 24) * Math.PI * 2),
])
export const DANCE_PETALS = { count: 140, roses: 6, seed: 11 }

/** The party balloons on the floors: each room's floor (x0, z0, x1, z1) and where they gather. */
export const FLOOR_BALLOON_AREAS: FloorBalloonArea[] = [
  { rect: [11.4, -20.6, 22.6, -1.9], count: 8, groups: [[13.4, -12.8], [19.8, -4.6]] }, // heart room
  { rect: [23.4, -20.6, 37.6, -13.5], count: 6, groups: [[27.2, -15.4], [34.2, -15.8]] }, // right gallery
]
