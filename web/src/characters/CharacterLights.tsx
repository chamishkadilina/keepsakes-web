import { useThree } from '@react-three/fiber'
import { useEffect } from 'react'
import { addCharacterLights } from './character'

/** The characters' own soft light and reflections. Only their lit materials use it; the baked museum is unlit. */
export function CharacterLights() {
  const scene = useThree((s) => s.scene)
  const gl = useThree((s) => s.gl)
  useEffect(() => addCharacterLights(scene, gl), [scene, gl])
  return null
}
