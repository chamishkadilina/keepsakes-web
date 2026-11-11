import * as THREE from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

/**
 * The girl (girl.glb, "White Wedding Dress Girl" by FERUL on CGTrader, royalty free): standing idle and walking, both
 * motion-captured (Microsoft Rocketbox, MIT). Her dress and long sleeves swing as she moves (a light spring simulation on
 * their bones: inertia, her legs pushing the dress). She faces +z; place and turn `object` yourself (her feet are at its
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

// ------------------------------------------------------------------------------------------------ her dress and sleeves
interface Joint {
  bone: THREE.Object3D;
  next: THREE.Object3D;              // the next bone in the chain (where this one ends)
  stiffness: number;                 // how strongly it swings back to its animated pose
  pose: THREE.Quaternion;            // as animated
  tail: THREE.Vector3;               // where its end is now (world) ...
  prev: THREE.Vector3;               // ... and was a step ago
}
const DRESS = [14, 7, 4], SLEEVE = [6, 3], DRAG = 0.35;                       // per bone, from the top down
const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _c = new THREE.Vector3(), _d = new THREE.Vector3();
const _q = new THREE.Quaternion(), _p = new THREE.Quaternion(), _down = new THREE.Vector3(0, -1, 0);

function pushOut(p: THREE.Vector3, a: THREE.Vector3, b: THREE.Vector3, radius: number) {
  const ab = _c.subVectors(b, a), t = THREE.MathUtils.clamp(_d.subVectors(p, a).dot(ab) / Math.max(ab.lengthSq(), 1e-6), 0, 1);
  const q = _d.copy(a).addScaledVector(ab, t), off = p.clone().sub(q), dist = off.length();
  if (dist < radius) p.copy(q).addScaledVector(dist > 1e-5 ? off.divideScalar(dist) : _down, radius);
}

/** Chains of bones (skirt_<k>_1.. and sleeve_<k>_1_<side>.., each ending in an _end bone), swung by inertia and
 * pushed out of her legs. */
function createCloth(object: THREE.Object3D) {
  const joints: Joint[] = [];
  object.traverse((o) => {
    const dress = /^skirt_\d+_1$/.test(o.name);
    if (!dress && !/^sleeve_\d+_1_[lr]$/.test(o.name)) return;
    const stiffness = dress ? DRESS : SLEEVE;
    for (let bone: THREE.Object3D | undefined = o, i = 0; bone; i++) {
      const next: THREE.Object3D | undefined = bone.children.find((c) => (c as THREE.Bone).isBone);
      if (!next) break;
      joints.push({ bone, next, stiffness: stiffness[Math.min(i, stiffness.length - 1)], pose: bone.quaternion.clone(),
        tail: new THREE.Vector3(), prev: new THREE.Vector3() });
      bone = /_end(_[lr])?$/.test(next.name) ? undefined : next;
    }
  });
  const legs: [THREE.Object3D, THREE.Object3D, number][] = [];
  for (const s of ["l", "r"]) {
    const thigh = object.getObjectByName(`thigh_${s}`), calf = object.getObjectByName(`calf_${s}`), foot = object.getObjectByName(`foot_${s}`);
    if (thigh && calf && foot) legs.push([thigh, calf, 0.085], [calf, foot, 0.06]);
  }
  const ends = legs.map(() => [new THREE.Vector3(), new THREE.Vector3()]);
  let started = false;

  const step = (dt: number) => {
    legs.forEach(([a, b], i) => { a.getWorldPosition(ends[i][0]); b.getWorldPosition(ends[i][1]); });
    for (const j of joints) {                                      // parents first: the chains were collected top down
      j.bone.quaternion.copy(j.pose);
      j.bone.updateMatrixWorld(true);
      const head = j.bone.getWorldPosition(_a), rest = j.next.getWorldPosition(_b);
      const length = rest.distanceTo(head);
      if (!started) { j.tail.copy(rest); j.prev.copy(rest); }
      const restDir = rest.sub(head).normalize();
      const next = j.tail.clone()
        .addScaledVector(_c.subVectors(j.tail, j.prev), 1 - DRAG)
        .addScaledVector(restDir, j.stiffness * dt);
      next.sub(head).setLength(length).add(head);
      legs.forEach(([, , radius], c) => pushOut(next, ends[c][0], ends[c][1], radius));
      next.sub(j.bone.getWorldPosition(_a)).setLength(length).add(_a);
      j.prev.copy(j.tail);
      j.tail.copy(next);
      const parentRot = j.bone.parent!.getWorldQuaternion(_p);                      // turn it to point there
      _q.setFromUnitVectors(restDir, next.sub(_a).normalize());
      j.bone.quaternion.copy(parentRot).invert().multiply(_q).multiply(parentRot).multiply(j.pose);
      j.bone.updateMatrixWorld(true);
    }
    started = true;
  };
  return {
    /** Before the animation: back to their animated pose (the mixer only writes values that change). */
    restore() { for (const j of joints) j.bone.quaternion.copy(j.pose); },
    update(dt: number) {
      for (const j of joints) j.pose.copy(j.bone.quaternion);
      const n = Math.min(4, Math.max(1, Math.ceil(dt * 60)));
      for (let i = 0; i < n; i++) step(Math.min(dt, 0.1) / n);
    },
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
  const cloth = createCloth(object);

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
      cloth.restore();
      mixer.update(dt);
      object.updateMatrixWorld(true);
      cloth.update(dt);
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
