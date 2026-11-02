import * as THREE from 'three'
import { MATERIALS } from '../config/frames'

/** A warm gold matcap drawn on a canvas: looks metallic with no lights. */
function goldMatcap(): THREE.Texture {
  const size = MATERIALS.goldMatcapSize
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')!
  // Highlight up and to the left, falling off to a dark rim.
  const g = ctx.createRadialGradient(size * 0.38, size * 0.32, 0, size / 2, size / 2, size / 2)
  const stops = MATERIALS.goldMatcap
  stops.forEach((colour, i) => g.addColorStop(i / (stops.length - 1), colour))
  ctx.fillStyle = g
  ctx.fillRect(0, 0, size, size)
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  return texture
}

/**
 * Shared by every frame and plant, created once. Unlit: each vertex carries its
 * slot's baked light (buildGallery), which tints the albedo.
 */
export const GALLERY_MATERIALS = {
  gold: new THREE.MeshMatcapMaterial({ name: 'gallery_gold', matcap: goldMatcap(), vertexColors: true }),
  mat: new THREE.MeshBasicMaterial({ name: 'gallery_mat', color: MATERIALS.mat, vertexColors: true }),
  pot: new THREE.MeshBasicMaterial({ name: 'gallery_pot', color: MATERIALS.pot, vertexColors: true }),
  leaf: new THREE.MeshBasicMaterial({ name: 'gallery_leaf', color: MATERIALS.leaf, vertexColors: true }),
}
