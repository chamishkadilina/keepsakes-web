/** Graybox lighting until the owner's baked lighting arrives (A7/A8). */
const SKY = '#cfd8e3'
const HEMISPHERE = { sky: '#fff6ea', ground: '#8a7d72', intensity: 1.8 }
const SUN = { position: [20, 30, 10] as const, intensity: 1.2 }

export function Lighting() {
  return (
    <>
      <color attach="background" args={[SKY]} />
      <hemisphereLight args={[HEMISPHERE.sky, HEMISPHERE.ground, HEMISPHERE.intensity]} />
      <directionalLight position={SUN.position} intensity={SUN.intensity} />
    </>
  )
}
