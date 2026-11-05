import * as THREE from "three";

/**
 * Candle flames: every candle and lantern in the museum burns with a small, softly flickering flame. The model lists
 * where each flame burns (the `candle_flames` empty: userData.flames = x, y, z, x, y, z, ... in Blender coordinates,
 * z up); the flames always turn to face you and stay upright, like real ones, and each flickers in its own rhythm.
 * Their warm light on the floors, walls and furniture is baked. One draw call; the flicker runs on the GPU (nothing to
 * update per frame). The floor reflection shows them too.
 *
 *   scene.add(createCandleFlames(gltf.scene));      // after applyBakedLighting
 */
const WIDTH = 0.1, HEIGHT = 0.125;    // the quad (metres): the flame with its warm halo round it
const BASE = 0.3;                     // where the wick is, from the quad's bottom (share of HEIGHT)
const WICK = 0.015;                   // the model marks each flame's middle, this far above its wick

let texture: THREE.CanvasTexture | null = null;

/**
 * The flame: a bright, almost white heart above the wick, warm yellow round it, orange towards its tip, a touch of blue
 * at the wick, in a soft warm halo (it stands in for the glow a real flame has in your eyes, so it shows across a room).
 */
function flameTexture(): THREE.CanvasTexture {
  if (texture) return texture;
  const w = 192, h = 240, canvas = document.createElement("canvas");
  canvas.width = w; canvas.height = h;
  const g = canvas.getContext("2d")!;
  const px = w / WIDTH, cx = w / 2, wick = h * (1 - BASE);         // canvas pixels per metre, the wick
  const mid = wick - 0.016 * px;
  const halo = g.createRadialGradient(cx, mid, 0, cx, mid, w / 2);
  halo.addColorStop(0, "rgba(255,190,110,0.5)");
  halo.addColorStop(0.25, "rgba(255,160,80,0.22)");
  halo.addColorStop(0.6, "rgba(255,140,60,0.06)");
  halo.addColorStop(1, "rgba(255,130,50,0)");
  g.fillStyle = halo;
  g.fillRect(0, 0, w, h);
  const tip = wick - 0.042 * px, r = 0.0068 * px;                  // a flame ~4 cm tall, ~1.4 cm wide
  const outer = new Path2D();                                       // teardrop: round at the wick, pointed at the top
  outer.moveTo(cx, tip);
  outer.bezierCurveTo(cx + r * 0.6, tip + (wick - tip) * 0.3, cx + r * 1.15, tip + (wick - tip) * 0.6, cx + r, wick - r * 0.9);
  outer.bezierCurveTo(cx + r * 0.85, wick + r * 0.15, cx - r * 0.85, wick + r * 0.15, cx - r, wick - r * 0.9);
  outer.bezierCurveTo(cx - r * 1.15, tip + (wick - tip) * 0.6, cx - r * 0.6, tip + (wick - tip) * 0.3, cx, tip);
  const body = g.createLinearGradient(0, tip, 0, wick);
  body.addColorStop(0, "rgba(255,120,30,0)");
  body.addColorStop(0.18, "rgba(255,150,50,0.9)");
  body.addColorStop(0.55, "rgba(255,214,120,1)");
  body.addColorStop(0.88, "rgba(255,238,195,1)");
  body.addColorStop(1, "rgba(150,140,255,0.55)");
  g.filter = "blur(1.5px)";
  g.fillStyle = body;
  g.fill(outer);
  const core = g.createRadialGradient(cx, wick - r * 2, 1, cx, wick - r * 2, r * 1.6);
  core.addColorStop(0, "rgba(255,255,248,1)");
  core.addColorStop(1, "rgba(255,246,220,0)");
  g.fillStyle = core;
  g.beginPath();
  g.ellipse(cx, wick - r * 2, r * 0.75, r * 1.9, 0, 0, Math.PI * 2);
  g.fill();
  texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const vertexShader = /* glsl */ `
  attribute float phase;
  uniform float time;
  varying vec2 vUv;
  varying float vBright;
  void main() {
    vUv = uv;
    vec3 base = (modelMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
    vec3 toCamera = cameraPosition - base;
    vec3 right = normalize(vec3(toCamera.z, 0.0, -toCamera.x) + vec3(1e-4, 0.0, 0.0));   // upright, turned to the viewer
    float flicker = 1.0 + 0.08 * sin(time * 8.3 + phase) + 0.05 * sin(time * 13.7 + phase * 2.1) + 0.03 * sin(time * 21.3 + phase * 3.7);
    float up = uv.y - ${BASE.toFixed(2)};
    float sway = (0.1 * sin(time * 2.3 + phase * 1.3) + 0.06 * sin(time * 5.9 + phase * 0.7)) * max(up, 0.0) * max(up, 0.0);
    vec3 p = base + right * ((uv.x - 0.5 + sway) * ${WIDTH.toFixed(3)}) + vec3(0.0, up * ${HEIGHT.toFixed(3)} * (up > 0.0 ? flicker : 1.0) - ${WICK.toFixed(3)}, 0.0);
    vBright = 0.85 + 0.15 * flicker;
    gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
  }`;

const fragmentShader = /* glsl */ `
  uniform sampler2D map;
  varying vec2 vUv;
  varying float vBright;
  void main() {
    vec4 c = texture2D(map, vUv);
    gl_FragColor = vec4(c.rgb * vBright, c.a);
    #include <colorspace_fragment>
  }`;

export function createCandleFlames(root: THREE.Object3D): THREE.InstancedMesh | THREE.Group {
  const list = root.getObjectByName("candle_flames")?.userData.flames as number[] | undefined;
  if (!list?.length) {
    console.warn("createCandleFlames: no candle_flames in the model");
    return new THREE.Group();
  }
  const count = list.length / 3;
  const material = new THREE.ShaderMaterial({
    uniforms: { map: { value: flameTexture() }, time: { value: 0 } },
    vertexShader, fragmentShader, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const flames = new THREE.InstancedMesh(new THREE.PlaneGeometry(1, 1), material, count);
  const phase = new Float32Array(count), m = new THREE.Matrix4();
  for (let i = 0; i < count; i++) {
    flames.setMatrixAt(i, m.makeTranslation(list[3 * i], list[3 * i + 2], -list[3 * i + 1]));   // Blender (x, y, z) -> three (x, z, -y)
    phase[i] = (i * 2.399) % (Math.PI * 2);
  }
  flames.geometry.setAttribute("phase", new THREE.InstancedBufferAttribute(phase, 1));
  flames.frustumCulled = false;                                   // spread through the whole museum; one cheap draw
  flames.name = "candle_flames";
  flames.onBeforeRender = () => { material.uniforms.time.value = performance.now() / 1000; };
  return flames;
}
