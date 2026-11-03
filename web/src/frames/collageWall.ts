import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { frameGeometry, frameMaterials } from "./photoFrame";
import { FRAME_WIDTH } from "./sweep";

/**
 * The collage in the backlit niche (heart room): the couple's photos as a mosaic in mixed sizes, each in exactly the
 * same frame as the single photos (rose-gold metal, warm-white mat, fine bevel), like a real gallery wall. No cast shadows:
 * the niche is lit from all sides, so the gaps between the frames show the clean warm wall.
 * Every gap between two frames is the same, the margin to the edge of the niche is the same on all four sides, and the
 * mosaic is centred. Photos keep their real aspect ratio and are never altered.
 * The arrangement is the best of a few thousand candidates (the same photos always give the same layout).
 * One draw call per photo plus two for all frames and mats together.
 *
 * The group faces +Z, centred on the `collage_board` slot.
 */
export interface CollageOptions {
  photos: THREE.Texture[];
  width: number;      // area to fill (the niche opening), metres
  height: number;
  gap?: number;       // space between two frames
  margin?: number;    // space between the mosaic and the edge of the area, the same on all sides
  seed?: number;      // another arrangement of the same photos
  light?: [number, number, number];   // baked light on the collage: the lit niche keeps the mats bright white
}

const FRAME_SCALE = 0.75;                                  // the single photos' frame, a little slimmer for smaller photos
const MAT = 0.035;                                         // mat width around each photo
const PAD = MAT + FRAME_WIDTH * FRAME_SCALE;               // mat + frame on each side of a photo
const CANDIDATES = 2000;                                   // random arrangements tried ...
const POLISH = 400;                                        // ... then single splits of the best one flipped
const MIN_SIDE = 0.16;                                     // no photo smaller than this (metres)

/**
 * Mosaic as a tree of side-by-side ("row") and stacked ("column") pairs. Every node's outer width is a straight
 * function of its height, w = a·h + b, so a tree has exact sizes with identical gaps everywhere.
 */
interface Node { a: number; b: number; row?: boolean; kids?: [Node, Node]; photo?: number }
interface Placed { photo: number; x: number; y: number; w: number; h: number }   // outer frame rect, (x, y) = centre

const leaf = (photo: number, aspect: number): Node => ({ a: aspect, b: 2 * PAD * (1 - aspect), photo });

function pair(row: boolean, k1: Node, k2: Node, gap: number): Node {
  if (row) return { a: k1.a + k2.a, b: k1.b + k2.b + gap, row, kids: [k1, k2] };
  const a = 1 / (1 / k1.a + 1 / k2.a);
  return { a, b: a * (k1.b / k1.a + k2.b / k2.a - gap), row, kids: [k1, k2] };
}

/** Random tree that tends to fit an area of the given aspect: wide areas split side by side, tall ones stack. */
function grow(ids: number[], aspects: number[], aspect: number, gap: number, rnd: () => number): Node {
  if (ids.length === 1) return leaf(ids[0], aspects[ids[0]]);
  const row = rnd() < aspect ** 3 / (1 + aspect ** 3);
  const n1 = THREE.MathUtils.clamp(Math.round(ids.length * (0.3 + 0.4 * rnd())), 1, ids.length - 1), share = n1 / ids.length;
  const k1 = grow(ids.slice(0, n1), aspects, row ? aspect * share : aspect / share, gap, rnd);
  const k2 = grow(ids.slice(n1), aspects, row ? aspect * (1 - share) : aspect / (1 - share), gap, rnd);
  return pair(row, k1, k2, gap);
}

/** Recomputes a and b of every node of a tree after a split was flipped. */
function refit(node: Node, gap: number) {
  if (!node.kids) return;
  refit(node.kids[0], gap); refit(node.kids[1], gap);
  const p = pair(node.row!, node.kids[0], node.kids[1], gap);
  node.a = p.a; node.b = p.b;
}

function splits(node: Node, out: Node[] = []): Node[] {
  if (node.kids) { out.push(node); splits(node.kids[0], out); splits(node.kids[1], out); }
  return out;
}

function place(node: Node, x: number, y: number, w: number, h: number, gap: number, out: Placed[]) {
  if (node.photo !== undefined) { out.push({ photo: node.photo, x: x + w / 2, y: y - h / 2, w, h }); return; }
  const [k1, k2] = node.kids!;
  if (node.row) {
    const w1 = k1.a * h + k1.b;
    place(k1, x, y, w1, h, gap, out);
    place(k2, x + w1 + gap, y, w - w1 - gap, h, gap, out);
  } else {
    const h1 = (w - k1.b) / k1.a;
    place(k1, x, y, w, h1, gap, out);
    place(k2, x, y - h1 - gap, w, h - h1 - gap, gap, out);
  }
}

/** Sizes the tree into the area (an equal margin all round when the shapes allow it) and scores the result. */
function evaluate(root: Node, width: number, height: number, gap: number, margin: number) {
  const m = (root.a * height + root.b - width) / (2 * (root.a - 1));       // margin that fits both sides exactly
  const exact = Number.isFinite(m) && m >= margin * 0.75 && m <= margin * 1.5;
  let w: number, h: number;
  if (exact) { w = width - 2 * m; h = height - 2 * m; } else {
    h = Math.min(height - 2 * margin, (width - 2 * margin - root.b) / root.a); w = root.a * h + root.b;
  }
  const placed: Placed[] = [];
  place(root, -w / 2, h / 2, w, h, gap, placed);
  const areas = placed.map((p) => Math.max(1e-6, Math.max(0, p.w - 2 * PAD) * Math.max(0, p.h - 2 * PAD)));
  const logs = areas.map(Math.log), mean = logs.reduce((s, v) => s + v, 0) / logs.length;
  const spread = Math.sqrt(logs.reduce((s, v) => s + (v - mean) ** 2, 0) / logs.length);
  const hero = placed[areas.indexOf(Math.max(...areas))];
  let cost = exact ? 2 * Math.abs(m - margin) / margin : 3 + (1 - (w * h) / ((width - 2 * margin) * (height - 2 * margin)));
  const variety = THREE.MathUtils.clamp(0.45 - placed.length / 150, 0.2, 0.4);   // mixed sizes; calmer with many photos
  cost += placed.length > 2 ? 3 * (spread - variety) ** 2 : 0;
  cost += Math.max(...areas) / Math.min(...areas) > 6 ? 1 : 0;              // no tiny photos next to huge ones
  cost += 0.6 * (Math.abs(hero.x) / w + Math.abs(hero.y) / h);              // the largest photo near the centre
  const smallest = Math.min(...placed.map((p) => Math.min(p.w, p.h) - 2 * PAD));
  if (smallest < MIN_SIDE) cost += 10 + 100 * (MIN_SIDE - smallest);         // far too many photos: least-bad layout
  return { cost, placed };
}

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

  let best: Placed[] = [], bestCost = Infinity, bestTree: Node | null = null;
  for (let i = 0; i < CANDIDATES; i++) {
    const ids = aspects.map((_, k) => k);
    for (let k = ids.length - 1; k > 0; k--) { const j = Math.floor(rnd() * (k + 1)); [ids[k], ids[j]] = [ids[j], ids[k]]; }
    const tree = grow(ids, aspects, width / height, gap, rnd);
    const { cost, placed } = evaluate(tree, width, height, gap, margin);
    if (cost < bestCost) { bestCost = cost; best = placed; bestTree = tree; }
  }
  const inner = bestTree ? splits(bestTree) : [];
  for (let i = 0; i < POLISH && inner.length; i++) {                         // fine-tune: flip one split, keep it if better
    const node = inner[Math.floor(rnd() * inner.length)];
    node.row = !node.row; refit(bestTree!, gap);
    const { cost, placed } = evaluate(bestTree!, width, height, gap, margin);
    if (cost < bestCost) { bestCost = cost; best = placed; } else { node.row = !node.row; refit(bestTree!, gap); }
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
