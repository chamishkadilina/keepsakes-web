# Game feel — how walking in the museum must feel

The couple should never think about controls. Moving feels calm, soft and effortless, like a slow walk together. Feel references: *Journey*, *Sky: Children of the Light*.

Every value below is a starting point. Tune it on a real phone and update this file with the final values.

## 1. Movement

| What | Value |
|---|---|
| Walk / run speed | Keep current values (owner approved) |
| Speed up to full | 0.25 s, eased (no instant start) |
| Slow down to stop | 0.2 s, eased (no sliding, no instant stop) |
| Direction | Relative to the camera (forward = where the camera looks) |
| Character turning | Smoothly turns to face the movement direction, ~0.12 s; never snaps, even for a 180° turn |
| Joystick | Analog: a small push walks slowly, a full push walks at full speed |
| Ground | Stays glued to the floor; no bouncing, no sliding on edges; steps up to 0.2 m |
| Walls | Slides smoothly along walls, never sticks or shakes |

## 2. Camera

| What | Value |
|---|---|
| Type | Spring arm behind the player, pivot at head height (1.5 m) |
| Distance | 3.2 m walking, 3.6 m running (eased over 0.4 s) |
| Pitch | Default 12° down; limits 35° down to 10° up |
| Follow | Position damping ~0.15 s; rotation lag ~0.2 s. Frame-rate independent: `1 - exp(-k·dt)` |
| Look-ahead | 0.4 m toward where the player is moving |
| Auto recentre | After 1.5 s of moving without touching the look control, swing slowly behind the player (0.6 s) |
| Field of view | 55° walking, 58° running (eased 0.4 s) |
| Walls | Sphere cast (radius 0.25 m) that ignores the player. Moves in fast (0.05 s), out slowly (0.4 s). Never shows the inside of a wall. |
| Too close | Below 1 m from the player, fade the player out smoothly |
| Follows | The interpolated visual position of the player, updated after the physics step |

## 3. Controls

**Phone**
- Floating joystick: touch anywhere on the left half; it appears under the thumb. 10% deadzone. Fades in and out softly.
- Look: drag on the right half. Smooth, with slight inertia. Same feel on every screen size.
- No buttons in the way of the photos. Big touch targets (≥ 44 px).

**Desktop**
- WASD or arrows to move, Shift to run.
- Mouse drag to look (or click to lock the pointer, Esc to release).

## 4. Moments (added in B2/B3)

- **Entering a room:** the camera eases back 0.3 m for 1 s to reveal the space.
- **Near a photo** (within 2.5 m and facing it): walking slows gently and the camera eases to frame the photo nicely. Moving away releases it.
- **Garden arch:** walking slows slightly and the camera rises a little as the garden opens up.
- **Sitting on a bench:** the camera moves smoothly to a fixed, beautiful view (no controls needed).

## 5. Quality bar (must pass on Mac 120 Hz and on a real phone)

| Check | Pass |
|---|---|
| Jitter score (`?debug`) | < 0.3 px, green the whole walk |
| Hitches (frames > 25 ms) | Almost none; none while walking straight |
| Frame rate | 60 fps desktop; steady ≥ 30 fps on a mid-range phone, 60 where possible |
| Camera through walls | Never |
| Testers | Nobody mentions the controls or the camera |
