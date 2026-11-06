import * as THREE from "three";

/**
 * The model's furniture and decor meshes of one material. props.py merges every piece into one mesh per material in
 * each part of the museum (prop_<zone>_<material>) and tags it with userData.prop = the material, e.g. "quote_board".
 */
export function findProps(root: THREE.Object3D, material: string): THREE.Mesh[] {
  const found: THREE.Mesh[] = [];
  root.traverse((o) => {
    if ((o as THREE.Mesh).isMesh && o.userData.prop === material) found.push(o as THREE.Mesh);
  });
  return found;
}
