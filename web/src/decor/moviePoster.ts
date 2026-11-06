import * as THREE from "three";
import { findProps } from "./findProps";
import { CALLIGRAPHY, SERIF, loadFonts } from "./fonts";
import { capitals, fit } from "./lettering";

/**
 * The "Now Showing" film poster in the cinema's lightbox, lit from within: their photo whole (never cropped or
 * stretched, as it is, in a fine gold frame), "A Love Story" in calligraphy, the two of them as its stars and a
 * tagline, on deep wine red. Call after applyBakedLighting; it only replaces the poster's material (no extra draw call).
 *
 *   await createMoviePoster(gltf.scene, { names: "Kasun & Nethmi", photo: texture });
 */
export interface MoviePosterOptions {
  names?: string;                    // "Kasun & Nethmi"
  photo?: THREE.Texture | CanvasImageSource;         // one of their photos (any shape; shown whole)
  title?: string;                    // default "A Love Story"
  tagline?: string;                  // default "Now showing, forever"
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const W = 1024, H = 1513;            // the poster's face, 0.9 m × 1.33 m (its UVs span the whole canvas)
const GOLD = "#d9b878", IVORY = "#f6ead8";

function draw({ names = "", photo, title = "A Love Story", tagline = "Now showing, forever" }: MoviePosterOptions): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  const bg = g.createRadialGradient(W / 2, H * 0.42, W * 0.1, W / 2, H * 0.5, H * 0.75);
  bg.addColorStop(0, "#4a1220");
  bg.addColorStop(1, "#16040a");
  g.fillStyle = bg;
  g.fillRect(0, 0, W, H);
  g.fillStyle = GOLD;
  capitals(g, "Now Showing", W / 2, 0.075 * H, 46, 0.6 * W);
  const image = (photo instanceof THREE.Texture ? photo.image : photo) as (CanvasImageSource & { width: number; height: number }) | undefined;
  if (image) {                                                                  // the photo, whole, as large as fits
    const iw = image.width, ih = image.height;
    const box = { x: 0.09 * W, y: 0.11 * H, w: 0.82 * W, h: 0.56 * H };
    const k = Math.min(box.w / iw, box.h / ih), w = iw * k, h = ih * k, x = box.x + (box.w - w) / 2, y = box.y + (box.h - h) / 2;
    g.drawImage(image, x, y, w, h);
    g.strokeStyle = GOLD; g.lineWidth = 4;
    g.strokeRect(x - 8, y - 8, w + 16, h + 16);
  }
  g.fillStyle = IVORY;
  g.textAlign = "center";
  fit(g, title, (s) => `${s}px "${CALLIGRAPHY}", cursive`, 150, 0.84 * W);
  g.fillText(title, W / 2, 0.775 * H);
  if (names) {
    g.fillStyle = GOLD;
    capitals(g, "Starring", W / 2, 0.83 * H, 28, 0.4 * W);
    g.fillStyle = IVORY;
    capitals(g, names, W / 2, 0.875 * H, 52, 0.84 * W);
  }
  g.fillStyle = GOLD;
  g.textAlign = "center";
  g.font = `600 30px "${SERIF}", serif`;
  g.fillText(tagline, W / 2, 0.94 * H);
  return canvas;
}

export async function createMoviePoster(root: THREE.Object3D, options: MoviePosterOptions = {}): Promise<void> {
  const face = findProps(root, "poster_face")[0];
  if (!face) {
    console.error("createMoviePoster: no poster_face in the model");
    return;
  }
  await loadFonts(options.fontsUrl);
  const texture = new THREE.CanvasTexture(draw(options));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;                                                       // glTF UV convention
  texture.anisotropy = 8;
  face.material = new THREE.MeshBasicMaterial({ map: texture, toneMapped: false });   // lit from within; the photo as it is
}
