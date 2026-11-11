import { useLoader } from '@react-three/fiber'
import { useEffect, useState } from 'react'
import type { Group } from 'three'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { clone } from 'three/addons/utils/SkeletonUtils.js'
import { createCharacter, type Character } from './character'

const GIRL_URL = '/models/girl.glb'
const withMeshopt = (loader: GLTFLoader) => loader.setMeshoptDecoder(MeshoptDecoder) // compressed like museum.glb

/** The girl from girl.glb: a fresh copy per mount, disposed on unmount. */
export function useGirl(): Character | null {
  const gltf = useLoader(GLTFLoader, GIRL_URL, withMeshopt)
  const [girl, setGirl] = useState<Character | null>(null)

  useEffect(() => {
    const character = createCharacter({ ...gltf, scene: clone(gltf.scene) as Group })
    setGirl(character)
    return () => character.dispose()
  }, [gltf])

  return girl
}

useLoader.preload(GLTFLoader, GIRL_URL, withMeshopt)
