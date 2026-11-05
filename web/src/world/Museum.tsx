import { useEffect, useRef, useState } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { LIGHTING } from '../config/lighting'
import {
  EAST_PATH,
  EAST_PETALS,
  FLOOR_BALLOON_AREAS,
  GARDEN_PATH,
  GARDEN_PETALS,
  HEART_CENTRE,
  HEART_WIDTH,
  PETAL_PATH,
  RIGHT_PATH,
  RIGHT_PETALS,
} from '../config/route'
import { animateBalloons } from '../decor/balloons'
import { createFloorBalloons, type FloorBalloons } from '../decor/floorBalloons'
import { getFootprints, isOnFootprint } from '../decor/footprints'
import { createNeonSign } from '../decor/neonSign'
import { createQuoteBoard } from '../decor/quoteBoard'
import { createRosePetalHeart, createRosePetals, type RosePetals } from '../decor/rosePetals'
import { createWelcomeSign } from '../decor/welcomeSign'
import { Gallery } from '../gallery/Gallery'
import { DEFAULT_QUOTE, NEON_TEXT, useGift, type Gift } from '../gift/gift'
import { applyBakedLighting } from '../lighting/bakedLighting'
import { createCandleFlames } from '../lighting/candleFlames'
import { addCeilingLights } from '../lighting/ceilingLights'
import { createCurtainLights } from '../lighting/curtainLights'
import { createDuskSky } from '../lighting/duskSky'
import { createFloorReflection } from '../lighting/floorReflection'
import { createProjectorBeam } from '../lighting/projectorBeam'
import { useWalk, visitorFeet } from '../store'
import { useMuseumColliders } from './useMuseumColliders'
import { visitorStart } from './visitorStart'

const MODEL_URL = '/models/museum.glb'
const FONTS_URL = '/fonts'
const GARDEN_FLOOR = 'floor_6_garden' // grass: no reflection

type FloorReflection = ReturnType<typeof createFloorReflection>
type Decor = {
  flames: THREE.Object3D
  curtainLights: THREE.Points
  sky: THREE.Object3D
  beam: THREE.Group | null
  petals: RosePetals[]
  floorBalloons: FloorBalloons
}

/** Baked light, the ceiling lamps, then the balloons, which float in the baked materials (design/lighting.md). */
async function light(scene: THREE.Object3D): Promise<void> {
  await applyBakedLighting(scene, LIGHTING.lightmapDir)
  addCeilingLights(scene)
  animateBalloons(scene)
}

// Once per loaded scene (React may run effects twice; this must not apply twice).
const lit = new WeakMap<THREE.Object3D, Promise<void>>()
function lightOnce(scene: THREE.Object3D): Promise<void> {
  if (!lit.has(scene)) lit.set(scene, light(scene))
  return lit.get(scene)!
}

/** Their words: the neon sign, the welcome sign and the quote board. */
async function writeWords(scene: THREE.Object3D, gift: Gift): Promise<void> {
  const names = `${gift.yourName} & ${gift.theirName}`
  await lightOnce(scene)
  await createNeonSign(scene, { text: NEON_TEXT })
  await createWelcomeSign(scene, {
    names,
    date: gift.metDate && `Since ${gift.metDate}`,
    note: gift.dedication,
    fontsUrl: FONTS_URL,
  })
  await createQuoteBoard(scene, { quote: gift.quote || DEFAULT_QUOTE, names, date: gift.date })
}

// Once per loaded scene too: each sign replaces its board's material and texture.
const written = new WeakMap<THREE.Object3D, Promise<void>>()
function writeWordsOnce(scene: THREE.Object3D, gift: Gift): Promise<void> {
  if (!written.has(scene)) written.set(scene, writeWords(scene, gift))
  return written.get(scene)!
}

/** What stands beside the model: the candle flames, the little lights behind the sheers, the dusk sky, the projector's beam, and the petals and floor balloons, clear of the furniture. */
function createDecor(scene: THREE.Object3D, footprints: ReturnType<typeof getFootprints>): Decor {
  const avoid = (x: number, z: number) => isOnFootprint(footprints, x, z)
  return {
    flames: createCandleFlames(scene),
    curtainLights: createCurtainLights(scene),
    sky: createDuskSky(),
    beam: createProjectorBeam(scene),
    petals: [
      createRosePetals(PETAL_PATH, { avoid }),
      createRosePetalHeart(HEART_CENTRE, HEART_WIDTH, { avoid }),
      createRosePetals(EAST_PATH, { ...EAST_PETALS, avoid }),
      createRosePetals(RIGHT_PATH, { ...RIGHT_PETALS, avoid }),
      createRosePetals(GARDEN_PATH, { ...GARDEN_PETALS, avoid }),
    ],
    floorBalloons: createFloorBalloons(FLOOR_BALLOON_AREAS, { footprints }),
  }
}

function disposeDrawn(root: THREE.Object3D): void {
  root.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh || obj instanceof THREE.Points)) return
    obj.geometry.dispose()
    ;(obj.material as THREE.Material).dispose()
  })
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
 * ceiling lamps and floor reflection (design/lighting.md), adds the candle flames,
 * the little lights behind the sheers, the dusk sky, the projector's beam, the rose petals and the
 * floor balloons, floats the heart balloons, writes the neon sign, the welcome sign and the quote
 * board, and reports where she starts and the footprints.
 * Colliders: useMuseumColliders. Photos and frames: Gallery.
 * Never builds geometry itself.
 */
export function Museum() {
  const { scene } = useGLTF(MODEL_URL)
  const gl = useThree((s) => s.gl)
  const root = useThree((s) => s.scene)
  const [decor, setDecor] = useState<Decor | null>(null)
  const gift = useGift((s) => s.gift)
  const reflection = useRef<FloorReflection | null>(null)
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
        const footprints = getFootprints(scene)
        setDecor(createDecor(scene, footprints))
        const start = visitorStart(scene, 'spawn_her')
        useWalk.getState().setLoaded(start.position, start.yaw, footprints)
      })
      .catch((err) => console.error('Baked lighting failed:', err))
    return () => {
      alive = false
      reflection.current?.dispose()
      reflection.current = null
    }
  }, [scene, gl, root])

  useEffect(() => {
    if (!gift) return
    writeWordsOnce(scene, gift).catch((err) => console.error('Neon sign, welcome sign or quote board failed:', err))
  }, [scene, gift])

  useEffect(() => {
    if (!decor) return
    return () => {
      disposeDrawn(decor.curtainLights)
      if (decor.beam) disposeDrawn(decor.beam)
    }
  }, [decor])

  // Before R3F renders the frame. <Museum /> mounts after <Player /> so the camera has already moved.
  useFrame(({ camera }, delta) => {
    reflection.current?.update(camera)
    decor?.petals.forEach((petals) => petals.update(camera.position, delta))
    decor?.floorBalloons.update(visitorFeet, delta) // her feet: the camera is 3.2 m behind her
  })

  // Shown only once lit, so the unlit glTF materials never flash on screen.
  if (!decor) return null
  return (
    <>
      <primitive object={scene} />
      <primitive object={decor.flames} />
      <primitive object={decor.curtainLights} />
      <primitive object={decor.sky} />
      {decor.beam && <primitive object={decor.beam} />}
      {decor.petals.map((petals) => (
        <primitive key={petals.uuid} object={petals} />
      ))}
      <primitive object={decor.floorBalloons} />
      <Gallery scene={scene} />
    </>
  )
}

useGLTF.preload(MODEL_URL)
