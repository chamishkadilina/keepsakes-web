import * as THREE from "three";
import { TREE_WIND, WIND_GLSL } from "./wind";

/**
 * The curtain of little warm lights hanging behind the foyer's ivory sheers, as couples string them at home: tiny
 * points of light that softly twinkle, each in its own slow rhythm, seen glowing through the voile. The model lists
 * where each light hangs (the `fairy_lights` empty, or the garden's `garden_lights`: userData.fairies = x, y, z, ... in
 * Blender coordinates, z up); their warm glow on the wall behind is baked. One draw call, animated on the GPU; drawn just before the sheers (so they show
 * through them) and before everything else that is see-through.
 *
 *   scene.add(createCurtainLights(gltf.scene));      // after applyBakedLighting
 */
export interface CurtainLightOptions {
  colour?: THREE.ColorRepresentation;  // warm white by default
  twinkle?: boolean;                   // each light softly brightens and dims in its own slow rhythm (default true)
  marker?: string;                     // the empty listing them (default fairy_lights; the garden's: garden_lights)
  size?: number;                       // each light's glow across (metres; default 0.08: a bright dot in a small soft glow)
  wind?: boolean;                      // they sway in the breeze with the garden's big tree (wind.ts; default false)
}

const vertexShader = (wind: boolean) => /* glsl */ `
  attribute float phase;
  uniform float time;
  uniform float twinkle;
  uniform float pixelsPerMetre;
  uniform float size;
  varying float vGlow;
  ${wind ? WIND_GLSL : ""}
  void main() {
    vec4 mv = modelViewMatrix * vec4(position${wind ? ` + ${TREE_WIND("position")}` : ""}, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = clamp(pixelsPerMetre * size / -mv.z, 1.5, 48.0);
    vGlow = 1.0 - twinkle * (0.22 + 0.22 * sin(time * (0.5 + 0.7 * phase) + phase * 40.0));
  }`;

const fragmentShader = /* glsl */ `
  uniform vec3 color;
  varying float vGlow;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float light = exp(-d * d * 90.0) + 0.45 * exp(-d * d * 12.0);
    gl_FragColor = vec4(color * light * vGlow, 1.0);
  }`;

export function createCurtainLights(root: THREE.Object3D, { colour = 0xffd9a8, twinkle = true, marker = "fairy_lights", size = 0.08, wind = false }: CurtainLightOptions = {}): THREE.Points {
  const flat: number[] = (root.getObjectByName(marker)?.userData.fairies as number[] | undefined) ?? [];
  if (!flat.length) console.error(`createCurtainLights: no ${marker} in the model`);
  const positions: number[] = [], phases: number[] = [];
  for (let i = 0; i + 2 < flat.length; i += 3) {
    positions.push(flat[i], flat[i + 2], -flat[i + 1]);             // Blender (x, y, z) -> three.js (x, z, -y)
    phases.push(Math.random());
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("phase", new THREE.Float32BufferAttribute(phases, 1));
  const uniforms = { color: { value: new THREE.Color(colour) }, time: { value: 0 }, twinkle: { value: twinkle ? 1 : 0 }, pixelsPerMetre: { value: 800 }, size: { value: size }, windTime: { value: 0 } };
  const lights = new THREE.Points(geometry, new THREE.ShaderMaterial({
    vertexShader: vertexShader(wind), fragmentShader, uniforms, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  }));
  lights.name = marker;
  lights.frustumCulled = false;
  lights.renderOrder = -2;                                         // before the sheers (-1) and all else see-through
  const buffer = new THREE.Vector2();
  lights.onBeforeRender = (renderer, _scene, camera) => {
    uniforms.time.value = uniforms.windTime.value = performance.now() / 1000;   // the same clock as wind.ts
    uniforms.pixelsPerMetre.value = renderer.getDrawingBufferSize(buffer).y * camera.projectionMatrix.elements[5] / 2;
  };
  return lights;
}
