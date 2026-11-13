# Route — The Museum of Us

One direction from the entrance to the garden. Positions in metres (x east, y north), from `museum.blend`. Doorways are 3 m wide and full wall height; no windows anywhere.

| # | From → to | Door | Position |
|---|---|---|---|
| 0 | Outside → Foyer | `door_01` Entrance | foyer south wall y = 0, x 4–7 |
| 1 | Foyer → Story gallery | `door_02` | y = 10, x 7.9–10.9 |
| 2 | Story gallery → Heart room | `door_03` | x = 11, y 10.5–13.5 |
| 3 | Heart room → Right gallery | `door_04` | x = 23, y 10.5–13.5 |
| 4 | Right gallery → Screen room | `door_05` | x = 26.5, y 1.7–4.7 |
| 5 | Screen room → Garden | `door_06` Arch (the only arched door) | x = 38, y 5–8 |

## The walk

0. **Entrance clearing** (x −4–16, y −14–0, in a little wood): they start side by side on the red carpet in front of the open entrance doors (`spawn_her` 5.0, −3.2; `spawn_him` 6.0, −3.2).
1. **Foyer:** enter from the south. Welcome wall ahead. Door to the story gallery in the north-east corner.
2. **Story gallery:** walk around the freestanding partition (x = 5.5, y 13.15–17.35). Framed photos on both sides. Leave east into the heart room.
3. **Heart room:** the big tall room. The collage board (first 12 photos, polaroid style) on the north wall, glowing as you enter. Framed photos on the side walls. Leave east.
4. **Right gallery:** the north wing runs east to the end wall and back (a small loop), then go down the narrow west strip.
5. **Screen room:** dark and cosy. Slideshow on `screen_surface` (north wall), bench with `seat_screen_1/2`. The arch on the east wall glows.
6. **Garden:** empty for now; later twilight, roses, stone path, the centrepiece photo on the easel (`slot_centrepiece`, optional), a bench for two (`seat_garden_1/2`). The end.

## Wayfinding rule

The next door is always the brightest thing in the room. Petal trail (`path_*`) on the floor along this route.

## Photo slots along the route

`slot_frame_01…43` are numbered in this walking order (foyer → story gallery → heart room → right gallery → screen room). Within a priority, photos fill frames in this order. Priority 1 frames are the big hero frames.
