import { useEffect, useMemo } from 'react'
import { createPhotoFrame, photoSizeForSlot } from '../frames/photoFrame'
import type { GiftPhoto } from '../gift/gift'
import { disposeGeometries } from './disposeGeometries'
import type { FrameSlot } from './slots'
import { usePhotoPlaque } from './usePhotoPlaque'
import { usePhotoTextures } from './usePhotoTextures'

/**
 * One photo in its ornate gold frame (frames/photoFrame.ts), hung on the wall at its slot.
 * The frame keeps the photo's own aspect ratio and fits inside the slot; the photo is never altered.
 * A photo with a caption gets its museum label under the frame.
 */
export function FramedPhoto({ slot, photo }: { slot: FrameSlot; photo: GiftPhoto }) {
  const photos = useMemo(() => [photo], [photo])
  const textures = usePhotoTextures(photos, slot.position)

  const frame = useMemo(() => {
    if (!textures) return null
    const [texture] = textures
    const image = texture.image as HTMLImageElement
    const { width, height } = photoSizeForSlot(image.width / image.height, slot.size)
    return createPhotoFrame({ photo: texture, width, height, light: slot.light })
  }, [textures, slot])

  useEffect(() => () => {
    if (frame) disposeGeometries(frame)
  }, [frame])

  usePhotoPlaque(frame, photo.caption, slot.light)

  if (!frame) return null
  return <primitive object={frame} position={slot.position} quaternion={slot.quaternion} />
}
