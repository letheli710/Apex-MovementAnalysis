# hsd_tel report

Inputs: 16 file(s); rows: 21269 (MT 14083, HSD 7126)

Validation: 0 error(s), 26 warning(s), 24 info

- warning `W_TELEPORT` message.log:3800 teleport in stream ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` message.log:4422 teleport in stream ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` message.log:5047 teleport in stream ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` message.log:5672 teleport in stream ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` message.log:6553 teleport in stream ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:3411 teleport in stream ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:4037 teleport in stream ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:4666 teleport in stream ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:5295 teleport in stream ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:6186 teleport in stream ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:6187 teleport in stream ('HSD', 'cl', 'edge', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:6360 teleport in stream ('HSD', 'cl', 'edge', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:6782 teleport in stream ('HSD', 'cl', 'edge', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` script.log:6956 teleport in stream ('HSD', 'cl', 'edge', None, '8f816a8c-8d9b-49f7-bd01-edfe09bb2337')
- warning `W_TELEPORT` message.log:3502 teleport in stream ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` message.log:4119 teleport in stream ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` message.log:4736 teleport in stream ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` message.log:5354 teleport in stream ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` message.log:6228 teleport in stream ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` script.log:833 teleport in stream ('HSD', 'sv', 'evt', 1.0, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` script.log:844 teleport in stream ('HSD', 'sv', 'evt', 1.0, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TELEPORT` script.log:849 teleport in stream ('HSD', 'sv', 'evt', 1.0, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')
- warning `W_TIME_BACKWARDS` script.log:711 t 33.5 -> 33.28573 in ('HSD', 'sv', 'evt', 1.0, '2ac768e3-cd14-4e8d-829e-da3d035f3fa7')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4730 | 0 | - | - |
| MT | cl | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r24001 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r24002 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r24003 | 241 | 0 | - | - |
| MT | cl | r24004 | 241 | 0 | - | - |
| MT | cl | r24005 | 240 | 0 | - | - |
| MT | cl | r24006 | 240 | 0 | - | - |
| HSD | cl | r0 | 4700 | 0 | - | - |
| HSD | cl | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r24001 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r24002 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r24003 | 241 | 0 | - | - |
| HSD | cl | r24004 | 241 | 0 | - | - |
| HSD | cl | r24005 | 240 | 0 | - | - |
| HSD | cl | r24006 | 240 | 0 | - | - |
| MT | sv | b0 | 4740 | 0 | - | - |
| MT | sv | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r24001 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r24002 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r24003 | 241 | 0 | - | - |
| MT | sv | r24004 | 241 | 0 | - | - |
| MT | sv | r24005 | 240 | 0 | - | - |
| MT | sv | r24006 | 240 | 0 | - | - |

Events: 40. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
