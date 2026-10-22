# hsd_tel report

Inputs: 16 file(s); rows: 26814 (MT 17842, HSD 8970)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3827 teleport in stream ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` message.log:4784 teleport in stream ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` message.log:5735 teleport in stream ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` message.log:6687 teleport in stream ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` message.log:7642 teleport in stream ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` script.log:3470 teleport in stream ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` script.log:5209 teleport in stream ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` script.log:6943 teleport in stream ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` script.log:8677 teleport in stream ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` script.log:10412 teleport in stream ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, 'bdba6511-2c8a-4d65-9269-dd79bb9d74dd')
- warning `W_TELEPORT` message.log:3618 teleport in stream ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_TELEPORT` message.log:4573 teleport in stream ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_TELEPORT` message.log:5522 teleport in stream ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_TELEPORT` message.log:6469 teleport in stream ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_TELEPORT` message.log:7417 teleport in stream ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '4a2a486f-4b3c-4c9b-b61b-497496786d86')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.75 -> 24.50816 in ('HSD', 'sv', 'evt', 1.0, '4a2a486f-4b3c-4c9b-b61b-497496786d86')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4274 | 0 | - | - |
| MT | cl | r90 | 770 | 299.147 | first_order (no) | - |
| MT | cl | r9811 | 770 | 299.147 | first_order (no) | - |
| MT | cl | r9812 | 770 | 299.144 | first_order (no) | - |
| MT | cl | r9813 | 770 | 299.147 | first_order (no) | - |
| MT | cl | r9814 | 770 | 299.147 | first_order (no) | - |
| MT | cl | r9815 | 770 | 299.149 | first_order (no) | - |
| HSD | cl | r0 | 4250 | 0 | - | - |
| HSD | cl | r90 | 770 | 299.147 | first_order (no) | - |
| HSD | cl | r9811 | 770 | 299.147 | first_order (no) | - |
| HSD | cl | r9812 | 770 | 299.144 | first_order (no) | - |
| HSD | cl | r9813 | 770 | 299.147 | first_order (no) | - |
| HSD | cl | r9814 | 770 | 299.147 | first_order (no) | - |
| HSD | cl | r9815 | 770 | 299.149 | first_order (no) | - |
| MT | sv | b0 | 4283 | 0 | - | - |
| MT | sv | r90 | 770 | 299.147 | first_order (no) | - |
| MT | sv | r9811 | 770 | 299.147 | first_order (no) | - |
| MT | sv | r9812 | 770 | 299.144 | first_order (no) | - |
| MT | sv | r9813 | 770 | 299.147 | first_order (no) | - |
| MT | sv | r9814 | 770 | 299.147 | first_order (no) | - |
| MT | sv | r9815 | 770 | 299.149 | first_order (no) | - |

Events: 146. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
