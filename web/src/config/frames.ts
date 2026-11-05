/**
 * Tuning for photos, frames and the collage. Sizes in metres.
 * The frames themselves come from frames/photoFrame.ts and frames/collageWall.ts (design/lighting.md).
 */

/** Which photo goes where (BUILD_SPEC §5). */
export const ASSIGN = {
  collageCount: 12, // the first 12 photos go on the collage
  // Turns in the frames' fill order that slot_frame_01–03 held before they left the foyer: those photos join the collage.
  foyerTurns: [0, 1, 6],
  defaultPriority: 3, // used when a slot_frame_NN has no "priority" property
}

export const PHOTO = {
  fullResDistance: 4, // m from the camera: swap the thumbnail for the full photo
  anisotropy: 8,
}

/** The collage in the heart-room niche, centred on `collage_board`: the niche opening (design/lighting.md). */
export const COLLAGE = {
  width: 5.28,
  height: 3.04,
}
