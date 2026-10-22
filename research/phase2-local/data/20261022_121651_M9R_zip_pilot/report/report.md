# hsd_tel report

Inputs: 16 file(s); rows: 26769 (MT 16226, HSD 10541)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3705 teleport in stream ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` message.log:4099 teleport in stream ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` message.log:4489 teleport in stream ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` message.log:4878 teleport in stream ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` message.log:5270 teleport in stream ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_MORE` message.log:0 8 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` script.log:3331 teleport in stream ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` script.log:4255 teleport in stream ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` script.log:5183 teleport in stream ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` script.log:6110 teleport in stream ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` script.log:7038 teleport in stream ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_MORE` script.log:0 8 more teleport rows in ('HSD', 'cl', 'frame', None, 'f9428f8a-768a-456a-a50a-f656d6ff71e6')
- warning `W_TELEPORT` message.log:3479 teleport in stream ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_TELEPORT` message.log:3887 teleport in stream ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_TELEPORT` message.log:4270 teleport in stream ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_TELEPORT` message.log:4652 teleport in stream ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_TELEPORT` message.log:5036 teleport in stream ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_MORE` message.log:0 8 more teleport rows in ('MT', 'sv', 'cmd', 1, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')
- warning `W_TIME_BACKWARDS` script.log:713 t 30.8 -> 30.49677 in ('HSD', 'sv', 'evt', 1.0, '0d422b8d-1a8b-4186-9f8b-1f9cd0b2d4e4')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3108 | 0 | - | - |
| MT | cl | r90 | 176 | 600 | - | linear (yes) |
| MT | cl | b1 | 194 | 0 | - | - |
| MT | cl | r12001 | 175 | 600 | - | linear (yes) |
| MT | cl | b2 | 197 | 0 | - | - |
| MT | cl | r12002 | 175 | 600 | - | linear (yes) |
| MT | cl | b3 | 197 | 0 | - | - |
| MT | cl | r12003 | 176 | 600 | - | linear (yes) |
| MT | cl | b4 | 197 | 0 | - | - |
| MT | cl | r12004 | 176 | 600 | - | linear (yes) |
| MT | cl | b5 | 196 | 0 | - | - |
| MT | cl | r12005 | 165 | 600 | - | - |
| MT | cl | b6 | 179 | 419.597 | - | - |
| MT | cl | r12006 | 166 | 600 | - | - |
| MT | cl | b7 | 180 | 419.785 | - | - |
| MT | cl | r12007 | 203 | 600 | linear (no) | - |
| MT | cl | b9 | 169 | 64.556 | - | - |
| MT | cl | r12008 | 202 | 600 | linear (no) | - |
| MT | cl | b11 | 170 | 58.265 | - | - |
| MT | cl | r12009 | 153 | 600 | - | - |
| MT | cl | b12 | 196 | 54.784 | - | - |
| MT | cl | r12010 | 153 | 600 | - | - |
| MT | cl | b13 | 197 | 58.246 | - | - |
| MT | cl | r12011 | 313 | 400 | - | linear (yes) |
| MT | cl | b14 | 177 | 0 | - | - |
| MT | cl | r12012 | 313 | 400 | - | linear (yes) |
| MT | cl | b15 | 148 | 0 | - | - |
| HSD | cl | r0 | 5477 | 430.305 | - | linear (yes) |
| HSD | cl | r90 | 361 | 600 | - | linear (yes) |
| HSD | cl | r12001 | 361 | 600 | - | linear (yes) |
| HSD | cl | r12002 | 361 | 600 | - | linear (yes) |
| HSD | cl | r12003 | 361 | 600 | - | linear (yes) |
| HSD | cl | r12004 | 361 | 600 | - | linear (yes) |
| HSD | cl | r12005 | 348 | 600 | - | - |
| HSD | cl | r12006 | 348 | 600 | - | - |
| HSD | cl | r12007 | 449 | 600 | linear (no) | - |
| HSD | cl | r12008 | 448 | 600 | linear (no) | - |
| HSD | cl | r12009 | 361 | 600 | - | - |
| HSD | cl | r12010 | 361 | 600 | - | - |
| HSD | cl | r12011 | 411 | 424.305 | - | linear (yes) |
| HSD | cl | r12012 | 411 | 423.325 | - | linear (yes) |
| MT | sv | b0 | 3123 | 0 | - | - |
| MT | sv | r90 | 176 | 600 | - | linear (yes) |
| MT | sv | b1 | 194 | 0 | - | - |
| MT | sv | r12001 | 175 | 600 | - | linear (yes) |
| MT | sv | b2 | 197 | 0 | - | - |
| MT | sv | r12002 | 175 | 600 | - | linear (yes) |
| MT | sv | b3 | 197 | 0 | - | - |
| MT | sv | r12003 | 176 | 600 | - | linear (yes) |
| MT | sv | b4 | 197 | 0 | - | - |
| MT | sv | r12004 | 176 | 600 | - | linear (yes) |
| MT | sv | b5 | 196 | 0 | - | - |
| MT | sv | r12005 | 165 | 600 | - | - |
| MT | sv | b6 | 179 | 419.597 | - | - |
| MT | sv | r12006 | 166 | 600 | - | - |
| MT | sv | b7 | 180 | 419.785 | - | - |
| MT | sv | r12007 | 203 | 600 | linear (no) | - |
| MT | sv | b9 | 169 | 64.556 | - | - |
| MT | sv | r12008 | 202 | 600 | linear (no) | - |
| MT | sv | b11 | 170 | 58.265 | - | - |
| MT | sv | r12009 | 153 | 600 | - | - |
| MT | sv | b12 | 196 | 54.784 | - | - |
| MT | sv | r12010 | 153 | 600 | - | - |
| MT | sv | b13 | 197 | 58.246 | - | - |
| MT | sv | r12011 | 313 | 400 | - | linear (yes) |
| MT | sv | b14 | 177 | 0 | - | - |
| MT | sv | r12012 | 313 | 400 | - | linear (yes) |
| MT | sv | b15 | 140 | 0 | - | - |

Events: 132. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
