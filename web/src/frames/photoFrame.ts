import * as THREE from "three";
import { createFrameMaterial } from "../lighting/matcaps";
import { FRAME_DEPTH, FRAME_PROFILE, FRAME_TONE, FRAME_WIDTH, type P, sweep } from "./sweep";

/**
 * Modern gallery frame: a slim rose-gold metal frame with softly rounded edges, a wide warm-white mat with a
 * fine rose-gold bevel around the photo, and the soft shadow the frame casts on the wall under the ceiling spot.
 * The same frame is used for the single photos and the collage. The photo itself is never altered.
 * 4 draw calls per frame.
 *
 * The group faces +Z with its back at z = 0 on the wall: place it like the Blender slot.
 */
export interface PhotoFrameOptions {
  photo: THREE.Texture;              // sRGB texture of the couple's photo
  width: number;                     // photo size in metres (the photo's real aspect ratio)
  height: number;
  light?: [number, number, number];  // the slot's baked light (userData.light_rgb)
}

const SHADOW_OPACITY = 0.5;          // the spot's share of the light on the wall right under the frame
const MAT_WHITE = new THREE.Color(0xfbf7f0);    // warm white mat board, shown as it is (like the photo)
const BEVEL = new THREE.Color(0xe8c2a6);        // fine rose-gold bevel around the photo

// ---------------------------------------------------------------- cast shadow

let shadowTexture: THREE.CanvasTexture | null = null;
/** Soft-edged box (alpha map, white = shadow): the left half of u fades in, the middle is solid. */
function createShadowTexture(): THREE.CanvasTexture {
  if (shadowTexture) return shadowTexture;
  const size = 64, canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const g = canvas.getContext("2d")!, image = g.createImageData(size, size);
  const fade = (t: number) => { const x = Math.min(1, Math.min(t, 1 - t) * 2); return x * x * (3 - 2 * x); };
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const a = Math.round(255 * fade((x + 0.5) / size) * fade((y + 0.5) / size)), i = (y * size + x) * 4;
      image.data[i] = image.data[i + 1] = image.data[i + 2] = a; image.data[i + 3] = 255;
    }
  }
  g.putImageData(image, 0, 0);
  shadowTexture = new THREE.CanvasTexture(canvas);
  return shadowTexture;
}

/** Shadow quad with soft edges of a fixed width (nine-slice): halfW × halfH core, `soft` metres of fade on each side. */
function shadowGeometry(halfW: number, halfH: number, soft: number): THREE.BufferGeometry {
  const xs = [-halfW - soft, -halfW + soft, halfW - soft, halfW + soft], ys = [-halfH - soft, -halfH + soft, halfH - soft, halfH + soft];
  const ts = [0, 0.5, 0.5, 1], position: number[] = [], uv: number[] = [], index: number[] = [];
  for (let j = 0; j < 4; j++) for (let i = 0; i < 4; i++) { position.push(xs[i], ys[j], 0); uv.push(ts[i], ts[j]); }
  for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) { const a = j * 4 + i; index.push(a, a + 1, a + 5, a, a + 5, a + 4); }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(position, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(index);
  return g;
}

let frameMaterial: THREE.MeshMatcapMaterial | null = null;
let matMaterial: THREE.MeshBasicMaterial | null = null;
let shadowMaterial: THREE.MeshBasicMaterial | null = null;

/** The three shared materials of every frame: rose-gold metal, mat (vertex colours) and the cast shadow. */
export function frameMaterials() {
  frameMaterial ??= createFrameMaterial({ vertexColors: true });
  matMaterial ??= new THREE.MeshBasicMaterial({ vertexColors: true, toneMapped: false });
  shadowMaterial ??= new THREE.MeshBasicMaterial({ color: 0x1a0d06, alphaMap: createShadowTexture(), transparent: true, opacity: SHADOW_OPACITY, depthWrite: false });
  return { frame: frameMaterial, mat: matMaterial, shadow: shadowMaterial };
}

/**
 * Geometry of the frame around one photo of width × height metres, centred at the origin, facing +Z:
 * the mat (`matWidth` wide), the metal frame (scale k: 1 = 3 cm wide) and its cast shadow (z = 0.002).
 */
export function frameGeometry(width: number, height: number, k: number, matWidth: number, light: [number, number, number]) {
  // the mat is as bright as the light on it allows: clean white under a spot, softer in a dim room
  const bright = THREE.MathUtils.clamp(0.2126 * light[0] + 0.7152 * light[1] + 0.0722 * light[2], 0.45, 1);
  const white = MAT_WHITE.clone().multiplyScalar(bright).toArray() as [number, number, number];
  const bevel = BEVEL.clone().multiplyScalar(bright).toArray() as [number, number, number];
  const matProfile: P[] = [[0, 0.004, "lip", true], [0.008, 0.0095, "face", true], [matWidth, 0.0095, "face", true]];
  const mat = sweep(width / 2, height / 2, matProfile, (b) => (b === "lip" ? bevel : white));

  const innerW = width / 2 + matWidth, innerH = height / 2 + matWidth;
  const profile = FRAME_PROFILE.map(([d, z, b, c]) => [d * k, z * k, b, c] as P);
  const frame = sweep(innerW, innerH, profile, (b) => FRAME_TONE[b]);

  // shadow cast by the ceiling spot (above and in front): drops below the frame, spreads a little sideways
  const outerW = innerW + FRAME_WIDTH * k, outerH = innerH + FRAME_WIDTH * k, depth = FRAME_DEPTH * k;
  const shadow = shadowGeometry(outerW + depth * 0.35, outerH, depth * 0.8).translate(0, -depth * 1.3, 0.002);
  return { mat, frame, shadow, outerW, outerH };
}

/** Frame scale k and mat width for a photo whose long side is `long` metres (wide mats, like a modern gallery). */
function proportions(long: number) {
  return { k: THREE.MathUtils.clamp(long / 1.1, 0.85, 1.25), mat: THREE.MathUtils.clamp(long * 0.11, 0.06, 0.16) };
}

/**
 * Photo size (metres) that keeps the whole frame inside a square slot of `slot` metres.
 * aspect = photo width / height (use the image's own size: never crop or stretch the photo).
 */
export function photoSizeForSlot(aspect: number, slot: number): { width: number; height: number } {
  const outer = (long: number) => { const { k, mat } = proportions(long); return long + 2 * mat + 2 * FRAME_WIDTH * k; };
  let lo = 0.1, hi = slot;
  for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (outer(mid) > slot) hi = mid; else lo = mid; }
  return aspect >= 1 ? { width: lo, height: lo / aspect } : { width: lo * aspect, height: lo };
}

export function createPhotoFrame({ photo, width, height, light = [0.8, 0.7, 0.62] }: PhotoFrameOptions): THREE.Group {
  const materials = frameMaterials();
  const { k, mat } = proportions(Math.max(width, height));
  const parts = frameGeometry(width, height, k, mat, light);

  const group = new THREE.Group();
  const image = new THREE.Mesh(new THREE.PlaneGeometry(width, height), new THREE.MeshBasicMaterial({ map: photo, toneMapped: false }));
  image.position.z = 0.004;                                        // the photo: untouched
  const shadow = new THREE.Mesh(parts.shadow, materials.shadow);
  shadow.renderOrder = -1;
  group.add(image, new THREE.Mesh(parts.mat, materials.mat), new THREE.Mesh(parts.frame, materials.frame), shadow);
  group.userData.outerSize = [parts.outerW * 2, parts.outerH * 2];
  return group;
}
