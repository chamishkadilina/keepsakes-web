import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { createSoftMatcap } from "../lighting/matcaps";

/**
 * Rose petals scattered along the walking path, deep red and blush pink, with a few whole roses.
 * They react to the visitor like real petals: the ones near the feet are pushed along, lift a little, spin and
 * flutter back down; roses roll a short way. Only the petals around the visitor move, the rest cost nothing.
 * Two InstancedMeshes = two draw calls. Skipped by the floor reflection (they lie on the floor).
 *
 *   const petals = createRosePetals(path);
 *   scene.add(petals);
 *   useFrame(({ camera }, delta) => petals.update(camera.position, delta));
 *
 * `path` is a list of floor points [x, z] in three.js coordinates (y up, floor at y = 0), in walking order.
 */
function petalGeometry(): THREE.BufferGeometry {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0.045, 0.02, 0.055, 0.08, 0.012, 0.1);
  shape.quadraticCurveTo(0, 0.092, -0.012, 0.1);
  shape.bezierCurveTo(-0.055, 0.08, -0.045, 0.02, 0, 0);
  const g = new THREE.ShapeGeometry(shape, 10);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {                        // cup the petal: edges curl up
    const x = p.getX(i), y = p.getY(i);
    p.setZ(i, 0.9 * x * x / 0.05 + 0.012 * Math.pow(y / 0.1, 2));
  }
  g.rotateX(-Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

/** A rose head: rings of cupped petals opening around a tight bud, ~8 cm across. */
function roseGeometry(): THREE.BufferGeometry {
  const petal = petalGeometry(), parts: THREE.BufferGeometry[] = [];
  const rings = [{ n: 3, r: 0.006, tilt: 1.25, s: 0.45 }, { n: 5, r: 0.014, tilt: 0.95, s: 0.6 }, { n: 6, r: 0.022, tilt: 0.6, s: 0.75 }, { n: 7, r: 0.03, tilt: 0.3, s: 0.85 }];
  rings.forEach(({ n, r, tilt, s }, k) => {
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + k * 0.7;
      const g = petal.clone().scale(s, s, s);
      g.rotateX(-tilt);                                      // stand the petal up
      g.translate(0, 0.004 * (4 - k), r);
      g.rotateY(a);
      parts.push(g);
    }
  });
  return mergeGeometries(parts)!;
}

const REACH = 0.45;           // around the visitor's feet, steps and the air they move push petals (metres)
const TETHER = 0.8;           // a petal never drifts further than this from where it was laid (keeps them off the walls)
const ROSE_RADIUS = 0.035;    // a rose head rolls like a ball of this radius

interface Item {
  p: THREE.Vector3; v: THREE.Vector3; home: THREE.Vector2; restY: number; scale: number;
  yaw: number; spin: number; tilt: THREE.Vector2; tiltV: THREE.Vector2; restTilt: THREE.Vector2;
  turn: number;               // which way it tends to spin (±1)
  q: THREE.Quaternion;        // orientation (roses roll)
  awake: boolean;
}

export class RosePetals extends THREE.Group {
  private readonly petals: THREE.InstancedMesh;
  private readonly roses: THREE.InstancedMesh;
  private readonly petalItems: Item[] = [];
  private readonly roseItems: Item[] = [];
  private readonly last = new THREE.Vector3();
  private readonly walk = new THREE.Vector2();             // the visitor's speed over the floor (m/s, smoothed)
  private readonly step2 = new THREE.Vector2();
  private started = false;
  private readonly m = new THREE.Matrix4();
  private readonly e = new THREE.Euler();
  private readonly s = new THREE.Vector3();
  private readonly roll = new THREE.Quaternion();
  private readonly axis = new THREE.Vector3();

  constructor(path: [number, number][], count: number, roses: number, seed: number) {
    super();
    const material = new THREE.MeshMatcapMaterial({ matcap: createSoftMatcap(), side: THREE.DoubleSide, toneMapped: false });
    let s = seed;
    const rnd = (a: number, b: number) => { s = (s * 16807) % 2147483647; return a + (s / 2147483647) * (b - a); };
    const c = new THREE.Color();
    const onPath = (spreadNear: number, spreadFar: number) => {
      const t = rnd(0, path.length - 1), k = Math.floor(t), f = t - k;
      const a = path[k], b = path[Math.min(k + 1, path.length - 1)];
      const spread = rnd(0, 1) < 0.8 ? spreadNear : spreadFar;           // most on the path, a few drift further
      return [a[0] + (b[0] - a[0]) * f + rnd(-spread, spread), a[1] + (b[1] - a[1]) * f + rnd(-spread, spread)];
    };
    const colour = () => (rnd(0, 1) < 0.72
      ? c.setHSL(rnd(0.975, 1.0), rnd(0.72, 0.88), rnd(0.3, 0.4))          // deep red
      : c.setHSL(rnd(0.97, 1.0), rnd(0.5, 0.65), rnd(0.74, 0.84)));         // blush pink
    const item = (x: number, y: number, z: number, i: number): Item => ({
      p: new THREE.Vector3(x, y, z), v: new THREE.Vector3(), home: new THREE.Vector2(x, z), restY: y, scale: 1,
      yaw: 0, spin: 0, tilt: new THREE.Vector2(), tiltV: new THREE.Vector2(), restTilt: new THREE.Vector2(),
      turn: i % 2 ? 1 : -1, q: new THREE.Quaternion(), awake: false,
    });

    this.petals = new THREE.InstancedMesh(petalGeometry(), material, count);
    for (let i = 0; i < count; i++) {
      const [x, z] = onPath(0.5, 1.5);
      const it = item(x, 0.002 + i * 0.00001, z, i);
      it.restTilt.set(rnd(-0.12, 0.12), 0); it.yaw = rnd(0, Math.PI * 2); it.restTilt.y = rnd(-0.12, 0.12);
      it.tilt.copy(it.restTilt); it.scale = rnd(0.7, 1.2);
      this.petalItems.push(it);
      this.petals.setColorAt(i, colour());
      this.writePetal(i);
    }
    this.roses = new THREE.InstancedMesh(roseGeometry(), material, roses);
    for (let i = 0; i < roses; i++) {
      const [x, z] = onPath(0.6, 1.2);
      const it = item(x, 0.03, z, i);
      it.q.setFromEuler(this.e.set(rnd(1.2, 1.5), rnd(0, Math.PI * 2), 0, "YXZ"));   // lying on its side
      it.scale = rnd(0.9, 1.15);
      this.roseItems.push(it);
      this.roses.setColorAt(i, colour());
      this.writeRose(i);
    }
    for (const mesh of [this.petals, this.roses]) {
      mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      mesh.frustumCulled = false;                             // instances move
      this.add(mesh);
    }
    this.userData.noReflection = true;
  }

  /** Call every frame with the visitor's (camera's) position and the frame time in seconds. */
  update(visitor: THREE.Vector3, delta: number): void {
    const dt = Math.min(delta, 1 / 30);                         // physics step (stays stable on slow frames)
    if (!this.started || dt <= 0) { this.last.copy(visitor); this.started = true; return; }
    const dx = visitor.x - this.last.x, dz = visitor.z - this.last.z;
    const jump = Math.hypot(dx, dz) > 1.5;                     // a teleport is not a step
    this.walk.lerp(this.step2.set(jump ? 0 : dx / delta, jump ? 0 : dz / delta), 1 - Math.exp(-8 * dt));
    this.last.copy(visitor);
    const speed = Math.min(this.walk.length(), 3);

    let moved = false;
    for (let i = 0; i < this.petalItems.length; i++) {
      if (this.step(this.petalItems[i], visitor, speed, dt, false)) { this.writePetal(i); moved = true; }
    }
    if (moved) this.petals.instanceMatrix.needsUpdate = true;
    moved = false;
    for (let i = 0; i < this.roseItems.length; i++) {
      if (this.step(this.roseItems[i], visitor, speed, dt, true)) { this.writeRose(i); moved = true; }
    }
    if (moved) this.roses.instanceMatrix.needsUpdate = true;
  }

  /** Moves one petal or rose; returns whether it moved. */
  private step(it: Item, visitor: THREE.Vector3, speed: number, dt: number, rose: boolean): boolean {
    const ox = it.p.x - visitor.x, oz = it.p.z - visitor.z, d = Math.hypot(ox, oz);
    const reach = rose ? REACH * 0.6 : REACH;
    if (speed > 0.15 && d < reach) {
      const f = (1 - d / reach) ** 2, push = ((rose ? 1.2 : 2.2) * f) / it.scale;   // bigger = heavier
      const rx = d > 1e-3 ? ox / d : 0, rz = d > 1e-3 ? oz / d : 0;    // away from the feet
      it.v.x += (this.walk.x * 0.8 + rx * speed * 1.6) * push * dt;   // mostly swept aside, a little carried along
      it.v.z += (this.walk.y * 0.8 + rz * speed * 1.6) * push * dt;
      if (!rose) {
        if (it.p.y < it.restY + 0.01) it.v.y = Math.max(it.v.y, Math.min(0.8, 0.75 * f * speed));   // a small hop
        it.spin += it.turn * 18 * f * speed * dt;
        it.tiltV.x += it.turn * 20 * f * speed * dt;
        it.tiltV.y -= it.turn * 14 * f * speed * dt;
      }
      it.awake = true;
    }
    if (!it.awake) return false;

    const air = it.p.y > it.restY + 1e-4 || it.v.y > 0;
    if (rose) {
      it.v.y = 0;
      it.v.x *= Math.exp(-5 * dt); it.v.z *= Math.exp(-5 * dt);
    } else {
      it.v.y -= 5 * dt;                                                  // light: air slows the fall
      const drag = Math.exp((air ? -2.2 : -9) * dt);                     // air drag, or the floor's grip
      it.v.x *= drag; it.v.z *= drag; it.v.y *= Math.exp(-2 * dt);
    }
    it.p.addScaledVector(it.v, dt);
    if (it.p.y < it.restY) { it.p.y = it.restY; it.v.y = Math.max(it.v.y, 0); }

    const hx = it.p.x - it.home.x, hz = it.p.z - it.home.y, far = Math.hypot(hx, hz);
    if (far > TETHER) {                                                  // stay near where it was laid
      it.p.x = it.home.x + (hx / far) * TETHER; it.p.z = it.home.y + (hz / far) * TETHER;
      const out = (it.v.x * hx + it.v.z * hz) / far;
      if (out > 0) { it.v.x -= (out * hx) / far; it.v.z -= (out * hz) / far; }
    }

    if (rose) {                                                          // roll along the floor
      const v = Math.hypot(it.v.x, it.v.z);
      if (v > 1e-4) it.q.premultiply(this.roll.setFromAxisAngle(this.axis.set(it.v.z / v, 0, -it.v.x / v), (v * dt) / ROSE_RADIUS));
    } else {
      it.yaw += it.spin * dt; it.spin *= Math.exp((air ? -1.5 : -6) * dt);
      if (!air) {                                                        // settles flat again on the floor
        it.tiltV.x += (it.restTilt.x - it.tilt.x) * 40 * dt; it.tiltV.y += (it.restTilt.y - it.tilt.y) * 40 * dt;
      }
      it.tiltV.multiplyScalar(Math.exp((air ? -1 : -6) * dt));
      it.tilt.addScaledVector(it.tiltV, dt);
    }

    const still = !air && Math.hypot(it.v.x, it.v.z) < 0.01 && Math.abs(it.spin) < 0.02
      && (rose || (it.tiltV.length() < 0.02 && it.tilt.distanceTo(it.restTilt) < 0.02));     // flat again before it sleeps
    if (still) it.awake = false;
    return true;
  }

  private writePetal(i: number) {
    const it = this.petalItems[i];
    it.q.setFromEuler(this.e.set(it.tilt.x, it.yaw, it.tilt.y, "XYZ"));
    this.petals.setMatrixAt(i, this.m.compose(it.p, it.q, this.s.setScalar(it.scale)));
  }

  private writeRose(i: number) {
    const it = this.roseItems[i];
    this.roses.setMatrixAt(i, this.m.compose(it.p, it.q, this.s.setScalar(it.scale)));
  }
}

export function createRosePetals(path: [number, number][], count = 300, roses = 14, seed = 7): RosePetals {
  return new RosePetals(path, count, roses, seed);
}
