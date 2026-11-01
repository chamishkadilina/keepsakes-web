import { useEffect, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { PHOTO } from '../config/frames'
import type { PlacedPhoto } from './buildGallery'
import type { PhotoFit } from './fitPhoto'

const loader = new THREE.TextureLoader()

function loadTexture(url: string, fit: PhotoFit): Promise<THREE.Texture> {
  return loader.loadAsync(url).then((texture) => {
    texture.colorSpace = THREE.SRGBColorSpace
    texture.anisotropy = PHOTO.anisotropy
    texture.repeat.set(...fit.repeat)
    texture.offset.set(...fit.offset)
    return texture
  })
}

/** One photo: shows the thumbnail first, swaps to full size when the camera comes close. */
export function Photo({ placed }: { placed: PlacedPhoto }) {
  const { photo, fit, position, quaternion } = placed
  const [texture, setTexture] = useState<THREE.Texture | null>(null)
  const alive = useRef(true)
  const wantFull = useRef(false)

  useEffect(() => {
    alive.current = true
    loadTexture(photo.thumb, fit)
      .then((t) => (alive.current && !wantFull.current ? setTexture(t) : t.dispose()))
      .catch((err) => console.error('Photo thumbnail failed:', photo.thumb, err))
    return () => {
      alive.current = false
    }
  }, [photo, fit])

  // Dispose the texture this one replaces (thumbnail → full), and the last one on unmount.
  useEffect(() => () => texture?.dispose(), [texture])

  useFrame(({ camera }) => {
    if (wantFull.current || camera.position.distanceTo(position) > PHOTO.fullResDistance) return
    wantFull.current = true
    loadTexture(photo.src, fit)
      .then((t) => (alive.current ? setTexture(t) : t.dispose()))
      .catch((err) => console.error('Photo failed:', photo.src, err))
  })

  if (!texture) return null
  return (
    <mesh position={position} quaternion={quaternion}>
      <planeGeometry args={[fit.width, fit.height]} />
      <meshBasicMaterial map={texture} color={PHOTO.color} />
    </mesh>
  )
}
