import * as THREE from 'three'
import { MATERIALS } from '../config/frames'

/** Shared by every frame and plant: one material each, created once. */
export const GALLERY_MATERIALS = {
  gold: new THREE.MeshStandardMaterial({ ...MATERIALS.gold, name: 'gallery_gold' }),
  mat: new THREE.MeshStandardMaterial({ ...MATERIALS.mat, name: 'gallery_mat' }),
  pot: new THREE.MeshStandardMaterial({ ...MATERIALS.pot, name: 'gallery_pot' }),
  leaf: new THREE.MeshStandardMaterial({ ...MATERIALS.leaf, name: 'gallery_leaf' }),
}
