import { useEffect } from 'react'
import { input } from './input'

/** Tracks held keys in `input.keys`; clears them when the window loses focus. */
export function useKeyboard() {
  useEffect(() => {
    const down = (e: KeyboardEvent) => input.keys.add(e.code)
    const up = (e: KeyboardEvent) => input.keys.delete(e.code)
    const clear = () => input.keys.clear()
    window.addEventListener('keydown', down)
    window.addEventListener('keyup', up)
    window.addEventListener('blur', clear)
    return () => {
      window.removeEventListener('keydown', down)
      window.removeEventListener('keyup', up)
      window.removeEventListener('blur', clear)
    }
  }, [])
}
