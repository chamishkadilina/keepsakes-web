import { create } from 'zustand'

/** The museum label under a photo. */
export type PhotoCaption = {
  title: string
  date?: string
  text?: string // a line or two of their story
}

export type GiftPhoto = {
  src: string
  thumb: string
  w: number
  h: number
  caption?: PhotoCaption
}

export type Gift = {
  theirName: string
  yourName: string
  dedication: string // also the handwritten line on the welcome sign, up to ~20 words
  quote?: string // the quote board in the heart room, up to ~45 words; "\n" starts a new line
  date?: string // their special date, shown under their names on the quote board
  metDate?: string // the day they met, e.g. "3 June 2019": "Since …" on the welcome sign
  finalWords: string
  music: string
  photos: GiftPhoto[]
  roomKey: string
}

export const DEFAULT_QUOTE = 'You are my today and all of my tomorrows.'
export const NEON_TEXT = 'forever us'

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
