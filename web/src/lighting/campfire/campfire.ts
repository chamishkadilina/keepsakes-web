import * as THREE from "three";
import { LIGHTING } from "../../config/lighting";
import { glowLogs, createCoals } from "./coals";
import { createSmoke, createSparks } from "./embers";
import { additive, BILLBOARD_VERTEX, createFlames, createHalo } from "./flames";

/**
 * The fire in the garden's ring of stones (the model's `campfire` marker): a bed of glowing coals, tongues of flame
 * licking up through the logs with a heat halo, the logs charred and glowing where the fire licks them, sparks and soft
 * smoke rising, and a warm glow on the grass that breathes with the flames. Not a light: the fire's warm light on the garden is baked (garden_layout.py FIRE_LIGHT); the
 * glow only adds its flicker. Animated on the GPU. Call before createCinemaLights (both patch the logs' material).
 *
 *   const fire = createCampfire(gltf.scene);  if (fire) scene.add(fire);
 */
const C = LIGHTING.campfire;

const groundFragment = /* glsl */ `
  uniform float time;
  uniform float strength;
  varying vec2 vUv;
  void main() {
    float r = length(vUv - 0.5) * 2.0;
    float flicker = 0.8 + 0.1 * sin(time * 7.3) + 0.06 * sin(time * 13.1 + 1.7) + 0.04 * sin(time * 23.0);
    gl_FragColor = vec4(vec3(1.0, 0.45, 0.15) * exp(-r * r * 5.0) * strength * flicker, 1.0);
  }`;

export function createCampfire(root: THREE.Object3D): THREE.Group | null {
  const marker = root.getObjectByName("campfire");
  if (!marker) return null;
  const fire = new THREE.Group();
  fire.name = "campfire";
  root.updateMatrixWorld(true);
  marker.getWorldPosition(fire.position);

  const time = { value: 0 }, pixelsPerMetre = { value: 800 };
  glowLogs(root, C.logs, fire.position, time);

  const coals = createCoals(time, C.coalRadius);
  coals.position.y = 0.06 - fire.position.y;                       // in the pit, under the logs
  coals.frustumCulled = false;                                     // it runs the fire's clock: always drawn
  const flames = createFlames(time, C.tongues, C.flameHeight, C.flameWidth, C.flameBase);
  const halo = createHalo(time, C.flameHeight);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(C.glowRadius * 2, C.glowRadius * 2).rotateX(-Math.PI / 2),
    additive(BILLBOARD_VERTEX, groundFragment, { time, strength: { value: C.glowStrength } }));
  ground.position.y = 0.02 - fire.position.y;                      // on the grass
  fire.add(coals, ground, flames, halo, createSparks(time, pixelsPerMetre, C.sparks, C.sparkRise),
    createSmoke(time, pixelsPerMetre, C.smoke, C.smokeRise));

  const size = new THREE.Vector2();
  coals.onBeforeRender = (renderer, _scene, camera) => {           // once a frame: the time, and the halo turns to you
    time.value = performance.now() / 1000;
    pixelsPerMetre.value = renderer.getDrawingBufferSize(size).y * camera.projectionMatrix.elements[5] / 2;
    halo.rotation.y = Math.atan2(camera.position.x - fire.position.x, camera.position.z - fire.position.z);
  };
  return fire;
}
