import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import type * as THREE from 'three'
import { FONTS_URL } from '../config/decor'
import { createLoveNotes } from '../decor/loveNotes'
import type { Gift } from '../gift/gift'
import { disposeDrawn } from './disposeDrawn'

/** The love notes, one per reason in the gift; none without reasons. */
function useLoveNotes(scene: THREE.Object3D, reasons: string[] | undefined, lit: boolean): void {
  const root = useThree((s) => s.scene)

  useEffect(() => {
    if (!lit || !reasons?.length) return
    let alive = true
    let notes: THREE.Group | null = null
    createLoveNotes(scene, reasons, { fontsUrl: FONTS_URL })
      .then((group) => {
        if (alive) root.add((notes = group))
        else disposeDrawn(group)
      })
      .catch((err) => console.error('Love notes failed:', err))
    return () => {
      alive = false
      if (!notes) return
      root.remove(notes)
      disposeDrawn(notes)
    }
  }, [scene, root, reasons, lit])
}

/** The decor that lives and dies with the gift. `lit`: the museum's baked materials are in place. */
export function useGiftDecor(scene: THREE.Object3D, gift: Gift | null, lit: boolean): void {
  useLoveNotes(scene, gift?.reasons, lit)
}
