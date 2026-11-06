import * as THREE from "three";

/**
 * The screen room's projector beam, like in a film hall: a soft cone of warm light from the ceiling projector's lens
 * (the projector_lens marker in museum.glb) to the corners of the screen (screen_surface), brightest at the lens, with
 * specks of dust drifting slowly through it. Additive light, no real-time lights; 2 draw calls, left out of the floor
 * reflection. Keep it on: it is the screen room's film-hall look, whether the screen shows their photos or a clip.
 *
 *   const beam = createProjectorBeam(gltf.scene);
 *   if (beam) scene.add(beam);
 */
export interface ProjectorBeamOptions {
  strength?: number;                 // brightness of the beam (1 = a soft haze in the dim room)
  color?: THREE.ColorRepresentation; // warm white
  dust?: number;                     // specks of dust in the beam (0 = none)
}

const beamVertex = /* glsl */ `
  varying vec2 vUv;
  varying float vFacing;
  void main() {
    vUv = uv;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vFacing = abs(dot(normalize(normalMatrix * normal), normalize(-mv.xyz)));
    gl_Position = projectionMatrix * mv;
  }`;

const beamFragment = /* glsl */ `
  uniform vec3 color;
  varying vec2 vUv;                                                // x across a side of the beam, y from the lens to the screen
  varying float vFacing;                                           // sides seen edge-on fade, so the cone reads as soft haze
  void main() {
    float edge = smoothstep(0.0, 0.45, vUv.x) * smoothstep(1.0, 0.55, vUv.x);
    float along = mix(1.0, 0.4, sqrt(vUv.y)) * smoothstep(0.0, 0.04, vUv.y);
    gl_FragColor = vec4(color * edge * along * smoothstep(0.03, 0.55, vFacing), 1.0);
  }`;

const dustVertex = /* glsl */ `
  attribute float phase;
  uniform float time;
  uniform float pixelsPerMetre;
  varying float vGlow;
  void main() {
    vec3 p = position + 0.05 * vec3(sin(time * 0.21 + phase * 6.3), sin(time * 0.17 + phase * 9.1), cos(time * 0.19 + phase * 4.7));
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = max(1.0, pixelsPerMetre * 0.01 / -mv.z);
    vGlow = 0.55 + 0.45 * sin(time * 0.7 + phase * 20.0);
  }`;

const dustFragment = /* glsl */ `
  uniform vec3 color;
  varying float vGlow;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    gl_FragColor = vec4(color * vGlow * smoothstep(0.5, 0.1, d), 1.0);
  }`;

/** World corners of a flat mesh (the screen), in order round its edge, moved `lift` metres off its face. */
function corners(mesh: THREE.Mesh, lift: number, towards: THREE.Vector3): THREE.Vector3[] {
  mesh.geometry.computeBoundingBox();
  const { min, max } = mesh.geometry.boundingBox!;
  const size = new THREE.Vector3().subVectors(max, min);
  const flat = size.x < size.y && size.x < size.z ? 0 : size.y < size.z ? 1 : 2;  // the axis the screen is thin along
  const [a, b] = [0, 1, 2].filter((k) => k !== flat);
  const local = [[0, 0], [1, 0], [1, 1], [0, 1]].map(([i, j]) => {
    const v = min.clone().lerp(max, 0.5);
    v.setComponent(a, i ? max.getComponent(a) : min.getComponent(a));
    v.setComponent(b, j ? max.getComponent(b) : min.getComponent(b));
    return v.applyMatrix4(mesh.matrixWorld);
  });
  const middle = local.reduce((m, v) => m.add(v), new THREE.Vector3()).multiplyScalar(0.25);
  const off = towards.clone().sub(middle).normalize().multiplyScalar(lift);
  return local.map((v) => v.add(off));
}

export function createProjectorBeam(root: THREE.Object3D, { strength = 1, color = 0xffe9cc, dust = 160 }: ProjectorBeamOptions = {}): THREE.Group | null {
  root.updateMatrixWorld(true);
  const lensMarker = root.getObjectByName("projector_lens"), screen = root.getObjectByName("screen_surface") as THREE.Mesh | undefined;
  if (!lensMarker || !screen?.isMesh) {
    console.error("createProjectorBeam: no projector_lens or screen_surface in the model");
    return null;
  }
  const lens = lensMarker.getWorldPosition(new THREE.Vector3());
  const far = corners(screen, 0.02, lens);
  const middle = far.reduce((m, v) => m.clone().add(v), new THREE.Vector3()).multiplyScalar(0.25);
  const near = far.map((v) => lens.clone().add(v.clone().sub(middle).multiplyScalar(0.012)));   // the lens's small window

  const positions: number[] = [], uvs: number[] = [];
  for (let i = 0; i < 4; i++) {                                    // four sides, each a strip from the lens to the screen
    const j = (i + 1) % 4;
    for (const [v, u, t] of [[near[i], 0, 0], [near[j], 1, 0], [far[j], 1, 1], [near[i], 0, 0], [far[j], 1, 1], [far[i], 0, 1]] as const) {
      positions.push(v.x, v.y, v.z);
      uvs.push(u, t);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geometry.computeVertexNormals();                                 // flat: every side has its own vertices
  const tint = new THREE.Color(color).multiplyScalar(0.2 * strength);
  const additive = { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false };
  const beam = new THREE.Mesh(geometry, new THREE.ShaderMaterial({
    vertexShader: beamVertex, fragmentShader: beamFragment, uniforms: { color: { value: tint } }, side: THREE.DoubleSide, ...additive,
  }));
  beam.name = "projector_beam";
  beam.frustumCulled = false;
  beam.renderOrder = 2;
  beam.userData.noReflection = true;
  const group = new THREE.Group();
  group.name = "projector";
  group.add(beam);

  if (dust > 0) {                                                  // specks of dust drifting through the light
    const points: number[] = [], phases: number[] = [];
    for (let k = 0; k < dust; k++) {
      const t = 0.08 + 0.9 * Math.random() ** 0.7, s = 0.12 + 0.76 * Math.random(), r = 0.12 + 0.76 * Math.random();
      const across = (q: THREE.Vector3[]) => q[0].clone().lerp(q[1], s).lerp(q[3].clone().lerp(q[2], s), r);
      const p = across(near).lerp(across(far), t);
      points.push(p.x, p.y, p.z);
      phases.push(Math.random());
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(points, 3));
    g.setAttribute("phase", new THREE.Float32BufferAttribute(phases, 1));
    const uniforms = { color: { value: new THREE.Color(color).multiplyScalar(0.5 * strength) }, time: { value: 0 }, pixelsPerMetre: { value: 800 } };
    const specks = new THREE.Points(g, new THREE.ShaderMaterial({ vertexShader: dustVertex, fragmentShader: dustFragment, uniforms, ...additive }));
    specks.name = "projector_dust";
    specks.frustumCulled = false;
    specks.renderOrder = 2;
    specks.userData.noReflection = true;
    const size = new THREE.Vector2();
    specks.onBeforeRender = (renderer, _scene, camera) => {
      uniforms.time.value = performance.now() / 1000;
      uniforms.pixelsPerMetre.value = renderer.getDrawingBufferSize(size).y * camera.projectionMatrix.elements[5] / 2;
    };
    group.add(specks);
  }
  return group;
}
