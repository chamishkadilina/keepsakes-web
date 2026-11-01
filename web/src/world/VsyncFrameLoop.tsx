import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'

/**
 * Drives r3f with the browser's frame timestamp (vsync-aligned) rather than
 * performance.now() read inside the callback, which wobbles slightly from
 * frame to frame. Steadier deltas = steadier camera follow.
 * Use with <Canvas frameloop="never">.
 */
export function VsyncFrameLoop() {
  const advance = useThree((s) => s.advance)
  const clock = useThree((s) => s.clock)

  useEffect(() => {
    let id = 0
    let first = true
    const tick = (ms: number) => {
      const t = ms / 1000
      if (first) {
        clock.elapsedTime = t // first frame: delta 0, not "time since page load"
        first = false
      }
      advance(t)
      id = requestAnimationFrame(tick)
    }
    id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [advance, clock])

  return null
}
