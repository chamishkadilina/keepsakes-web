import * as THREE from "three";
import { findProps } from "./findProps";
import { CALLIGRAPHY, loadFonts } from "./fonts";
import { GOLD, INK, capitals, heartRule, paper, wrap } from "./lettering";

/**
 * The quote board in the heart room, on the gold easel left of the collage: the couple's own quote in calligraphy on
 * ivory, a fine gold border, a gold rule with a little heart, and their names and date in an elegant serif. The
 * board's roses frame two corners, so the writing keeps to the middle. Lit by the board's own baked light.
 * Call after applyBakedLighting; it only replaces the board's material (no extra draw call).
 *
 *   await createQuoteBoard(gltf.scene, { quote: "You are my today and all of my tomorrows.", names: "Kasun & Nethmi", date: "14 February 2021" });
 */
export interface QuoteBoardOptions {
  quote: string;                     // the quote; "\n" starts a new line. Up to ~45 words fit nicely
  names?: string;                    // under the quote, e.g. "Kasun & Nethmi"
  date?: string;                     // under the names, e.g. "14 February 2021"
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const W = 1080, H = 1498;            // the board's face, 0.93 m × 1.29 m (its UVs span the whole canvas)

function draw({ quote, names, date }: QuoteBoardOptions): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  paper(g, W, H);

  const signed = !!(names || date);
  const box = { left: 0.17 * W, right: 0.83 * W, top: 0.26 * H, bottom: (signed ? 0.63 : 0.72) * H };
  let size = 124, lines: string[] = [];
  for (; size > 40; size -= 4) {                                               // the quote as large as it fits
    g.font = `${size}px "${CALLIGRAPHY}", cursive`;
    lines = wrap(g, quote, box.right - box.left);
    if (lines.length * size * 1.25 <= box.bottom - box.top) break;
  }
  if (lines.length * size * 1.25 > box.bottom - box.top) console.warn("createQuoteBoard: the quote is too long for the board");
  const lineHeight = size * 1.25;
  g.fillStyle = INK;
  g.textAlign = "center";
  let y = (box.top + box.bottom) / 2 - (lines.length * lineHeight) / 2 + size * 0.85;
  for (const line of lines) {
    g.fillText(line, W / 2, y);
    y += lineHeight;
  }
  if (!signed) return canvas;
  const rule = box.bottom + 0.045 * H;                                         // gold rule with a little heart
  heartRule(g, W / 2, rule, 170, 17);
  if (names) {
    g.fillStyle = INK;
    capitals(g, names, W / 2, rule + 0.07 * H, 52, 0.62 * W);
  }
  if (date) {
    g.fillStyle = GOLD;
    capitals(g, date, W / 2, rule + (names ? 0.115 : 0.07) * H, 34, 0.56 * W);
  }
  return canvas;
}

export async function createQuoteBoard(root: THREE.Object3D, options: QuoteBoardOptions): Promise<void> {
  const board = findProps(root, "quote_board")[0];
  if (!board) {
    console.error("createQuoteBoard: no quote_board in the model");
    return;
  }
  await loadFonts(options.fontsUrl);
  const texture = new THREE.CanvasTexture(draw(options));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;                                                       // glTF UV convention
  texture.anisotropy = 8;
  const intensity = (root.userData.lightmapIntensity as number | undefined) ?? 1;
  board.material = new THREE.MeshBasicMaterial({ map: texture, color: new THREE.Color(intensity, intensity, intensity), vertexColors: true });
}
