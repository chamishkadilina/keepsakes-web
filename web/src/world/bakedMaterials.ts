import * as THREE from 'three'
import type { Lightmaps } from './lightmaps'

// three's MeshBasicMaterial multiplies the lightmap by 1/π, so scale it back up.
const LIGHTMAP_FACTOR = Math.PI
const BLACK = new THREE.Color(0, 0, 0)

/**
 * Swaps every museum material for an unlit MeshBasicMaterial that draws the
 * baked light (design/lighting.md), and removes any exported lights.
 */
export function applyBakedMaterials(scene: THREE.Object3D, lightmaps: Lightmaps) {
  const lights: THREE.Object3D[] = []
  const shared = new Map<string, THREE.MeshBasicMaterial>()

  scene.traverse((obj) => {
    if (obj instanceof THREE.Light) lights.push(obj)
    if (!(obj instanceof THREE.Mesh) || obj.material instanceof THREE.MeshBasicMaterial) return
    const src = obj.material as THREE.MeshStandardMaterial
    const group = obj.userData.lightmap_group as string | undefined
    const key = `${src.uuid}:${group ?? obj.uuid}`
    let material = shared.get(key)
    if (!material) {
      material = bakedMaterial(obj, src, group, lightmaps)
      shared.set(key, material)
    }
    obj.material = material
  })

  lights.forEach((light) => light.removeFromParent())
}

function bakedMaterial(
  mesh: THREE.Mesh,
  src: THREE.MeshStandardMaterial,
  group: string | undefined,
  lightmaps: Lightmaps,
): THREE.MeshBasicMaterial {
  const material = new THREE.MeshBasicMaterial({ name: src.name, color: src.color, map: src.map, side: THREE.DoubleSide })
  const light = mesh.userData.light_rgb as [number, number, number] | undefined

  if (group) {
    material.lightMap = lightmaps.textures[group] ?? null
    material.lightMapIntensity = lightmaps.intensity * LIGHTMAP_FACTOR
    if (!material.lightMap) console.warn(`museum.glb: "${mesh.name}" has unknown lightmap_group "${group}"`)
  } else if (light) {
    material.color.multiply(new THREE.Color(...light))
  } else if (src.emissive && !src.emissive.equals(BLACK)) {
    material.color.copy(src.emissive).multiplyScalar(src.emissiveIntensity)
  } else {
    console.warn(`museum.glb: "${mesh.name}" has no lightmap_group or light_rgb; drawn unlit`)
  }
  return material
}
