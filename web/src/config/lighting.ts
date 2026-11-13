/**
 * Baked lighting (design/lighting.md). All light comes from the Blender bake,
 * applied by lighting/bakedLighting.ts. No real-time lights, no post-processing.
 */
export const LIGHTING = {
  lightmapDir: '/models/lightmaps',
  exposure: 1, // AgX tone mapping
  gardenLights: { size: 0.17, colour: 0xffc98a, wind: true }, // the little lights in the garden's tree, draped to the walls and strung over the entrance: m, warm; they sway with it
  foliageMipScale: 0.35, // leaf cards: how much their alpha is raised per halving of their texture (foliage.ts)
  cinema: {
    box: [26.5, -13, 38, -1.5] as const, // the screen room: x0, z0, x1, z1 (three.js metres), along the middle of its walls
    edge: 0.125, // soft edge, either side of the box: half a wall, so it stays inside the walls
    dimmed: 0.3, // its brightness while a video plays
    fade: 1.5, // seconds
  },
  nightSky: {
    moon: { azimuth: 105, elevation: 26 }, // degrees: east-south-east, ahead of the bench (tools/bake/design.py MOON)
    meteorGap: [35, 90] as const, // seconds between shooting stars (random in this range): rare, a little gift each time
    meteorTime: [1.0, 1.6] as const, // seconds each one takes to cross
    meteorAzimuth: [25, 155] as const, // degrees from north: the sky ahead of the bench, where the couple look
    meteorElevation: [30, 65] as const, // degrees above the horizon where it starts
    meteorFall: [14, 24] as const, // degrees it drops
    meteorDrift: [8, 20] as const, // degrees it slides sideways (left or right)
  },
  fireflies: {
    count: 16, // a few, not a swarm
    blinkEvery: [12, 35] as const, // seconds between one firefly's flashes (each its own, in this range)
    area: [39.5, -14.5, 50.5, -1.5] as const, // the garden inside its border: x0, z0, x1, z1 (three.js metres)
    height: [0.3, 2.2] as const, // m above the grass
    drift: 0.7, // m each one wanders from its spot
    colour: 0xd8ff8a, // soft yellow-green
  },
  wind: {
    speed: 1.1, // radians per second for a 1 m plant; taller ones sway slower
    direction: 30, // degrees from three.js +x towards +z: where the breeze blows (each plant leans a little its own way)
    amplitude: 0.024, // m of sway at the top per √m of height: the big tree about 8 cm, a fern about 2 cm. Cosy, not stormy
    stiffness: 1.3, // low down they hardly move
    flutter: 0.008, // m: leaves trembling softly
    still: ['trunk', 'bark', 'branches', 'twigs'], // parts that sway but don't tremble
    treeHeight: 11, // m: the big jacaranda (tools/bake/garden_assets.py TREES); its little lights sway with it
  },
  campfire: {
    flameHeight: 0.95, // m: the tallest tongues of flame
    flameWidth: 0.42, // m: each tongue at its widest
    tongues: 30, // flames born on the coals, licking up, breaking off and fading, again and again
    flameBase: 0.2, // m: the spread of the coals they rise from
    coalRadius: 0.42, // m: the bed of glowing coals in the pit
    sparks: 60,
    sparkRise: 2.6, // m a spark rises before it fades
    smoke: 10,
    smokeRise: 2.8, // m the smoke curls up before it fades
    glowRadius: 3.2, // m: the flicker of its light on the grass
    glowStrength: 0.22,
    logs: ['prop_garden_firewood_bark', 'prop_garden_firewood_end', 'prop_garden_dry_branches_medium_01'], // charred and glowing where the fire licks them
  },
}
