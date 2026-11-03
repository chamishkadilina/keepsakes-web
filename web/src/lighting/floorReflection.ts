import * as THREE from "three";

/**
 * Soft glossy reflections on the polished wood floor (lamps, frames and walls mirrored, blurred, faded by angle).
 * The scene is rendered once more from a mirrored camera into a small texture each frame.
 * Everything in the museum is unlit (baked), so this extra pass is cheap.
 *
 *   const reflection = createFloorReflection(gl, scene, floorMeshes);
 *   useFrame(({ camera }) => reflection.update(camera));       // before the main render
 */
export interface FloorReflectionOptions {
  floorY?: number;       // height of the floor surface
  resolution?: number;   // share of the screen resolution (0.5 = half)
  strength?: number;     // 1 = polished lacquer
  roughness?: number;    // blur of the reflection (0 = mirror, 1 = satin lacquer)
}

export function createFloorReflection(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  floors: THREE.Mesh[],
  { floorY = 0, resolution = 0.35, strength = 0.5, roughness = 0.6 }: FloorReflectionOptions = {},
) {
  // mipmapped, so the glossy blur stays cheap (a few taps of a pre-blurred level)
  const target = new THREE.WebGLRenderTarget(1, 1, {
    colorSpace: THREE.SRGBColorSpace, depthBuffer: true, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter,
  });
  const mirror = new THREE.PerspectiveCamera();
  const textureMatrix = new THREE.Matrix4();
  const uniforms = {
    tReflect: { value: target.texture },
    reflectMatrix: { value: textureMatrix },
    reflectTexel: { value: new THREE.Vector2() },
    reflectStrength: { value: strength },
    reflectBlur: { value: roughness * 2.0 },
  };

  for (const floor of floors) {
    const material = floor.material as THREE.MeshBasicMaterial;
    material.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, uniforms);
      shader.vertexShader = shader.vertexShader
        .replace("#include <common>", "#include <common>\nuniform mat4 reflectMatrix;\nvarying vec4 vReflectUv;\nvarying vec3 vReflectWorld;")
        .replace("#include <project_vertex>", `#include <project_vertex>
          vec4 reflectWorld = modelMatrix * vec4(transformed, 1.0);
          vReflectWorld = reflectWorld.xyz;
          vReflectUv = reflectMatrix * reflectWorld;`);
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>
          uniform sampler2D tReflect; uniform vec2 reflectTexel; uniform float reflectStrength; uniform float reflectBlur;
          varying vec4 vReflectUv; varying vec3 vReflectWorld;`)
        .replace("#include <opaque_fragment>", `{
          vec2 uv = vReflectUv.xy / vReflectUv.w;
          #ifdef USE_MAP
            uv.y += (dot(sampledDiffuseColor.rgb, vec3(0.333)) - 0.3) * 0.012;   // wood grain ripples the reflection
          #endif
          vec2 o = reflectTexel * vec2(1.5, 2.0) * exp2(reflectBlur);      // glossy blur, stretched vertically like real floors
          vec3 r = texture2D(tReflect, uv, reflectBlur).rgb * 0.17
            + (texture2D(tReflect, uv + vec2(0.0, o.y), reflectBlur).rgb + texture2D(tReflect, uv - vec2(0.0, o.y), reflectBlur).rgb) * 0.145
            + (texture2D(tReflect, uv + vec2(0.0, 2.0 * o.y), reflectBlur).rgb + texture2D(tReflect, uv - vec2(0.0, 2.0 * o.y), reflectBlur).rgb) * 0.105
            + (texture2D(tReflect, uv + vec2(0.0, 3.0 * o.y), reflectBlur).rgb + texture2D(tReflect, uv - vec2(0.0, 3.0 * o.y), reflectBlur).rgb) * 0.06
            + (texture2D(tReflect, uv + vec2(o.x, 0.0), reflectBlur).rgb + texture2D(tReflect, uv - vec2(o.x, 0.0), reflectBlur).rgb) * 0.105;
          float facing = max(normalize(cameraPosition - vReflectWorld).y, 0.0);
          float fresnel = 0.04 + 0.96 * pow(1.0 - facing, 5.0);              // stronger at grazing angles, like real lacquer
          outgoingLight = mix(outgoingLight, r, clamp(fresnel * reflectStrength, 0.0, 1.0));
        }
        #include <opaque_fragment>`);
    };
    material.customProgramCacheKey = () => "floorReflection";
    material.needsUpdate = true;
  }

  const size = new THREE.Vector2(), cam = new THREE.Vector3(), look = new THREE.Vector3(), clip = new THREE.Vector4(), q = new THREE.Vector4();
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -floorY), viewPlane = new THREE.Plane();
  const hidden: THREE.Object3D[] = [];

  function update(camera: THREE.Camera) {
    const perspective = camera as THREE.PerspectiveCamera;
    renderer.getDrawingBufferSize(size).multiplyScalar(resolution).floor();
    if (target.width !== size.x || target.height !== size.y) {
      target.setSize(size.x, size.y);
      uniforms.reflectTexel.value.set(1 / size.x, 1 / size.y);
    }

    // mirror the camera below the floor
    cam.setFromMatrixPosition(camera.matrixWorld);
    if (cam.y < floorY) return;
    look.set(0, 0, -1).transformDirection(camera.matrixWorld).add(cam);
    mirror.position.set(cam.x, 2 * floorY - cam.y, cam.z);
    mirror.up.set(0, 1, 0).transformDirection(camera.matrixWorld).reflect(plane.normal);
    mirror.lookAt(look.x, 2 * floorY - look.y, look.z);
    mirror.near = perspective.near; mirror.far = perspective.far;
    mirror.updateMatrixWorld();
    mirror.projectionMatrix.copy(perspective.projectionMatrix);
    mirror.layers.mask = camera.layers.mask;

    textureMatrix.set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1)
      .multiply(mirror.projectionMatrix).multiply(mirror.matrixWorldInverse);

    // oblique near plane: nothing below the floor is drawn into the reflection
    viewPlane.copy(plane).applyMatrix4(mirror.matrixWorldInverse);
    clip.set(viewPlane.normal.x, viewPlane.normal.y, viewPlane.normal.z, viewPlane.constant);
    const p = mirror.projectionMatrix.elements;
    q.set((Math.sign(clip.x) + p[8]) / p[0], (Math.sign(clip.y) + p[9]) / p[5], -1, (1 + p[10]) / p[14]);
    clip.multiplyScalar(2 / clip.dot(q));
    p[2] = clip.x; p[6] = clip.y; p[10] = clip.z + 1 - 0.003; p[14] = clip.w;

    // render without the floor itself and flat floor decor
    hidden.length = 0;
    scene.traverseVisible((o) => { if (o.userData.noReflection) hidden.push(o); });
    floors.forEach((f) => hidden.push(f));
    hidden.forEach((o) => (o.visible = false));
    const previous = renderer.getRenderTarget();
    renderer.setRenderTarget(target);
    renderer.clear();
    renderer.render(scene, mirror);
    renderer.setRenderTarget(previous);
    hidden.forEach((o) => (o.visible = true));
  }

  function dispose() { target.dispose(); }
  return { update, dispose };
}
