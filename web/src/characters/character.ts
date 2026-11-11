import * as THREE from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

/**
 * The girl (girl.glb, "White Wedding Dress Girl" by FERUL on CGTrader, royalty free), with motion-captured idles and
 * walks (Microsoft Rocketbox, MIT) and the things that make her feel alive:
 *  - she eases between standing, a stroll, a walk and a brisk walk, her steps matching her speed over the floor;
 *  - standing, she now and then looks around or shifts her weight;
 *  - her dress, long sleeves and hair swing as she moves (a light spring simulation on their bones);
 *  - she blinks;
 *  - she turns her head to what she is given to look at (the camera, a photo), as far as is comfortable;
 *  - she leans a little into her turns, and soft shadows under her feet ground her.
 * She faces +z; place and turn `object` yourself (her feet are at its origin).
 *
 *   addCharacterLights(scene, renderer);          // once: soft warm light for the characters
 *   const girl = createCharacter(await loader.loadAsync("/models/girl.glb"));
 *   scene.add(girl.object);
 *   girl.move(speed);         // every frame, her speed over the floor in m/s (0 = standing)
 *   girl.lookAt(point);       // optional, any time: a world position to look at, or null to look ahead
 *   girl.update(delta);       // every frame
 *
 * She looks best walked at about WALK_SPEED, and no faster than MAX_SPEED (she doesn't run).
 */
export const WALK_SPEED = 1.0;       // m/s: her natural walk
export const MAX_SPEED = 1.75;       // m/s: her brisk walk

export interface Character {
  object: THREE.Object3D;
  move(speed: number): void;
  lookAt(point: THREE.Vector3 | null): void;
  update(dt: number): void;
  dispose(): void;
}

const GAITS: [string, number][] = [["Walk_Slow", 0.769], ["Walk", 1.008], ["Walk_Fast", 1.592]];   // clip, its speed (m/s)
const EXTRAS = ["Idle_Look", "Idle_Shift"];                                   // played now and then while she stands
const REFLECTIONS = 0.3;                                                       // how much of the room her surfaces mirror
const { clamp, smoothstep } = THREE.MathUtils;

/** Soft warm light from above and the front with a cool fill and a gentle rim, and soft reflections. Only the
 * characters use lit materials, so the baked museum is unaffected. Returns a function that removes them. */
export function addCharacterLights(scene: THREE.Scene, renderer?: THREE.WebGLRenderer): () => void {
  const sky = new THREE.HemisphereLight(0xfff1e4, 0x8a6f5c, 1.15);
  const key = new THREE.DirectionalLight(0xffe9d6, 1.5);
  key.position.set(0.5, 1.0, 0.8);
  const fill = new THREE.DirectionalLight(0xe6ecff, 0.45);
  fill.position.set(-0.8, 0.4, 0.3);
  const rim = new THREE.DirectionalLight(0xffe2cc, 0.7);
  rim.position.set(-0.4, 0.8, -0.9);
  scene.add(sky, key, fill, rim);
  let env: THREE.Texture | undefined;
  if (renderer && !scene.environment) {
    const pmrem = new THREE.PMREMGenerator(renderer);
    env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    scene.environment = env;
  }
  return () => {
    scene.remove(sky, key, fill, rim);
    if (env && scene.environment === env) scene.environment = null;
    env?.dispose();
  };
}

// ------------------------------------------------------------------------------------------------ standing and walking
/** Blends her idles and walks by her speed. The walks start on the same footfall, so they are played in step. */
function createLocomotion(mixer: THREE.AnimationMixer, clips: THREE.AnimationClip[]) {
  const posed = (name: string) => {                                           // an action whose time and weight are set here
    const action = mixer.clipAction(THREE.AnimationClip.findByName(clips, name));
    action.play();
    action.setEffectiveTimeScale(0);
    action.setEffectiveWeight(0);
    return action;
  };
  const idle = mixer.clipAction(THREE.AnimationClip.findByName(clips, "Idle"));
  idle.play();
  const extras = EXTRAS.map(posed);
  const gaits = GAITS.map(([name, speed]) => {
    const action = posed(name), seconds = action.getClip().duration;
    return { action, speed, seconds, stride: speed * seconds };
  });
  const share = gaits.map(() => 0);
  let target = 0, speed = 0, step = 0, stood = 0, extra = -1, extraTime = 0, wait = 5 + Math.random() * 5;

  return {
    get speed() { return speed; },
    move(v: number) { target = Math.max(0, v); },
    update(dt: number) {
      speed += (target - speed) * (1 - Math.exp(-dt * (target > speed ? 7 : 9)));
      const moving = smoothstep(speed, 0.05, 0.5), last = gaits.length - 1;
      share.fill(0);
      if (speed <= gaits[0].speed) share[0] = 1;
      else if (speed >= gaits[last].speed) share[last] = 1;
      else {
        const i = gaits.findIndex((_, k) => k < last && speed <= gaits[k + 1].speed);
        share[i + 1] = (speed - gaits[i].speed) / (gaits[i + 1].speed - gaits[i].speed);
        share[i] = 1 - share[i + 1];
      }
      const stride = gaits.reduce((sum, g, i) => sum + g.stride * share[i], 0);
      step = moving < 0.001 ? 0 : (step + (dt * clamp(speed, 0.5, MAX_SPEED * 1.15)) / stride) % 1;
      gaits.forEach((g, i) => {
        g.action.time = step * g.seconds;
        g.action.setEffectiveWeight(moving * share[i]);
      });

      stood = moving < 0.02 ? stood + dt : 0;                                   // now and then, a little life
      if (extra < 0 && stood > wait) { extra = Math.floor(Math.random() * extras.length); extraTime = 0; }
      let ease = 0;
      if (extra >= 0) {
        const seconds = extras[extra].getClip().duration;
        extraTime += dt;
        ease = smoothstep(Math.min(extraTime, seconds - extraTime), 0, 0.8);
        extras[extra].time = Math.min(extraTime, seconds);
        if (extraTime >= seconds || moving > 0.95) { extra = -1; stood = 0; wait = 5 + Math.random() * 7; ease = 0; }
      }
      extras.forEach((action, i) => action.setEffectiveWeight(i === extra ? (1 - moving) * ease : 0));
      idle.setEffectiveWeight((1 - moving) * (1 - ease));
    },
  };
}

// ------------------------------------------------------------------------------------------------ her dress, sleeves and hair
interface Joint {
  bone: THREE.Object3D;
  next: THREE.Object3D;              // the next bone in the chain (where this one ends)
  stiffness: number;                 // how strongly it swings back to its animated pose
  drag: number;
  capsules: number[];                // which of her body's capsules push it out
  pose: THREE.Quaternion;            // as animated
  tail: THREE.Vector3;               // where its end is now (world) ...
  prev: THREE.Vector3;               // ... and was a step ago
}
const CLOTH: { chain: RegExp; stiffness: number[]; drag: number; capsules: number[] }[] = [   // stiffness per bone, top down
  { chain: /^skirt_\d+_1$/, stiffness: [14, 7, 4], drag: 0.35, capsules: [0, 1, 2, 3] },
  { chain: /^sleeve_\d+_1_[lr]$/, stiffness: [6, 3], drag: 0.35, capsules: [] },
  { chain: /^hair_\d+_1$/, stiffness: [22, 13, 9], drag: 0.45, capsules: [4] },
];
const CAPSULES: [string, string, number][] = [                                // from bone, to bone, radius (m)
  ["thigh_l", "calf_l", 0.085], ["calf_l", "foot_l", 0.06], ["thigh_r", "calf_r", 0.085], ["calf_r", "foot_r", 0.06],
  ["spine_02", "neck_01", 0.085],
];
const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _c = new THREE.Vector3(), _d = new THREE.Vector3();
const _q = new THREE.Quaternion(), _p = new THREE.Quaternion(), _down = new THREE.Vector3(0, -1, 0);

function pushOut(p: THREE.Vector3, a: THREE.Vector3, b: THREE.Vector3, radius: number) {
  const ab = _c.subVectors(b, a), t = clamp(_d.subVectors(p, a).dot(ab) / Math.max(ab.lengthSq(), 1e-6), 0, 1);
  const q = _d.copy(a).addScaledVector(ab, t), off = _c.subVectors(p, q), dist = off.length();
  if (dist < radius) p.copy(q).addScaledVector(dist > 1e-5 ? off.divideScalar(dist) : _down, radius);
}

/** Chains of bones (each ending in an _end bone), swung by inertia and pushed out of her body. */
function createCloth(object: THREE.Object3D) {
  const joints: Joint[] = [];
  object.traverse((o) => {
    const kind = CLOTH.find((k) => k.chain.test(o.name));
    if (!kind) return;
    for (let bone: THREE.Object3D | undefined = o, i = 0; bone; i++) {
      const next: THREE.Object3D | undefined = bone.children.find((c) => (c as THREE.Bone).isBone);
      if (!next) break;
      joints.push({ bone, next, stiffness: kind.stiffness[Math.min(i, kind.stiffness.length - 1)], drag: kind.drag,
        capsules: kind.capsules, pose: bone.quaternion.clone(), tail: new THREE.Vector3(), prev: new THREE.Vector3() });
      bone = /_end(_[lr])?$/.test(next.name) ? undefined : next;
    }
  });
  const capsules = CAPSULES.map(([from, to, radius]) => ({ from: object.getObjectByName(from), to: object.getObjectByName(to),
    radius, a: new THREE.Vector3(), b: new THREE.Vector3() }));
  const at = new THREE.Vector3(), was = new THREE.Vector3();
  let started = false;

  const step = (dt: number) => {
    for (const c of capsules) { c.from?.getWorldPosition(c.a); c.to?.getWorldPosition(c.b); }
    for (const j of joints) {                                      // parents first: the chains were collected top down
      j.bone.quaternion.copy(j.pose);
      j.bone.updateMatrixWorld(true);
      const head = j.bone.getWorldPosition(_a), rest = j.next.getWorldPosition(_b);
      const length = rest.distanceTo(head);
      if (!started) { j.tail.copy(rest); j.prev.copy(rest); }
      const restDir = rest.sub(head).normalize();
      const next = at.copy(j.tail)
        .addScaledVector(_c.subVectors(j.tail, j.prev), 1 - j.drag)
        .addScaledVector(restDir, j.stiffness * dt);
      next.sub(head).setLength(length).add(head);
      for (const i of j.capsules) pushOut(next, capsules[i].a, capsules[i].b, capsules[i].radius);
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
      if (object.getWorldPosition(_a).distanceTo(was) > 0.6) started = false;       // she was placed elsewhere: settle there
      was.copy(_a);
      const n = clamp(Math.ceil(dt * 60), 1, 3);
      for (let i = 0; i < n; i++) step(Math.min(dt, 0.1) / n);
    },
  };
}

// ------------------------------------------------------------------------------------------------ her gaze
const GAZE: [string, number][] = [["spine_03", 0.15], ["neck_01", 0.35], ["head", 0.5]];   // bone, its share of the turn
const HAIR_STAYS = 0.75;                                                       // how much of the turn her long hair sits out

/** Turns her head (and a little of her shoulders) towards a point: up to about 60 degrees to a side, never craning
 * at what is behind her. Her hair down her back mostly stays on her back. */
function createGaze(object: THREE.Object3D) {
  const posed = (bone?: THREE.Object3D) => (bone ? [{ bone, pose: bone.quaternion.clone() }] : []);
  const bones = GAZE.flatMap(([name, share]) => posed(object.getObjectByName(name)).map((b) => ({ ...b, share })));
  const hair: { bone: THREE.Object3D; pose: THREE.Quaternion }[] = [];
  object.traverse((o) => { if (/^hair_\d+_1$/.test(o.name)) hair.push(...posed(o)); });
  const head = object.getObjectByName("head");
  const target = new THREE.Vector3(), up = new THREE.Vector3(), side = new THREE.Vector3();
  const turn = new THREE.Quaternion(), tilt = new THREE.Quaternion();
  let wanted = false, yaw = 0, pitch = 0;
  /** Turns a bone by `amount` of her gaze, in the world's axes. */
  const apply = (bone: THREE.Object3D, amount: number) => {
    const parent = bone.parent!.getWorldQuaternion(_p);
    turn.setFromAxisAngle(up, yaw * amount).multiply(tilt.setFromAxisAngle(side, -pitch * amount));
    bone.quaternion.premultiply(_q.copy(parent).invert().multiply(turn).multiply(parent));
    bone.updateMatrixWorld(true);
  };
  return {
    lookAt(point: THREE.Vector3 | null) {
      wanted = !!point;
      if (point) target.copy(point);
    },
    /** Before the animation: back to their animated pose (the mixer only writes values that change). */
    restore() { for (const b of [...bones, ...hair]) b.bone.quaternion.copy(b.pose); },
    /** After the animation, with her world matrices up to date. */
    update(dt: number, walking: number) {
      for (const b of [...bones, ...hair]) b.pose.copy(b.bone.quaternion);
      let wantYaw = 0, wantPitch = 0;
      const facing = object.getWorldQuaternion(_q);
      up.set(0, 1, 0).applyQuaternion(facing);
      side.set(1, 0, 0).applyQuaternion(facing);
      if (wanted && head) {
        const to = _a.copy(target).sub(head.getWorldPosition(_b)).applyQuaternion(facing.invert());   // in her own axes
        const y = Math.atan2(to.x, to.z), p = Math.atan2(to.y, Math.hypot(to.x, to.z));
        const within = (1 - smoothstep(Math.abs(y), 1.4, 1.9)) * (1 - 0.4 * walking);
        wantYaw = clamp(y, -1.05, 1.05) * within;
        wantPitch = clamp(p, -0.3, 0.4) * within;
      }
      const ease = 1 - Math.exp(-dt * 3.5);
      yaw += (wantYaw - yaw) * ease;
      pitch += (wantPitch - pitch) * ease;
      if (Math.abs(yaw) < 1e-4 && Math.abs(pitch) < 1e-4) return;
      let turned = 0;
      for (const b of bones) {
        apply(b.bone, b.share);
        if (b.bone.name !== "spine_03") turned += b.share;
      }
      for (const b of hair) apply(b.bone, -turned * HAIR_STAYS);
    },
  };
}

// ------------------------------------------------------------------------------------------------ her blink
/** Her one shape key closes her eyes: a blink every few seconds, now and then two. */
function createBlink(object: THREE.Object3D) {
  const meshes: THREE.Mesh[] = [];
  object.traverse((o) => { if ((o as THREE.Mesh).morphTargetInfluences?.length) meshes.push(o as THREE.Mesh); });
  const SECONDS = 0.16;
  let time = 0, next = 1.5 + Math.random() * 3;
  return {
    update(dt: number) {
      time += dt;
      if (time > next + SECONDS) next = time + (Math.random() < 0.2 ? 0.12 : 2 + Math.random() * 4);
      const closed = time > next ? Math.sin(((time - next) / SECONDS) * Math.PI) : 0;
      for (const m of meshes) m.morphTargetInfluences![0] = closed;
    },
  };
}

// ------------------------------------------------------------------------------------------------ her shadows
/** A soft shadow under her and a darker one under each foot, fading as the foot lifts. */
function createShadows(object: THREE.Object3D) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 64;
  const g = canvas.getContext("2d")!, fade = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  fade.addColorStop(0, "rgba(0,0,0,1)");
  fade.addColorStop(0.45, "rgba(0,0,0,0.5)");
  fade.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = fade;
  g.fillRect(0, 0, 64, 64);
  const map = new THREE.CanvasTexture(canvas);
  const blob = (width: number, depth: number, opacity: number) => {
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, depth).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({ map, color: 0x000000, transparent: true, opacity, depthWrite: false }));
    mesh.position.y = 0.02;
    mesh.name = "character_shadow";
    object.add(mesh);
    return mesh;
  };
  const body = blob(1.0, 1.0, 0.3);
  const feet = ["foot_l", "foot_r"].map((name) => ({ bone: object.getObjectByName(name), mesh: blob(0.2, 0.36, 0.5) }));
  return {
    update() {
      body.position.x = body.position.z = 0;
      for (const { bone, mesh } of feet) {
        if (!bone) continue;
        const p = object.worldToLocal(bone.getWorldPosition(_a));
        mesh.position.set(p.x, 0.021, p.z + 0.04);
        (mesh.material as THREE.MeshBasicMaterial).opacity = 0.5 * (1 - smoothstep(p.y, 0.15, 0.3));
        body.position.x += p.x / 2;
        body.position.z += p.z / 2;
      }
    },
  };
}

export function createCharacter(gltf: GLTF): Character {
  const object = gltf.scene;
  const materials: THREE.MeshStandardMaterial[] = [];
  object.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    mesh.frustumCulled = false;                                                      // skinned: she moves past her bounds
    for (const m of [mesh.material].flat() as THREE.MeshStandardMaterial[]) {
      m.side = THREE.DoubleSide;                                                     // her dress and sleeves are single sheets
      materials.push(m);
    }
  });
  const mixer = new THREE.AnimationMixer(object);
  const motion = createLocomotion(mixer, gltf.animations);
  const cloth = createCloth(object);
  const gaze = createGaze(object);
  const blink = createBlink(object);
  const shadows = createShadows(object);
  const root = object.getObjectByName("Root");
  const stand = root?.quaternion.clone();
  const facing = new THREE.Vector3();
  let heading: number | undefined, turning = 0, lean = 0, lit = false;

  return {
    object,
    move: motion.move,
    lookAt: gaze.lookAt,
    update(dt) {
      if (!lit) {                                                  // her share of the room's reflections, once she is in it
        let top: THREE.Object3D = object;
        while (top.parent) top = top.parent;
        const env = (top as THREE.Scene).environment;
        if (env) {
          for (const m of materials) { m.envMap = env; m.envMapIntensity = REFLECTIONS; m.needsUpdate = true; }
          lit = true;
        }
      }
      cloth.restore();
      gaze.restore();
      motion.update(dt);
      mixer.update(dt);

      object.getWorldDirection(facing);                            // she leans into her turns
      const now = Math.atan2(facing.x, facing.z);
      const turned = heading === undefined ? 0 : Math.atan2(Math.sin(now - heading), Math.cos(now - heading));
      heading = now;
      if (dt > 0) turning += (clamp(turned / dt, -4, 4) - turning) * (1 - Math.exp(-dt * 6));
      lean += (clamp(-turning * motion.speed * 0.03, -0.08, 0.08) - lean) * (1 - Math.exp(-dt * 5));
      if (root && stand) {
        const forward = _b.set(0, 0, 1).applyQuaternion(object.getWorldQuaternion(_q))
          .applyQuaternion(root.parent!.getWorldQuaternion(_p).invert());
        root.quaternion.copy(stand).premultiply(_q.setFromAxisAngle(forward, lean));
      }

      object.updateMatrixWorld(true);
      gaze.update(dt, smoothstep(motion.speed, 0.05, 0.5));
      cloth.update(dt);
      blink.update(dt);
      shadows.update();
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
