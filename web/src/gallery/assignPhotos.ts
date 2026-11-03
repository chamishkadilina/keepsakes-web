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
 */
export function assignPhotos(photoCount: number, frames: FrameSlot[]): Assignment {
  const collageCount = Math.min(photoCount, ASSIGN.collageCount)
  const collage = Array.from({ length: collageCount }, (_, i) => i)

  const assigned = new Map<FrameSlot, number>()
  if (photoCount > 0) {
    const byPriority = [...frames].sort((a, b) => a.priority - b.priority || a.number - b.number)
    byPriority.forEach((slot, i) => assigned.set(slot, (collageCount + i) % photoCount))
  }
  return { collage, frames: assigned }
}
