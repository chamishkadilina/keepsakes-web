import * as THREE from "three";

/**
 * The sky over the garden: a romantic dusk, warm peach low down (the colour of the baked sky light), rose and mauve
 * above, deepening to indigo overhead, with the first faint stars. It only shows in the garden and through its door.
 * A dome that travels with the camera (keep the camera's far plane above 100 m). 1 draw call.
 *
 *   scene.add(createDuskSky());
 */
const vertexShader = /* glsl */ `
  varying vec3 vDirection;
  void main() {
    vDirection = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;

const fragmentShader = /* glsl */ `
  varying vec3 vDirection;
  float hash(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
  void main() {
    vec3 d = normalize(vDirection);
    float h = max(d.y, 0.0);
    vec3 horizon = vec3(0.93, 0.55, 0.42), rose = vec3(0.52, 0.27, 0.36), dusk = vec3(0.16, 0.12, 0.27), night = vec3(0.035, 0.035, 0.09);
    vec3 c = mix(horizon, rose, smoothstep(0.0, 0.18, h));
    c = mix(c, dusk, smoothstep(0.12, 0.5, h));
    c = mix(c, night, smoothstep(0.45, 1.0, h));
    vec3 cell = floor(d * 160.0);                                   // a few faint stars, more of them higher up
    vec3 spot = (cell + 0.25 + 0.5 * vec3(hash(cell), hash(cell + 3.1), hash(cell + 7.3))) / 160.0;
    float star = step(0.993, hash(cell + 11.0)) * smoothstep(0.004, 0.0, length(d - spot)) * smoothstep(0.3, 0.7, h);
    c += star * vec3(1.0, 0.94, 0.84) * (0.4 + 0.6 * hash(cell + 5.0));
    gl_FragColor = vec4(c, 1.0);
    #include <colorspace_fragment>
  }`;

export function createDuskSky(): THREE.Mesh {
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(90, 48, 24),
    new THREE.ShaderMaterial({ vertexShader, fragmentShader, side: THREE.BackSide, depthWrite: false }),
  );
  sky.name = "dusk_sky";
  sky.frustumCulled = false;
  sky.renderOrder = -1;
  sky.onBeforeRender = (_renderer, _scene, camera) => {             // centred on whoever looks (also the reflection)
    sky.position.setFromMatrixPosition(camera.matrixWorld);
    sky.updateMatrixWorld();
  };
  return sky;
}
