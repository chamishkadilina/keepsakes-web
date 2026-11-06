import * as THREE from "three";
import { createLatexMatcap } from "../lighting/matcaps";
import { type Footprint, keepOffFootprints } from "./footprints";

/**
 * Party balloons lying on the floor, a little fun: round latex balloons in red, blush, ivory and gold gathered in a few
 * loose groups. Walk into them and they roll and bounce away from her feet (the faster she walks, the further), knock
 * into each other, bounce off the furniture and stay inside their room, rolling to a stop like real balloons.
 * One draw call for all of them (they show in the floor reflection); update() costs well under 0.1 ms per frame.
 *
 *   const balloons = createFloorBalloons(FLOOR_BALLOON_AREAS, { footprints });
 *   scene.add(balloons);
 *   useFrame(({ camera }, delta) => balloons.update(camera.position, delta));
 */
export interface FloorBalloonArea {
  rect: [number, number, number, number];   // the room's floor: x0, z0, x1, z1 (three.js metres); balloons stay inside it
  count: number;
  groups?: [number, number][];               // where they gather ([x, z]); spread round the room if left out
}

export interface FloorBalloonOptions {
  footprints?: Footprint[];                  // getFootprints(): never placed on furniture, bounce off it
  colours?: THREE.ColorRepresentation[];
  light?: number;                            // brightness, to match the rooms (1 = as tuned for the museum)
  seed?: number;
}

const RADIUS = 0.15;                         // the balloon's round middle (metres); 0.17 along its length
const DRAG = 1.4;                            // per second: rolls to a stop in about two seconds
const KICK = 0.55;                           // her feet: within this distance of the visitor they are pushed

interface Ball {
  p: THREE.Vector3;                           // y = height of its middle above the floor
  v: THREE.Vector3;
  q: THREE.Quaternion;
  rect: [number, number, number, number];
}

function balloonGeometry(): THREE.BufferGeometry {
  const body = new THREE.SphereGeometry(RADIUS, 24, 16);
  body.scale(1, 1.13, 1);                                           // a little longer than round, like a real balloon
  const knot = new THREE.CylinderGeometry(0.012, 0.02, 0.03, 8);
  knot.translate(0, -RADIUS * 1.13 - 0.012, 0);
  const merged = new THREE.BufferGeometry();
  const parts = [body.toNonIndexed(), knot.toNonIndexed()];
  for (const name of ["position", "normal"]) {
    const arrays = parts.map((g) => g.getAttribute(name).array as Float32Array);
    const all = new Float32Array(arrays.reduce((n, a) => n + a.length, 0));
    let at = 0;
    for (const a of arrays) { all.set(a, at); at += a.length; }
    merged.setAttribute(name, new THREE.BufferAttribute(all, 3));
  }
  return merged;
}

export class FloorBalloons extends THREE.InstancedMesh {
  private readonly balls: Ball[] = [];
  private readonly footprints: Footprint[];
  private readonly last = new THREE.Vector3();
  private readonly walk = new THREE.Vector3();
  private started = false;
  private readonly m = new THREE.Matrix4();
  private readonly roll = new THREE.Quaternion();
  private readonly axis = new THREE.Vector3();
  private readonly d = new THREE.Vector3();
  private readonly one = new THREE.Vector3(1, 1, 1);

  constructor(areas: FloorBalloonArea[], { footprints = [], colours = [0xc8102e, 0xf2a7b6, 0xf6efe6, 0xd9b26b, 0xe0284f], light = 1, seed = 5 }: FloorBalloonOptions = {}) {
    const count = areas.reduce((n, a) => n + a.count, 0);
    super(balloonGeometry(), new THREE.MeshMatcapMaterial({ matcap: createLatexMatcap(), color: new THREE.Color(light, light, light) }), count);
    this.name = "floor_balloons";
    this.footprints = footprints;
    let s = seed;
    const rnd = (a: number, b: number) => { s = (s * 16807) % 2147483647; return a + (s / 2147483647) * (b - a); };
    const c = new THREE.Color();
    for (const area of areas) {
      const [x0, z0, x1, z1] = area.rect;
      const groups = area.groups ?? [[x0 + (x1 - x0) * 0.25, z0 + (z1 - z0) * 0.3], [x0 + (x1 - x0) * 0.7, z0 + (z1 - z0) * 0.65]];
      for (let i = 0; i < area.count; i++) {
        const [gx, gz] = groups[i % groups.length];
        const p = new THREE.Vector3();
        for (let tries = 0; tries < 40; tries++) {                   // loosely round the group, clear of furniture and each other
          p.set(THREE.MathUtils.clamp(gx + rnd(-0.9, 0.9), x0 + RADIUS, x1 - RADIUS), RADIUS, THREE.MathUtils.clamp(gz + rnd(-0.9, 0.9), z0 + RADIUS, z1 - RADIUS));
          const free = this.balls.every((b) => b.p.distanceTo(p) > RADIUS * 2.1);
          const clear = !footprints.some((f) => f.walkable === false && this.inside(f, p));
          if (free && clear) break;
        }
        const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.PI / 2 + rnd(-0.3, 0.3), rnd(0, Math.PI * 2), 0, "YXZ"));
        this.balls.push({ p, v: new THREE.Vector3(), q, rect: area.rect });
        this.setColorAt(this.balls.length - 1, c.set(colours[Math.floor(rnd(0, colours.length))]));
      }
    }
    this.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.frustumCulled = false;
    this.write();
  }

  private inside(f: Footprint, p: THREE.Vector3): boolean {
    const q = this.d.copy(p).applyMatrix4(f.toLocal);
    if (f.radius !== null) return Math.hypot(q.x, q.z) < f.radius + RADIUS;
    return Math.abs(q.x) < f.halfWidth + RADIUS && Math.abs(q.z) < f.halfDepth + RADIUS;
  }

  private write() {
    this.balls.forEach((b, i) => this.setMatrixAt(i, this.m.compose(b.p, b.q, this.one)));
    this.instanceMatrix.needsUpdate = true;
  }

  /** Call every frame with the visitor's position (her feet are under it) and the frame's seconds. */
  update(visitor: THREE.Vector3, dt: number): void {
    dt = Math.min(dt, 0.05);
    if (!this.started) { this.last.copy(visitor); this.started = true; }
    this.walk.set(visitor.x - this.last.x, 0, visitor.z - this.last.z).divideScalar(Math.max(dt, 1e-4));
    this.last.copy(visitor);
    let moving = false;
    for (const b of this.balls) {
      const dx = b.p.x - visitor.x, dz = b.p.z - visitor.z, dist = Math.hypot(dx, dz);
      if (dist < KICK + RADIUS && dist > 1e-4) {                  // her feet: pushed away, harder the faster she walks
        const push = Math.max(0.7, this.walk.length() * 1.5);
        b.v.x += (dx / dist) * push * dt * 12; b.v.z += (dz / dist) * push * dt * 12;
        if (b.p.y <= RADIUS + 1e-3) b.v.y = Math.min(0.9, 0.35 + this.walk.length() * 0.25);   // a little hop
        const out = KICK + RADIUS - dist;
        b.p.x += (dx / dist) * out; b.p.z += (dz / dist) * out;
      }
      if (b.v.lengthSq() < 1e-6 && b.p.y <= RADIUS + 1e-3) continue;
      moving = true;
      b.v.y -= 2.5 * dt;                                           // light as a balloon: it falls back slowly
      b.p.addScaledVector(b.v, dt);
      if (b.p.y < RADIUS) { b.p.y = RADIUS; b.v.y = Math.abs(b.v.y) > 0.2 ? -b.v.y * 0.4 : 0; }
      const k = Math.exp(-DRAG * dt);
      b.v.x *= k; b.v.z *= k;
      const [x0, z0, x1, z1] = b.rect;                             // the room's walls
      if (b.p.x < x0 + RADIUS) { b.p.x = x0 + RADIUS; b.v.x = Math.abs(b.v.x) * 0.5; }
      if (b.p.x > x1 - RADIUS) { b.p.x = x1 - RADIUS; b.v.x = -Math.abs(b.v.x) * 0.5; }
      if (b.p.z < z0 + RADIUS) { b.p.z = z0 + RADIUS; b.v.z = Math.abs(b.v.z) * 0.5; }
      if (b.p.z > z1 - RADIUS) { b.p.z = z1 - RADIUS; b.v.z = -Math.abs(b.v.z) * 0.5; }
      const bx = b.p.x, bz = b.p.z;
      keepOffFootprints(b.p, RADIUS, this.footprints);             // furniture: bounce off it
      if (b.p.x !== bx || b.p.z !== bz) { b.v.x *= -0.5; b.v.z *= -0.5; }
      const speed = Math.hypot(b.v.x, b.v.z);                      // roll as it goes
      if (speed > 1e-4) {
        this.axis.set(b.v.z, 0, -b.v.x).normalize();
        b.q.premultiply(this.roll.setFromAxisAngle(this.axis, (speed * dt) / RADIUS));
      }
    }
    for (let i = 0; i < this.balls.length; i++) {                  // knock into each other
      for (let j = i + 1; j < this.balls.length; j++) {
        const a = this.balls[i], b = this.balls[j];
        const dx = b.p.x - a.p.x, dz = b.p.z - a.p.z, dist = Math.hypot(dx, dz);
        if (dist >= RADIUS * 2 || dist < 1e-5) continue;
        const nx = dx / dist, nz = dz / dist, overlap = RADIUS * 2 - dist;
        a.p.x -= nx * overlap / 2; a.p.z -= nz * overlap / 2; b.p.x += nx * overlap / 2; b.p.z += nz * overlap / 2;
        const rel = (b.v.x - a.v.x) * nx + (b.v.z - a.v.z) * nz;
        if (rel < 0) { a.v.x += rel * nx * 0.9; a.v.z += rel * nz * 0.9; b.v.x -= rel * nx * 0.9; b.v.z -= rel * nz * 0.9; }
        moving = true;
      }
    }
    if (moving) this.write();
  }
}

export function createFloorBalloons(areas: FloorBalloonArea[], options: FloorBalloonOptions = {}): FloorBalloons {
  return new FloorBalloons(areas, options);
}
