import * as THREE from "three";
import { findProps } from "./findProps";
import { HAND, loadFonts } from "./fonts";

/**
 * The neon sign in the corridor: their words in glowing pink script on clear acrylic, like a real neon. The first time
 * you come near, it switches on with a little flicker. Writes on the model's neon_text panel (its pink glow on the
 * wall is baked). Call after applyBakedLighting; no extra draw call.
 *
 *   await createNeonSign(gltf.scene, { text: "forever us" });
 */
export interface NeonSignOptions {
  text?: string;                     // a few words on one line ("forever us", "Kasun & Nethmi"); ~22 characters fit
  colour?: string;                   // the neon's glow (CSS colour), pink by default
  flicker?: boolean;                 // false: shine from the start (no switching on as you come near)
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

const W = 2048, H = 664;             // the panel's words area, 1.42 m × 0.46 m (its UVs span the whole canvas): sharp up close
const NEAR = 8;                      // switches on when you come this close (metres)
const FLICKER = [0, 1, 0, 0, 0.6, 0, 1, 0.3, 1];   // its first moments, one step every 70 ms, then steady

/** The words as glass tubes: a white-hot core with a coloured rim, crisp edged, in a soft glow close round them. */
function draw(text: string, colour: string): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d")!;
  g.fillStyle = "#000";                                           // black adds nothing (additive): only the neon shows
  g.fillRect(0, 0, W, H);
  let size = 440;
  const font = () => `500 ${size}px "${HAND}", cursive`;
  g.font = font();
  const width = g.measureText(text).width;
  if (width > W * 0.86) size *= (W * 0.86) / width;
  const x = W / 2, y = H * 0.52;
  const tubes = document.createElement("canvas");                 // the tubes on their own, then lit onto the panel
  tubes.width = W; tubes.height = H;
  const t = tubes.getContext("2d")!;
  for (const c of [g, t]) { c.font = font(); c.textAlign = "center"; c.textBaseline = "middle"; c.lineJoin = "round"; }
  t.fillStyle = "#fff4f8";                                        // hottest in the middle of each tube ...
  t.fillText(text, x, y);
  t.globalCompositeOperation = "source-atop";
  t.strokeStyle = colour;                                         // ... its own colour towards the glass's edges
  t.lineWidth = size * 0.05;
  t.strokeText(text, x, y);
  g.fillStyle = g.shadowColor = colour;
  g.globalAlpha = 0.5;                                            // the glow, close round the tubes
  for (const blur of [64, 28]) { g.shadowBlur = blur; g.fillText(text, x, y); }
  g.globalAlpha = 1;
  g.shadowBlur = 10;                                              // a thin halo hugging the glass
  g.drawImage(tubes, 0, 0);
  return canvas;
}

export async function createNeonSign(root: THREE.Object3D, { text = "forever us", colour = "#ff4fa0", flicker = true, fontsUrl }: NeonSignOptions = {}): Promise<void> {
  const panel = findProps(root, "neon_text")[0];
  if (!panel) {
    console.error("createNeonSign: no neon_text in the model");
    return;
  }
  await loadFonts(fontsUrl);
  const texture = new THREE.CanvasTexture(draw(text.trim(), colour));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;                                                       // glTF UV convention
  texture.anisotropy = 8;                                                      // read at an angle along the corridor
  const material = new THREE.MeshBasicMaterial({
    map: texture, color: flicker ? 0x000000 : 0xffffff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false,
  });
  panel.material = material;
  panel.visible = true;
  if (!flicker) return;

  panel.updateWorldMatrix(true, false);
  panel.geometry.computeBoundingSphere();
  const centre = panel.geometry.boundingSphere!.center.clone().applyMatrix4(panel.matrixWorld);
  const eye = new THREE.Vector3();
  let start = -1;
  panel.onBeforeRender = (_renderer, _scene, camera) => {
    if (start < 0) {
      eye.setFromMatrixPosition(camera.matrixWorld);
      if (Math.hypot(eye.x - centre.x, eye.z - centre.z) > NEAR) return;
      start = performance.now();
    }
    const step = Math.floor((performance.now() - start) / 70);
    material.color.setScalar(step < FLICKER.length ? FLICKER[step] : 1);
    if (step >= FLICKER.length) panel.onBeforeRender = () => {};               // on for good
  };
}
