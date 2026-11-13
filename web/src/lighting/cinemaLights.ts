import * as THREE from "three";
import { LIGHTING } from "../config/lighting";

/**
 * Dims the screen room while a video plays, like a real cinema. Not a light: the baked materials (MeshBasic and matcap)
 * multiply their colour by a shared dim value inside the room's box, so it costs almost nothing. The box's edge runs
 * inside the walls, so the rooms next door stay as they are; it only shows in the doorways, as a soft line on the floor.
 * Left bright: everything drawn by a ShaderMaterial (the beam, flames, sheers), the poster, the glowing lenses and the
 * video plane (userData.cinemaScreen). The couple's photos are never touched: call this before the Gallery mounts, on
 * the model and the decor only.
 *
 *   const cinema = createCinemaLights(gltf.scene, ...petals);   // after createFloorReflection, which replaces the floors' patch
 *   useFrame((_, delta) => cinema.update(delta));
 *   cinema.dim(true);                                           // a video starts; dim(false) when it ends or is paused
 */
export interface CinemaLights {
  dim(on: boolean): void;
  update(dt: number): void;
}

type Bakeable = THREE.MeshBasicMaterial | THREE.MeshMatcapMaterial;
type Uniforms = Record<string, THREE.IUniform>;

const { box, dimmed, fade, edge } = LIGHTING.cinema;

function isBaked(material: THREE.Material): material is Bakeable {
  const { isMeshBasicMaterial, isMeshMatcapMaterial } = material as THREE.MeshBasicMaterial & THREE.MeshMatcapMaterial;
  return (isMeshBasicMaterial || isMeshMatcapMaterial) && material.name !== "lens_glow";
}

/** Adds the dimming on top of whatever the material's shader already does (floor reflection, floating balloons). */
function patch(material: Bakeable, uniforms: Uniforms): void {
  const key = material.customProgramCacheKey();
  const look = material.onBeforeCompile.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    look(shader, renderer);
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec2 vCinemaSpot;")
      .replace("#include <project_vertex>", `#include <project_vertex>
        vec4 cinemaSpot = vec4(transformed, 1.0);
        #ifdef USE_INSTANCING
          cinemaSpot = instanceMatrix * cinemaSpot;
        #endif
        vCinemaSpot = (modelMatrix * cinemaSpot).xz;`);
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>
        uniform float cinemaDim; uniform vec4 cinemaBox; uniform float cinemaEdge;
        varying vec2 vCinemaSpot;`)
      .replace("#include <opaque_fragment>", `{
          vec2 inside = min(vCinemaSpot - cinemaBox.xy, cinemaBox.zw - vCinemaSpot);
          outgoingLight *= mix(1.0, cinemaDim, smoothstep(-cinemaEdge, cinemaEdge, min(inside.x, inside.y)));
        }
        #include <opaque_fragment>`);
  };
  material.customProgramCacheKey = () => `${key}|cinemaLights`;
  material.needsUpdate = true;
}

export function createCinemaLights(...roots: THREE.Object3D[]): CinemaLights {
  const cinemaDim = { value: 1 };
  const uniforms = { cinemaDim, cinemaBox: { value: new THREE.Vector4(...box) }, cinemaEdge: { value: edge } };
  const patched = new Set<THREE.Material>();
  for (const root of roots) {
    root.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh || mesh.userData.cinemaScreen || mesh.userData.prop === "poster_face") return;
      for (const material of [mesh.material].flat()) {
        if (patched.has(material) || !isBaked(material)) continue;
        patched.add(material);
        patch(material, uniforms);
      }
    });
  }

  let amount = 0, goal = 0;                                      // 0 = the room as baked, 1 = fully dimmed
  return {
    dim(on) { goal = on ? 1 : 0; },
    update(dt) {
      if (amount === goal) return;
      const step = dt / fade;
      amount = goal > amount ? Math.min(goal, amount + step) : Math.max(goal, amount - step);
      cinemaDim.value = THREE.MathUtils.lerp(1, dimmed, THREE.MathUtils.smoothstep(amount, 0, 1));
    },
  };
}
