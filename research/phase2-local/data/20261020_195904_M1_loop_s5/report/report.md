# hsd_tel report

Inputs: 16 file(s); rows: 32613 (MT 21725, HSD 10886)

Validation: 0 error(s), 17 warning(s), 2 info

- warning `W_TELEPORT` message.log:4320 teleport in stream ('MT', 'cl', 'cmd', 1, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` message.log:5754 teleport in stream ('MT', 'cl', 'cmd', 1, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` message.log:7184 teleport in stream ('MT', 'cl', 'cmd', 1, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` message.log:8614 teleport in stream ('MT', 'cl', 'cmd', 1, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` message.log:10042 teleport in stream ('MT', 'cl', 'cmd', 1, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` script.log:4005 teleport in stream ('HSD', 'cl', 'frame', None, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` script.log:5441 teleport in stream ('HSD', 'cl', 'frame', None, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` script.log:6877 teleport in stream ('HSD', 'cl', 'frame', None, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` script.log:8313 teleport in stream ('HSD', 'cl', 'frame', None, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` script.log:9749 teleport in stream ('HSD', 'cl', 'frame', None, '9f7646d7-618b-4436-99ee-eb9d8935bbba')
- warning `W_TELEPORT` message.log:4134 teleport in stream ('MT', 'sv', 'cmd', 1, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TELEPORT` message.log:5559 teleport in stream ('MT', 'sv', 'cmd', 1, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TELEPORT` message.log:6984 teleport in stream ('MT', 'sv', 'cmd', 1, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TELEPORT` message.log:8410 teleport in stream ('MT', 'sv', 'cmd', 1, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TELEPORT` message.log:9836 teleport in stream ('MT', 'sv', 'cmd', 1, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TELEPORT` script.log:730 teleport in stream ('HSD', 'sv', 'evt', 1.0, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.7 -> 23.50885 in ('HSD', 'sv', 'evt', 1.0, '15d81c3d-f850-4f3c-bc35-6bdc6d60a70a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3205 | 0 | - | - |
| MT | cl | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r31 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r32 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r33 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r34 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r35 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3185 | 0 | - | - |
| HSD | cl | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r31 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r32 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r33 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r34 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r35 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3214 | 0 | - | - |
| MT | sv | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r31 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r32 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r33 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r34 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r35 | 1274 | 199.525 | first_order (yes) | linear (yes) |

Events: 68. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
