import * as THREE from "three";
import { LIGHTING } from "../config/lighting";

/**
 * Leaf cards cut out by their texture's alpha (alpha MASK) keep their leaves at a distance. Far away the GPU reads
 * smaller, averaged copies of the texture (mipmaps), whose alpha drops below the cut-off, so a whole tree would fade
 * to bare branches. Here the alpha is raised by how small the texture is drawn, so a leaf covers about as much at any
 * distance (the usual game fix for alpha-tested foliage).
 *
 *   keepLeavesAtDistance(material);   // a MeshBasicMaterial with a map and alphaTest > 0
 */
export function keepLeavesAtDistance(material: THREE.MeshBasicMaterial): void {
  const key = material.customProgramCacheKey();
  const before = material.onBeforeCompile.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    before(shader, renderer);
    shader.fragmentShader = shader.fragmentShader.replace("#include <alphatest_fragment>", `
      #ifdef USE_MAP
        vec2 texel = vMapUv * vec2(textureSize(map, 0));
        float level = max(0.0, 0.5 * log2(max(dot(dFdx(texel), dFdx(texel)), dot(dFdy(texel), dFdy(texel)))));
        diffuseColor.a *= 1.0 + level * ${LIGHTING.foliageMipScale.toFixed(2)};
      #endif
      #include <alphatest_fragment>`);
  };
  material.customProgramCacheKey = () => `${key}|leaves`;
  material.needsUpdate = true;
}
