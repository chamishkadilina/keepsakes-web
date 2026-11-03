import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { frameGeometry, frameMaterials } from "./photoFrame";
import { FRAME_WIDTH } from "./sweep";

/**
 * The collage in the backlit niche (heart room): a gallery wall like a real home, each photo in exactly the same
 * frame as the single photos (rose-gold metal, warm-white mat, fine bevel). No cast shadows: the niche is lit from all
 * sides, so the gaps show the clean warm wall.
 * Frames of different sizes are fitted together like a puzzle around the middle: no rows or columns, no big holes,
 * the same small gap between neighbouring frames, the outline free and uneven, the whole wall centred in the niche.
 * Photos keep their real aspect ratio and are never altered. The same photos always give the same layout.
 * One draw call per photo plus two for all frames and mats together.
 *
 * The group faces +Z, centred on the `collage_board` slot.
 */
export interface CollageOptions {
  photos: THREE.Texture[];
  width: number;      // area the wall may use (the niche opening), metres
  height: number;
  gap?: number;       // space between two frames
  margin?: number;    // smallest space between the frames and the edge of the area
  seed?: number;      // another arrangement of the same photos
  light?: [number, number, number];   // baked light on the collage: the lit niche keeps the mats bright white
}

const FRAME_SCALE = 0.75;                                  // the single photos' frame, a little slimmer for smaller photos
const MAT = 0.035;                                         // mat width around each photo
const PAD = MAT + FRAME_WIDTH * FRAME_SCALE;               // mat + frame on each side of a photo
const TRIES = 12;                                          // size mixes tried (the best-filling one is kept)

interface Placed { photo: number; x: number; y: number; w: number; h: number }   // outer frame rect, (x, y) = centre

/**
 * Packs frames (photo sizes × scale) around the middle, biggest first: each new frame goes to the free spot next to an
 * already hung frame (exactly `gap` away, lined up with its top, middle or bottom / left, centre or right) that is
 * closest to the middle of the area. Returns the frames centred on the origin.
 */
function pack(sizes: [number, number][], order: number[], scale: number, gap: number, width: number, height: number): Placed[] {
  const placed: Placed[] = [];
  const free = (x: number, y: number, w: number, h: number) =>
    placed.every((p) => Math.abs(p.x - x) >= (p.w + w) / 2 + gap - 1e-6 || Math.abs(p.y - y) >= (p.h + h) / 2 + gap - 1e-6);
  for (const id of order) {
    const w = sizes[id][0] * scale + 2 * PAD, h = sizes[id][1] * scale + 2 * PAD;
    if (!placed.length) { placed.push({ photo: id, x: 0, y: 0, w, h }); continue; }
    let best: [number, number] = [0, 0], bestScore = Infinity;
    for (const p of placed) {
      const ex = (p.w + w) / 2 + gap, ey = (p.h + h) / 2 + gap;
      const ys = [p.y, p.y + (p.h - h) / 2, p.y - (p.h - h) / 2], xs = [p.x, p.x + (p.w - w) / 2, p.x - (p.w - w) / 2];
      const spots: [number, number][] = [
        ...ys.map((y) => [p.x + ex, y] as [number, number]), ...ys.map((y) => [p.x - ex, y] as [number, number]),
        ...xs.map((x) => [x, p.y + ey] as [number, number]), ...xs.map((x) => [x, p.y - ey] as [number, number]),
      ];
      for (const [x, y] of spots) {
        const score = (x / width) ** 2 + (y / height) ** 2;   // closest to the middle, in the shape of the niche
        if (score < bestScore && free(x, y, w, h)) { bestScore = score; best = [x, y]; }
      }
    }
    placed.push({ photo: id, x: best[0], y: best[1], w, h });
  }
  const x0 = Math.min(...placed.map((p) => p.x - p.w / 2)), x1 = Math.max(...placed.map((p) => p.x + p.w / 2));
  const y0 = Math.min(...placed.map((p) => p.y - p.h / 2)), y1 = Math.max(...placed.map((p) => p.y + p.h / 2));
  placed.forEach((p) => { p.x -= (x0 + x1) / 2; p.y -= (y0 + y1) / 2; });
  return placed;
}

const extent = (placed: Placed[]) => ({
  w: Math.max(...placed.map((p) => p.x + p.w / 2)) * 2, h: Math.max(...placed.map((p) => p.y + p.h / 2)) * 2,
});

const aspectOf = (t: THREE.Texture) => {
  const img = t.image as { width?: number; height?: number } | undefined;
  return img?.width && img?.height ? img.width / img.height : 1.5;
};

export function createCollageWall({ photos, width, height, gap = 0.05, margin = 0.1, seed = 1, light = [1, 1, 1] }: CollageOptions): THREE.Group {
  const wall = new THREE.Group();
  if (!photos.length) return wall;
  const aspects = photos.map(aspectOf);
  let s = (Math.floor(Math.abs(seed)) % 2147483646) + 1;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const W = width - 2 * margin, H = height - 2 * margin;

  let best: Placed[] = [], bestFill = -1;
  for (let t = 0; t < TRIES; t++) {
    // a mix of sizes: a few large, most medium, some small (relative photo area 0.55–1.6)
    const areas = aspects.map(() => [0.55, 0.8, 1, 1, 1.25, 1.6][Math.floor(rnd() * 6)]);
    const sizes = aspects.map((a, i) => [Math.sqrt(areas[i] * a), Math.sqrt(areas[i] / a)] as [number, number]);
    const order = aspects.map((_, i) => i).sort((a, b) => areas[b] - areas[a] || a - b);
    let lo = 0, hi = Math.max(W, H);                       // largest photo scale whose wall fits the niche
    for (let i = 0; i < 16; i++) {
      const mid = (lo + hi) / 2, e = extent(pack(sizes, order, mid, gap, W, H));
      if (e.w <= W && e.h <= H) lo = mid; else hi = mid;
    }
    const placed = pack(sizes, order, lo, gap, W, H);
    const fill = placed.reduce((sum, p) => sum + p.w * p.h, 0);
    if (fill > bestFill) { bestFill = fill; best = placed; }
  }

  const materials = frameMaterials();
  const mats: THREE.BufferGeometry[] = [], frames: THREE.BufferGeometry[] = [];
  for (const { photo, x, y, w, h } of best) {
    const pw = w - 2 * PAD, ph = h - 2 * PAD;
    const image = new THREE.Mesh(new THREE.PlaneGeometry(pw, ph), new THREE.MeshBasicMaterial({ map: photos[photo], toneMapped: false }));
    image.position.set(x, y, 0.004);                               // the photo: untouched
    wall.add(image);
    const parts = frameGeometry(pw, ph, FRAME_SCALE, MAT, light);
    mats.push(parts.mat.translate(x, y, 0)); frames.push(parts.frame.translate(x, y, 0));
  }
  wall.add(new THREE.Mesh(mergeGeometries(mats)!, materials.mat), new THREE.Mesh(mergeGeometries(frames)!, materials.frame));
  return wall;
}
