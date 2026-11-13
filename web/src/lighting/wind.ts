import * as THREE from "three";
import { LIGHTING } from "../config/lighting";

/**
 * A soft night breeze through the garden: every tree, bush and flower sways a little in its own rhythm, slower and wider
 * the taller it is, stiff at its foot, in gentle gusts; leaves tremble faintly. Each plant's rhythm and height come
 * with the model, in the garden plants' second UV set (TEXCOORD_1, loaded as `uv1` = phase 0..1, height in m;
 * tools/bake/garden.py), renamed `windData` here so no texture ever reads it as UVs. Only the vertex shader
 * moves them: their baked light stays. The big jacaranda's little lights sway with it (curtainLights.ts, `wind`).
 *
 *   const wind = addWind(gltf.scene);   // after applyBakedLighting
 *   wind.update();                      // every frame
 */
const W = LIGHTING.wind;
const f = (n: number) => n.toFixed(4);
const angle = (W.direction * Math.PI) / 180;

/** GLSL: `windOffset(p, phase, height, flutter)`: how far a point of a plant at world position p (m, y up) is blown now. */
export const WIND_GLSL = /* glsl */ `
  uniform float windTime;
  vec3 windOffset(vec3 p, float phase, float height, float flutter) {
    if (height <= 0.0) return vec3(0.0);
    float rise = clamp(p.y / height, 0.0, 1.0);
    float t = windTime * ${f(W.speed)} * pow(height, -0.35) + phase * 6.2832;     // taller: slower
    float gust = 0.6 + 0.4 * sin(windTime * 0.11 + phase * 3.0) * sin(windTime * 0.047 + 1.3);
    float sway = (sin(t) + 0.35 * sin(t * 2.17 + 1.0)) * gust;
    float turn = ${f(angle)} + (phase - 0.5) * 0.8;                                  // each leans a little its own way
    float bend = ${f(W.amplitude)} * sqrt(height) * pow(rise, ${f(W.stiffness)}) * sway;
    vec3 tremble = flutter * gust * rise * vec3(sin(windTime * 5.3 + dot(p, vec3(3.1, 2.3, 2.7))),
      0.5 * sin(windTime * 6.1 + dot(p, vec3(2.2, 3.7, 1.9))), sin(windTime * 4.7 + dot(p, vec3(1.7, 2.9, 3.3))));
    return vec3(cos(turn), 0.0, sin(turn)) * bend + tremble;
  }`;

/** The GLSL call for the big jacaranda (phase 0), at world position `p`: its little lights hang in it. */
export const TREE_WIND = (p: string) => `windOffset(${p}, 0.0, ${f(W.treeHeight)}, 0.0)`;

function blow(mesh: THREE.Mesh, time: THREE.IUniform): void {
  const material = mesh.material as THREE.MeshBasicMaterial;
  const flutter = W.still.some((part) => mesh.name.includes(part)) ? 0 : W.flutter;
  const key = material.customProgramCacheKey();
  const before = material.onBeforeCompile.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    before(shader, renderer);
    shader.uniforms.windTime = time;
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", `#include <common>\nattribute vec2 windData;\n${WIND_GLSL}`)
      .replace("#include <begin_vertex>", `#include <begin_vertex>
        { vec3 windAt = (modelMatrix * vec4(transformed, 1.0)).xyz;
          transformed += (vec4(windOffset(windAt, windData.x, windData.y, ${f(flutter)}), 0.0) * modelMatrix).xyz; }`);
  };
  material.customProgramCacheKey = () => `${key}|wind-${flutter}`;
  material.needsUpdate = true;
}

/** Sets every garden plant (a garden mesh with a second UV set) swaying; `update` moves the breeze on every frame. */
export function addWind(root: THREE.Object3D): { update: () => void } {
  const time = { value: 0 };
  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    const data = mesh.isMesh && mesh.name.startsWith("prop_garden_") ? mesh.geometry.getAttribute("uv1") : undefined;
    if (!data) return;
    mesh.geometry.setAttribute("windData", data);
    mesh.geometry.deleteAttribute("uv1");
    blow(mesh, time);
  });
  return { update: () => { time.value = performance.now() / 1000; } };
}
