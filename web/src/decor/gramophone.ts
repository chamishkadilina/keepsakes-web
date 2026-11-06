import * as THREE from "three";
import { findProps } from "./findProps";
import { SERIF, loadFonts } from "./fonts";
import { wrap } from "./lettering";

/**
 * The gramophone by the heart room's dance floor plays their song. Its record (grooves, and a wine-red label with the
 * song's title) turns while the song plays: whenever someone stands on the dance floor, fading in as they step on and
 * out as they step off, and softly when they are close to it; or everywhere after play(). The model marks the dance
 * floor (`dance_floor`: its middle, userData.radius) and holds the record (gramophone_record). Browsers only start
 * sound after a tap: call unlock() from your "enter the museum" tap. Each visitor hears it on their own device.
 *
 *   const gramophone = await createGramophone(gltf.scene, { song: songUrl, title: "Perfect" });
 *   enterButton.addEventListener("click", () => gramophone.unlock());
 *   useFrame(({ camera }, delta) => gramophone.update(camera.position, delta));
 */
export interface GramophoneOptions {
  song?: string;                     // their song (an mp3/m4a URL); without it the record still turns on the dance floor
  title?: string;                    // on the record's label, e.g. "Perfect"
  volume?: number;                   // on the dance floor, 0..1 (default 0.8)
  fontsUrl?: string;                 // folder with the fonts (web/public/fonts)
}

export interface Gramophone {
  update(visitor: THREE.Vector3, dt: number): void;   // every frame, with the visitor's position
  unlock(): void;                                     // from a tap: lets the browser play the song
  play(): void;                                       // play at full volume wherever the visitor is
  stop(): void;                                       // back to playing on and near the dance floor only
  dispose(): void;
}

const NEAR = 5;                      // heard softly up to this far beyond the dance floor's edge (metres)
const SPIN = (33 / 60) * Math.PI * 2;                // 33 turns a minute

function drawRecord(title: string): HTMLCanvasElement {
  const S = 512, c = S / 2, canvas = document.createElement("canvas");
  canvas.width = canvas.height = S;
  const g = canvas.getContext("2d")!;
  g.fillStyle = "#121010";
  g.fillRect(0, 0, S, S);
  for (let r = 0.48 * S; r > 0.2 * S; r -= 3) {                                 // the grooves
    g.strokeStyle = Math.round(r / 3) % 2 ? "#1c1919" : "#0d0b0b";
    g.lineWidth = 1.5;
    g.beginPath(); g.arc(c, c, r, 0, Math.PI * 2); g.stroke();
  }
  g.fillStyle = "#7d1426";                                                       // the label
  g.beginPath(); g.arc(c, c, 0.19 * S, 0, Math.PI * 2); g.fill();
  g.strokeStyle = "#d8b878"; g.lineWidth = 3;
  g.beginPath(); g.arc(c, c, 0.175 * S, 0, Math.PI * 2); g.stroke();
  g.fillStyle = "#e9cf98";
  g.textAlign = "center";
  g.font = `600 17px "${SERIF}", serif`;
  g.fillText("O U R   S O N G", c, c - 0.08 * S);
  let size = 30, lines: string[] = [];
  for (; size > 14; size -= 2) {
    g.font = `600 ${size}px "${SERIF}", serif`;
    lines = wrap(g, title, 0.3 * S);
    if (lines.length <= 2) break;
  }
  lines.slice(0, 2).forEach((l, i) => g.fillText(l, c, c + 0.06 * S + i * size * 1.1 - (lines.length > 1 ? size * 0.55 : 0)));
  g.fillStyle = "#121010";
  g.beginPath(); g.arc(c, c, 0.012 * S, 0, Math.PI * 2); g.fill();
  return canvas;
}

export async function createGramophone(root: THREE.Object3D, { song, title = "", volume = 0.8, fontsUrl }: GramophoneOptions = {}): Promise<Gramophone> {
  const record = findProps(root, "gramophone_record")[0];
  const floor = root.getObjectByName("dance_floor");
  if (!record || !floor) console.error("createGramophone: no gramophone_record or dance_floor in the model");

  const pivot = new THREE.Group();                                               // the record turns about its middle
  if (record?.parent) {
    await loadFonts(fontsUrl);
    const texture = new THREE.CanvasTexture(drawRecord(title));
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.flipY = false;                                                       // glTF UV convention
    texture.anisotropy = 4;
    const intensity = (root.userData.lightmapIntensity as number | undefined) ?? 1;
    record.material = new THREE.MeshBasicMaterial({ map: texture, color: new THREE.Color(intensity, intensity, intensity), vertexColors: true });
    record.updateWorldMatrix(true, false);
    pivot.position.copy(record.parent.worldToLocal(new THREE.Box3().setFromObject(record).getCenter(new THREE.Vector3())));
    record.parent.add(pivot);
    pivot.updateWorldMatrix(true, false);
    pivot.attach(record);
  }
  const centre = floor ? floor.getWorldPosition(new THREE.Vector3()) : new THREE.Vector3();
  const radius = (floor?.userData.radius as number | undefined) ?? 1.25;

  const audio = song ? new Audio(song) : null;
  let unlocked = false, forced = false, level = 0, speed = 0;
  let quietNear = true;                                                          // false where volume is fixed (iOS): no soft playing nearby
  if (audio) {
    audio.loop = true;
    audio.preload = "auto";
    audio.volume = 0.5;
    quietNear = audio.volume === 0.5;
    audio.volume = 0;
  }

  return {
    update(visitor, dt) {
      const d = Math.hypot(visitor.x - centre.x, visitor.z - centre.z) - radius;  // 0 or less: on the dance floor
      const near = quietNear ? Math.max(0, 1 - d / NEAR) * 0.35 : 0;
      const target = forced || d <= 0 ? 1 : near;
      level += (target - level) * Math.min(1, dt * 1.5);                         // fades in and out
      if (audio && unlocked) {
        audio.volume = Math.min(1, level * volume);
        if (level > 0.01 && audio.paused) void audio.play().catch(() => {});
        if (level < 0.005 && !audio.paused) audio.pause();
      }
      speed += ((target > 0.5 || level > 0.05 ? SPIN : 0) - speed) * Math.min(1, dt * 2);   // spins up, slows to a stop
      pivot.rotation.y -= speed * dt;
    },
    unlock() {
      if (!audio || unlocked) return;
      unlocked = true;
      void audio.play().then(() => { if (level < 0.005) audio.pause(); }).catch(() => {});   // starting it in the tap unlocks it
    },
    play() { forced = true; },
    stop() { forced = false; },
    dispose() {
      audio?.pause();
      audio?.removeAttribute("src");
    },
  };
}
