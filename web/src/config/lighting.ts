/**
 * Baked lighting (design/lighting.md). All light comes from the Blender bake:
 * lightmaps for static meshes, `light_rgb` per slot. No real-time lights.
 */
export const LIGHTING = {
  lightmapDir: '/models/lightmaps',
  manifest: 'lightmaps.json',
  lightmapAnisotropy: 4,
  exposure: 1, // AgX tone mapping
  /** Linear sky colour = the bake's world colour (0.10, 0.12, 0.22) × strength 0.35. */
  sky: [0.035, 0.042, 0.077] as [number, number, number],
  /** Used (with a warning) for a slot exported without `light_rgb`. */
  fallbackLight: [0.2, 0.2, 0.2] as const,
  characterTintTime: 0.3, // s to follow the floor light under the player
  floorProbeHeight: 0.5, // m above the feet the floor ray starts
}
