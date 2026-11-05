import { useEffect } from 'react'
import { interactionGroups, useRapier } from '@react-three/rapier'
import type { Collider, ColliderDesc } from '@dimforge/rapier3d-compat'
import * as THREE from 'three'

type RapierApi = ReturnType<typeof useRapier>['rapier']

const EPS = 1e-4

// Floors have their own collision group so the ground ray can see only them.
const SOLID_GROUPS = interactionGroups(0)
const FLOOR_GROUPS = interactionGroups(1)
export const GROUND_RAY_GROUPS = interactionGroups([0, 1], [1])

/** True when every vertex sits on a corner of the mesh's bounding box. */
function isAxisAlignedBox(positions: ArrayLike<number>, box: THREE.Box3): boolean {
  for (let i = 0; i < positions.length; i += 3) {
    const onX = Math.abs(positions[i] - box.min.x) < EPS || Math.abs(positions[i] - box.max.x) < EPS
    const onY = Math.abs(positions[i + 1] - box.min.y) < EPS || Math.abs(positions[i + 1] - box.max.y) < EPS
    const onZ = Math.abs(positions[i + 2] - box.min.z) < EPS || Math.abs(positions[i + 2] - box.max.z) < EPS
    if (!onX || !onY || !onZ) return false
  }
  return true
}

/**
 * Box-shaped meshes (floors, `col_*` boxes) become cuboids: a flat top with no
 * triangle seams for the character controller to catch on. Everything else
 * (walls) becomes a trimesh with internal-edge fixing.
 */
function colliderFor(mesh: THREE.Mesh, rapier: RapierApi): ColliderDesc {
  const geometry = (mesh.geometry as THREE.BufferGeometry).clone().applyMatrix4(mesh.matrixWorld)
  const positions = geometry.attributes.position.array
  geometry.computeBoundingBox()
  const box = geometry.boundingBox!

  if (isAxisAlignedBox(positions, box)) {
    geometry.dispose()
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())
    return rapier.ColliderDesc.cuboid(size.x / 2, size.y / 2, size.z / 2).setTranslation(center.x, center.y, center.z)
  }

  const vertices = new Float32Array(positions)
  const indices = geometry.index
    ? new Uint32Array(geometry.index.array)
    : Uint32Array.from({ length: vertices.length / 3 }, (_, i) => i)
  geometry.dispose()
  return rapier.ColliderDesc.trimesh(vertices, indices, rapier.TriMeshFlags.FIX_INTERNAL_EDGES)
}

/**
 * Turns the museum's meshes (walls, floors and invisible `col_*` boxes) into
 * fixed colliders in world space. Built by hand instead of
 * `<RigidBody colliders="trimesh">` so floors can be seam-free cuboids.
 * `prop_*` meshes are skipped: each holds one material of all the furniture in
 * the museum, and the visitor walks round the footprints instead (movement.ts).
 */
export function useMuseumColliders(scene: THREE.Object3D) {
  const { world, rapier } = useRapier()

  useEffect(() => {
    scene.updateMatrixWorld(true)
    const body = world.createRigidBody(rapier.RigidBodyDesc.fixed())
    const colliders: Collider[] = []
    scene.traverse((obj) => {
      if (!(obj instanceof THREE.Mesh) || obj.name.startsWith('prop_')) return
      const groups = obj.name.startsWith('floor_') ? FLOOR_GROUPS : SOLID_GROUPS
      colliders.push(world.createCollider(colliderFor(obj, rapier).setCollisionGroups(groups), body))
    })
    return () => {
      colliders.forEach((c) => world.removeCollider(c, false))
      world.removeRigidBody(body)
    }
  }, [scene, world, rapier])
}
