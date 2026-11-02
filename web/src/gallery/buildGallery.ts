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

/**
 * Everything the gallery draws: a few merged meshes plus one plane per photo.
 * Merged meshes carry each slot's baked light as vertex colours (design/lighting.md);
 * photos never do: they show their exact original colours.
 */
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

  // Gold is a matcap: its light is normalised so the brightest slot = 1.
  const goldScale = 1 / brightestLight(slots)
  const add = (list: THREE.BufferGeometry[], geometry: THREE.BufferGeometry, matrix: THREE.Matrix4, light: THREE.Color) =>
    list.push(paint(geometry, light).applyMatrix4(matrix))
  const addGold = (geometry: THREE.BufferGeometry, matrix: THREE.Matrix4, light: THREE.Color) =>
    add(gold, geometry, matrix, light.clone().multiplyScalar(goldScale))

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
      add(white, quadGeometry(fit.width + 2 * m, fit.height + 2 * m, { x: 0, y: 0, z: FRAME.matZ }), centre, slot.light)
      addGold(mouldingGeometry(hw + m, hh + m), centre, slot.light)
    } else if (style === 'polaroid') {
      const w = fit.width + 2 * POLAROID.side
      const h = fit.height + POLAROID.top + POLAROID.bottom
      add(white, quadGeometry(w, h, { x: 0, y: (POLAROID.top - POLAROID.bottom) / 2, z: POLAROID.z }), centre, slot.light)
    } else {
      addGold(mouldingGeometry(hw, hh), centre, slot.light)
      add(white, quadGeometry(fit.width, fit.height, { x: 0, y: 0, z: -FRAME.wallGap }, true), centre, slot.light)
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
    add(pots, parts.pot, at, slot.light)
    parts.leaves.forEach((leaf) => add(leaves, leaf, at, slot.light))
    plantSpots.push(spot)
  }

  const assignment = assignPhotos(photos.length, slots)
  assignment.collage.forEach((index, slot) => placePhoto(slot, index, 'polaroid'))
  assignment.frames.forEach((index, slot) => placePhoto(slot, index, 'frame'))
  assignment.emptyFrames.forEach(placePlant)
  if (slots.centrepiece && assignment.centrepiece !== null) placePhoto(slots.centrepiece, assignment.centrepiece, 'board')
  if (slots.collageBoard) {
    const board = slots.collageBoard
    addGold(mouldingGeometry(board.width / 2, board.height / 2), board.matrix, board.light)
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

function brightestLight(slots: MuseumSlots): number {
  const all = [...slots.frames, ...slots.collage, slots.collageBoard, slots.centrepiece]
  return Math.max(...all.map((slot) => (slot ? Math.max(slot.light.r, slot.light.g, slot.light.b) : 0)), 1e-6)
}

/** Fills a geometry's vertex colours with one colour. */
function paint(geometry: THREE.BufferGeometry, color: THREE.Color): THREE.BufferGeometry {
  const count = geometry.getAttribute('position').count
  const colors = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) color.toArray(colors, i * 3)
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  return geometry
}

function merge(list: THREE.BufferGeometry[]): THREE.BufferGeometry | null {
  if (list.length === 0) return null
  const merged = mergeGeometries(list)
  list.forEach((g) => g.dispose())
  return merged
}
