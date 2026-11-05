import * as THREE from "three";
import { findProps } from "./findProps";
import { CALLIGRAPHY, HAND, loadFonts } from "./fonts";
import { GOLD, INK, capitals, heartRule, paper, wrap } from "./lettering";

/**
 * The title wall in the foyer, straight ahead as she comes in, in its own spotlight: "Welcome to" in small capitals,
 * "The Museum of Us" in calligraphy, the couple's names, a gold rule with a little heart, the date, and his note in
 * handwriting. Roses frame its top-left and bottom-right corners, so the writing keeps to the middle. Lit by the
 * board's own baked light. Call after applyBakedLighting; it only replaces the board's material (no extra draw call).
 *
 *   await createWelcomeSign(gltf.scene, { names: "Kasun & Nethmi", date: "Since 3 June 2019", note: "Every photo here is a moment I never want to forget." });
 */
export interface WelcomeSignOptions {
  names?: string;                    // e.g. "Kasun & Nethmi"
  date?: string;                     // under the names, e.g. "Since 3 June 2019"
  note?: string;                     // his words in handwriting at the bottom (up to ~30 words)
  title?: string;                    // default "The Museum of Us"
  line?: string;                     // the small capitals above the title, default "Welcome to"
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const W = 2048;                      // the board's face across (its UVs span the whole canvas); its height follows the board

/** Sets the largest font (from `size` down) at which `text` is no wider than `width`; returns that size. */
function fit(g: CanvasRenderingContext2D, text: string, font: (size: number) => string, size: number, width: number): number {
  g.font = font(size);
  const w = g.measureText(text).width;
  if (w > width) { size = Math.floor(size * width / w); g.font = font(size); }
  return size;
}

function draw(H: number, { names, date, note, title = "The Museum of Us", line = "Welcome to" }: WelcomeSignOptions): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  paper(g, W, H);
  const calligraphy = (s: number) => `${s}px "${CALLIGRAPHY}", cursive`;
  g.fillStyle = GOLD;
  capitals(g, line, W / 2, 0.16 * H, 60, 0.42 * W);
  g.fillStyle = INK;
  g.textAlign = "center";
  fit(g, title, calligraphy, 300, 0.76 * W);
  g.fillText(title, W / 2, 0.355 * H);
  let y = 0.355 * H;
  if (names) {
    fit(g, names, calligraphy, 170, 0.62 * W);
    y = 0.525 * H;
    g.fillText(names, W / 2, y);
  }
  y += 0.07 * H;
  heartRule(g, W / 2, y, 300, 24);
  if (date) {
    g.fillStyle = GOLD;
    capitals(g, date, W / 2, y + 0.08 * H, 54, 0.5 * W);
    y += 0.08 * H;
  }
  if (note) {
    g.fillStyle = INK;
    g.textAlign = "center";
    const room = Math.floor((0.93 * H - (y + 0.095 * H)) / 1.25);              // down to just above the bottom roses
    let size = 80, lines: string[] = [];
    for (; size > 30; size -= 2) {                                             // the note as large as fits in three lines
      g.font = `500 ${size}px "${HAND}", cursive`;
      lines = wrap(g, note, 0.6 * W);
      if (lines.length <= 3 && lines.length * size <= room) break;
    }
    if (lines.length > 3) {
      console.warn("createWelcomeSign: the note is too long for the board, it is cut after three lines");
      lines = [...lines.slice(0, 2), `${lines[2].replace(/[\s.,;:]+$/, "")}…`];
    }
    let at = y + 0.095 * H + size * 0.35;
    for (const l of lines) { g.fillText(l, W / 2, at); at += size * 1.25; }
  }
  return canvas;
}

export async function createWelcomeSign(root: THREE.Object3D, options: WelcomeSignOptions = {}): Promise<void> {
  const board = findProps(root, "welcome_board")[0];
  if (!board) {
    console.error("createWelcomeSign: no welcome_board in the model");
    return;
  }
  board.updateWorldMatrix(true, false);
  const size = new THREE.Box3().setFromObject(board).getSize(new THREE.Vector3());   // hung on a wall: across, and up
  const H = Math.round(W * size.y / Math.max(size.x, size.z));
  await loadFonts(options.fontsUrl);
  const texture = new THREE.CanvasTexture(draw(H, options));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;                                                       // glTF UV convention
  texture.anisotropy = 8;
  const intensity = (root.userData.lightmapIntensity as number | undefined) ?? 1;
  board.material = new THREE.MeshBasicMaterial({ map: texture, color: new THREE.Color(intensity, intensity, intensity), vertexColors: true });
}
