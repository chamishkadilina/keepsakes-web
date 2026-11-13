import * as THREE from "three";
import { NOISE } from "./flames";

/** Sparks rising from the fire, twinkling and fading, and soft wisps of smoke curling up above it. */
const sparkVertex = /* glsl */ `
  attribute vec3 seed;
  uniform float time;
  uniform float rise;
  uniform float pixelsPerMetre;
  varying float vGlow;
  void main() {
    float life = fract(time * (0.22 + 0.18 * seed.x) + seed.y);
    float swirl = time * (1.0 + seed.z) + seed.x * 20.0;
    vec3 drift = vec3(sin(swirl), 0.0, cos(swirl * 0.8)) * 0.3 * life + vec3(0.25, 0.0, 0.1) * life * life;
    vec4 mv = modelViewMatrix * vec4(position + drift + vec3(0.0, life * rise * (0.6 + 0.6 * seed.z), 0.0), 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = clamp(pixelsPerMetre * 0.022 * (1.0 - life * 0.5) / -mv.z, 1.0, 9.0);
    vGlow = pow(1.0 - life, 1.5) * (0.55 + 0.45 * sin(time * 14.0 + seed.z * 40.0));
  }`;

const sparkFragment = /* glsl */ `
  varying float vGlow;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    gl_FragColor = vec4(vec3(1.0, 0.6, 0.2) * exp(-d * d * 5.0) * vGlow * 2.0, 1.0);
  }`;

const smokeVertex = /* glsl */ `
  attribute vec3 seed;
  uniform float time;
  uniform float rise;
  uniform float pixelsPerMetre;
  varying float vLife;
  varying float vSeed;
  void main() {
    float life = fract(time * 0.07 + seed.x);
    vec3 drift = vec3(sin(time * 0.3 + seed.y * 6.0) * 0.25 + 0.4 * life, 0.0, cos(time * 0.25 + seed.z * 6.0) * 0.2) * life;
    vec4 mv = modelViewMatrix * vec4(position + drift + vec3(0.0, 0.7 + life * rise, 0.0), 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = clamp(pixelsPerMetre * (0.35 + life * 0.9) / -mv.z, 2.0, 220.0);
    vLife = life; vSeed = seed.z;
  }`;

const smokeFragment = /* glsl */ `
  uniform float time;
  varying float vLife;
  varying float vSeed;
  ${NOISE}
  void main() {
    vec2 p = gl_PointCoord - 0.5;
    float wisp = fbm(p * 3.0 + vec2(vSeed * 10.0, time * 0.15)) * (1.0 - smoothstep(0.15, 0.5, length(p)));
    float alpha = wisp * smoothstep(0.0, 0.15, vLife) * (1.0 - smoothstep(0.5, 1.0, vLife)) * 0.22;
    gl_FragColor = vec4(vec3(0.16, 0.15, 0.17), alpha);
  }`;

function points(count: number, spread: number, y: number): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(
    Array.from({ length: count * 3 }, (_, k) => (k % 3 === 1 ? y : (Math.random() - 0.5) * spread)), 3));
  geometry.setAttribute("seed", new THREE.Float32BufferAttribute(Array.from({ length: count * 3 }, Math.random), 3));
  return geometry;
}

export function createSparks(time: THREE.IUniform, pixelsPerMetre: THREE.IUniform, count: number, rise: number): THREE.Points {
  const sparks = new THREE.Points(points(count, 0.35, 0.25), new THREE.ShaderMaterial({
    vertexShader: sparkVertex, fragmentShader: sparkFragment, uniforms: { time, rise: { value: rise }, pixelsPerMetre },
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  }));
  sparks.frustumCulled = false;
  return sparks;
}

export function createSmoke(time: THREE.IUniform, pixelsPerMetre: THREE.IUniform, count: number, rise: number): THREE.Points {
  const smoke = new THREE.Points(points(count, 0.2, 0), new THREE.ShaderMaterial({
    vertexShader: smokeVertex, fragmentShader: smokeFragment, uniforms: { time, rise: { value: rise }, pixelsPerMetre },
    transparent: true, depthWrite: false, toneMapped: false,
  }));
  smoke.frustumCulled = false;
  smoke.renderOrder = 1;                                             // after the flames, so it drifts over them
  return smoke;
}
