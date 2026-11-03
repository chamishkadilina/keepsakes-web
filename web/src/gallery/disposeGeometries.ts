import * as THREE from 'three'

/** Frees the geometry built for a frame or collage. Materials are shared by the frame builders and stay. */
export function disposeGeometries(root: THREE.Object3D): void {
  root.traverse((obj) => {
    if (obj instanceof THREE.Mesh) obj.geometry.dispose()
  })
}
