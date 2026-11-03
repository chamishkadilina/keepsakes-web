/**
 * Baked lighting (design/lighting.md). All light comes from the Blender bake,
 * applied by lighting/bakedLighting.ts. No real-time lights, no post-processing.
 */
export const LIGHTING = {
  lightmapDir: '/models/lightmaps',
  exposure: 1, // AgX tone mapping
  /** Linear sky colour = the bake's world colour (0.10, 0.12, 0.22) × strength 0.35. */
  sky: [0.035, 0.042, 0.077] as [number, number, number],
}
