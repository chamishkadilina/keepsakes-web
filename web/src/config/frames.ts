/**
 * Every tuning value for photos, frames and the empty-frame plant.
 * Sizes in metres. "z" is measured from the slot plane, positive = into the room.
 */

/** Which photo goes where (BUILD_SPEC §5). */
export const ASSIGN = {
  collageCount: 12, // the first 12 photos go on the collage board
  defaultPriority: 3, // used when a slot_frame_NN has no "priority" property
}

export const PHOTO = {
  minAspect: 9 / 16, // taller photos are centre-cropped to this
  maxAspect: 16 / 9, // wider photos are centre-cropped to this
  fullResDistance: 4, // m from the camera: swap the thumbnail for the full photo
  anisotropy: 8,
}

/** Gallery frame: white mat + gold mitred moulding. */
export const FRAME = {
  matWidth: 0.08,
  matZ: -0.005, // mat sits just behind the photo
  mouldingWidth: 0.06,
  mouldingDepth: 0.04,
  wallGap: 0.03, // slot planes sit this far in front of the wall; the moulding's back touches the wall
  /**
   * Moulding cross-section, inner edge → outer edge, as [across 0–1 of the width,
   * height 0–1 of the depth above the wall]. Swept around the photo with mitred corners.
   */
  profile: [
    [0, 0.6],
    [0, 0.85],
    [0.35, 1],
    [0.75, 1],
    [1, 0.7],
    [1, 0],
  ] as const,
}

/** Collage photos: thin white polaroid border. */
export const POLAROID = {
  side: 0.025,
  top: 0.025,
  bottom: 0.07,
  z: -0.001,
}

/** Albedo colours; the baked light per slot multiplies them (design/lighting.md). */
export const MATERIALS = {
  mat: '#ffffff',
  pot: '#b0674a',
  leaf: '#4f7d3a',
  /** Gold matcap, generated in code: highlight → body → shadow from the centre out. */
  goldMatcap: ['#fff4d0', '#e0b85c', '#a87a2c', '#4a3210'] as const,
  goldMatcapSize: 256,
}

/** Placeholder shown on the floor below an empty frame. */
export const PLANT = {
  wallDistance: 0.35, // m from the slot plane into the room
  potRadiusTop: 0.14,
  potRadiusBottom: 0.1,
  potHeight: 0.28,
  leafCount: 7,
  leafLength: 0.42,
  leafWidth: 0.07,
  leafTilt: 0.45, // rad from vertical
  colliderHalf: [0.2, 0.35, 0.2] as const, // so the player can't walk through it
}
