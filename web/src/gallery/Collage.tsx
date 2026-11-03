import { useEffect, useMemo } from 'react'
import { COLLAGE } from '../config/frames'
import { createCollageWall } from '../frames/collageWall'
import type { GiftPhoto } from '../gift/gift'
import { disposeGeometries } from './disposeGeometries'
import type { Placement } from './slots'
import { usePhotoTextures } from './usePhotoTextures'

/** The heart-room niche: all collage photos as a mosaic of thin gold frames (frames/collageWall.ts). */
export function Collage({ photos, placement }: { photos: GiftPhoto[]; placement: Placement }) {
  const textures = usePhotoTextures(photos, placement.position)
  const wall = useMemo(
    () => (textures ? createCollageWall({ photos: textures, width: COLLAGE.width, height: COLLAGE.height }) : null),
    [textures],
  )

  useEffect(() => () => {
    if (wall) disposeGeometries(wall)
  }, [wall])

  if (!wall) return null
  return <primitive object={wall} position={placement.position} quaternion={placement.quaternion} />
}
