/**
 * Baked lighting (design/lighting.md). All light comes from the Blender bake,
 * applied by lighting/bakedLighting.ts. No real-time lights, no post-processing.
 */
export const LIGHTING = {
  lightmapDir: '/models/lightmaps',
  exposure: 1, // AgX tone mapping
}
