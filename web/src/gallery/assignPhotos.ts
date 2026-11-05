import { ASSIGN } from '../config/frames'
import type { FrameSlot } from './slots'

export type Assignment = {
  collage: number[] // photo indices, in order
  frames: Map<FrameSlot, number> // slot → photo index
}

/**
 * BUILD_SPEC §5: the first 12 photos go on the collage, the rest fill frames
 * by priority (1 → 2 → 3), route order within a priority. Every frame gets a
 * photo, so the museum never looks empty: once they run out, they start again from #1.
 * The foyer has no frames any more: the photos of its turns go on the collage too,
 * and every other frame keeps the photo of its own turn.
 */
export function assignPhotos(photoCount: number, frames: FrameSlot[]): Assignment {
  const collageCount = Math.min(photoCount, ASSIGN.collageCount)
  const foyerPhotos = ASSIGN.foyerTurns.map((turn) => collageCount + turn).filter((i) => i < photoCount)
  const collage = [...Array.from({ length: collageCount }, (_, i) => i), ...foyerPhotos]

  const assigned = new Map<FrameSlot, number>()
  if (photoCount > 0) {
    const byPriority = [...frames].sort((a, b) => a.priority - b.priority || a.number - b.number)
    let turn = 0
    for (const slot of byPriority) {
      while (ASSIGN.foyerTurns.includes(turn)) turn++
      assigned.set(slot, (collageCount + turn++) % photoCount)
    }
  }
  return { collage, frames: assigned }
}
