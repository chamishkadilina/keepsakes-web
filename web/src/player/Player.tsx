import { useEffect, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { CapsuleCollider, RigidBody, useBeforePhysicsStep, useRapier, type RapierRigidBody } from '@react-three/rapier'
import type { Collider, KinematicCharacterController } from '@dimforge/rapier3d-compat'
import type { Group, Material, Mesh } from 'three'
import { MAX_SPEED } from '../characters/character'
import { useGirl } from '../characters/useGirl'
import { GAZE, MOVEMENT, PHYSICS, PLAYER } from '../config/gameFeel'
import { nearestPhoto } from '../gallery/photoSpots'
import { resetLook } from '../input/input'
import { turnAngle } from '../lib/smoothing'
import { useWalk, visitorFeet } from '../store'
import { GARDEN, roomAt } from '../world/rooms'
import { cameraYaw, resetRig, updateCamera } from './cameraRig'
import { fadeOpacity, setOpacity } from './fade'
import { CAPSULE_CENTER, createController, newMoveState, stepMovement } from './movement'

/**
 * Her: a collision capsule moved by the character controller in the physics
 * step, with her character (girl.glb) standing in it. The camera runs in
 * useFrame *after* the step (Physics updatePriority = -1) and follows the
 * capsule's interpolated position.
 */
export function Player() {
  const rapierCtx = useRapier()
  const { world, rapier } = rapierCtx
  const body = useRef<RapierRigidBody>(null)
  const collider = useRef<Collider>(null)
  const visual = useRef<Group>(null)
  const materials = useRef<Material[]>([])
  const controller = useRef<KinematicCharacterController | null>(null)
  const state = useRef(newMoveState())
  const opacity = useRef(1)
  const { loaded, spawn, spawnYaw, resetCount } = useWalk()
  const girl = useGirl()

  // Collect her materials for the camera fade.
  useEffect(() => {
    const list: Material[] = []
    girl?.object.traverse((o) => {
      if ((o as Mesh).isMesh) list.push((o as Mesh).material as Material)
    })
    materials.current = list
    opacity.current = 1
  }, [girl])

  useEffect(() => {
    const c = createController(world)
    controller.current = c
    return () => world.removeCharacterController(c)
  }, [world])

  // Place at spawn_her on load and on Restart, facing the title wall.
  useEffect(() => {
    const p = { x: spawn[0], y: spawn[1] + CAPSULE_CENTER + MOVEMENT.skin, z: spawn[2] }
    body.current?.setTranslation(p, true)
    body.current?.setNextKinematicTranslation(p)
    state.current = { ...newMoveState(), heading: spawnYaw }
    if (visual.current) visual.current.rotation.y = spawnYaw
    resetLook(spawnYaw)
    resetRig()
  }, [loaded, spawn, spawnYaw, resetCount])

  useBeforePhysicsStep((w) => {
    const b = body.current
    const col = collider.current
    const c = controller.current
    if (!b || !col || !c) return
    const dt = Math.min(w.timestep, PHYSICS.maxDelta)
    const walk = useWalk.getState()
    const next = stepMovement(state.current, c, world, rapier, col, b, cameraYaw(), walk.footprints, dt)
    b.setNextKinematicTranslation(next)

    if (state.current.moved) walk.start()
    const room = roomAt(next.x, next.z)
    walk.setRoom(room)
    if (room === GARDEN) walk.finish()
    if (next.y < MOVEMENT.fallResetHeight) walk.restart()
  })

  useFrame((frame, delta) => {
    const v = visual.current
    const col = collider.current
    const b = body.current
    if (!v || !col || !b) return
    const dt = Math.min(delta, PHYSICS.maxDelta)

    v.getWorldPosition(visitorFeet)
    visitorFeet.y -= CAPSULE_CENTER
    v.rotation.y = turnAngle(v.rotation.y, state.current.heading, MOVEMENT.turnTime, MOVEMENT.turnSpeed, dt)

    const aspect = frame.size.width / frame.size.height
    const motion = state.current.motion
    const dist = updateCamera(frame.camera, visitorFeet, motion, MOVEMENT.walkSpeed, rapierCtx, col, b, aspect, dt)

    opacity.current = fadeOpacity(opacity.current, dist, dt)
    setOpacity(materials.current, opacity.current)
    v.visible = opacity.current > 0.01

    if (girl) {
      const groundSpeed = Math.min(state.current.groundSpeed, MAX_SPEED)
      girl.move(groundSpeed)
      girl.lookAt(groundSpeed < GAZE.stillBelow ? nearestPhoto(visitorFeet, GAZE.photoReach) : null)
      girl.update(dt)
    }
  })

  return (
    <RigidBody ref={body} type="kinematicPosition" colliders={false} position={[spawn[0], spawn[1] + CAPSULE_CENTER, spawn[2]]}>
      <CapsuleCollider ref={collider} args={[PLAYER.halfHeight, PLAYER.radius]} />
      <group ref={visual}>
        {/* Her feet at the capsule's bottom; she faces +Z, the capsule's heading faces −Z. */}
        {girl && <primitive object={girl.object} position-y={-CAPSULE_CENTER} rotation-y={Math.PI} />}
      </group>
    </RigidBody>
  )
}
