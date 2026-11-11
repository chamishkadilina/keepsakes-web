/**
 * Baked lighting (design/lighting.md). All light comes from the Blender bake,
 * applied by lighting/bakedLighting.ts. No real-time lights, no post-processing.
 */
export const LIGHTING = {
  lightmapDir: '/models/lightmaps',
  exposure: 1, // AgX tone mapping
  cinema: {
    box: [26.5, -13, 38, -1.5] as const, // the screen room: x0, z0, x1, z1 (three.js metres), along the middle of its walls
    edge: 0.125, // soft edge, either side of the box: half a wall, so it stays inside the walls
    dimmed: 0.3, // its brightness while a video plays
    fade: 1.5, // seconds
  },
}
