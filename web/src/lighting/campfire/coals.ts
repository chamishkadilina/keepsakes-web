import * as THREE from "three";
import { NOISE } from "./flames";

/**
 * The fire's bed of coals (charcoal with glowing cracks that slowly pulse), and its logs and kindling burnt black
 * where the fire licks them, with embers glowing in the char: their baked materials, patched near the fire.
 */
const coalFragment = /* glsl */ `
  uniform float time;
  varying vec2 vUv;
  ${NOISE}
  void main() {
    vec2 p = (vUv - 0.5) * 2.0;
    float r = length(p);
    float cracks = 1.0 - smoothstep(0.0, 0.08, abs(fbm(p * 4.0 + 7.0) - 0.5));          // the lines between the coals
    float pulse = 0.6 + 0.4 * fbm(p * 3.0 + vec2(time * 0.35, -time * 0.25));
    float glow = cracks * pulse * (1.0 - smoothstep(0.2, 0.95, r)) + 0.35 * (1.0 - smoothstep(0.0, 0.6, r)) * pulse;
    vec3 colour = mix(vec3(0.035, 0.028, 0.025), vec3(1.0, 0.3, 0.04), clamp(glow, 0.0, 1.0));
    colour += vec3(1.0, 0.7, 0.3) * pow(clamp(glow, 0.0, 1.0), 3.0) * 0.6;
    gl_FragColor = vec4(colour, 1.0 - smoothstep(0.8, 1.0, r));
  }`;

const COAL_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

export function createCoals(time: THREE.IUniform, radius: number): THREE.Mesh {
  const material = new THREE.ShaderMaterial({ vertexShader: COAL_VERTEX, fragmentShader: coalFragment, uniforms: { time },
    transparent: true, toneMapped: false });
  return new THREE.Mesh(new THREE.CircleGeometry(radius, 32).rotateX(-Math.PI / 2), material);
}

/** The logs (and kindling) are charred where they are low and close to the fire, embers flickering in the char. */
export function glowLogs(root: THREE.Object3D, names: readonly string[], fire: THREE.Vector3, time: THREE.IUniform): void {
  for (const name of names) {
    const mesh = root.getObjectByName(name) as THREE.Mesh | undefined;
    if (!mesh) continue;
    const material = mesh.material as THREE.MeshBasicMaterial;
    const key = material.customProgramCacheKey();
    const before = material.onBeforeCompile.bind(material);
    material.onBeforeCompile = (shader, renderer) => {
      before(shader, renderer);
      shader.uniforms.time = time;
      shader.uniforms.fireCentre = { value: fire };
      shader.vertexShader = shader.vertexShader
        .replace("#include <common>", "#include <common>\nvarying vec3 vLogSpot;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvLogSpot = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>
          uniform float time; uniform vec3 fireCentre; varying vec3 vLogSpot;
          ${NOISE}`)
        .replace("#include <opaque_fragment>", `{
            vec3 d = vLogSpot - fireCentre;
            float near = (1.0 - smoothstep(0.0, 0.42, length(d.xz))) * (1.0 - smoothstep(0.0, 0.6, d.y));
            float ember = fbm(vLogSpot.xz * 14.0 + vLogSpot.y * 9.0 + vec2(time * 0.6, -time * 0.4));
            outgoingLight *= 1.0 - 0.8 * smoothstep(0.0, 0.6, near);                                   // charred
            outgoingLight += vec3(1.0, 0.3, 0.04) * near * smoothstep(0.42, 0.75, ember) * 2.2;
          }
          #include <opaque_fragment>`);
    };
    material.customProgramCacheKey = () => `${key}|logGlow`;
    material.needsUpdate = true;
  }
}
