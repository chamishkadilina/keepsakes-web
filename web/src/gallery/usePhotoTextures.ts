import { useEffect, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { PHOTO } from '../config/frames'
import type { GiftPhoto } from '../gift/gift'

const textureLoader = new THREE.TextureLoader()
const imageLoader = new THREE.ImageLoader()

function loadThumbnail(url: string): Promise<THREE.Texture> {
  return textureLoader.loadAsync(url).then((texture) => {
    texture.colorSpace = THREE.SRGBColorSpace
    texture.anisotropy = PHOTO.anisotropy
    return texture
  })
}

/**
 * The photos' textures, thumbnails first (null until all have loaded). When the camera
 * comes within `PHOTO.fullResDistance` of `near`, each texture swaps to the full-size
 * image in place, so frames built around it stay as they are.
 */
export function usePhotoTextures(photos: GiftPhoto[], near: THREE.Vector3): THREE.Texture[] | null {
  const [textures, setTextures] = useState<THREE.Texture[] | null>(null)
  const upgraded = useRef(false)

  useEffect(() => {
    let alive = true
    let loaded: THREE.Texture[] = []
    upgraded.current = false
    Promise.all(photos.map((photo) => loadThumbnail(photo.thumb)))
      .then((list) => {
        loaded = list
        if (alive) setTextures(list)
        else list.forEach((t) => t.dispose())
      })
      .catch((err) => console.error('Photo thumbnails failed:', err))
    return () => {
      alive = false
      loaded.forEach((t) => t.dispose())
      setTextures(null)
    }
  }, [photos])

  useFrame(({ camera }) => {
    if (!textures || upgraded.current || camera.position.distanceTo(near) > PHOTO.fullResDistance) return
    upgraded.current = true
    textures.forEach((texture, i) =>
      imageLoader
        .loadAsync(photos[i].src)
        .then((image) => {
          texture.image = image
          texture.needsUpdate = true
        })
        .catch((err) => console.error('Photo failed:', photos[i].src, err)),
    )
  })

  return textures
}
