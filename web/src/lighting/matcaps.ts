import * as THREE from "three";

/**
 * Matcaps drawn in code (no downloaded files). A matcap gives a surface believable shading with no lights,
 * so small objects (gold, fixtures, petals) look solid and premium on every device at almost no cost.
 */
function drawMatcap(size: number, draw: (g: CanvasRenderingContext2D, size: number) => void): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  draw(canvas.getContext("2d")!, size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function highlight(g: CanvasRenderingContext2D, size: number, x: number, y: number, r: number, color: string) {
  const h = g.createRadialGradient(x * size, y * size, 0, x * size, y * size, r * size);
  h.addColorStop(0, color);
  h.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = h;
  g.fillRect(0, 0, size, size);
}

let gold: THREE.CanvasTexture | null = null;
let soft: THREE.CanvasTexture | null = null;

/** Polished gold leaf: bright warm highlights from the ceiling lights, deep brown in the carved hollows. */
export function createGoldMatcap(): THREE.CanvasTexture {
  return (gold ??= drawMatcap(256, (g, size) => {
    const body = g.createLinearGradient(0, 0, 0, size);
    body.addColorStop(0.0, "#fff1c4");
    body.addColorStop(0.2, "#f2cf7a");
    body.addColorStop(0.45, "#c99a42");
    body.addColorStop(0.7, "#8a6127");
    body.addColorStop(0.88, "#4f3416");
    body.addColorStop(1.0, "#2f1f0e");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.32, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(45,28,12,0)");
    rim.addColorStop(1, "rgba(45,28,12,0.65)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.4, 0.24, 0.34, "rgba(255,214,140,0.45)");
    highlight(g, size, 0.42, 0.2, 0.08, "rgba(255,250,228,0.95)");
    highlight(g, size, 0.7, 0.62, 0.18, "rgba(255,190,110,0.18)");    // warm bounce from the floor
  }));
}

/**
 * Gold material (frames, ornaments, gold lines, lamp trims). Shown exactly as drawn, not tone-mapped:
 * tone mapping would wash the gold out to a pale beige.
 */
export function createGoldMaterial(options: THREE.MeshMatcapMaterialParameters = {}): THREE.MeshMatcapMaterial {
  return new THREE.MeshMatcapMaterial({ matcap: createGoldMatcap(), toneMapped: false, ...options });
}

let roseGold: THREE.CanvasTexture | null = null;

/** Satin rose gold (photo frames): soft, warm and light with a gentle sheen. Modern and romantic, not antique. */
export function createFrameMatcap(): THREE.CanvasTexture {
  return (roseGold ??= drawMatcap(256, (g, size) => {
    const body = g.createLinearGradient(0, 0, 0, size);
    body.addColorStop(0.0, "#fff3ec");
    body.addColorStop(0.25, "#f2d3c2");
    body.addColorStop(0.5, "#dcac92");
    body.addColorStop(0.75, "#b07c64");
    body.addColorStop(1.0, "#76503f");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.34, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(70,52,34,0)");
    rim.addColorStop(1, "rgba(70,52,34,0.35)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.42, 0.3, 0.42, "rgba(255,246,232,0.35)");       // broad satin sheen
    highlight(g, size, 0.44, 0.22, 0.1, "rgba(255,255,255,0.7)");        // soft hot spot
    highlight(g, size, 0.66, 0.66, 0.2, "rgba(255,214,190,0.14)");      // warm blush from the room
  }));
}

/** Material for the photo frames (single frames and the collage): rose gold, shown exactly as drawn. */
export function createFrameMaterial(options: THREE.MeshMatcapMaterialParameters = {}): THREE.MeshMatcapMaterial {
  return new THREE.MeshMatcapMaterial({ matcap: createFrameMatcap(), toneMapped: false, ...options });
}

/** Soft studio shading in white: tint it with the material colour (fixtures, track lights, petals). */
export function createSoftMatcap(): THREE.CanvasTexture {
  return (soft ??= drawMatcap(128, (g, size) => {
    const body = g.createLinearGradient(0, 0, 0, size);
    body.addColorStop(0, "#ffffff");
    body.addColorStop(0.5, "#d9d4ce");
    body.addColorStop(1, "#7a7570");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.3, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(60,55,50,0)");
    rim.addColorStop(1, "rgba(60,55,50,0.55)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.4, 0.28, 0.2, "rgba(255,255,255,0.35)");
  }));
}
