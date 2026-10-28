# hsd_tel report

Inputs: 16 file(s); rows: 24822 (MT 16572, HSD 8248)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3872 teleport in stream ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` message.log:4714 teleport in stream ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` message.log:5563 teleport in stream ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` message.log:6403 teleport in stream ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` message.log:7241 teleport in stream ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` script.log:3524 teleport in stream ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` script.log:5037 teleport in stream ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` script.log:6551 teleport in stream ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` script.log:8059 teleport in stream ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` script.log:9568 teleport in stream ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '68b6d4d7-6990-464f-9dd3-2698c146fc4e')
- warning `W_TELEPORT` message.log:3667 teleport in stream ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_TELEPORT` message.log:4502 teleport in stream ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_TELEPORT` message.log:5336 teleport in stream ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_TELEPORT` message.log:6164 teleport in stream ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_TELEPORT` message.log:6992 teleport in stream ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')
- warning `W_TIME_BACKWARDS` script.log:716 t 23.75 -> 23.61901 in ('HSD', 'sv', 'evt', 1.0, 'e4f7805d-7c9e-4eaf-9d3a-7eaf76ff78d7')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4271 | 0 | - | - |
| MT | cl | r90 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21211 | 662 | 299 | first_order (no) | linear (no) |
| MT | cl | r21212 | 662 | 299 | first_order (no) | linear (no) |
| MT | cl | r21213 | 662 | 299 | first_order (no) | linear (no) |
| MT | cl | r21214 | 662 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21215 | 662 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r0 | 4248 | 0 | - | - |
| HSD | cl | r90 | 662 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21211 | 662 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21212 | 662 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21213 | 662 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21214 | 662 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21215 | 662 | 299.001 | first_order (no) | linear (no) |
| MT | sv | b0 | 4276 | 0 | - | - |
| MT | sv | r90 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21211 | 662 | 299 | first_order (no) | linear (no) |
| MT | sv | r21212 | 662 | 299 | first_order (no) | linear (no) |
| MT | sv | r21213 | 662 | 299 | first_order (no) | linear (no) |
| MT | sv | r21214 | 662 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21215 | 662 | 299.001 | first_order (no) | linear (no) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
