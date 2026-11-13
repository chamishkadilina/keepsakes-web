import * as THREE from "three";
import { findProps } from "./findProps";

/**
 * The heart foil balloons float: each one bobs gently, drifts a little and slowly turns to and fro about its own middle
 * on its own rhythm, so its foil catches the light; its ribbon follows (where a ribbon is tied to a side table, a seat or a
 * weight, it moves less towards the knot). Balloons at the ceiling only bob down from it. The model stores each
 * balloon's rhythm in its second UV set (props.py "bob" = phase, weight) and its middle in its third ("pivot" = x, z).
 * The visitor pushes them too: a balloon within REACH of her sways away and springs back, its ribbon still tied at the
 * weight. Floating runs on the GPU; update() only moves one small spring per balloon. No extra draw call.
 *
 *   const balloons = animateBalloons(gltf.scene);      // after applyBakedLighting
 *   useFrame(({ camera }, delta) => balloons.update(camera.position, delta));
 */
export interface FloatingBalloons {
  update(visitor: THREE.Vector3, dt: number): void;
}

const REACH = 0.8;                   // she pushes balloons within this distance (metres)
const PUSH = 12;                     // how hard, right beside her; fades to nothing at REACH (m/s²)
const SPRING = 10;                   // pulls a balloon back to its place (per s²)
const DAMPING = 3.5;                 // settles it after one small sway (per s)
const MAX_STEP = 0.05;               // longest step of the springs (seconds), so a slow frame never throws them

export function animateBalloons(root: THREE.Object3D): FloatingBalloons {
  const time = { value: 0 };
  const push = { value: new Float32Array(0) };                      // each balloon's offset: x, z
  const balloons = new Map<string, number>();                       // a balloon's pivot -> its index
  const pivots: number[] = [];                                      // x, z of each balloon (the meshes sit at the origin)
  for (const mesh of findProps(root, "balloon_foil")) {
    const bob = mesh.geometry.getAttribute("uv1"), pivot = mesh.geometry.getAttribute("uv2");
    if (!bob || !pivot) continue;
    mesh.geometry.setAttribute("bob", bob);
    mesh.geometry.setAttribute("pivot", pivot);
    const index = new Float32Array(pivot.count);
    for (let i = 0; i < pivot.count; i++) {
      const x = pivot.getX(i), z = pivot.getY(i), key = `${x.toFixed(3)},${z.toFixed(3)}`;
      if (!balloons.has(key)) { balloons.set(key, balloons.size); pivots.push(x, z); }
      index[i] = balloons.get(key)!;
    }
    mesh.geometry.setAttribute("balloon", new THREE.BufferAttribute(index, 1));
    const material = mesh.material as THREE.Material;
    if (!material.userData.floats) {
      material.userData.floats = true;
      const look = material.onBeforeCompile.bind(material), lookKey = material.customProgramCacheKey.bind(material);
      material.onBeforeCompile = (shader, renderer) => {
        look(shader, renderer);                                     // the foil's own shading (bakedLighting.ts)
        shader.uniforms.bobTime = time;
        shader.uniforms.balloonPush = push;
        shader.vertexShader = shader.vertexShader
          .replace("#include <common>", `#include <common>
            attribute vec2 bob;
            attribute vec2 pivot;
            attribute float balloon;
            uniform float bobTime;
            uniform vec2 balloonPush[${balloons.size}];`)
          .replace("#include <beginnormal_vertex>", `#include <beginnormal_vertex>
            float bt = bobTime + bob.x * 4.0;
            float yaw = bob.y * 0.26 * sin(bt * 0.55 + bob.x);                 // turns to and fro, about every 11 s
            float cy = cos(yaw), sy = sin(yaw);
            objectNormal.xz = vec2(cy * objectNormal.x + sy * objectNormal.z, cy * objectNormal.z - sy * objectNormal.x);`)
          .replace("#include <begin_vertex>", `#include <begin_vertex>
            vec2 arm = transformed.xz - pivot;
            transformed.xz = pivot + vec2(cy * arm.x + sy * arm.y, cy * arm.y - sy * arm.x);
            transformed += bob.y * vec3(0.03 * sin(bt * 0.53 + bob.x), -0.025 * (1.0 - sin(bt * 1.55)), 0.03 * cos(bt * 0.47 + bob.x * 1.7));
            transformed.xz += bob.y * balloonPush[int(balloon + 0.5)];`);
      };
      material.customProgramCacheKey = () => `${lookKey()}|floatingBalloons`;
      material.needsUpdate = true;
    }
  }

  const offset = (push.value = new Float32Array(pivots.length));
  const speed = new Float32Array(pivots.length);
  return {
    update(visitor, dt) {
      time.value = performance.now() / 1000;
      const step = Math.min(dt, MAX_STEP);
      for (let i = 0; i < pivots.length; i += 2) {
        let ax = -SPRING * offset[i] - DAMPING * speed[i], az = -SPRING * offset[i + 1] - DAMPING * speed[i + 1];
        const dx = pivots[i] + offset[i] - visitor.x, dz = pivots[i + 1] + offset[i + 1] - visitor.z;
        const dist = Math.hypot(dx, dz);
        if (dist < REACH && dist > 1e-4) {
          const force = (PUSH * (1 - dist / REACH)) / dist;
          ax += dx * force;
          az += dz * force;
        }
        speed[i] += ax * step;
        speed[i + 1] += az * step;
        offset[i] += speed[i] * step;
        offset[i + 1] += speed[i + 1] * step;
      }
    },
  };
}
