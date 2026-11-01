import { useWalk } from '../store'

/** Full-screen cover until the museum has loaded. */
export function Loading() {
  const loaded = useWalk((s) => s.loaded)
  if (loaded) return null
  return <div className="loading">Loading the museum…</div>
}
