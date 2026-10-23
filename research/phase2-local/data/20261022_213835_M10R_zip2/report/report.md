# hsd_tel report

Inputs: 16 file(s); rows: 24039 (MT 15441, HSD 8596)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3670 teleport in stream ('MT', 'cl', 'cmd', 1, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` message.log:5115 teleport in stream ('MT', 'cl', 'cmd', 1, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` message.log:6089 teleport in stream ('MT', 'cl', 'cmd', 1, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` message.log:7047 teleport in stream ('MT', 'cl', 'cmd', 1, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:3288 teleport in stream ('HSD', 'cl', 'frame', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:7113 teleport in stream ('HSD', 'cl', 'frame', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:10934 teleport in stream ('HSD', 'cl', 'frame', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:14769 teleport in stream ('HSD', 'cl', 'frame', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:10935 teleport in stream ('HSD', 'cl', 'edge', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` script.log:14770 teleport in stream ('HSD', 'cl', 'edge', None, '5d529c2f-a797-407c-aa62-11f39210498d')
- warning `W_TELEPORT` message.log:3438 teleport in stream ('MT', 'sv', 'cmd', 1, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` message.log:4842 teleport in stream ('MT', 'sv', 'cmd', 1, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` message.log:5773 teleport in stream ('MT', 'sv', 'cmd', 1, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` message.log:6681 teleport in stream ('MT', 'sv', 'cmd', 1, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` script.log:938 teleport in stream ('HSD', 'sv', 'evt', 1.0, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` script.log:979 teleport in stream ('HSD', 'sv', 'evt', 1.0, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` script.log:1046 teleport in stream ('HSD', 'sv', 'evt', 1.0, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TELEPORT` script.log:1087 teleport in stream ('HSD', 'sv', 'evt', 1.0, '6e1f36ba-0373-4292-b073-63eb133b9de3')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.55 -> 24.23104 in ('HSD', 'sv', 'evt', 1.0, '6e1f36ba-0373-4292-b073-63eb133b9de3')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3265 | 0 | - | - |
| MT | cl | r90 | 1202 | 199.525 | first_order (no) | linear (no) |
| MT | cl | r17101 | 844 | 393.576 | first_order (no) | linear (no) |
| MT | cl | b1 | 58 | 592.073 | - | - |
| MT | cl | r17102 | 845 | 394.469 | first_order (no) | linear (no) |
| MT | cl | b2 | 183 | 592.073 | - | - |
| MT | cl | r17103 | 1203 | 199.525 | first_order (no) | linear (no) |
| HSD | cl | r0 | 3752 | 986.789 | - | - |
| HSD | cl | r90 | 1203 | 199.525 | first_order (no) | linear (no) |
| HSD | cl | r17101 | 1203 | 986.789 | first_order (no) | linear (no) |
| HSD | cl | r17102 | 1203 | 986.789 | first_order (no) | linear (no) |
| HSD | cl | r17103 | 1203 | 199.525 | first_order (no) | linear (no) |
| MT | sv | b0 | 3281 | 0 | - | - |
| MT | sv | r90 | 1202 | 199.525 | first_order (no) | linear (no) |
| MT | sv | r17101 | 844 | 393.576 | first_order (no) | linear (no) |
| MT | sv | b1 | 58 | 592.076 | - | - |
| MT | sv | r17102 | 845 | 394.469 | first_order (no) | linear (no) |
| MT | sv | b2 | 178 | 592.077 | - | - |
| MT | sv | r17103 | 1203 | 199.525 | first_order (no) | linear (no) |

Events: 22. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
