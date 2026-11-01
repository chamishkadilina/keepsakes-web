import { PHOTO } from '../config/frames'

/** How a photo sits in its box: shown size in metres plus the texture crop. */
export type PhotoFit = {
  width: number
  height: number
  repeat: [number, number]
  offset: [number, number]
}

/**
 * Clamps the aspect to 9:16–16:9 (centre-cropping anything beyond), then
 * fits the photo inside the box without cropping further (contain).
 */
export function fitPhoto(photoW: number, photoH: number, boxW: number, boxH: number): PhotoFit {
  const aspect = photoW / photoH
  const shown = Math.min(PHOTO.maxAspect, Math.max(PHOTO.minAspect, aspect))
  const cropX = aspect > shown ? shown / aspect : 1
  const cropY = aspect < shown ? aspect / shown : 1
  const height = Math.min(boxH, boxW / shown)
  return {
    width: height * shown,
    height,
    repeat: [cropX, cropY],
    offset: [(1 - cropX) / 2, (1 - cropY) / 2],
  }
}
