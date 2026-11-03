import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { AgXToneMapping, SRGBColorSpace } from 'three'
import { Physics } from '@react-three/rapier'
import { CAMERA, PHYSICS } from './config/gameFeel'
import { LIGHTING } from './config/lighting'
import { Controls } from './input/Controls'
import { useKeyboard } from './input/useKeyboard'
import { Player } from './player/Player'
import { Hud } from './ui/Hud'
import { Loading } from './ui/Loading'
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
        gl={{
          antialias: true,
          powerPreference: 'high-performance',
          toneMapping: AgXToneMapping,
          toneMappingExposure: LIGHTING.exposure,
          outputColorSpace: SRGBColorSpace,
        }}
      >
        <VsyncFrameLoop />
        {/* No lights and no post-processing: all light is baked (design/lighting.md). */}
        <color attach="background" args={LIGHTING.sky} />
        <Suspense fallback={null}>
          {/* Steps before default useFrames (priority 0), so the camera sees this frame's interpolated player. */}
          <Physics timeStep={PHYSICS.timeStep} interpolate updatePriority={-1}>
            {/* Player first: its camera update runs before the museum's floor reflection each frame. */}
            <Player />
            <Museum />
          </Physics>
        </Suspense>
      </Canvas>
      {/* Soft dark corners: a CSS overlay, so no shader ever touches the photos. */}
      <div className="vignette" />
      <Controls />
      <Hud />
      <Loading />
    </>
  )
}
