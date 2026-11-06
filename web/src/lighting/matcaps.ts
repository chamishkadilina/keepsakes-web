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

let satinBlack: THREE.CanvasTexture | null = null;

/** Satin black (track lights): deep warm black with a soft sheen from the room's lights and a warm bounce from the floor. */
export function createSatinBlackMatcap(): THREE.CanvasTexture {
  return (satinBlack ??= drawMatcap(128, (g, size) => {
    const body = g.createLinearGradient(0, 0, 0, size);
    body.addColorStop(0, "#5c544e");
    body.addColorStop(0.35, "#2b2624");
    body.addColorStop(0.72, "#151312");
    body.addColorStop(1, "#2a1d16");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.32, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(8,6,5,0)");
    rim.addColorStop(1, "rgba(8,6,5,0.6)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.42, 0.26, 0.32, "rgba(255,236,214,0.2)");     // broad satin sheen
    highlight(g, size, 0.44, 0.2, 0.09, "rgba(255,246,236,0.42)");     // soft hot spot
  }));
}

let velvet: THREE.CanvasTexture | null = null;

/**
 * Velvet: deep where it faces you, its pile catching the light where it turns away (the soft glowing edges of
 * real velvet). Tint it with the material colour (sofas, cushions, roses).
 */
export function createVelvetMatcap(): THREE.CanvasTexture {
  return (velvet ??= drawMatcap(128, (g, size) => {
    const c = size / 2;
    const body = g.createRadialGradient(c, c * 0.96, 0, c, c, c);
    body.addColorStop(0, "#c2c2c2");
    body.addColorStop(0.55, "#c8c8c8");
    body.addColorStop(0.8, "#dcdcdc");
    body.addColorStop(0.93, "#f3f3f3");
    body.addColorStop(1, "#ffffff");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const shade = g.createLinearGradient(0, 0, 0, size);                   // lit from the ceiling: a little darker below
    shade.addColorStop(0, "rgba(255,255,255,0.08)");
    shade.addColorStop(0.55, "rgba(0,0,0,0)");
    shade.addColorStop(1, "rgba(0,0,0,0.16)");
    g.fillStyle = shade;
    g.fillRect(0, 0, size, size);
  }));
}

let foil: THREE.CanvasTexture | null = null;

/**
 * Mylar foil (the heart balloons): mirror-bright highlights of the ceiling lights, deep where it
 * reflects the dark floor, bright at the edges. Tint it with the balloon's colour.
 */
export function createFoilMatcap(): THREE.CanvasTexture {
  return (foil ??= drawMatcap(256, (g, size) => {
    const body = g.createLinearGradient(0, 0, 0, size);
    body.addColorStop(0, "#ffffff");
    body.addColorStop(0.3, "#cfcfcf");
    body.addColorStop(0.6, "#8c8c8c");
    body.addColorStop(0.85, "#5a5a5a");
    body.addColorStop(1, "#7a7a7a");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.3, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(255,255,255,0)");
    rim.addColorStop(0.8, "rgba(255,255,255,0.12)");
    rim.addColorStop(1, "rgba(255,255,255,0.45)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.36, 0.26, 0.2, "rgba(255,255,255,0.5)");
    highlight(g, size, 0.38, 0.22, 0.06, "rgba(255,255,255,1)");          // the hot spot of a ceiling light
    highlight(g, size, 0.66, 0.36, 0.05, "rgba(255,255,255,0.55)");        // a second, smaller light
    highlight(g, size, 0.5, 0.82, 0.22, "rgba(255,200,150,0.18)");         // warm bounce from the floor
  }));
}

let bulb: THREE.CanvasTexture | null = null;

/** A glowing golden bulb: light gold in its middle, bright gold round it, a deeper gold at its edge. */
export function createBulbMatcap(): THREE.CanvasTexture {
  return (bulb ??= drawMatcap(64, (g, size) => {
    const glow = g.createRadialGradient(size * 0.47, size * 0.45, 0, size / 2, size / 2, size * 0.5);
    glow.addColorStop(0, "#ffeaa0");
    glow.addColorStop(0.4, "#ffc93c");
    glow.addColorStop(0.8, "#f5a524");
    glow.addColorStop(1, "#e08a16");
    g.fillStyle = glow;
    g.fillRect(0, 0, size, size);
  }));
}

let latex: THREE.CanvasTexture | null = null;

/**
 * Latex balloon: a soft satin body, a little deeper towards its edges, with the bright, sharp reflection of a ceiling
 * light and a faint second one. Tint it with the balloon's colour.
 */
export function createLatexMatcap(): THREE.CanvasTexture {
  return (latex ??= drawMatcap(256, (g, size) => {
    const body = g.createRadialGradient(size * 0.42, size * 0.38, size * 0.05, size / 2, size / 2, size * 0.52);
    body.addColorStop(0, "#ffffff");
    body.addColorStop(0.55, "#d6d6d6");
    body.addColorStop(0.85, "#9a9a9a");
    body.addColorStop(1, "#6e6e6e");
    g.fillStyle = body;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.36, 0.28, 0.1, "rgba(255,255,255,0.7)");
    highlight(g, size, 0.37, 0.26, 0.035, "rgba(255,255,255,1)");          // the hot spot of a ceiling light
    highlight(g, size, 0.66, 0.4, 0.04, "rgba(255,255,255,0.35)");
  }));
}

let glass: THREE.CanvasTexture | null = null;

/**
 * Clear glass, drawn additively: nothing where you look straight through it, a faint sheen where it turns away from you
 * and a soft reflection of the ceiling lights. Black = invisible.
 */
export function createGlassMatcap(): THREE.CanvasTexture {
  return (glass ??= drawMatcap(128, (g, size) => {
    g.fillStyle = "#000";
    g.fillRect(0, 0, size, size);
    const rim = g.createRadialGradient(size / 2, size / 2, size * 0.28, size / 2, size / 2, size * 0.5);
    rim.addColorStop(0, "rgba(255,250,240,0)");
    rim.addColorStop(1, "rgba(255,250,240,0.28)");
    g.fillStyle = rim;
    g.fillRect(0, 0, size, size);
    g.globalCompositeOperation = "lighter";
    highlight(g, size, 0.36, 0.3, 0.16, "rgba(255,246,230,0.16)");
    highlight(g, size, 0.38, 0.24, 0.05, "rgba(255,250,240,0.4)");
  }));
}

/** Glass of the vitrines, lanterns and the neon's acrylic panel: it only adds its reflections. */
export function createGlassMaterial(): THREE.MeshMatcapMaterial {
  return new THREE.MeshMatcapMaterial({
    matcap: createGlassMatcap(), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false,
  });
}

/** Soft studio shading in white: tint it with the material colour (fixtures, petals). */
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
