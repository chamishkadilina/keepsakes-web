import * as THREE from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

/**
 * The girl (girl.glb, "White Wedding Dress Girl" by FERUL on CGTrader, royalty free): standing idle and walking, both
 * motion-captured (Microsoft Rocketbox, MIT). She faces +z; place and turn `object` yourself (her feet are at its
 * origin).
 *
 *   addCharacterLights(scene, renderer);          // once: soft warm light for the characters
 *   const girl = createCharacter(await loader.loadAsync("/models/girl.glb"));
 *   scene.add(girl.object);
 *   girl.move(speed);         // every frame, her speed over the floor in m/s: standing or walking
 *   girl.update(delta);       // every frame
 */
export interface Character {
  object: THREE.Object3D;
  move(speed: number): void;
  update(dt: number): void;
  dispose(): void;
}

const WALK = 0.87;                   // m/s her walk covers at normal speed
const FADE = 0.3;                    // crossfade (s)

/** Soft warm light from above and the front with a gentle rim, and soft reflections. Only the characters use lit
 * materials, so the baked museum is unaffected. Returns a function that removes them. */
export function addCharacterLights(scene: THREE.Scene, renderer?: THREE.WebGLRenderer): () => void {
  const sky = new THREE.HemisphereLight(0xfff0e2, 0x6b5243, 0.9);
  const key = new THREE.DirectionalLight(0xffe7d2, 1.1);
  key.position.set(0.4, 1.0, 0.7);
  const rim = new THREE.DirectionalLight(0xffd9c2, 0.5);
  rim.position.set(-0.5, 0.8, -0.9);
  scene.add(sky, key, rim);
  let env: THREE.Texture | undefined;
  if (renderer && !scene.environment) {
    const pmrem = new THREE.PMREMGenerator(renderer);
    env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    scene.environment = env;
  }
  return () => {
    scene.remove(sky, key, rim);
    if (env && scene.environment === env) scene.environment = null;
    env?.dispose();
  };
}

export function createCharacter(gltf: GLTF): Character {
  const object = gltf.scene;
  object.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    mesh.frustumCulled = false;                                                      // skinned: she moves past her bounds
    for (const m of [mesh.material].flat() as THREE.MeshStandardMaterial[]) {
      m.side = THREE.DoubleSide;                                                     // her dress and sleeves are single sheets
      m.envMapIntensity = 0.35;
    }
  });

  const mixer = new THREE.AnimationMixer(object);
  const idle = mixer.clipAction(THREE.AnimationClip.findByName(gltf.animations, "Idle"));
  const walk = mixer.clipAction(THREE.AnimationClip.findByName(gltf.animations, "Walk"));
  let current = idle;
  idle.play();

  return {
    object,
    move(speed) {
      const next = speed < 0.12 ? idle : walk;
      if (next === walk) walk.timeScale = THREE.MathUtils.clamp(speed / WALK, 0.6, 1.8);
      if (next === current) return;
      next.reset().play();
      next.crossFadeFrom(current, FADE, true);
      current = next;
    },
    update(dt) {
      mixer.update(dt);
    },
    dispose() {
      mixer.stopAllAction();
      object.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (!mesh.isMesh) return;
        mesh.geometry.dispose();
        for (const m of [mesh.material].flat() as THREE.MeshStandardMaterial[]) {
          for (const t of [m.map, m.normalMap, m.roughnessMap, m.metalnessMap]) t?.dispose();
          m.dispose();
        }
      });
    },
  };
}
