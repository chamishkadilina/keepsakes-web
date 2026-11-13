/** Tuning for the decor that shows the gift's words (design/lighting.md). */
export const FONTS_URL = '/fonts'

/** Night birds now and then crossing the garden's sky (decor/nightBirds.ts): rare, like the shooting stars. */
export const NIGHT_BIRDS = {
  gap: [70, 160] as const, // seconds between flights (random in this range)
  flock: [1, 3] as const, // birds flying together
  speed: [6, 8] as const, // m/s
  height: [7, 12] as const, // m above the garden: low enough to cross the sky above its walls
  pass: [3, 18] as const, // m from the garden's middle where their straight line passes: over it, or close by
  reach: 60, // m from the middle where they appear and vanish
  middle: [45, -8] as const, // the garden's middle: three.js x, z
  span: 1.3, // m: wingspan (a night heron)
  colour: 0x9a9cb4, // pale grey-blue, lit by the moon and the garden's glow from below: they show against the dark sky
  firstWait: [20, 45] as const, // seconds before the first flight, so a visit sees one
}
