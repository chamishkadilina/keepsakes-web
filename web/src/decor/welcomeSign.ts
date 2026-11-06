import * as THREE from "three";
import { findProps } from "./findProps";
import { CALLIGRAPHY, HAND, loadFonts } from "./fonts";
import { GOLD, INK, boardAspect, boardMaterial, capitals, fit, heartRule, paper, wrap } from "./lettering";

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

function draw(H: number, { names, date, note, title = "The Museum of Us", line = "Welcome to" }: WelcomeSignOptions): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  paper(g, W, H);
  const calligraphy = (s: number) => `${s}px "${CALLIGRAPHY}", cursive`;
  g.fillStyle = GOLD;
  capitals(g, line, W / 2, 0.13 * H, 64, 0.42 * W);
  g.fillStyle = INK;
  g.textAlign = "center";
  fit(g, title, calligraphy, 310, 0.8 * W);
  let y = 0.37 * H;
  g.fillText(title, W / 2, y);
  if (names) {
    fit(g, names, calligraphy, 185, 0.66 * W);
    y += 0.18 * H;
    g.fillText(names, W / 2, y);
  }
  y += 0.07 * H;
  heartRule(g, W / 2, y, 320, 26);
  if (date) {
    g.fillStyle = GOLD;
    y += 0.08 * H;
    capitals(g, date, W / 2, y, 64, 0.5 * W);
  }
  if (note) {
    g.fillStyle = INK;
    g.textAlign = "center";
    const top = y + 0.08 * H, room = 0.93 * H - top;                            // down to just above the bottom roses
    let size = 84, lines: string[] = [];
    for (; size > 30; size -= 2) {                                             // the note as large as fits, in up to three lines
      g.font = `500 ${size}px "${HAND}", cursive`;
      lines = wrap(g, note, 0.62 * W);
      if (lines.length <= 3 && size * (1.05 + 1.22 * (lines.length - 1)) <= room) break;
    }
    if (lines.length > 3) {
      console.warn("createWelcomeSign: the note is too long for the board, it is cut after three lines");
      lines = [...lines.slice(0, 2), `${lines[2].replace(/[\s.,;:]+$/, "")}…`];
    }
    let at = top + size * 0.8;
    for (const l of lines) { g.fillText(l, W / 2, at); at += size * 1.22; }
  }
  return canvas;
}

export async function createWelcomeSign(root: THREE.Object3D, options: WelcomeSignOptions = {}): Promise<void> {
  const board = findProps(root, "welcome_board")[0];
  if (!board) {
    console.error("createWelcomeSign: no welcome_board in the model");
    return;
  }
  await loadFonts(options.fontsUrl);
  board.material = boardMaterial(root, draw(Math.round(W / boardAspect(board)), options));
}
