import { useEffect, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { CapsuleCollider, RigidBody, useBeforePhysicsStep, useRapier, type RapierRigidBody } from '@react-three/rapier'
import type { Collider, KinematicCharacterController } from '@dimforge/rapier3d-compat'
import { Color, type Group, type MeshBasicMaterial } from 'three'
import { MOVEMENT, PHYSICS, PLAYER } from '../config/gameFeel'
import { resetLook } from '../input/input'
import { dampAngle } from '../lib/smoothing'
import { useWalk, visitorFeet } from '../store'
import { GARDEN, roomAt } from '../world/rooms'
import { cameraYaw, resetRig, updateCamera } from './cameraRig'
import { fadeOpacity, setOpacity } from './fade'
import { CAPSULE_CENTER, createController, newMoveState, stepMovement } from './movement'

// Unlit colours of the capsule and its nose.
const ALBEDO = [new Color('#e9a6a0'), new Color('#5a3b36')]

/**
 * Placeholder player: a capsule moved by the character controller in the
 * physics step. The camera runs in useFrame *after* the step (Physics
 * updatePriority = -1) and follows the capsule's interpolated position.
 */
export function Player() {
  const rapierCtx = useRapier()
  const { world, rapier } = rapierCtx
  const body = useRef<RapierRigidBody>(null)
  const collider = useRef<Collider>(null)
  const visual = useRef<Group>(null)
  const materials = useRef<MeshBasicMaterial[]>([])
  const controller = useRef<KinematicCharacterController | null>(null)
  const state = useRef(newMoveState())
  const opacity = useRef(1)
  const { loaded, spawn, spawnYaw, resetCount } = useWalk()

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
    v.rotation.y = dampAngle(v.rotation.y, state.current.heading, MOVEMENT.turnTime, dt)

    const aspect = frame.size.width / frame.size.height
    const motion = state.current.motion
    const dist = updateCamera(frame.camera, visitorFeet, motion, MOVEMENT.walkSpeed, rapierCtx, col, b, aspect, dt)

    opacity.current = fadeOpacity(opacity.current, dist, dt)
    setOpacity(materials.current, opacity.current)
    v.visible = opacity.current > 0.01
  })

  return (
    <RigidBody ref={body} type="kinematicPosition" colliders={false} position={[spawn[0], spawn[1] + CAPSULE_CENTER, spawn[2]]}>
      <CapsuleCollider ref={collider} args={[PLAYER.halfHeight, PLAYER.radius]} />
      <group ref={visual}>
        <mesh>
          <capsuleGeometry args={[PLAYER.radius, PLAYER.halfHeight * 2, 6, 16]} />
          <meshBasicMaterial ref={(m) => { if (m) materials.current[0] = m }} color={ALBEDO[0]} />
        </mesh>
        {/* Small "nose" so you can see which way the capsule faces. */}
        <mesh position={[0, 0.55, -PLAYER.radius]}>
          <boxGeometry args={[0.16, 0.08, 0.12]} />
          <meshBasicMaterial ref={(m) => { if (m) materials.current[1] = m }} color={ALBEDO[1]} />
        </mesh>
      </group>
    </RigidBody>
  )
}
