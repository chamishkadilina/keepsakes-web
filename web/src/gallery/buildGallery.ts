import * as THREE from 'three'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { FRAME, PLANT, POLAROID } from '../config/frames'
import type { GiftPhoto } from '../gift/gift'
import { assignPhotos } from './assignPhotos'
import { fitPhoto, type PhotoFit } from './fitPhoto'
import { mouldingGeometry, quadGeometry } from './frameGeometry'
import { plantParts } from './plantGeometry'
import type { MuseumSlots, Slot } from './slots'

export type PlacedPhoto = {
  key: string
  photo: GiftPhoto
  fit: PhotoFit
  position: THREE.Vector3
  quaternion: THREE.Quaternion
}

/** Everything the gallery draws: a few merged meshes plus one plane per photo. */
export type GalleryLayout = {
  gold: THREE.BufferGeometry | null
  white: THREE.BufferGeometry | null
  pots: THREE.BufferGeometry | null
  leaves: THREE.BufferGeometry | null
  photos: PlacedPhoto[]
  plantSpots: THREE.Vector3[]
}

type Style = 'frame' | 'polaroid' | 'board'

const DOWN = new THREE.Vector3(0, -1, 0)

/** Builds frames, polaroids and plants around the slots for this gift's photos. */
export function buildGallery(slots: MuseumSlots, photos: GiftPhoto[], floors: THREE.Object3D[]): GalleryLayout {
  const gold: THREE.BufferGeometry[] = []
  const white: THREE.BufferGeometry[] = []
  const pots: THREE.BufferGeometry[] = []
  const leaves: THREE.BufferGeometry[] = []
  const placed: PlacedPhoto[] = []
  const plantSpots: THREE.Vector3[] = []

  const add = (list: THREE.BufferGeometry[], geometry: THREE.BufferGeometry, matrix: THREE.Matrix4) =>
    list.push(geometry.applyMatrix4(matrix))

  function placePhoto(slot: Slot, index: number, style: Style) {
    const photo = photos[index]
    const fit = fitPhoto(photo.w, photo.h, slot.width, slot.height)
    // A board photo rests its bottom edge on the easel ledge; others are centred.
    const y = style === 'board' ? (fit.height - slot.height) / 2 : 0
    const centre = new THREE.Matrix4().makeTranslation(0, y, 0).premultiply(slot.matrix)
    const hw = fit.width / 2
    const hh = fit.height / 2

    if (style === 'frame') {
      const m = FRAME.matWidth
      add(white, quadGeometry(fit.width + 2 * m, fit.height + 2 * m, { x: 0, y: 0, z: FRAME.matZ }), centre)
      add(gold, mouldingGeometry(hw + m, hh + m), centre)
    } else if (style === 'polaroid') {
      const w = fit.width + 2 * POLAROID.side
      const h = fit.height + POLAROID.top + POLAROID.bottom
      add(white, quadGeometry(w, h, { x: 0, y: (POLAROID.top - POLAROID.bottom) / 2, z: POLAROID.z }), centre)
    } else {
      add(gold, mouldingGeometry(hw, hh), centre)
      add(white, quadGeometry(fit.width, fit.height, { x: 0, y: 0, z: -FRAME.wallGap }, true), centre)
    }

    const position = new THREE.Vector3()
    const quaternion = new THREE.Quaternion()
    centre.decompose(position, quaternion, new THREE.Vector3())
    placed.push({ key: `${slot.name}:${index}`, photo, fit, position, quaternion })
  }

  function placePlant(slot: Slot) {
    const front = new THREE.Vector3().setFromMatrixColumn(slot.matrix, 2)
    const spot = new THREE.Vector3().setFromMatrixPosition(slot.matrix).addScaledVector(front, PLANT.wallDistance)
    const hit = new THREE.Raycaster(spot, DOWN).intersectObjects(floors, false)[0]
    if (!hit) return
    spot.y = hit.point.y
    const parts = plantParts(slot.number * 2.4)
    const at = new THREE.Matrix4().makeTranslation(spot.x, spot.y, spot.z)
    add(pots, parts.pot, at)
    parts.leaves.forEach((leaf) => add(leaves, leaf, at))
    plantSpots.push(spot)
  }

  const assignment = assignPhotos(photos.length, slots)
  assignment.collage.forEach((index, slot) => placePhoto(slot, index, 'polaroid'))
  assignment.frames.forEach((index, slot) => placePhoto(slot, index, 'frame'))
  assignment.emptyFrames.forEach(placePlant)
  if (slots.centrepiece && assignment.centrepiece !== null) placePhoto(slots.centrepiece, assignment.centrepiece, 'board')
  if (slots.collageBoard) {
    const board = slots.collageBoard
    add(gold, mouldingGeometry(board.width / 2, board.height / 2), board.matrix)
  }

  return {
    gold: merge(gold),
    white: merge(white),
    pots: merge(pots),
    leaves: merge(leaves),
    photos: placed,
    plantSpots,
  }
}

function merge(list: THREE.BufferGeometry[]): THREE.BufferGeometry | null {
  if (list.length === 0) return null
  const merged = mergeGeometries(list)
  list.forEach((g) => g.dispose())
  return merged
}
