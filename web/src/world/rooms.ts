// Floor areas from BUILD_SPEC §2, in Blender metres (x east, y north).
// In three.js (glTF, Y up) the same point is (x, height, -y).
type Area = [x0: number, x1: number, y0: number, y1: number]

const ROOMS: { name: string; areas: Area[] }[] = [
  { name: 'Garden', areas: [[38, 52, 0, 16]] },
  { name: 'Screen room', areas: [[26.5, 38, 1.5, 13]] },
  { name: 'Right gallery', areas: [[23, 38, 13, 21], [23, 26.5, 1.5, 13]] },
  { name: 'Heart room', areas: [[11, 23, 1.5, 21]] },
  { name: 'Story gallery', areas: [[0, 11, 10, 21]] },
  { name: 'Foyer', areas: [[0, 11, 0, 10]] },
]

/** Room name for a three.js world position, or 'Outside'. */
export function roomAt(x: number, z: number): string {
  const y = -z
  for (const room of ROOMS) {
    for (const [x0, x1, y0, y1] of room.areas) {
      if (x >= x0 && x <= x1 && y >= y0 && y <= y1) return room.name
    }
  }
  return 'Outside'
}

export const GARDEN = 'Garden'
