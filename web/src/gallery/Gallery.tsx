import { useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { useGift } from '../gift/gift'
import { assignPhotos } from './assignPhotos'
import { Collage } from './Collage'
import { FramedPhoto } from './FramedPhoto'
import { setPhotoSpots } from './photoSpots'
import { findSlots } from './slots'

/** Fills the museum with the gift's photos (BUILD_SPEC §5): the collage niche and every gallery frame. */
export function Gallery({ scene }: { scene: THREE.Object3D }) {
  const gift = useGift((s) => s.gift)
  const slots = useMemo(() => findSlots(scene), [scene])
  const content = useMemo(() => {
    if (!gift) return null
    const { collage, frames } = assignPhotos(gift.photos.length, slots.frames)
    return {
      collage: collage.map((i) => gift.photos[i]),
      frames: [...frames].map(([slot, i]) => ({ slot, photo: gift.photos[i] })),
    }
  }, [gift, slots])

  useEffect(() => {
    slots.planes.forEach((plane) => (plane.visible = false))
  }, [slots])

  useEffect(() => {
    setPhotoSpots(content?.frames.map(({ slot }) => slot) ?? [])
    return () => setPhotoSpots([])
  }, [content])

  if (!content) return null
  return (
    <group>
      {slots.collage && content.collage.length > 0 && <Collage photos={content.collage} placement={slots.collage} />}
      {content.frames.map(({ slot, photo }) => (
        <FramedPhoto key={slot.name} slot={slot} photo={photo} />
      ))}
    </group>
  )
}
