import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Physics } from '@react-three/rapier'
import { CAMERA, PHYSICS } from './config/gameFeel'
import { Controls } from './input/Controls'
import { useKeyboard } from './input/useKeyboard'
import { Player } from './player/Player'
import { Hud } from './ui/Hud'
import { Loading } from './ui/Loading'
import { Lighting } from './world/Lighting'
import { Museum } from './world/Museum'
import { VsyncFrameLoop } from './world/VsyncFrameLoop'

export function App() {
  useKeyboard()
  return (
    <>
      <Canvas
        frameloop="never"
        dpr={[1, 2]}
        camera={{ fov: CAMERA.fovWalk, near: CAMERA.near, far: CAMERA.far }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
      >
        <VsyncFrameLoop />
        <Lighting />
        <Suspense fallback={null}>
          {/* Steps before default useFrames (priority 0), so the camera sees this frame's interpolated player. */}
          <Physics timeStep={PHYSICS.timeStep} interpolate updatePriority={-1}>
            <Museum />
            <Player />
          </Physics>
        </Suspense>
      </Canvas>
      <Controls />
      <Hud />
      <Loading />
    </>
  )
}
