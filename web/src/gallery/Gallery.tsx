import { useEffect, useMemo } from 'react'
import { CuboidCollider, RigidBody } from '@react-three/rapier'
import * as THREE from 'three'
import { PLANT } from '../config/frames'
import { useGift } from '../gift/gift'
import { buildGallery } from './buildGallery'
import { GALLERY_MATERIALS } from './materials'
import { Photo } from './Photo'
import { findSlots } from './slots'

function floorsOf(scene: THREE.Object3D): THREE.Object3D[] {
  const floors: THREE.Object3D[] = []
  scene.traverse((obj) => {
    if (obj.name.startsWith('floor_')) floors.push(obj)
  })
  return floors
}

/** Fills the museum's slots with the gift's photos, frames built in code (BUILD_SPEC §5). */
export function Gallery({ scene }: { scene: THREE.Object3D }) {
  const gift = useGift((s) => s.gift)
  const slots = useMemo(() => findSlots(scene), [scene])
  const layout = useMemo(
    () => (gift ? buildGallery(slots, gift.photos, floorsOf(scene)) : null),
    [slots, gift, scene],
  )

  useEffect(() => {
    slots.planes.forEach((plane) => (plane.visible = false))
  }, [slots])

  useEffect(
    () => () => {
      if (!layout) return
      ;[layout.gold, layout.white, layout.pots, layout.leaves].forEach((g) => g?.dispose())
    },
    [layout],
  )

  if (!layout) return null
  const [hx, hy, hz] = PLANT.colliderHalf
  return (
    <group>
      {layout.gold && <mesh geometry={layout.gold} material={GALLERY_MATERIALS.gold} />}
      {layout.white && <mesh geometry={layout.white} material={GALLERY_MATERIALS.mat} />}
      {layout.pots && <mesh geometry={layout.pots} material={GALLERY_MATERIALS.pot} />}
      {layout.leaves && <mesh geometry={layout.leaves} material={GALLERY_MATERIALS.leaf} />}
      {layout.photos.map((placed) => (
        <Photo key={placed.key} placed={placed} />
      ))}
      {layout.plantSpots.length > 0 && (
        <RigidBody type="fixed" colliders={false}>
          {layout.plantSpots.map((p, i) => (
            <CuboidCollider key={i} args={[hx, hy, hz]} position={[p.x, p.y + hy, p.z]} />
          ))}
        </RigidBody>
      )}
    </group>
  )
}
