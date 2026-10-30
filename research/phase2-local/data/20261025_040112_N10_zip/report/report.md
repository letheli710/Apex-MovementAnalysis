# hsd_tel report

Inputs: 16 file(s); rows: 16855 (MT 10063, HSD 6732)

Validation: 0 error(s), 19 warning(s), 28 info

- warning `W_TELEPORT` message.log:3916 teleport in stream ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` message.log:4225 teleport in stream ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` message.log:4526 teleport in stream ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` message.log:4829 teleport in stream ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` message.log:5138 teleport in stream ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` script.log:3568 teleport in stream ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` script.log:4133 teleport in stream ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` script.log:4702 teleport in stream ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` script.log:5271 teleport in stream ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` script.log:5841 teleport in stream ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '36297ac7-9b4b-470b-8f85-cb9c6decca6e')
- warning `W_TELEPORT` message.log:3653 teleport in stream ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_TELEPORT` message.log:3977 teleport in stream ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_TELEPORT` message.log:4277 teleport in stream ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_TELEPORT` message.log:4577 teleport in stream ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_TELEPORT` message.log:4876 teleport in stream ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '2c5a8270-50a9-4a2d-81af-07b40268af92')
- warning `W_TIME_BACKWARDS` script.log:718 t 26.35 -> 26.17659 in ('HSD', 'sv', 'evt', 1.0, '2c5a8270-50a9-4a2d-81af-07b40268af92')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3281 | 0 | - | - |
| MT | cl | r90 | 120 | 600 | - | - |
| MT | cl | b1 | 169 | 401.268 | - | - |
| MT | cl | r24101 | 119 | 600 | - | - |
| MT | cl | b2 | 172 | 412.481 | - | - |
| MT | cl | r24102 | 120 | 600 | - | - |
| MT | cl | b3 | 173 | 402.078 | - | - |
| MT | cl | r24103 | 120 | 600 | - | - |
| MT | cl | b4 | 173 | 401.233 | - | - |
| MT | cl | r24104 | 120 | 600 | - | - |
| MT | cl | b5 | 172 | 400.509 | - | - |
| MT | cl | r24105 | 120 | 600 | - | - |
| MT | cl | b6 | 134 | 401.706 | - | - |
| HSD | cl | r0 | 4252 | 422.898 | - | linear (yes) |
| HSD | cl | r90 | 385 | 600 | - | - |
| HSD | cl | r24101 | 385 | 600 | - | - |
| HSD | cl | r24102 | 385 | 600 | - | - |
| HSD | cl | r24103 | 385 | 600 | - | - |
| HSD | cl | r24104 | 385 | 600 | - | - |
| HSD | cl | r24105 | 385 | 600 | - | - |
| MT | sv | b0 | 3297 | 0 | - | - |
| MT | sv | r90 | 120 | 600 | - | - |
| MT | sv | b1 | 169 | 401.268 | - | - |
| MT | sv | r24101 | 119 | 600 | - | - |
| MT | sv | b2 | 172 | 412.481 | - | - |
| MT | sv | r24102 | 120 | 600 | - | - |
| MT | sv | b3 | 173 | 402.078 | - | - |
| MT | sv | r24103 | 120 | 600 | - | - |
| MT | sv | b4 | 173 | 401.233 | - | - |
| MT | sv | r24104 | 120 | 600 | - | - |
| MT | sv | b5 | 172 | 400.509 | - | - |
| MT | sv | r24105 | 120 | 600 | - | - |
| MT | sv | b6 | 131 | 401.706 | - | - |

Events: 50. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
