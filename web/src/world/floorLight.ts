import * as THREE from 'three'
import { LIGHTING } from '../config/lighting'

/** Reads the baked floor light under any point (for tinting characters). */
let floors: THREE.Object3D[] = []
let pixels: ImageData | null = null
let intensity = 0

const ray = new THREE.Raycaster()
const DOWN = new THREE.Vector3(0, -1, 0)
const origin = new THREE.Vector3()

/** Called once the museum is loaded: the floor meshes and their lightmap. */
export function setFloorLight(floorMeshes: THREE.Object3D[], lightmap: THREE.Texture, lightmapIntensity: number) {
  const image = lightmap.image as HTMLImageElement
  const canvas = document.createElement('canvas')
  canvas.width = image.width
  canvas.height = image.height
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(image, 0, 0)
  pixels = ctx.getImageData(0, 0, image.width, image.height)
  floors = floorMeshes
  intensity = lightmapIntensity
}

/** Writes the linear light on the floor below `feet` into `out`. False if there is no floor. */
export function floorLightAt(feet: THREE.Vector3, out: THREE.Color): boolean {
  if (!pixels) return false
  origin.set(feet.x, feet.y + LIGHTING.floorProbeHeight, feet.z)
  ray.set(origin, DOWN)
  const uv = ray.intersectObjects(floors, false)[0]?.uv1
  if (!uv) return false
  // flipY is false: v = 0 is the top row of the image.
  const x = THREE.MathUtils.clamp(Math.floor(uv.x * pixels.width), 0, pixels.width - 1)
  const y = THREE.MathUtils.clamp(Math.floor(uv.y * pixels.height), 0, pixels.height - 1)
  const i = (y * pixels.width + x) * 4
  const d = pixels.data
  out.setRGB(d[i] / 255, d[i + 1] / 255, d[i + 2] / 255, THREE.SRGBColorSpace).multiplyScalar(intensity)
  return true
}
