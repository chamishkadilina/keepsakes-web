import { create } from 'zustand'

type Vec3 = [number, number, number]

/** Walk-test state: spawn point, current room and the entrance → garden timer. */
type WalkState = {
  loaded: boolean
  spawn: Vec3
  room: string
  startedAt: number | null
  finishedAt: number | null
  resetCount: number
  setLoaded: (spawn: Vec3) => void
  setRoom: (room: string) => void
  start: () => void
  finish: () => void
  restart: () => void
}

export const useWalk = create<WalkState>((set, get) => ({
  loaded: false,
  spawn: [0, 0, 0], // replaced by spawn_her when the museum loads
  room: '',
  startedAt: null,
  finishedAt: null,
  resetCount: 0,
  setLoaded: (spawn) => set({ loaded: true, spawn }),
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
