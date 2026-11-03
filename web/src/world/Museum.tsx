import { useEffect, useMemo, useRef, useState } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { LIGHTING } from '../config/lighting'
import { ROUTE } from '../config/route'
import { createRosePetals } from '../decor/rosePetals'
import { Gallery } from '../gallery/Gallery'
import { applyBakedLighting } from '../lighting/bakedLighting'
import { addCeilingLights } from '../lighting/ceilingLights'
import { createFloorReflection } from '../lighting/floorReflection'
import { useWalk } from '../store'
import { useMuseumColliders } from './useMuseumColliders'

const MODEL_URL = '/models/museum.glb'
const GARDEN_FLOOR = 'floor_6_garden' // grass: no reflection

type FloorReflection = ReturnType<typeof createFloorReflection>

/** Baked light, then the ceiling lamps (design/lighting.md). */
async function light(scene: THREE.Object3D): Promise<void> {
  await applyBakedLighting(scene, LIGHTING.lightmapDir)
  addCeilingLights(scene)
}

// Once per loaded scene (React may run effects twice; this must not apply twice).
const lit = new WeakMap<THREE.Object3D, Promise<void>>()
function lightOnce(scene: THREE.Object3D): Promise<void> {
  if (!lit.has(scene)) lit.set(scene, light(scene))
  return lit.get(scene)!
}

function woodFloors(scene: THREE.Object3D): THREE.Mesh[] {
  const floors: THREE.Mesh[] = []
  scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh && obj.name.startsWith('floor_') && obj.name !== GARDEN_FLOOR) floors.push(obj)
  })
  return floors
}

/**
 * Loads the hand-made museum, hides `col_*` boxes, applies its baked lighting,
 * ceiling lamps and floor reflection (design/lighting.md), scatters rose petals
 * along the route and reports `spawn_her`.
 * Colliders: useMuseumColliders. Photos and frames: Gallery.
 * Never builds geometry itself.
 */
export function Museum() {
  const { scene } = useGLTF(MODEL_URL)
  const gl = useThree((s) => s.gl)
  const root = useThree((s) => s.scene)
  const [ready, setReady] = useState(false)
  const reflection = useRef<FloorReflection | null>(null)
  const petals = useMemo(() => createRosePetals(ROUTE.waypoints), [])
  useMuseumColliders(scene)

  useEffect(() => {
    let alive = true
    scene.traverse((obj) => {
      if (obj.name.startsWith('col_')) obj.visible = false
    })
    lightOnce(scene)
      .then(() => {
        if (!alive) return
        reflection.current = createFloorReflection(gl, root, woodFloors(scene))
        setReady(true)
        const spawn = scene.getObjectByName('spawn_her')
        const p = new THREE.Vector3()
        if (spawn) spawn.getWorldPosition(p)
        else console.warn('museum.glb has no spawn_her; using origin')
        useWalk.getState().setLoaded([p.x, p.y, p.z])
      })
      .catch((err) => console.error('Baked lighting failed:', err))
    return () => {
      alive = false
      reflection.current?.dispose()
      reflection.current = null
    }
  }, [scene, gl, root])

  // Before R3F renders the frame. <Museum /> mounts after <Player /> so the camera has already moved.
  useFrame(({ camera }, delta) => {
    reflection.current?.update(camera)
    petals.update(camera.position, delta)
  })

  // Shown only once lit, so the unlit glTF materials never flash on screen.
  if (!ready) return null
  return (
    <>
      <primitive object={scene} />
      <primitive object={petals} />
      <Gallery scene={scene} />
    </>
  )
}

useGLTF.preload(MODEL_URL)
