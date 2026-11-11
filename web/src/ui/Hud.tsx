import { useEffect, useRef, useState } from 'react'
import { useWalk } from '../store'
import { Credits } from './Credits'

function format(ms: number) {
  const s = Math.floor(ms / 1000)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

const isTouch = matchMedia('(pointer: coarse)').matches
const HINT_VISIBLE_MS = 4000 // after the first step

/** Walk-test HUD: timer from first step to the garden, current room, restart. */
export function Hud() {
  const { room, startedAt, finishedAt, restart } = useWalk()
  const timeRef = useRef<HTMLDivElement>(null)
  const [hint, setHint] = useState(true)

  useEffect(() => {
    let frame = 0
    const tick = () => {
      const s = useWalk.getState()
      const ms = s.startedAt === null ? 0 : (s.finishedAt ?? performance.now()) - s.startedAt
      if (timeRef.current) timeRef.current.textContent = format(ms)
      frame = requestAnimationFrame(tick)
    }
    tick()
    return () => cancelAnimationFrame(frame)
  }, [])

  useEffect(() => {
    if (startedAt !== null) {
      const t = setTimeout(() => setHint(false), HINT_VISIBLE_MS)
      return () => clearTimeout(t)
    }
  }, [startedAt])

  const done = finishedAt !== null
  return (
    <>
      <div className="hud">
        <div>
          <div ref={timeRef} className={done ? 'hud-time done' : 'hud-time'}>0:00</div>
          <div className="hud-room">{done ? 'Reached the garden 🌹' : room}</div>
        </div>
        <div className="hud-buttons">
          <Credits />
          <button onClick={restart}>Restart</button>
        </div>
      </div>
      {hint && (
        <div className="hint">
          {isTouch ? 'Left thumb: walk · Right thumb: look' : 'WASD to walk · drag to look · Shift to run'}
        </div>
      )}
    </>
  )
}
