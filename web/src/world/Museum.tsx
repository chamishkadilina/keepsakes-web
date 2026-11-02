import { useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { Gallery } from '../gallery/Gallery'
import { useWalk } from '../store'
import { applyBakedMaterials } from './bakedMaterials'
import { setFloorLight } from './floorLight'
import { useLightmaps } from './lightmaps'
import { useMuseumColliders } from './useMuseumColliders'

const MODEL_URL = '/models/museum.glb'

/**
 * Loads the hand-made museum, hides `col_*` boxes, draws it with its baked
 * lightmaps (design/lighting.md) and reports `spawn_her`.
 * Colliders: useMuseumColliders. Photos and frames: Gallery.
 * Never builds geometry itself.
 */
export function Museum() {
  const { scene } = useGLTF(MODEL_URL)
  const lightmaps = useLightmaps()
  useMuseumColliders(scene)

  useEffect(() => {
    const floors: THREE.Object3D[] = []
    scene.traverse((obj) => {
      if (obj.name.startsWith('col_')) obj.visible = false
      if (obj.userData.lightmap_group === 'floors') floors.push(obj)
    })
    applyBakedMaterials(scene, lightmaps)
    scene.updateMatrixWorld(true)
    if (lightmaps.textures.floors) setFloorLight(floors, lightmaps.textures.floors, lightmaps.intensity)
    const spawn = scene.getObjectByName('spawn_her')
    const p = new THREE.Vector3()
    if (spawn) spawn.getWorldPosition(p)
    else console.warn('museum.glb has no spawn_her; using origin')
    useWalk.getState().setLoaded([p.x, p.y, p.z])
  }, [scene, lightmaps])

  return (
    <>
      <primitive object={scene} />
      <Gallery scene={scene} />
    </>
  )
}

useGLTF.preload(MODEL_URL)
