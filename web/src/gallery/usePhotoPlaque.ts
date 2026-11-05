import { useEffect } from 'react'
import * as THREE from 'three'
import { createPhotoPlaque } from '../frames/photoPlaque'
import type { PhotoCaption } from '../gift/gift'
import type { FrameSlot } from './slots'

const GAP = 0.08 // m between the frame and its label

/** Frees what only this label uses; the frame's geometry is freed with the frame. */
function disposePlaque(plaque: THREE.Mesh): void {
  const material = plaque.material as THREE.MeshBasicMaterial
  material.map?.dispose()
  material.dispose()
  plaque.geometry.dispose()
}

/** Hangs the photo's museum label under its frame, only when the photo has a caption. */
export function usePhotoPlaque(frame: THREE.Group | null, caption: PhotoCaption | undefined, light: FrameSlot['light']): void {
  useEffect(() => {
    if (!frame || !caption) return
    let alive = true
    let hung: THREE.Mesh | null = null
    createPhotoPlaque({ ...caption, light })
      .then((plaque) => {
        if (!alive) return disposePlaque(plaque)
        plaque.position.y = -(frame.userData.outerSize[1] / 2 + GAP + plaque.userData.height / 2)
        frame.add(plaque)
        hung = plaque
      })
      .catch((err) => console.error('Photo label failed:', err))
    return () => {
      alive = false
      if (!hung) return
      frame.remove(hung)
      disposePlaque(hung)
    }
  }, [frame, caption, light])
}
