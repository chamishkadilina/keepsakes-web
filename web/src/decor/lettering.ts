import * as THREE from "three";
import { SERIF } from "./fonts";

/**
 * Shared lettering for the boards the couple's words are written on (the title wall, the chapter boards, the quote
 * board): ivory paper with a fine double gold border, lines wrapped to a width, spaced serif capitals, a little gold
 * heart, and the board's material lit by its own baked light.
 */
export const INK = "#5a1822", GOLD = "#a8814a", PAPER = "#f6f0e4";

/** Ivory paper, softly deeper towards its edges, with a fine double gold border. */
export function paper(g: CanvasRenderingContext2D, w: number, h: number): void {
  g.fillStyle = PAPER;
  g.fillRect(0, 0, w, h);
  const shade = g.createRadialGradient(w / 2, h / 2, h * 0.25, w / 2, h / 2, h * 0.78);
  shade.addColorStop(0, "rgba(140, 100, 60, 0)");
  shade.addColorStop(1, "rgba(140, 100, 60, 0.1)");
  g.fillStyle = shade;
  g.fillRect(0, 0, w, h);
  g.strokeStyle = GOLD;
  g.lineWidth = 3;
  g.strokeRect(44, 44, w - 88, h - 88);
  g.lineWidth = 1.2;
  g.strokeRect(58, 58, w - 116, h - 116);
}

/** The words of `text` in lines no wider than `width` at the current font ("\n" breaks a line). */
export function wrap(g: CanvasRenderingContext2D, text: string, width: number): string[] {
  const lines: string[] = [];
  for (const row of text.trim().split("\n")) {
    let line = "";
    for (const word of row.trim().split(/\s+/).filter(Boolean)) {
      const next = line ? `${line} ${word}` : word;
      if (line && g.measureText(next).width > width) {
        lines.push(line);
        line = word;
      } else line = next;
    }
    if (line) lines.push(line);
  }
  return lines;
}

/** Spaced capitals centred on x, made smaller if they would be wider than `width`. */
export function capitals(g: CanvasRenderingContext2D, text: string, x: number, y: number, size: number, width: number): void {
  const chars = [...text.toUpperCase()];
  const measure = (s: number) => {
    g.font = `600 ${s}px "${SERIF}", serif`;
    const widths = chars.map((ch) => g.measureText(ch).width);
    return { widths, spacing: s * 0.2, total: widths.reduce((a, b) => a + b, 0) + s * 0.2 * (chars.length - 1) };
  };
  let m = measure(size);
  if (m.total > width) m = measure(size * width / m.total);
  let at = x - m.total / 2;
  g.textAlign = "left";
  chars.forEach((ch, i) => { g.fillText(ch, at, y); at += m.widths[i] + m.spacing; });
}

/** A little filled heart centred on (x, y), `s` = its half width. */
export function heart(g: CanvasRenderingContext2D, x: number, y: number, s: number): void {
  g.beginPath();
  g.moveTo(x, y + s * 0.42);
  g.bezierCurveTo(x - s * 1.1, y - s * 0.3, x - s * 0.5, y - s * 1.05, x, y - s * 0.42);
  g.bezierCurveTo(x + s * 0.5, y - s * 1.05, x + s * 1.1, y - s * 0.3, x, y + s * 0.42);
  g.fill();
}

/** A gold rule with a little heart in its middle, centred on x. */
export function heartRule(g: CanvasRenderingContext2D, x: number, y: number, half: number, size: number): void {
  g.fillStyle = GOLD;
  g.strokeStyle = GOLD;
  g.lineWidth = 2;
  for (const s of [-1, 1]) {
    g.beginPath();
    g.moveTo(x + s * size * 1.8, y);
    g.lineTo(x + s * half, y);
    g.stroke();
  }
  heart(g, x, y, size);
}

/** Sets the largest font (from `size` down) at which `text` is no wider than `width`; returns that size. */
export function fit(g: CanvasRenderingContext2D, text: string, font: (size: number) => string, size: number, width: number): number {
  g.font = font(size);
  const w = g.measureText(text).width;
  if (w > width) { size = Math.floor(size * width / w); g.font = font(size); }
  return size;
}

/** A board hung on a wall: its face's width over its height, from its mesh. */
export function boardAspect(board: THREE.Mesh): number {
  board.updateWorldMatrix(true, false);
  const size = new THREE.Box3().setFromObject(board).getSize(new THREE.Vector3());
  return Math.max(size.x, size.z) / size.y;
}

/** The board's material once written: the canvas (its UVs span the whole face), lit by the board's own baked light. */
export function boardMaterial(root: THREE.Object3D, canvas: HTMLCanvasElement): THREE.MeshBasicMaterial {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;                                                       // glTF UV convention
  texture.anisotropy = 8;
  const intensity = (root.userData.lightmapIntensity as number | undefined) ?? 1;
  return new THREE.MeshBasicMaterial({ map: texture, color: new THREE.Color(intensity, intensity, intensity), vertexColors: true });
}
