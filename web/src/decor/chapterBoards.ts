import * as THREE from "three";
import { findProps } from "./findProps";
import { SERIF, TEXT, loadFonts } from "./fonts";
import { INK, boardAspect, boardMaterial, fit, heartRule, paper, wrap } from "./lettering";

/**
 * Each chapter's title on its board, straight ahead as you come into its room, in the style of the foyer's title wall:
 * the title large in an elegant serif, a gold rule with a little heart and, if he wrote one, his line under it in a
 * clear book serif (italic), large enough to read from across the room.
 * The story gallery's board reads "How It Began", the right gallery's "Reasons I Love You" (both can be changed).
 * Roses frame two corners, so the writing keeps to the middle. Lit by the boards' own baked light. Call after
 * applyBakedLighting; it only replaces the boards' materials (no extra draw call).
 *
 *   await createChapterBoards(gltf.scene, { story: { line: "It started with one hello." }, reasons: {} });
 */
export interface Chapter {
  title?: string;                    // the chapter's name (a few words; "\n" breaks it into two lines)
  line?: string;                     // his line under it (up to ~20 words), or none
}

export interface ChapterBoardOptions {
  story?: Chapter;                   // the story gallery: "How It Began"
  reasons?: Chapter;                 // the right gallery: "Reasons I Love You"
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const W = 2048;                      // the board's face across (its UVs span the whole canvas); its height follows the board
const BOARDS = { story: ["chapter_story", "How It Began"], reasons: ["chapter_reasons", "Reasons\nI Love You"] } as const;

function draw(H: number, title: string, line?: string): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  paper(g, W, H);
  g.fillStyle = INK;
  g.textAlign = "center";
  const font = (size: number) => `600 ${size}px "${SERIF}", serif`;
  let rows = title.split("\n").map((r) => r.trim()).filter(Boolean);
  if (rows.length === 1 && fit(g, rows[0], font, 330, 0.76 * W) < 230 && rows[0].includes(" ")) {
    const words = rows[0].split(/\s+/);                                       // too long for one line: two, evenly split
    const split = (k: number) => [words.slice(0, k).join(" "), words.slice(k).join(" ")];
    const widest = (k: number) => Math.max(...split(k).map((r) => g.measureText(r).width));
    let best = 1;
    for (let k = 2; k < words.length; k++) if (widest(k) < widest(best)) best = k;
    rows = split(best);
  }
  rows = rows.slice(0, 2);
  const size = Math.min(...rows.map((r) => fit(g, r, font, rows.length > 1 ? 270 : 330, 0.76 * W)));
  g.font = font(size);
  let y = (rows.length > 1 ? (line ? 0.31 : 0.4) : (line ? 0.45 : 0.55)) * H;
  rows.forEach((r, i) => g.fillText(r, W / 2, y + i * size * 0.95));
  y += (rows.length - 1) * size * 0.95;
  heartRule(g, W / 2, y + 0.12 * H, 300, 26);
  if (line) {
    g.fillStyle = INK;
    g.textAlign = "center";
    let size = 104, lines: string[] = [];
    for (; size > 48; size -= 2) {                                             // as large as fits in two lines
      g.font = `italic 500 ${size}px "${TEXT}", serif`;
      lines = wrap(g, line, 0.7 * W);
      if (lines.length <= 2) break;
    }
    if (lines.length > 2) {
      console.warn("createChapterBoards: a line is too long for its board, it is cut after two lines");
      lines = [lines[0], `${lines[1].replace(/[\s.,;:]+$/, "")}…`];
    }
    lines.forEach((l, i) => g.fillText(l, W / 2, y + 0.26 * H + i * size * 1.22));
  }
  return canvas;
}

export async function createChapterBoards(root: THREE.Object3D, { story = {}, reasons = {}, fontsUrl }: ChapterBoardOptions = {}): Promise<void> {
  await loadFonts(fontsUrl);
  for (const [key, chapter] of [["story", story], ["reasons", reasons]] as const) {
    const [material, title] = BOARDS[key];
    const board = findProps(root, material)[0];
    if (!board) {
      console.error(`createChapterBoards: no ${material} in the model`);
      continue;
    }
    board.material = boardMaterial(root, draw(Math.round(W / boardAspect(board)), chapter.title ?? title, chapter.line));
  }
}
