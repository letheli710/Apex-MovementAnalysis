# hsd_tel report

Inputs: 16 file(s); rows: 24003 (MT 15589, HSD 8412)

Validation: 0 error(s), 13 warning(s), 6 info

- warning `W_TELEPORT` message.log:3573 teleport in stream ('MT', 'cl', 'cmd', 1, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` message.log:5681 teleport in stream ('MT', 'cl', 'cmd', 1, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` message.log:7795 teleport in stream ('MT', 'cl', 'cmd', 1, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` script.log:3208 teleport in stream ('HSD', 'cl', 'frame', None, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` script.log:4595 teleport in stream ('HSD', 'cl', 'frame', None, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` script.log:6169 teleport in stream ('HSD', 'cl', 'frame', None, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` script.log:7558 teleport in stream ('HSD', 'cl', 'frame', None, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` script.log:9132 teleport in stream ('HSD', 'cl', 'frame', None, 'c8a5d6f2-cddf-42c0-b38d-8ee8ddce1173')
- warning `W_TELEPORT` message.log:3342 teleport in stream ('MT', 'sv', 'cmd', 1, '4a47769b-ff47-4d62-a5d9-770005ac0164')
- warning `W_TELEPORT` message.log:5442 teleport in stream ('MT', 'sv', 'cmd', 1, '4a47769b-ff47-4d62-a5d9-770005ac0164')
- warning `W_TELEPORT` message.log:7533 teleport in stream ('MT', 'sv', 'cmd', 1, '4a47769b-ff47-4d62-a5d9-770005ac0164')
- warning `W_TELEPORT` script.log:774 teleport in stream ('HSD', 'sv', 'evt', 1.0, '4a47769b-ff47-4d62-a5d9-770005ac0164')
- warning `W_TIME_BACKWARDS` script.log:716 t 24.0 -> 23.86246 in ('HSD', 'sv', 'evt', 1.0, '4a47769b-ff47-4d62-a5d9-770005ac0164')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2970 | 0 | - | - |
| MT | cl | r90 | 470 | 0 | - | - |
| MT | cl | b1 | 141 | 0 | - | - |
| MT | cl | b2 | 1474 | 0 | - | - |
| MT | cl | r4422 | 471 | 0 | - | - |
| MT | cl | b3 | 143 | 0 | - | - |
| MT | cl | b4 | 1469 | 0 | - | - |
| MT | cl | r4424 | 470 | 0 | - | - |
| MT | cl | b5 | 128 | 0 | - | - |
| HSD | cl | r0 | 6567 | 1280.02 | linear (no) | - |
| HSD | cl | r90 | 602 | 1280.02 | linear (no) | - |
| HSD | cl | r4422 | 602 | 1280.02 | linear (no) | - |
| HSD | cl | r4424 | 601 | 1280.02 | linear (no) | - |
| MT | sv | b0 | 2983 | 0 | - | - |
| MT | sv | r90 | 472 | 0 | - | - |
| MT | sv | b1 | 123 | 0 | - | - |
| MT | sv | r4421 | 18 | 0 | - | - |
| MT | sv | b2 | 1474 | 0 | - | - |
| MT | sv | r4422 | 476 | 0 | - | - |
| MT | sv | b3 | 124 | 0 | - | - |
| MT | sv | r4423 | 18 | 0 | - | - |
| MT | sv | b4 | 1469 | 0 | - | - |
| MT | sv | r4424 | 469 | 0 | - | - |
| MT | sv | b5 | 124 | 0 | - | - |

Events: 32. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
