import * as THREE from "three";
import { HAND, SERIF, loadFonts } from "../decor/fonts";

/**
 * A small museum label for a photo, like in a real gallery: its title in serif capitals, the date in gold and a line or
 * two of their story in handwriting, on a cream card with a fine gold edge, standing a little off the wall with a soft
 * shadow. As bright as the light on its wall. One draw call. Hang it under the photo's frame:
 *
 *   const frame = createPhotoFrame({ photo, width, height, light });
 *   const plaque = await createPhotoPlaque({ title: "Our first date", date: "14 February 2021", text: "You were late. I didn't mind.", light });
 *   plaque.position.y = -(frame.userData.outerSize[1] / 2 + 0.08 + plaque.userData.height / 2);
 *   frame.add(plaque);
 *
 * Faces +Z like the frame. Only make one where the photo has a caption.
 */
export interface PhotoPlaqueOptions {
  title: string;                     // e.g. "Our first date" (up to two lines)
  date?: string;                     // e.g. "14 February 2021"
  text?: string;                     // a line or two of their story (up to three lines)
  light?: [number, number, number];  // the slot's baked light (userData.light_rgb), as for the frame
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const PX = 1600;                     // canvas pixels per metre
const CARD = 0.24;                   // card width (metres)
const PAD = 0.016, EDGE = 0.012;     // padding inside the card; margin round it for the shadow
const INK = "#5a1822", GOLD = "#a8814a", PAPER = "#f8f2e8", LINE = "#c9a46a";

function lines(g: CanvasRenderingContext2D, text: string, width: number, max: number): string[] {
  const out: string[] = [];
  let line = "";
  for (const word of text.trim().split(/\s+/).filter(Boolean)) {
    const next = line ? `${line} ${word}` : word;
    if (line && g.measureText(next).width > width) { out.push(line); line = word; } else line = next;
  }
  if (line) out.push(line);
  if (out.length > max) { out.length = max; out[max - 1] = `${out[max - 1].replace(/[\s.,;:]+$/, "")}…`; }
  return out;
}

/** Rounded rectangle path (canvas roundRect is missing on older phones). */
function card(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

function spaced(g: CanvasRenderingContext2D, text: string, x: number, y: number, spacing: number) {
  const chars = [...text];
  const total = chars.reduce((a, ch) => a + g.measureText(ch).width, 0) + spacing * (chars.length - 1);
  let at = x - total / 2;
  g.textAlign = "left";
  for (const ch of chars) { g.fillText(ch, at, y); at += g.measureText(ch).width + spacing; }
}

export async function createPhotoPlaque({ title, date, text, light = [0.8, 0.7, 0.62], fontsUrl }: PhotoPlaqueOptions): Promise<THREE.Mesh> {
  await loadFonts(fontsUrl);
  const m = (metres: number) => Math.round(metres * PX);
  const canvas = document.createElement("canvas"), g = canvas.getContext("2d")!;
  const inner = m(CARD - 2 * PAD);
  const titleSize = m(0.0115), dateSize = m(0.0072), textSize = m(0.0105);
  g.font = `600 ${titleSize}px "${SERIF}", serif`;
  const titleLines = lines(g, title.toUpperCase(), inner * 0.92, 2);
  g.font = `500 ${textSize}px "${HAND}", cursive`;
  const textLines = text ? lines(g, text, inner, 3) : [];
  const height = PAD * 2 + titleLines.length * 0.016 + (date ? 0.013 : 0) + 0.008 + textLines.length * 0.0145;

  canvas.width = m(CARD + 2 * EDGE); canvas.height = m(height + 2 * EDGE);
  const x0 = m(EDGE), y0 = m(EDGE), w = m(CARD), h = m(height);
  g.shadowColor = "rgba(40,18,8,0.4)"; g.shadowBlur = m(0.006); g.shadowOffsetY = m(0.003);
  g.fillStyle = PAPER;
  card(g, x0, y0, w, h, m(0.002)); g.fill();
  g.shadowColor = "transparent";
  g.strokeStyle = LINE; g.lineWidth = Math.max(1, m(0.0006));
  card(g, x0 + m(0.005), y0 + m(0.005), w - m(0.01), h - m(0.01), m(0.001)); g.stroke();

  const cx = canvas.width / 2;
  let y = y0 + m(PAD);
  g.textBaseline = "top";
  g.fillStyle = INK; g.font = `600 ${titleSize}px "${SERIF}", serif`;
  for (const line of titleLines) { spaced(g, line, cx, y, titleSize * 0.12); y += m(0.016); }
  if (date) {
    g.fillStyle = GOLD; g.font = `600 ${dateSize}px "${SERIF}", serif`;
    spaced(g, date.toUpperCase(), cx, y, dateSize * 0.2); y += m(0.013);
  }
  g.strokeStyle = LINE;                                            // a short gold rule
  g.beginPath(); g.moveTo(cx - m(0.014), y + m(0.003)); g.lineTo(cx + m(0.014), y + m(0.003)); g.stroke();
  y += m(0.008);
  g.fillStyle = INK; g.font = `500 ${textSize}px "${HAND}", cursive`; g.textAlign = "center";
  for (const line of textLines) { g.fillText(line, cx, y); y += m(0.0145); }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  const bright = THREE.MathUtils.clamp(0.2126 * light[0] + 0.7152 * light[1] + 0.0722 * light[2], 0.45, 1);
  const plaque = new THREE.Mesh(
    new THREE.PlaneGeometry(CARD + 2 * EDGE, height + 2 * EDGE),
    new THREE.MeshBasicMaterial({ map: texture, color: new THREE.Color(bright, bright, bright), transparent: true, toneMapped: false }),
  );
  plaque.position.z = 0.006;                                       // stands a little off the wall
  plaque.userData.height = height;                                 // the card's height (without its shadow margin)
  plaque.userData.noReflection = true;                             // too small to show in the floor reflection
  return plaque;
}
