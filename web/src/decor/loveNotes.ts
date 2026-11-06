import * as THREE from "three";
import { HAND, SERIF, loadFonts } from "./fonts";
import { GOLD, INK, heart, wrap } from "./lettering";

/**
 * Love notes hanging over the right gallery's open middle, one for each of his reasons (up to 24): cream cards on thin
 * red and gold ribbons from the ceiling, each reason in his handwriting on both sides with its number, slowly turning and
 * swaying a little. The model lists where they hang (the `love_notes` empty: userData.notes = x, y, z of a card's
 * middle, then its ribbon's top height, ... in Blender coordinates), in an order that spreads any number of cards over
 * the room. They hang above head height, so you walk under them. Not baked: `light` matches them to the room.
 * 2 draw calls, animated on the GPU (nothing to update per frame); left out of the floor reflection.
 *
 *   scene.add(await createLoveNotes(gltf.scene, ["Your laugh", "The way you hold my hand", "You make every day lighter"]));
 */
export interface LoveNoteOptions {
  light?: number;                    // brightness, to match the room (default 0.85)
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const CARD_W = 0.22, CARD_H = 0.3;   // a card (metres)
const CELL_W = 320, CELL_H = 436;    // a card on the texture (pixels)
const COLS = 6, MAX = 24;
const RIBBON = 0.007;                // ribbon width (metres)

function drawCards(reasons: string[]): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = COLS * CELL_W;
  canvas.height = Math.ceil(reasons.length / COLS) * CELL_H;
  const g = canvas.getContext("2d")!;
  reasons.forEach((reason, i) => {
    const x0 = (i % COLS) * CELL_W, y0 = Math.floor(i / COLS) * CELL_H, cx = x0 + CELL_W / 2;
    g.fillStyle = "#f7f1e6";
    g.fillRect(x0, y0, CELL_W, CELL_H);
    g.strokeStyle = GOLD;
    g.lineWidth = 3;
    g.strokeRect(x0 + 14, y0 + 14, CELL_W - 28, CELL_H - 28);
    g.fillStyle = "#b3202c";
    heart(g, cx, y0 + 52, 13);
    g.fillStyle = INK;
    g.textAlign = "center";
    let size = 54, lines: string[] = [];
    for (; size > 22; size -= 2) {                                             // as large as fits in five lines
      g.font = `500 ${size}px "${HAND}", cursive`;
      lines = wrap(g, reason, CELL_W - 64);
      if (lines.length <= 5 && lines.length * size * 1.2 <= CELL_H - 170) break;
    }
    let y = y0 + CELL_H / 2 - ((lines.length - 1) * size * 1.2) / 2 + size * 0.3;
    for (const line of lines) { g.fillText(line, cx, y); y += size * 1.2; }
    g.fillStyle = GOLD;
    g.font = `600 26px "${SERIF}", serif`;
    g.fillText(`No. ${i + 1}`, cx, y0 + CELL_H - 40);
  });
  return canvas;
}

const vertexShader = /* glsl */ `
  attribute vec3 pivot;              // the card's middle
  attribute float phase;
  attribute float hang;              // 1 at the card, 0 at the ribbon's top (it stays put)
  uniform float time;
  varying vec2 vUv;
  varying vec3 vColor;
  void main() {
    float turn = phase * 6.2832 + 0.45 * sin(time * (0.21 + 0.1 * phase) + phase * 17.0);
    float c = cos(turn), s = sin(turn);
    vec3 p = vec3(c * position.x + s * position.z, position.y, c * position.z - s * position.x);
    vec2 swing = 0.025 * hang * vec2(sin(time * 0.55 + phase * 9.0), cos(time * 0.43 + phase * 5.0));
    vUv = uv;
    #ifdef USE_COLOR
      vColor = color;
    #endif
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pivot + p + vec3(swing.x, 0.0, swing.y), 1.0);
  }`;

const cardShader = /* glsl */ `
  uniform sampler2D map;
  uniform float light;
  varying vec2 vUv;
  void main() {
    gl_FragColor = vec4(texture2D(map, vUv).rgb * light, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`;

const ribbonShader = /* glsl */ `
  uniform float light;
  varying vec3 vColor;
  void main() {
    gl_FragColor = vec4(vColor * light, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`;

export async function createLoveNotes(root: THREE.Object3D, reasons: string[], { light = 0.85, fontsUrl }: LoveNoteOptions = {}): Promise<THREE.Group> {
  const group = new THREE.Group();
  group.name = "love_notes";
  let marker: THREE.Object3D | undefined;
  root.traverse((o) => { if (o.userData.notes) marker = o; });
  const spots: number[] = (marker?.userData.notes as number[] | undefined) ?? [];
  const texts = reasons.map((r) => r.trim()).filter(Boolean).slice(0, Math.min(MAX, spots.length / 4));
  if (!spots.length) console.error("createLoveNotes: no love_notes in the model");
  if (reasons.length > MAX) console.warn(`createLoveNotes: only the first ${MAX} reasons hang in the gallery`);
  if (!texts.length) return group;
  await loadFonts(fontsUrl);
  const texture = new THREE.CanvasTexture(drawCards(texts));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  const rows = Math.ceil(texts.length / COLS);

  const card = { position: [] as number[], uv: [] as number[], pivot: [] as number[], phase: [] as number[], hang: [] as number[] };
  const ribbon = { position: [] as number[], color: [] as number[], pivot: [] as number[], phase: [] as number[], hang: [] as number[] };
  const red = new THREE.Color(0xb3202c), gold = new THREE.Color(0xd8b06a);
  texts.forEach((_, i) => {
    const [x, y, z, top] = spots.slice(i * 4, i * 4 + 4);
    const pivot = [x, z, -y], phase = (i * 0.618) % 1;                         // Blender (x, y, z) -> three.js (x, z, -y)
    const u0 = ((i % COLS) * CELL_W) / (COLS * CELL_W), u1 = u0 + 1 / COLS;
    const v1 = 1 - Math.floor(i / COLS) / rows, v0 = v1 - 1 / rows;
    const quad = [[-CARD_W / 2, -CARD_H / 2, u0, v0], [CARD_W / 2, -CARD_H / 2, u1, v0], [CARD_W / 2, CARD_H / 2, u1, v1],
      [-CARD_W / 2, -CARD_H / 2, u0, v0], [CARD_W / 2, CARD_H / 2, u1, v1], [-CARD_W / 2, CARD_H / 2, u0, v1]];
    for (const side of [1, -1]) {                                              // its front, and its back mirrored (the same words)
      for (const [px, py, u, v] of quad) {
        card.position.push(side * px, py, side * 0.001); card.uv.push(u, v);
        card.pivot.push(...pivot); card.phase.push(phase); card.hang.push(1);
      }
    }
    const length = top - z, colour = i % 2 ? gold : red;                       // two crossed strips up to the ceiling
    for (const [ax, az] of [[1, 0], [0, 1]]) {
      const corners = [[-1, CARD_H / 2, 1], [1, CARD_H / 2, 1], [1, length, 0], [-1, CARD_H / 2, 1], [1, length, 0], [-1, length, 0]];
      for (const [s, py, h] of corners) {
        ribbon.position.push(ax * s * RIBBON / 2, py, az * s * RIBBON / 2);
        ribbon.color.push(colour.r, colour.g, colour.b);
        ribbon.pivot.push(...pivot); ribbon.phase.push(phase); ribbon.hang.push(h);
      }
    }
  });

  const uniforms = { time: { value: 0 }, light: { value: light }, map: { value: texture } };
  const build = (data: Record<string, number[]>, sizes: Record<string, number>) => {
    const geometry = new THREE.BufferGeometry();
    for (const [name, values] of Object.entries(data)) geometry.setAttribute(name, new THREE.Float32BufferAttribute(values, sizes[name]));
    return geometry;
  };
  const cards = new THREE.Mesh(build(card, { position: 3, uv: 2, pivot: 3, phase: 1, hang: 1 }),
    new THREE.ShaderMaterial({ vertexShader, fragmentShader: cardShader, uniforms }));
  const ribbons = new THREE.Mesh(build(ribbon, { position: 3, color: 3, pivot: 3, phase: 1, hang: 1 }),
    new THREE.ShaderMaterial({ vertexShader, fragmentShader: ribbonShader, uniforms, vertexColors: true, side: THREE.DoubleSide }));
  for (const mesh of [cards, ribbons]) {
    mesh.frustumCulled = false;                                                // placed by the shader
    mesh.userData.noReflection = true;
    group.add(mesh);
  }
  cards.onBeforeRender = () => { uniforms.time.value = performance.now() / 1000; };
  return group;
}
