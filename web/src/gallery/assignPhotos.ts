import { ASSIGN } from '../config/frames'
import type { MuseumSlots, Slot } from './slots'

export type Assignment = {
  collage: Map<Slot, number> // slot → photo index
  frames: Map<Slot, number>
  emptyFrames: Slot[]
  centrepiece: number | null
}

/**
 * BUILD_SPEC §5: the first 12 photos go on the collage, the rest fill frames
 * by priority (1 → 2 → 3), route order within a priority. The centrepiece
 * shows photo #1.
 */
export function assignPhotos(photoCount: number, slots: MuseumSlots): Assignment {
  const collage = new Map<Slot, number>()
  const collageCount = Math.min(photoCount, ASSIGN.collageCount, slots.collage.length)
  for (let i = 0; i < collageCount; i++) collage.set(slots.collage[i], i)

  const frames = new Map<Slot, number>()
  const byPriority = [...slots.frames].sort((a, b) => a.priority - b.priority || a.number - b.number)
  byPriority.forEach((slot, i) => {
    const photo = collageCount + i
    if (photo < photoCount) frames.set(slot, photo)
  })

  return {
    collage,
    frames,
    emptyFrames: slots.frames.filter((slot) => !frames.has(slot)),
    centrepiece: slots.centrepiece && photoCount > 0 ? 0 : null,
  }
}
