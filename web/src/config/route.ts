/**
 * The walking route (design/route.md) as floor waypoints [x, z] in three.js
 * coordinates (Blender (x, y) → three.js (x, −y)): entrance → foyer → around the
 * story partition → heart room → right gallery loop → strip → screen room → garden.
 */
export const ROUTE = {
  waypoints: [
    [5.5, -0.5], [5.5, -5], [9.4, -9], [9.4, -11], [8.4, -13], [8.4, -18.5], [5.5, -19.4],
    [2.6, -18.5], [2.6, -12], [5.5, -11.6], [8.5, -12], [11, -12], [14, -12], [17, -14], [20, -12],
    [23, -12], [24.75, -14.5], [30, -17], [36, -17.5], [36, -15], [30, -15], [24.75, -13],
    [24.75, -8], [24.75, -3.2], [26.5, -3.2], [29, -4.5], [32.25, -7], [35.5, -6.5], [38, -6.5],
    [42, -7], [45, -8]
  ] as [number, number][],
}
