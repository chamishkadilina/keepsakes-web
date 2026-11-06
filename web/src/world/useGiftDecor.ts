import { useEffect, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import type * as THREE from 'three'
import { DEFAULT_SONG, FONTS_URL } from '../config/decor'
import { createGramophone, type Gramophone } from '../decor/gramophone'
import { createLoveNotes } from '../decor/loveNotes'
import type { Gift } from '../gift/gift'
import { visitorFeet } from '../store'
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

/**
 * The gramophone: their song, or the default one. There is no "open your gift" tap yet (BUILD_SPEC B3),
 * so her first tap or key press unlocks the sound.
 */
function useGramophone(scene: THREE.Object3D, gift: Gift | null, lit: boolean): void {
  const gramophone = useRef<Gramophone | null>(null)

  useEffect(() => {
    if (!lit || !gift) return
    let alive = true
    const unlock = () => gramophone.current?.unlock()
    createGramophone(scene, {
      song: gift.song ?? DEFAULT_SONG.url,
      title: gift.songTitle ?? DEFAULT_SONG.title,
      fontsUrl: FONTS_URL,
    })
      .then((made) => {
        if (alive) gramophone.current = made
        else made.dispose()
      })
      .catch((err) => console.error('Gramophone failed:', err))
    window.addEventListener('pointerup', unlock)
    window.addEventListener('keydown', unlock)
    return () => {
      alive = false
      window.removeEventListener('pointerup', unlock)
      window.removeEventListener('keydown', unlock)
      gramophone.current?.dispose()
      gramophone.current = null
    }
  }, [scene, gift, lit])

  // Her feet, not the camera: the camera is 3.2 m behind her, off the dance floor while she stands on it.
  useFrame((_, delta) => gramophone.current?.update(visitorFeet, delta))
}

/** The decor that lives and dies with the gift. `lit`: the museum's baked materials are in place. */
export function useGiftDecor(scene: THREE.Object3D, gift: Gift | null, lit: boolean): void {
  useLoveNotes(scene, gift?.reasons, lit)
  useGramophone(scene, gift, lit)
}
