import { Vector3 } from 'three'
import { create } from 'zustand'
import type { Footprint } from './decor/footprints'

type Vec3 = [number, number, number]

/** Walk-test state: spawn point, current room and the entrance → garden timer. */
type WalkState = {
  loaded: boolean
  spawn: Vec3
  spawnYaw: number
  footprints: Footprint[]
  room: string
  startedAt: number | null
  finishedAt: number | null
  resetCount: number
  setLoaded: (spawn: Vec3, spawnYaw: number, footprints: Footprint[]) => void
  setRoom: (room: string) => void
  start: () => void
  finish: () => void
  restart: () => void
}

/** Her feet, moved by Player every frame. Not in the store: that would re-render every frame. */
export const visitorFeet = new Vector3()

export const useWalk = create<WalkState>((set, get) => ({
  loaded: false,
  spawn: [0, 0, 0], // replaced by spawn_her when the museum loads
  spawnYaw: 0, // turned to the title wall when the museum loads
  footprints: [], // where the furniture stands, also set when the museum loads
  room: '',
  startedAt: null,
  finishedAt: null,
  resetCount: 0,
  setLoaded: (spawn, spawnYaw, footprints) => set({ loaded: true, spawn, spawnYaw, footprints }),
  setRoom: (room) => {
    if (get().room !== room) set({ room })
  },
  start: () => {
    if (get().startedAt === null) set({ startedAt: performance.now() })
  },
  finish: () => {
    const { startedAt, finishedAt } = get()
    if (startedAt !== null && finishedAt === null) set({ finishedAt: performance.now() })
  },
  restart: () => set((s) => ({ startedAt: null, finishedAt: null, resetCount: s.resetCount + 1 })),
}))
