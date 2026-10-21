# hsd_tel report

Inputs: 16 file(s); rows: 21549 (MT 14346, HSD 7201)

Validation: 0 error(s), 14 warning(s), 2 info

- warning `W_TELEPORT` message.log:2061 teleport in stream ('MT', 'cl', 'cmd', 1, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` message.log:3491 teleport in stream ('MT', 'cl', 'cmd', 1, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` message.log:4921 teleport in stream ('MT', 'cl', 'cmd', 1, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` message.log:6348 teleport in stream ('MT', 'cl', 'cmd', 1, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` script.log:1755 teleport in stream ('HSD', 'cl', 'frame', None, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` script.log:3191 teleport in stream ('HSD', 'cl', 'frame', None, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` script.log:4627 teleport in stream ('HSD', 'cl', 'frame', None, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` script.log:6062 teleport in stream ('HSD', 'cl', 'frame', None, '80000223-56fc-410f-ae0a-1bddf8c17bf2')
- warning `W_TELEPORT` message.log:1875 teleport in stream ('MT', 'sv', 'cmd', 1, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')
- warning `W_TELEPORT` message.log:3300 teleport in stream ('MT', 'sv', 'cmd', 1, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')
- warning `W_TELEPORT` message.log:4725 teleport in stream ('MT', 'sv', 'cmd', 1, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')
- warning `W_TELEPORT` message.log:6150 teleport in stream ('MT', 'sv', 'cmd', 1, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')
- warning `W_TELEPORT` script.log:730 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.25 -> 25.06652 in ('HSD', 'sv', 'evt', 1.0, 'b0603bb1-e943-4621-a8b4-4996b42c65b0')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 778 | 0 | - | - |
| MT | cl | r21 | 1287 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r22 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r23 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r24 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r25 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 771 | 0 | - | - |
| HSD | cl | r21 | 1287 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r22 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r23 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r24 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r25 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 789 | 0 | - | - |
| MT | sv | r21 | 1287 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r22 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r23 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r24 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r25 | 1273 | 199.525 | first_order (yes) | linear (yes) |

Events: 57. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
