import { useMemo } from 'react'
import { useLoader } from '@react-three/fiber'
import * as THREE from 'three'
import { LIGHTING } from '../config/lighting'

type Manifest = { intensity: number; maps: Record<string, { file: string }> }

export type Lightmaps = {
  intensity: number // final colour = albedo × lightmap_linear × intensity
  textures: Record<string, THREE.Texture> // by lightmap_group
}

/** Loads lightmaps.json and one lightmap per group (suspends until ready). */
export function useLightmaps(): Lightmaps {
  const json = useLoader(THREE.FileLoader, `${LIGHTING.lightmapDir}/${LIGHTING.manifest}`) as string
  const manifest = useMemo(() => JSON.parse(json) as Manifest, [json])
  const groups = useMemo(() => Object.keys(manifest.maps), [manifest])
  const textures = useLoader(
    THREE.TextureLoader,
    groups.map((g) => `${LIGHTING.lightmapDir}/${manifest.maps[g].file}`),
  )

  return useMemo(() => {
    const byGroup: Record<string, THREE.Texture> = {}
    textures.forEach((texture, i) => {
      texture.colorSpace = THREE.SRGBColorSpace
      texture.flipY = false
      texture.channel = 1 // TEXCOORD_1
      texture.anisotropy = LIGHTING.lightmapAnisotropy
      texture.needsUpdate = true
      byGroup[groups[i]] = texture
    })
    return { intensity: manifest.intensity, textures: byGroup }
  }, [textures, manifest, groups])
}
