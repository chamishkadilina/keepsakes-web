import * as THREE from "three";

/**
 * The fire's flames, as a real fire burns: many tongues of flame, each born on the coals, stretching up and licking
 * sideways, then breaking off and fading as new ones rise beneath it. Each tongue is a ragged, noise-eroded teardrop
 * with a hot yellow-white foot and orange-red tips; where they overlap the fire's heart burns brightest. They stay
 * upright and turn to face you; a soft heat halo glows round them. Additive, not lit, untouched by tone mapping.
 */
export const NOISE = /* glsl */ `
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
  }
  float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 5; i++) { v += a * noise(p); p *= 2.03; a *= 0.5; } return v; }`;

export const BILLBOARD_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

const tongueVertex = /* glsl */ `
  attribute vec4 seed;
  uniform float time;
  uniform float height;
  uniform float width;
  uniform float base;
  varying vec2 vUv;
  varying float vLife;
  varying float vSeed;
  void main() {
    float age = time * (0.75 + 0.5 * seed.x) + seed.y, life = fract(age), cycle = floor(age);
    float a = fract(seed.z + cycle * 0.618) * 6.2832, r = base * sqrt(fract(seed.w + cycle * 0.382));   // a new spot each time
    float k = fract(seed.x + cycle * 0.754);
    vec3 foot = vec3(cos(a) * r, 0.0, sin(a) * r) * (1.0 - 0.5 * life);              // drawn in to the middle as it rises
    foot.y = height * 0.45 * life * life;                                             // breaking off the coals, late in life
    foot.xz += vec2(sin(time * 2.3 + seed.x * 9.0), cos(time * 1.9 + seed.y * 7.0)) * 0.05 * life;
    float tall = height * (0.45 + 0.55 * k) * (1.0 - 0.4 * r / max(base, 0.001)) * (0.55 + 0.6 * life);   // tallest in the middle
    float wide = width * (0.6 + 0.4 * seed.w) * (1.0 - 0.45 * life);
    vec3 right = normalize(vec3(viewMatrix[0][0], 0.0, viewMatrix[2][0]));           // upright, turned to the camera
    vec3 at = foot + right * (uv.x - 0.5) * wide + vec3(0.0, uv.y * tall, 0.0);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(at, 1.0);
    vUv = uv; vLife = life; vSeed = seed.x + seed.z;
  }`;

const tongueFragment = /* glsl */ `
  uniform float time;
  varying vec2 vUv;
  varying float vLife;
  varying float vSeed;
  ${NOISE}
  void main() {
    vec2 p = vUv;
    float n = fbm(vec2(p.x * 2.6 + vSeed * 13.0, p.y * 2.2 - time * 2.4 - vSeed * 5.0));
    float lick = (n - 0.5) * 0.5 * p.y;                                              // the tongue bends and licks
    float halfWidth = 0.5 * pow(1.0 - p.y, 0.75) * (0.55 + 0.45 * smoothstep(0.0, 0.3, p.y));   // round foot, pointed tip
    float shape = 1.0 - smoothstep(0.5, 1.0, abs(p.x - 0.5 - lick) / max(halfWidth, 0.001));
    float fade = smoothstep(0.0, 0.12, vLife) * (1.0 - smoothstep(0.5, 1.0, vLife));
    float heat = shape * (0.45 + 0.9 * n) * (1.05 - 0.8 * p.y) * fade - vLife * 0.25;  // eroding as it dies
    heat = clamp(heat, 0.0, 1.0) * smoothstep(0.0, 0.1, p.y);
    vec3 colour = mix(vec3(0.45, 0.06, 0.01), vec3(1.0, 0.34, 0.05), smoothstep(0.04, 0.3, heat));
    colour = mix(colour, vec3(1.0, 0.66, 0.22), smoothstep(0.3, 0.6, heat));
    colour = mix(colour, vec3(1.0, 0.9, 0.68), smoothstep(0.65, 0.95, heat));          // the hot foot
    gl_FragColor = vec4(colour * smoothstep(0.02, 0.25, heat) * 0.55, 1.0);
  }`;

const haloFragment = /* glsl */ `
  uniform float time;
  varying vec2 vUv;
  void main() {
    vec2 d = (vUv - vec2(0.5, 0.4)) * vec2(1.0, 0.8);
    float flicker = 0.85 + 0.08 * sin(time * 9.1) + 0.07 * sin(time * 15.7 + 1.3);
    gl_FragColor = vec4(vec3(1.0, 0.42, 0.1) * exp(-dot(d, d) * 14.0) * 0.28 * flicker, 1.0);
  }`;

export function additive(vertexShader: string, fragmentShader: string, uniforms: Record<string, THREE.IUniform>) {
  return new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms, transparent: true, depthWrite: false,
    blending: THREE.AdditiveBlending, toneMapped: false, side: THREE.DoubleSide });
}

/** `count` tongues of flame (one draw call) rising from a bed `base` metres across. */
export function createFlames(time: THREE.IUniform, count: number, height: number, width: number, base: number): THREE.Mesh {
  const plane = new THREE.PlaneGeometry(1, 1).translate(0, 0.5, 0);   // its foot at the bottom
  const geometry = new THREE.InstancedBufferGeometry();
  geometry.setIndex(plane.index);
  geometry.setAttribute("position", plane.getAttribute("position"));
  geometry.setAttribute("uv", plane.getAttribute("uv"));
  geometry.instanceCount = count;
  geometry.setAttribute("seed", new THREE.InstancedBufferAttribute(new Float32Array(Array.from({ length: count * 4 }, Math.random)), 4));
  const tongues = new THREE.Mesh(geometry, additive(tongueVertex, tongueFragment,
    { time, height: { value: height }, width: { value: width }, base: { value: base } }));
  tongues.frustumCulled = false;                                   // drawn where the shader puts them
  return tongues;
}

/** The soft heat halo round the flames; turn it to the camera each frame. */
export function createHalo(time: THREE.IUniform, height: number): THREE.Mesh {
  return new THREE.Mesh(new THREE.PlaneGeometry(height * 2.2, height * 2.2).translate(0, height * 0.65, 0),
    additive(BILLBOARD_VERTEX, haloFragment, { time }));
}
