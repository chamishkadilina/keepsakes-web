import * as THREE from "three";
import { createGoldMaterial } from "./matcaps";
import { createTrackLights, type Lamp } from "./trackLights";

/**
 * Real-looking light fittings over the simple shapes in museum.glb:
 * recessed downlights (polished gold trim, deep reflector, hot lens), the gallery track lights (trackLights.ts) and
 * a soft glare on every lamp that grows when you look into the beam, the way the eye and a camera see real lamps.
 * 11 draw calls for all lamps. No real-time lights.
 */
const FITTINGS = [
  { name: "downlight_fixtures", glare: 0.7, strength: 0.8, cutoff: -0.1 },   // recessed downlights in the ceiling trays
  { name: "light_lenses", glare: 0.45, strength: 0.9, cutoff: 0.4 },         // track spots: the lens hides deep in the head
];

function canvasTexture(size: number, draw: (g: CanvasRenderingContext2D, c: number) => void): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  draw(canvas.getContext("2d")!, size / 2);
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Looking up into the lamp: hot lens, golden reflector rings, dark baffle at the rim. */
const lensTexture = () => canvasTexture(128, (g, c) => {
  const r = g.createRadialGradient(c, c, 0, c, c, c);
  r.addColorStop(0, "#fffcf4");
  r.addColorStop(0.45, "#fff0d2");
  r.addColorStop(0.6, "#ffd08a");
  r.addColorStop(0.8, "#c88a40");
  r.addColorStop(0.93, "#6a4018");
  r.addColorStop(1, "#2a1608");
  g.fillStyle = r;
  g.fillRect(0, 0, c * 2, c * 2);
  g.strokeStyle = "rgba(255,220,160,0.25)";                   // fine reflector rings
  for (let k = 0.48; k < 0.95; k += 0.09) { g.lineWidth = 1.5; g.beginPath(); g.arc(c, c, c * k, 0, Math.PI * 2); g.stroke(); }
});

/** Glare: a hot core and a long, faint warm falloff (no visible edge). */
const glareTexture = () => canvasTexture(128, (g, c) => {
  const r = g.createRadialGradient(c, c, 0, c, c, c);
  r.addColorStop(0, "rgba(255,250,240,1)");
  r.addColorStop(0.1, "rgba(255,238,210,0.75)");
  r.addColorStop(0.25, "rgba(255,212,160,0.3)");
  r.addColorStop(0.5, "rgba(255,180,115,0.09)");
  r.addColorStop(1, "rgba(255,160,95,0)");
  g.fillStyle = r;
  g.fillRect(0, 0, c * 2, c * 2);
});

/** Finds each lamp in a merged fitting mesh: groups vertices within 20 cm; the lamp faces along its mean normal. */
function lamps(mesh: THREE.Mesh): Lamp[] {
  const { position, normal } = mesh.geometry.attributes;
  const v = new THREE.Vector3(), n = new THREE.Vector3(), normalMatrix = new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld);
  const found: { p: THREE.Vector3; axis: THREE.Vector3; count: number }[] = [];
  for (let i = 0; i < position.count; i++) {
    v.fromBufferAttribute(position, i).applyMatrix4(mesh.matrixWorld);
    let lamp = found.find((l) => l.p.distanceTo(v) < 0.2);
    if (!lamp) found.push((lamp = { p: new THREE.Vector3(), axis: new THREE.Vector3(), count: 0 }));
    lamp.p.multiplyScalar(lamp.count).add(v).divideScalar(++lamp.count);                 // running mean
    if (normal) lamp.axis.add(n.fromBufferAttribute(normal, i).applyMatrix3(normalMatrix));
  }
  return found.map(({ p, axis }) => ({ p, axis: axis.lengthSq() > 0 ? axis.normalize() : new THREE.Vector3(0, -1, 0) }));
}

interface Glare extends Lamp { size: number; strength: number; cutoff: number }

/**
 * Glare sprites: brighter and larger when the camera looks into the lamp's beam, gone when the lamp is seen from
 * further off its beam than `cutoff` (cosine). Works in the floor reflection too.
 */
function createGlare(points: Glare[]): THREE.Points {
  const geometry = new THREE.BufferGeometry().setFromPoints(points.map(({ p }) => p));
  geometry.setAttribute("axis", new THREE.Float32BufferAttribute(points.flatMap(({ axis }) => axis.toArray()), 3));
  geometry.setAttribute("size", new THREE.Float32BufferAttribute(points.map(({ size }) => size), 1));
  geometry.setAttribute("strength", new THREE.Float32BufferAttribute(points.map(({ strength }) => strength), 1));
  geometry.setAttribute("cutoff", new THREE.Float32BufferAttribute(points.map(({ cutoff }) => cutoff), 1));
  const uniforms = { map: { value: glareTexture() }, scale: { value: 360 } };
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: /* glsl */ `
      attribute vec3 axis; attribute float size; attribute float strength; attribute float cutoff;
      uniform float scale;
      varying float vStrength;
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        vec3 toCamera = normalize(cameraPosition - world.xyz);
        float along = dot(toCamera, axis);
        float facing = smoothstep(0.35, 1.0, along);                 // 1 = looking straight into the beam
        vStrength = strength * (0.4 + 0.6 * facing) * smoothstep(cutoff, cutoff + 0.35, along);   // none from behind or beside the lamp
        gl_PointSize = min(size * (0.75 + 0.5 * facing) * scale / -(viewMatrix * world).z, 256.0);
        // drawn a little towards the camera (same spot on screen) so the ceiling around the lamp never cuts the glow
        world.xyz += toCamera * min(size * 0.5 / max(abs(along), 0.2), 1.0);
        gl_Position = projectionMatrix * viewMatrix * world;
      }`,
    fragmentShader: /* glsl */ `
      uniform sampler2D map;
      varying float vStrength;
      void main() {
        vec4 t = texture2D(map, gl_PointCoord);
        gl_FragColor = vec4(t.rgb * t.a * vStrength, 1.0);
      }`,
    blending: THREE.AdditiveBlending, transparent: true, depthWrite: false,
  });
  const glare = new THREE.Points(geometry, material);
  const size = new THREE.Vector2();
  glare.onBeforeRender = (renderer) => {                        // sprite size follows the target being drawn (screen or reflection)
    const target = renderer.getRenderTarget();
    uniforms.scale.value = (target ? target.height : renderer.getDrawingBufferSize(size).y) / 2;
  };
  glare.frustumCulled = false;
  glare.raycast = () => {};                                     // a light effect: never catches clicks or taps
  return glare;
}

export function addCeilingLights(root: THREE.Object3D, brightness = 1): THREE.Group {
  root.updateMatrixWorld(true);
  const group = new THREE.Group();
  group.name = "ceiling_lights";
  const glare: Glare[] = [];
  const lens = new THREE.MeshBasicMaterial({ map: lensTexture(), toneMapped: false });
  let downlights: THREE.Vector3[] = [];
  for (const f of FITTINGS) {
    const mesh = root.getObjectByName(f.name) as THREE.Mesh | undefined;
    if (!mesh) continue;
    let found = lamps(mesh);
    if (f.name === "downlight_fixtures") {
      downlights = found.map(({ p }) => p);
      mesh.visible = false;                                      // replaced by the detailed lamps below
    } else {
      const track = createTrackLights(root, found, lens);       // detailed rails and spots, lenses in their new heads
      group.add(track.group);
      found = track.lenses;
      mesh.removeFromParent();
    }
    found.forEach(({ p, axis }) => glare.push({ p: p.clone().addScaledVector(axis, 0.02), axis, size: f.glare, strength: f.strength * brightness, cutoff: f.cutoff }));
  }
  if (!glare.length) return group;

  // recessed downlight (radius 7.5 cm), facing down, top at the ceiling surface
  if (downlights.length) {
    const trim = new THREE.LatheGeometry([
      [0.046, 0.0], [0.047, -0.004], [0.052, -0.007], [0.064, -0.008], [0.072, -0.006], [0.0765, -0.002], [0.077, 0.0],
    ].map(([r, y]) => new THREE.Vector2(r, y)), 48);
    const disc = new THREE.CircleGeometry(0.047, 40).rotateX(Math.PI / 2).translate(0, -0.001, 0);
    const parts = [
      new THREE.InstancedMesh(trim, createGoldMaterial({ color: 0xf2dfc0, side: THREE.DoubleSide }), downlights.length),
      new THREE.InstancedMesh(disc, lens, downlights.length),
    ];
    const m = new THREE.Matrix4();
    downlights.forEach((p, i) => parts.forEach((part) => part.setMatrixAt(i, m.makeTranslation(p.x, p.y, p.z))));
    parts.forEach((part) => { part.frustumCulled = false; group.add(part); });
  }

  group.add(createGlare(glare));
  root.add(group);
  return group;
}
