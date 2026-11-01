import { create } from 'zustand'

export type GiftPhoto = {
  src: string
  thumb: string
  w: number
  h: number
  caption: string
}

export type Gift = {
  theirName: string
  yourName: string
  dedication: string
  finalWords: string
  music: string
  photos: GiftPhoto[]
  roomKey: string
}

const DEMOS = ['6', '30']
const DEFAULT_DEMO = '30'

/** `?demo=6` or `?demo=30` picks the demo gift file (BUILD_SPEC §5). */
function demoUrl(): string {
  const asked = new URLSearchParams(window.location.search).get('demo') ?? DEFAULT_DEMO
  const demo = DEMOS.includes(asked) ? asked : DEFAULT_DEMO
  return `/demo/demo-gift-${demo}.json`
}

export const useGift = create<{ gift: Gift | null }>(() => ({ gift: null }))

fetch(demoUrl())
  .then((res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.url}`)
    return res.json() as Promise<Gift>
  })
  .then((gift) => useGift.setState({ gift }))
  .catch((err) => console.error('Could not load the demo gift:', err))
