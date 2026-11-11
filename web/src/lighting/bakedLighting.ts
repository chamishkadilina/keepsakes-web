import * as THREE from "three";
import { createBulbMatcap, createFoilMatcap, createGlassMaterial, createGoldMaterial, createSatinBlackMatcap, createSoftMatcap, createVelvetMatcap } from "./matcaps";
import { createSheerMaterial } from "./sheerMaterial";

/**
 * Applies the museum's baked lighting (tested against design/web-reference/*.png).
 * Also hides the photo-slot placeholders (slot_*, collage_board): they only mark where the frames go.
 * Furniture, exhibits and decor (prop_<zone>_<material>) carry their light in their vertices: velvet (sofas, cushions,
 * curtains, the cinema's stage) and gold get their sheen, the heart balloons their foil shine, rugs and marble keep
 * their texture, roses, leaves and curtains show both sides; the projector is satin white and black with a softly
 * glowing lens, the cinema screen softly lit white in its black frame, the bulbs of the light strings glow bright gold;
 * the foyer's sheers are see-through ivory voile (the little lights behind them, createCurtainLights, glow through);
 * glass only adds its reflections; the neon sign's words are hidden until createNeonSign writes them. The lightmaps'
 * intensity is kept in root.userData.lightmapIntensity (used by the title wall and the quote board).
 * No real-time lights: the look is identical on every device and costs almost nothing.
 *
 *   final colour = albedo × baked light × intensity
 *
 * three.js lightmap shaders divide by PI, so lightMapIntensity = intensity × PI.
 */
interface LightmapManifest {
  intensity: number;
  maps: Record<string, { file: string }>;
}

const TRIM = ["skirting", "crown_moulding", "door_jambs", "cove_"];
const GOLD = ["gold_trim", "brass_soft"];
const VELVET = ["velvet_rose", "velvet_cream", "rose_petal", "rose_blush", "curtain_velvet"];   // sofas, cushions, roses, curtains
const DOUBLE_SIDED = ["rose_petal", "rose_blush", "rose_leaf", "olive_leaf", "fig_leaf", "ficus_leaf", "velvet_cream", "curtain_velvet"];   // single surfaces
const VELVET_GAIN = 1.35;                            // velvet: ~0.75 of its colour where it faces you, brighter at its edges
const GOLD_GAIN = 2.0;                               // gold matcap × baked light: like the lamp trims in a lit room
const FOIL_GAIN = 1.5;                               // foil matcap × balloon colour × baked light
const SCREEN_WHITE = 0.88;                           // the cinema screen, as if the projector were on it

/** Lightmap group from the object's name (used if the glb was exported without custom properties). */
function groupFromName(name: string): string | null {
  if (name === "walls" || name === "partition_cap") return "walls";
  if (name.startsWith("floor_")) return "floors";
  if (name.startsWith("ceiling_")) return "ceilings";
  if (name === "garden_walls") return "garden_walls";
  return null;
}

export async function applyBakedLighting(root: THREE.Object3D, lightmapsUrl: string, anisotropy = 4): Promise<void> {
  const manifest: LightmapManifest = await (await fetch(`${lightmapsUrl}/lightmaps.json`)).json();
  const loader = new THREE.TextureLoader();
  const maps: Record<string, THREE.Texture> = {};
  await Promise.all(
    Object.entries(manifest.maps).map(async ([group, info]) => {
      const t = await loader.loadAsync(`${lightmapsUrl}/${info.file}`);
      t.flipY = false;                 // glTF UV convention
      t.channel = 1;                   // TEXCOORD_1 = lightmap UV
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = anisotropy;
      maps[group] = t;
    }),
  );

  const lightmapIntensity = manifest.intensity * Math.PI;
  const gold = createGoldMaterial();
  const glass = createGlassMaterial();
  const glow = new THREE.MeshBasicMaterial({ color: 0xfff0d8, toneMapped: false });
  glow.name = "lens_glow";                                    // stays bright when the cinema dims (cinemaLights.ts)
  const bulbs = new THREE.MeshMatcapMaterial({ matcap: createBulbMatcap(), toneMapped: false });
  const sheer = createSheerMaterial();
  const screen = new THREE.MeshBasicMaterial({ color: new THREE.Color(SCREEN_WHITE, SCREEN_WHITE, SCREEN_WHITE * 0.98) });
  const vertexLit = new Map<THREE.Material, THREE.Material>();
  /** Material for a surface whose light is baked into its vertices: velvet and gold keep their sheen, the rest is matte
   *  (with its texture, if it has one). */
  const litByVertex = (old: THREE.MeshStandardMaterial) => {
    if (!vertexLit.has(old)) {
      const color = old.color.clone().multiplyScalar(manifest.intensity);
      const side = DOUBLE_SIDED.includes(old.name) ? THREE.DoubleSide : THREE.FrontSide;
      if (old.map) { old.map.anisotropy = anisotropy; old.map.colorSpace = THREE.SRGBColorSpace; }
      const m = VELVET.includes(old.name)
        ? new THREE.MeshMatcapMaterial({ matcap: createVelvetMatcap(), color: color.multiplyScalar(VELVET_GAIN), vertexColors: true, side })
        : old.name === "gold_metal"
          ? createGoldMaterial({ color: new THREE.Color(0xf2dfc0).multiplyScalar(manifest.intensity * GOLD_GAIN), vertexColors: true })
          : old.name === "balloon_foil"
            ? new THREE.MeshMatcapMaterial({ matcap: createFoilMatcap(), map: old.map ?? null, color: color.multiplyScalar(FOIL_GAIN), vertexColors: true })
          : old.name === "projector_black"                 // the projector shows its shape in its own shading, even in the dim room
            ? new THREE.MeshMatcapMaterial({ matcap: createSatinBlackMatcap(), toneMapped: false })
          : old.name === "projector_white"
            ? new THREE.MeshMatcapMaterial({ matcap: createSoftMatcap(), color: new THREE.Color(0.86, 0.85, 0.83) })
            : new THREE.MeshBasicMaterial({ color, map: old.map ?? null, vertexColors: true, side });
      m.name = old.name;
      vertexLit.set(old, m);
    }
    return vertexLit.get(old)!;
  };
  root.userData.lightmapIntensity = manifest.intensity;
  const lights: THREE.Object3D[] = [];
  let lit = 0;

  root.traverse((object) => {
    if ((object as THREE.Light).isLight) { lights.push(object); return; }
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const old = mesh.material as THREE.MeshStandardMaterial;
    const data = mesh.userData;
    if (old.name?.endsWith("_placeholder")) { mesh.visible = false; return; }   // photo slots and the dark collage board: positions only
    if (old.name === "neon_text") { mesh.visible = false; return; }             // the neon's words: createNeonSign (neonSign.ts)

    const group: string | null = data.lightmap_group ?? groupFromName(mesh.name);
    if (group && maps[group]) {
      // walls, floors, ceilings: albedo texture × lightmap
      if (old.map) { old.map.anisotropy = anisotropy; old.map.colorSpace = THREE.SRGBColorSpace; }
      mesh.material = new THREE.MeshBasicMaterial({
        map: old.map ?? null, color: old.color, lightMap: maps[group], lightMapIntensity: lightmapIntensity,
      });
      lit++;
    } else if (data.light_vertex || (TRIM.some((t) => mesh.name.startsWith(t)) && mesh.geometry.attributes.color)) {
      // thin mouldings, tray cornices, collage niche, gold lines, furniture, exhibits, decor: light baked into vertex colours (COLOR_0)
      mesh.material = litByVertex(old);
      lit++;
    } else if (old.name === "glass") {
      mesh.material = glass;                                  // lanterns, the neon's acrylic panel
    } else if (GOLD.includes(old.name)) {
      mesh.material = gold;                                   // gold and brass without baked light (lamp fittings)
    } else if (old.name === "bulb_glow") {
      mesh.material = bulbs;                                  // the light strings' bulbs: bright gold
    } else if (old.name === "sheer_ivory") {
      mesh.material = sheer;                                  // the foyer's sheers, drawn after the little lights behind them
      mesh.renderOrder = -1;                                  // (curtainLights.ts) and before all else see-through
    } else if (old.name === "screen_white") {
      mesh.material = screen;                                 // the cinema screen (their video plays just in front of it)
    } else if (old.name === "led_glow" || old.name === "lens_glow") {
      mesh.material = glow;                                   // spot lenses, niche LEDs, the projector's lens
    } else if (old.isMeshStandardMaterial) {
      // everything else (track rails and heads): shaded in its own colour, never black
      mesh.material = new THREE.MeshMatcapMaterial({ matcap: createSoftMatcap(), color: old.color });
    }
  });
  lights.forEach((light) => light.removeFromParent());
  if (lit === 0) console.error("applyBakedLighting: no surface received baked light. Check the museum.glb and lightmaps path.");
}
