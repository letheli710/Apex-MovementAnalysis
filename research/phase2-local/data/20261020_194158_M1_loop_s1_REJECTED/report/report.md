# hsd_tel report

Inputs: 22 file(s); rows: 248944 (MT 165967, HSD 82977)

Validation: 0 error(s), 18 warning(s), 2 info

- warning `W_TELEPORT` message.1.log:35566 teleport in stream ('MT', 'cl', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:36860 teleport in stream ('MT', 'cl', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:38152 teleport in stream ('MT', 'cl', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:39447 teleport in stream ('MT', 'cl', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:40746 teleport in stream ('MT', 'cl', 'cmd', 1)
- warning `W_TELEPORT` script.log:6474 teleport in stream ('HSD', 'cl', 'frame', None)
- warning `W_TELEPORT` script.log:7770 teleport in stream ('HSD', 'cl', 'frame', None)
- warning `W_TELEPORT` script.log:9063 teleport in stream ('HSD', 'cl', 'frame', None)
- warning `W_TELEPORT` script.log:10360 teleport in stream ('HSD', 'cl', 'frame', None)
- warning `W_TELEPORT` script.log:11660 teleport in stream ('HSD', 'cl', 'frame', None)
- warning `W_TELEPORT` message.1.log:35439 teleport in stream ('MT', 'sv', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:36717 teleport in stream ('MT', 'sv', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:37994 teleport in stream ('MT', 'sv', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:39273 teleport in stream ('MT', 'sv', 'cmd', 1)
- warning `W_TELEPORT` message.1.log:40555 teleport in stream ('MT', 'sv', 'cmd', 1)
- warning `W_TELEPORT` script.log:732 teleport in stream ('HSD', 'sv', 'evt', 1.0)
- warning `W_TELEPORT` script.log:738 teleport in stream ('HSD', 'sv', 'evt', 1.0)
- warning `W_TIME_BACKWARDS` script.log:715 t 25.4 -> 25.08519 in ('HSD', 'sv', 'evt', 1.0)

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 75384 | 0 | - | - |
| MT | cl | r90 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r11 | 1259 | 199.525 | - | - |
| MT | cl | r12 | 1257 | 199.525 | - | - |
| MT | cl | r13 | 1260 | 199.525 | - | - |
| MT | cl | r14 | 1261 | 199.525 | - | - |
| MT | cl | r15 | 1260 | 199.525 | - | - |
| HSD | cl | r0 | 75349 | 0 | - | - |
| HSD | cl | r90 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r11 | 1259 | 199.525 | - | - |
| HSD | cl | r12 | 1257 | 199.525 | - | - |
| HSD | cl | r13 | 1260 | 199.525 | - | - |
| HSD | cl | r14 | 1261 | 199.525 | - | - |
| HSD | cl | r15 | 1260 | 199.525 | - | - |
| MT | sv | b0 | 75409 | 0 | - | - |
| MT | sv | r90 | 1273 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r11 | 1260 | 199.525 | - | - |
| MT | sv | r12 | 1259 | 199.525 | - | - |
| MT | sv | r13 | 1260 | 199.525 | - | - |
| MT | sv | r14 | 1262 | 199.525 | - | - |
| MT | sv | r15 | 1261 | 199.525 | - | - |

Events: 68. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
