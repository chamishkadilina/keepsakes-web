import * as THREE from "three";
import { LIGHTING } from "../config/lighting";

/**
 * Fireflies over the garden at night: small soft yellow-green lights, each wandering slowly round its own spot and
 * dark most of the time and glowing up for a moment, now and then, each in its own rhythm. Not a light: nothing around them is lit. One draw call, animated on the
 * GPU (nothing to update per frame).
 *
 *   scene.add(createFireflies());
 */
const { count, area, height, drift, colour, blinkEvery } = LIGHTING.fireflies;
const SIZE = 0.07;                     // each firefly's glow across (metres)

const vertexShader = /* glsl */ `
  attribute vec3 seed;
  uniform float time;
  uniform float drift;
  uniform float pixelsPerMetre;
  varying float vGlow;
  void main() {
    float t = time * (0.12 + 0.1 * seed.x);
    vec3 wander = drift * vec3(sin(t + seed.y * 6.3), 0.4 * sin(t * 1.7 + seed.z * 6.3), cos(t * 0.8 + seed.x * 6.3));
    vec4 mv = modelViewMatrix * vec4(position + wander, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = clamp(pixelsPerMetre * ${SIZE.toFixed(3)} / -mv.z, 1.5, 32.0);
    float every = mix(${blinkEvery[0].toFixed(1)}, ${blinkEvery[1].toFixed(1)}, seed.y);           // seconds between its flashes
    float beat = 0.5 + 0.5 * sin(time * 6.2832 / every + seed.z * 40.0);
    vGlow = pow(beat, 400.0);                                       // dark, then a soft flash of about a second
  }`;

const fragmentShader = /* glsl */ `
  uniform vec3 color;
  varying float vGlow;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float light = exp(-d * d * 60.0) + 0.35 * exp(-d * d * 8.0);
    gl_FragColor = vec4(color * light * vGlow, 1.0);
  }`;

export function createFireflies(): THREE.Points {
  const positions: number[] = [], seeds: number[] = [];
  for (let i = 0; i < count; i++) {
    positions.push(THREE.MathUtils.lerp(area[0], area[2], Math.random()), THREE.MathUtils.lerp(height[0], height[1], Math.random()),
      THREE.MathUtils.lerp(area[1], area[3], Math.random()));
    seeds.push(Math.random(), Math.random(), Math.random());
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("seed", new THREE.Float32BufferAttribute(seeds, 3));
  const uniforms = { color: { value: new THREE.Color(colour) }, time: { value: 0 }, drift: { value: drift }, pixelsPerMetre: { value: 800 } };
  const fireflies = new THREE.Points(geometry, new THREE.ShaderMaterial({
    vertexShader, fragmentShader, uniforms, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  }));
  fireflies.name = "fireflies";
  fireflies.frustumCulled = false;
  const size = new THREE.Vector2();
  fireflies.onBeforeRender = (renderer, _scene, camera) => {
    uniforms.time.value = performance.now() / 1000;
    uniforms.pixelsPerMetre.value = renderer.getDrawingBufferSize(size).y * camera.projectionMatrix.elements[5] / 2;
  };
  return fireflies;
}
