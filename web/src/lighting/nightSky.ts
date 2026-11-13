import * as THREE from "three";
import { LIGHTING } from "../config/lighting";

/**
 * The night over the garden: deep blue-black overhead, a soft violet glow low down, a faint Milky Way, softly twinkling
 * stars, a glowing moon, and now and then a shooting star at a random time, across the sky ahead of the bench. Only shows in the garden and
 * through its door. A dome that travels with the camera (keep the camera's far plane above 100 m). 1 draw call.
 * Not a light: the garden's light is baked.
 *
 *   const sky = new NightSky();  scene.add(sky);
 *   useFrame((_, delta) => sky.update(delta));
 */
const vertexShader = /* glsl */ `
  varying vec3 vDirection;
  void main() {
    vDirection = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;

const fragmentShader = /* glsl */ `
  uniform float uTime;
  uniform vec3 uMoon;
  uniform vec3 uMeteorFrom, uMeteorTo;
  uniform float uMeteor;                                            // the shooting star's progress 0..1, < 0: none
  varying vec3 vDirection;

  float hash(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
  float noise(vec3 p) {
    vec3 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash(i), hash(i + vec3(1, 0, 0)), u.x), mix(hash(i + vec3(0, 1, 0)), hash(i + vec3(1, 1, 0)), u.x), u.y),
               mix(mix(hash(i + vec3(0, 0, 1)), hash(i + vec3(1, 0, 1)), u.x), mix(hash(i + vec3(0, 1, 1)), hash(i + vec3(1, 1, 1)), u.x), u.y), u.z);
  }
  // One layer of stars: at most one per cell of the direction grid, each twinkling in its own rhythm.
  float stars(vec3 d, float cells, float chance, float size) {
    vec3 cell = floor(d * cells);
    vec3 spot = (cell + 0.25 + 0.5 * vec3(hash(cell), hash(cell + 3.1), hash(cell + 7.3))) / cells;
    float twinkle = 0.75 + 0.25 * sin(uTime * (0.6 + 1.8 * hash(cell + 9.0)) + 6.283 * hash(cell + 5.0));
    return step(chance, hash(cell + 11.0)) * (1.0 - smoothstep(0.0, size, length(d - spot))) * (0.35 + 0.65 * hash(cell + 2.0)) * twinkle;
  }

  void main() {
    vec3 d = normalize(vDirection);
    float h = max(d.y, 0.0);
    vec3 c = mix(vec3(0.075, 0.06, 0.15), vec3(0.025, 0.03, 0.085), smoothstep(0.0, 0.3, h));   // violet low, deep blue
    c = mix(c, vec3(0.006, 0.008, 0.028), smoothstep(0.25, 0.95, h));                          // to blue-black overhead
    c += vec3(0.05, 0.022, 0.04) * exp(-h * 12.0);                                             // a last rose glow at the horizon

    vec3 band = normalize(vec3(0.35, 0.25, 0.9));                                              // the Milky Way, faint
    float milky = exp(-pow(dot(d, band) / 0.2, 2.0)) * (0.55 * noise(d * 7.0) + 0.45 * noise(d * 17.0));
    c += vec3(0.05, 0.05, 0.075) * milky * smoothstep(0.05, 0.35, h);

    float sky = smoothstep(0.02, 0.15, h);                                                    // no stars in the haze
    c += vec3(0.85, 0.88, 1.0) * stars(d, 240.0, 0.975, 0.0022) * 0.8 * sky;
    c += vec3(1.0, 0.95, 0.85) * stars(d, 90.0, 0.99, 0.0035) * 1.3 * (1.0 + 0.6 * milky) * sky;

    float moon = dot(d, uMoon);                                                               // a big, soft, glowing moon
    float disc = smoothstep(0.99955, 0.99965, moon);
    c += vec3(0.25, 0.27, 0.38) * exp(-(1.0 - moon) * 45.0) + vec3(0.12, 0.12, 0.16) * exp(-(1.0 - moon) * 400.0);
    c = mix(c, vec3(1.0, 0.96, 0.86) * (0.85 + 0.15 * noise(d * 400.0)), disc);

    if (uMeteor >= 0.0) {                                                                     // a shooting star
      vec3 head = normalize(mix(uMeteorFrom, uMeteorTo, uMeteor));
      vec3 tail = normalize(mix(uMeteorFrom, uMeteorTo, max(uMeteor - 0.45, 0.0)));
      vec3 ab = head - tail;
      float t = clamp(dot(d - tail, ab) / max(dot(ab, ab), 1e-8), 0.0, 1.0);
      float dist = length(d - (tail + ab * t));
      float fade = smoothstep(0.0, 0.12, uMeteor) * (1.0 - smoothstep(0.65, 1.0, uMeteor));
      float core = (1.0 - smoothstep(0.0, 0.0024, dist)) * t * t;                         // a bright line, brightest at its head
      float glow = (1.0 - smoothstep(0.0, 0.009, dist)) * t * t * 0.35;                  // in a soft haze
      float spark = (1.0 - smoothstep(0.0, 0.007, length(d - head))) * 0.9;
      c += vec3(1.0, 0.95, 0.88) * (core + glow + spark) * fade * 2.0;
    }

    gl_FragColor = vec4(c, 1.0);
    #include <colorspace_fragment>
  }`;

const { meteorGap, meteorTime, meteorAzimuth, meteorElevation, meteorFall, meteorDrift, moon } = LIGHTING.nightSky;
const DEG = Math.PI / 180;
const random = (range: readonly [number, number]) => range[0] + Math.random() * (range[1] - range[0]);
const direction = (azimuth: number, elevation: number, out = new THREE.Vector3()) =>  // azimuth from north (−z) towards east (+x)
  out.set(Math.sin(azimuth) * Math.cos(elevation), Math.sin(elevation), -Math.cos(azimuth) * Math.cos(elevation));

export class NightSky extends THREE.Mesh<THREE.SphereGeometry, THREE.ShaderMaterial> {
  private readonly uniforms = {
    uTime: { value: 0 },
    uMoon: { value: direction(moon.azimuth * DEG, moon.elevation * DEG) },
    uMeteorFrom: { value: new THREE.Vector3() },
    uMeteorTo: { value: new THREE.Vector3() },
    uMeteor: { value: -1 },
  };
  private wait = random(meteorGap) / 2;                           // the first one comes a little sooner
  private duration = 1;

  constructor() {
    super(new THREE.SphereGeometry(90, 48, 24));
    this.material = new THREE.ShaderMaterial({ uniforms: this.uniforms, vertexShader, fragmentShader, side: THREE.BackSide, depthWrite: false });
    this.name = "night_sky";
    this.frustumCulled = false;
    this.renderOrder = -1;
    this.onBeforeRender = (_renderer, _scene, camera) => {       // centred on whoever looks (also the reflection)
      this.position.setFromMatrixPosition(camera.matrixWorld);
      this.updateMatrixWorld();
    };
  }

  update(dt: number): void {
    const u = this.uniforms;
    u.uTime.value += dt;
    if (u.uMeteor.value >= 0) {
      u.uMeteor.value += dt / this.duration;
      if (u.uMeteor.value > 1) u.uMeteor.value = -1;
      return;
    }
    this.wait -= dt;
    if (this.wait > 0) return;
    const azimuth = random(meteorAzimuth) * DEG, elevation = random(meteorElevation) * DEG;
    const drift = random(meteorDrift) * DEG * (Math.random() < 0.5 ? -1 : 1);
    direction(azimuth, elevation, u.uMeteorFrom.value);
    direction(azimuth + drift, elevation - random(meteorFall) * DEG, u.uMeteorTo.value);
    this.duration = random(meteorTime);
    this.wait = random(meteorGap);
    u.uMeteor.value = 0;
  }
}
