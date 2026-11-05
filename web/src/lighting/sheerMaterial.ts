import * as THREE from "three";

/**
 * Ivory voile for the foyer's sheer curtains: see-through where it faces you, denser where its folds turn away (as the
 * fabric layers up there), so the folds read softly without dark stripes, and the little lights and the warm wall
 * behind glow through it. Unlit (the foyer's light is in its colour); both sides drawn. Used by applyBakedLighting.
 */
const vertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vNormal = normalMatrix * normal;
    vView = -mv.xyz;
    gl_Position = projectionMatrix * mv;
  }`;

const fragmentShader = /* glsl */ `
  uniform vec3 color;
  uniform float opacity;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    float facing = abs(dot(normalize(vNormal), normalize(vView)));
    gl_FragColor = vec4(color * (0.9 + 0.1 * facing), min(opacity * (1.9 - 0.9 * facing), 0.9));
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`;

export function createSheerMaterial(colour: THREE.ColorRepresentation = 0xf2e7d8, opacity = 0.34): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader, fragmentShader, uniforms: { color: { value: new THREE.Color(colour) }, opacity: { value: opacity } },
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
  });
}
