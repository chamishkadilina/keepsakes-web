import { useCallback, useEffect, type RefObject } from 'react'
import { CONTROLS } from '../config/gameFeel'
import { addLook } from './input'

/** Desktop: click to lock the pointer and look with the mouse; Esc releases (browser default). */
export function usePointerLock(target: RefObject<HTMLElement>) {
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (document.pointerLockElement !== target.current) return
      addLook(-e.movementX * CONTROLS.pointerLockLook, e.movementY * CONTROLS.pointerLockLook)
    }
    document.addEventListener('mousemove', onMove)
    return () => document.removeEventListener('mousemove', onMove)
  }, [target])

  return useCallback(() => {
    const el = target.current
    // Some browsers return a promise that rejects if the user exits quickly.
    if (el && document.pointerLockElement !== el) Promise.resolve(el.requestPointerLock()).catch(() => {})
  }, [target])
}
