import * as THREE from "three";
import { NIGHT_BIRDS } from "../config/decor";

/**
 * Now and then, rarely, a night bird or two cross the sky over the garden: dark shapes faintly lit by the moon, slow
 * wingbeats in bouts with glides between, passing in a straight line and gone. Pale, so they show against the night. Each bird is 4 triangles, moved on the
 * CPU only while they fly. Not a light.
 *
 *   const birds = new NightBirds();  scene.add(birds);
 *   useFrame((_, delta) => birds.update(delta));
 */
const B = NIGHT_BIRDS;
const random = (range: readonly [number, number]) => range[0] + Math.random() * (range[1] - range[0]);
const FLOCK = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(-1.4, 0.2, -1.7), new THREE.Vector3(1.5, -0.3, -2.2)];   // behind the leader
const UP = new THREE.Vector3(0, 1, 0);

interface Bird { mesh: THREE.Mesh; positions: THREE.BufferAttribute; beat: number; rate: number }

function makeBird(material: THREE.Material): Bird {
  const geometry = new THREE.BufferGeometry();
  const positions = new THREE.BufferAttribute(new Float32Array(8 * 3), 3);
  geometry.setAttribute("position", positions);
  geometry.setIndex([0, 1, 2, 0, 4, 1, 2, 6, 3, 4, 5, 7]);         // body to elbow, elbow to wingtip; both sides
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return { mesh, positions, beat: Math.random() * 6.28, rate: 9 + Math.random() * 2 };
}

/** Wings at `angle` (radians up): head, tail, then each side's elbow, wingtip and elbow back (forward is +z). */
function shape(bird: Bird, angle: number): void {
  const s = B.span, p = bird.positions;
  const elbowX = 0.24 * s * Math.cos(angle), elbowY = 0.24 * s * Math.sin(angle);
  const tipX = elbowX + 0.26 * s * Math.cos(angle * 1.3), tipY = elbowY + 0.26 * s * Math.sin(angle * 1.3);
  const points = [[0, 0, 0.3], [0, 0, -0.32], [-elbowX, elbowY, 0.06], [-tipX, tipY, -0.12], [elbowX, elbowY, 0.06],
    [tipX, tipY, -0.12], [-elbowX * 0.92, elbowY, -0.1], [elbowX * 0.92, elbowY, -0.1]];
  points.forEach(([x, y, z], i) => p.setXYZ(i, x, y, z * s));
  p.needsUpdate = true;
}

export class NightBirds extends THREE.Group {
  private readonly birds: Bird[];
  private readonly from = new THREE.Vector3();
  private readonly to = new THREE.Vector3();
  private readonly heading = new THREE.Quaternion();
  private readonly at = new THREE.Vector3();
  private wait = random(B.firstWait);
  private time = 0;
  private duration = 0;
  private count = 0;

  constructor() {
    super();
    this.name = "night_birds";
    const material = new THREE.MeshBasicMaterial({ color: B.colour, side: THREE.DoubleSide, fog: false });
    this.birds = FLOCK.map(() => makeBird(material));
    for (const bird of this.birds) { bird.mesh.visible = false; this.add(bird.mesh); }
  }

  update(dt: number): void {
    if (this.duration > 0) return this.fly(dt);
    this.wait -= dt;
    if (this.wait <= 0) this.start();
  }

  /** A straight line across the sky, passing the garden's middle at a distance, from one far side to the other. */
  private start(): void {
    const across = Math.random() * Math.PI * 2, pass = random(B.pass), half = Math.sqrt(B.reach ** 2 - pass ** 2);
    const dir = new THREE.Vector3(Math.cos(across), 0, Math.sin(across)), side = new THREE.Vector3(-dir.z, 0, dir.x);
    const middle = new THREE.Vector3(B.middle[0], 0, B.middle[1]).addScaledVector(side, pass * (Math.random() < 0.5 ? -1 : 1));
    this.from.copy(middle).addScaledVector(dir, -half).setY(random(B.height));
    this.to.copy(middle).addScaledVector(dir, half).setY(random(B.height));
    this.heading.setFromRotationMatrix(new THREE.Matrix4().lookAt(this.to, this.from, UP));
    this.duration = this.from.distanceTo(this.to) / random(B.speed);
    this.time = 0;
    this.count = Math.round(random([B.flock[0] - 0.49, B.flock[1] + 0.49]));
    this.birds.forEach((bird, i) => { bird.mesh.visible = i < this.count; });
  }

  private fly(dt: number): void {
    this.time += dt;
    const t = this.time / this.duration;
    if (t >= 1) {
      this.duration = 0; this.wait = random(B.gap);
      for (const bird of this.birds) bird.mesh.visible = false;
      return;
    }
    const at = this.at.lerpVectors(this.from, this.to, t);
    this.birds.forEach((bird, i) => {
      if (i >= this.count) return;
      bird.beat += dt * bird.rate;
      const flapping = THREE.MathUtils.clamp(0.5 + 1.5 * Math.sin(this.time * 0.7 + i * 1.7), 0, 1);   // bouts, then glides
      shape(bird, 0.08 + flapping * 0.5 * Math.sin(bird.beat));
      bird.mesh.quaternion.copy(this.heading);
      bird.mesh.position.copy(FLOCK[i]).applyQuaternion(this.heading).add(at);
      bird.mesh.position.y -= 0.04 * flapping * Math.sin(bird.beat);   // the body dips as the wings rise
    });
  }
}
