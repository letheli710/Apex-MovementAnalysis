# hsd_tel report

Inputs: 16 file(s); rows: 17354 (MT 10341, HSD 7011)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3698 teleport in stream ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` message.log:4008 teleport in stream ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` message.log:4312 teleport in stream ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` message.log:4614 teleport in stream ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` message.log:4937 teleport in stream ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` script.log:3322 teleport in stream ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` script.log:3889 teleport in stream ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` script.log:4458 teleport in stream ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` script.log:5027 teleport in stream ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` script.log:5612 teleport in stream ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '010a00a2-e5d7-4fab-93cd-bb455e327ed3')
- warning `W_TELEPORT` message.log:3472 teleport in stream ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_TELEPORT` message.log:3800 teleport in stream ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_TELEPORT` message.log:4100 teleport in stream ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_TELEPORT` message.log:4399 teleport in stream ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_TELEPORT` message.log:4712 teleport in stream ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '16049507-b2e6-4e26-81f4-c505a4f97814')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.35 -> 23.08739 in ('HSD', 'sv', 'evt', 1.0, '16049507-b2e6-4e26-81f4-c505a4f97814')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3091 | 0 | - | - |
| MT | cl | r90 | 120 | 600 | - | - |
| MT | cl | b1 | 171 | 402.08 | - | - |
| MT | cl | r20361 | 120 | 600 | - | - |
| MT | cl | b2 | 172 | 402.085 | - | - |
| MT | cl | r20362 | 119 | 600 | - | - |
| MT | cl | b3 | 173 | 412.506 | - | - |
| MT | cl | r20363 | 118 | 600 | - | linear (yes) |
| MT | cl | b4 | 188 | 0 | - | - |
| MT | cl | r20364 | 120 | 600 | - | - |
| MT | cl | b5 | 172 | 402.059 | - | - |
| MT | cl | r20365 | 120 | 600 | - | - |
| MT | cl | b6 | 173 | 402.055 | - | - |
| MT | cl | r20366 | 120 | 600 | - | - |
| MT | cl | b7 | 136 | 402.068 | - | - |
| HSD | cl | r0 | 4256 | 422.92 | - | linear (yes) |
| HSD | cl | r90 | 385 | 600 | - | - |
| HSD | cl | r20361 | 385 | 600 | - | - |
| HSD | cl | r20362 | 385 | 600 | - | - |
| HSD | cl | r20363 | 385 | 600 | - | linear (yes) |
| HSD | cl | r20364 | 385 | 600 | - | - |
| HSD | cl | r20365 | 385 | 600 | - | - |
| HSD | cl | r20366 | 385 | 600 | - | - |
| MT | sv | b0 | 3113 | 0 | - | - |
| MT | sv | r90 | 120 | 600 | - | - |
| MT | sv | b1 | 171 | 402.08 | - | - |
| MT | sv | r20361 | 120 | 600 | - | - |
| MT | sv | b2 | 172 | 402.085 | - | - |
| MT | sv | r20362 | 119 | 600 | - | - |
| MT | sv | b3 | 173 | 412.506 | - | - |
| MT | sv | r20363 | 118 | 600 | - | linear (yes) |
| MT | sv | b4 | 188 | 0 | - | - |
| MT | sv | r20364 | 120 | 600 | - | - |
| MT | sv | b5 | 172 | 402.059 | - | - |
| MT | sv | r20365 | 120 | 600 | - | - |
| MT | sv | b6 | 173 | 402.055 | - | - |
| MT | sv | r20366 | 120 | 600 | - | - |
| MT | sv | b7 | 131 | 402.068 | - | - |

Events: 58. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
