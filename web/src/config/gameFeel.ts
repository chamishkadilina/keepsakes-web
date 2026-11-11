/**
 * Every tuning value for how walking feels. Mirrors design/game-feel.md;
 * change values here (and in that file), nowhere else.
 * Times are "seconds to reach ~95% of the way".
 */
const DEG = Math.PI / 180

/** §1 Movement */
export const MOVEMENT = {
  walkSpeed: 2.2, // m/s (owner approved)
  runSpeed: 4.0, // m/s, Shift (owner approved)
  speedUpTime: 0.25, // s, eased in and out
  slowDownTime: 0.2, // s, eased, no sliding
  stopBelowSpeed: 0.02, // m/s: snap to a stop under this when there is no input
  turnTime: 0.12, // s to face the movement direction
  runMinPush: 0.5, // joystick push needed for Shift-run to count as running
  stepHeight: 0.2, // m
  stepMinWidth: 0.15, // m of free floor needed on top of a step
  maxSlope: 50 * DEG,
  groundSnap: 0.3, // m: stick to a floor up to this far below
  skin: 0.02, // m gap kept between capsule and world (controller offset)
  gravity: 20, // m/s²
  maxFallSpeed: 30, // m/s
  fallResetHeight: -10, // m: below this, back to the entrance
}

/** Collision capsule; her character (girl.glb) stands in it. */
export const PLAYER = {
  radius: 0.3, // m
  halfHeight: 0.6, // m: total height = 2 × (0.6 + 0.3) = 1.8 m
}

/** §2 Camera */
export const CAMERA = {
  pivotHeight: 1.5, // m above the feet
  armWalk: 3.2, // m
  armRun: 3.6, // m
  armTime: 0.4, // s
  followTime: 0.15, // s position damping
  rotationLagTime: 0.2, // s
  lookAhead: 0.4, // m toward where the player is moving
  movingAbove: 0.3, // m/s: slower than this counts as standing still
  recentreAfter: 1.5, // s of moving without touching look
  recentreTime: 0.6, // s
  recentreMaxAngle: 135 * DEG, // don't swing round when walking toward the camera
  pitchDefault: 12 * DEG, // down
  pitchMaxDown: 35 * DEG,
  pitchMaxUp: 10 * DEG,
  fovWalk: 55, // degrees, landscape
  fovRun: 58,
  fovTime: 0.4, // s
  portraitKeepWidth: 60, // degrees of horizontal view kept on portrait phones…
  portraitMaxFov: 82, // …up to this vertical FOV (plus the run boost)
  near: 0.05, // m
  far: 200, // m
  wallProbeRadius: 0.35, // m sphere cast, ignores the player
  wallInTime: 0.15, // s
  wallOutTime: 0.4, // s
  wallMinArm: 0.3, // m
  wallSafeOvershoot: 0.2, // m past the probe contact (probe radius − 0.15 m margin)
  fadeStart: 1.0, // m: player starts fading when the camera is closer
  fadeEnd: 0.5, // m: fully transparent
  fadeTime: 0.3, // s
}

/** §3 Controls */
export const CONTROLS = {
  joystickRadius: 50, // px
  joystickDeadzone: 0.1,
  touchTurnPerShortSide: 2.8, // rad for a swipe across the screen's short side
  mouseDragLook: 0.004, // rad per px
  pointerLockLook: 0.0025, // rad per px
  clickSlop: 4, // px: a mouse press that moves less is a click (locks the pointer)
  swipeSmoothingTime: 0.12, // s, smooths swipe speed for inertia
  inertiaTime: 0.5, // s for look inertia to die out
  inertiaStopAfterHold: 60, // ms: a finger held still this long before lifting doesn't fling
}

/** Physics loop */
export const PHYSICS = {
  timeStep: 1 / 60, // s
  maxDelta: 1 / 30, // s, clamp for movement and camera
}
