import * as THREE from "three";
import { findProps } from "./findProps";
import { CALLIGRAPHY, loadFonts } from "./fonts";
import { GOLD, boardMaterial, heart } from "./lettering";

/**
 * The round ivory rug in the foyer's open middle with the couple's initials woven into it: their first letters in gold
 * calligraphy either side of a little heart, inside a ring of tiny roses and a dusty-rose border with fine gold lines,
 * read from the entrance. Lit by the rug's own baked light. Call after applyBakedLighting; it only replaces the rug's
 * material (no extra draw call).
 *
 *   await createMonogramRug(gltf.scene, { names: "Kasun & Nethmi" });
 */
export interface MonogramRugOptions {
  names?: string;                    // "Kasun & Nethmi": the initials are their first letters
  initials?: [string, string];       // or give the two letters directly
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const S = 1024;                      // the rug's texture (its UVs span the square round it)
const IVORY = "#f3ebdf", ROSE = "#c99aa1", BLUSH = "#e6b9bf", RED = "#9e2a3a";

/** The initials from "Kasun & Nethmi" (or "Kasun and Nethmi"). */
function initialsOf(names = ""): [string, string] {
  const parts = names.split(/\s*(?:&|\band\b|\+)\s*/i).map((n) => n.trim()).filter(Boolean);
  return [(parts[0] ?? "").charAt(0).toUpperCase(), (parts[1] ?? "").charAt(0).toUpperCase()];
}

function draw([a, b]: [string, string]): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = S;
  const g = canvas.getContext("2d")!;
  const c = S / 2, ring = (r: number, width: number, style: string) => {
    g.strokeStyle = style; g.lineWidth = width;
    g.beginPath(); g.arc(c, c, r, 0, Math.PI * 2); g.stroke();
  };
  g.fillStyle = IVORY;
  g.fillRect(0, 0, S, S);
  const shade = g.createRadialGradient(c, c, S * 0.1, c, c, S * 0.5);       // soft wool, a little deeper towards its edge
  shade.addColorStop(0, "rgba(255,255,255,0.18)");
  shade.addColorStop(1, "rgba(150,110,80,0.10)");
  g.fillStyle = shade;
  g.fillRect(0, 0, S, S);
  ring(0.455 * S, 0.05 * S, ROSE);                                             // the border, between fine gold lines
  ring(0.427 * S, 3, GOLD);
  ring(0.483 * S, 3, GOLD);
  ring(0.33 * S, 2, GOLD);
  for (let k = 0; k < 36; k++) {                                               // a ring of tiny roses and leaves
    const t = (k / 36) * Math.PI * 2, x = c + Math.cos(t) * 0.375 * S, y = c + Math.sin(t) * 0.375 * S;
    g.fillStyle = k % 2 ? BLUSH : RED;
    g.beginPath(); g.arc(x, y, 0.011 * S, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#7f9466";
    g.beginPath(); g.ellipse(x + Math.cos(t + 1.2) * 0.016 * S, y + Math.sin(t + 1.2) * 0.016 * S, 0.009 * S, 0.004 * S, t, 0, Math.PI * 2); g.fill();
  }
  g.fillStyle = GOLD;
  g.textAlign = "center";
  g.textBaseline = "alphabetic";
  g.font = `${0.25 * S}px "${CALLIGRAPHY}", cursive`;
  g.fillText(a, c - 0.165 * S, c + 0.07 * S);
  g.fillText(b, c + 0.17 * S, c + 0.07 * S);
  g.fillStyle = RED;
  heart(g, c, c - 0.01 * S, 0.04 * S);
  return canvas;
}

export async function createMonogramRug(root: THREE.Object3D, { names, initials, fontsUrl }: MonogramRugOptions = {}): Promise<void> {
  const rug = findProps(root, "monogram_rug")[0];
  if (!rug) {
    console.error("createMonogramRug: no monogram_rug in the model");
    return;
  }
  await loadFonts(fontsUrl);
  rug.material = boardMaterial(root, draw(initials ?? initialsOf(names)));
}
