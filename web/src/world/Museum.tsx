import { useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { useWalk } from '../store'
import { useMuseumColliders } from './useMuseumColliders'

const MODEL_URL = '/models/museum.glb'

// Meshes exported without a material get glTF's default (fully metallic → black).
// Until the owner assigns materials in Blender (A3), show them as matte plaster.
const PLACEHOLDER = new THREE.MeshStandardMaterial({ color: '#ece6dc', roughness: 0.9, metalness: 0, side: THREE.DoubleSide })

/**
 * Loads the hand-made museum, hides `col_*` boxes, gives material-less meshes a
 * placeholder, and reports `spawn_her`. Colliders: useMuseumColliders.
 * Never builds geometry itself.
 */
export function Museum() {
  const { scene } = useGLTF(MODEL_URL)
  useMuseumColliders(scene)

  useEffect(() => {
    scene.traverse((obj) => {
      if (obj.name.startsWith('col_')) obj.visible = false
      if (obj instanceof THREE.Mesh) {
        if ((obj.material as THREE.Material).name === '') {
          console.warn(`museum.glb: "${obj.name}" has no material, using placeholder`)
          obj.material = PLACEHOLDER
        }
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material]
        mats.forEach((m) => (m.side = THREE.DoubleSide))
      }
    })
    scene.updateMatrixWorld(true)
    const spawn = scene.getObjectByName('spawn_her')
    const p = new THREE.Vector3()
    if (spawn) spawn.getWorldPosition(p)
    else console.warn('museum.glb has no spawn_her; using origin')
    useWalk.getState().setLoaded([p.x, p.y, p.z])
  }, [scene])

  return <primitive object={scene} />
}

useGLTF.preload(MODEL_URL)
