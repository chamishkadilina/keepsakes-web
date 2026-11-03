import * as THREE from "three";
import { createGoldMaterial, createSoftMatcap } from "./matcaps";

/**
 * Applies the museum's baked lighting (tested against design/web-reference/*.png).
 * Also hides the photo-slot placeholders (slot_*, collage_board): they only mark where the frames go.
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
  const glow = new THREE.MeshBasicMaterial({ color: 0xfff0d8, toneMapped: false });
  const lights: THREE.Object3D[] = [];
  let lit = 0;

  root.traverse((object) => {
    if ((object as THREE.Light).isLight) { lights.push(object); return; }
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const old = mesh.material as THREE.MeshStandardMaterial;
    const data = mesh.userData;
    if (old.name?.endsWith("_placeholder")) { mesh.visible = false; return; }   // photo slots and the dark collage board: positions only

    const group: string | null = data.lightmap_group ?? groupFromName(mesh.name);
    if (group && maps[group]) {
      // walls, floors, ceilings: albedo texture × lightmap
      if (old.map) { old.map.anisotropy = anisotropy; old.map.colorSpace = THREE.SRGBColorSpace; }
      mesh.material = new THREE.MeshBasicMaterial({
        map: old.map ?? null, color: old.color, lightMap: maps[group], lightMapIntensity: lightmapIntensity,
      });
      lit++;
    } else if (data.light_vertex || (TRIM.some((t) => mesh.name.startsWith(t)) && mesh.geometry.attributes.color)) {
      // thin mouldings, tray cornices, collage niche, gold lines: light baked into vertex colours (COLOR_0)
      mesh.material = new THREE.MeshBasicMaterial({ color: old.color.clone().multiplyScalar(manifest.intensity), vertexColors: true });
      lit++;
    } else if (GOLD.includes(old.name)) {
      mesh.material = gold;                                   // gold and brass without baked light (lamp fittings)
    } else if (old.name === "led_glow") {
      mesh.material = glow;                                   // spot lenses, collage niche LED strips
    } else if (old.isMeshStandardMaterial) {
      // everything else (track rails and heads): shaded in its own colour, never black
      mesh.material = new THREE.MeshMatcapMaterial({ matcap: createSoftMatcap(), color: old.color });
    }
  });
  lights.forEach((light) => light.removeFromParent());
  if (lit === 0) console.error("applyBakedLighting: no surface received baked light. Check the museum.glb and lightmaps path.");
}
