import * as THREE from "three";
import { findProps } from "./findProps";

/**
 * The heart foil balloons float: each one bobs gently, drifts a little and slowly turns to and fro about its own middle
 * on its own rhythm, so its foil catches the light; its ribbon follows (where a ribbon is tied to a side table, a seat or a
 * weight, it moves less towards the knot). Balloons at the ceiling only bob down from it. The model stores each
 * balloon's rhythm in its second UV set (props.py "bob" = phase, weight) and its middle in its third ("pivot" = x, z).
 * Runs on the GPU: nothing to update per frame, no extra draw call.
 *
 *   animateBalloons(gltf.scene);      // after applyBakedLighting
 */
export function animateBalloons(root: THREE.Object3D): void {
  const time = { value: 0 };
  const tick = () => { time.value = performance.now() / 1000; };
  for (const mesh of findProps(root, "balloon_foil")) {
    const bob = mesh.geometry.getAttribute("uv1"), pivot = mesh.geometry.getAttribute("uv2");
    if (!bob || !pivot) continue;
    mesh.geometry.setAttribute("bob", bob);
    mesh.geometry.setAttribute("pivot", pivot);
    const material = mesh.material as THREE.Material;
    if (!material.userData.floats) {
      material.userData.floats = true;
      const look = material.onBeforeCompile.bind(material), lookKey = material.customProgramCacheKey.bind(material);
      material.onBeforeCompile = (shader, renderer) => {
        look(shader, renderer);                                     // the foil's own shading (bakedLighting.ts)
        shader.uniforms.bobTime = time;
        shader.vertexShader = shader.vertexShader
          .replace("#include <common>", "#include <common>\nattribute vec2 bob;\nattribute vec2 pivot;\nuniform float bobTime;")
          .replace("#include <beginnormal_vertex>", `#include <beginnormal_vertex>
            float bt = bobTime + bob.x * 4.0;
            float yaw = bob.y * 0.26 * sin(bt * 0.55 + bob.x);                 // turns to and fro, about every 11 s
            float cy = cos(yaw), sy = sin(yaw);
            objectNormal.xz = vec2(cy * objectNormal.x + sy * objectNormal.z, cy * objectNormal.z - sy * objectNormal.x);`)
          .replace("#include <begin_vertex>", `#include <begin_vertex>
            vec2 arm = transformed.xz - pivot;
            transformed.xz = pivot + vec2(cy * arm.x + sy * arm.y, cy * arm.y - sy * arm.x);
            transformed += bob.y * vec3(0.03 * sin(bt * 0.53 + bob.x), -0.025 * (1.0 - sin(bt * 1.55)), 0.03 * cos(bt * 0.47 + bob.x * 1.7));`);
      };
      material.customProgramCacheKey = () => `${lookKey()}|floatingBalloons`;
      material.needsUpdate = true;
    }
    mesh.onBeforeRender = tick;
  }
}
