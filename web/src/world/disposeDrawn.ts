import * as THREE from 'three'

/** Frees the GPU memory of everything drawn under `root`, including a shader's `map`. */
export function disposeDrawn(root: THREE.Object3D): void {
  root.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh || obj instanceof THREE.Points)) return
    obj.geometry.dispose()
    const material = obj.material as THREE.ShaderMaterial
    material.uniforms?.map?.value?.dispose()
    material.dispose()
  })
}
