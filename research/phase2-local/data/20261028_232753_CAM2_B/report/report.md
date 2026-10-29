# hsd_tel report

Inputs: 16 file(s); rows: 37844 (MT 24824, HSD 13018)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:7971 teleport in stream ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` message.log:8532 teleport in stream ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` message.log:9093 teleport in stream ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` message.log:9655 teleport in stream ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` message.log:10219 teleport in stream ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'cl', 'cmd', 1, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` script.log:7604 teleport in stream ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` script.log:8233 teleport in stream ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` script.log:8863 teleport in stream ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` script.log:9493 teleport in stream ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` script.log:10124 teleport in stream ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_MORE` script.log:0 4 more teleport rows in ('HSD', 'cl', 'frame', None, '8902010b-38fe-4053-b880-fa8b9e8d3235')
- warning `W_TELEPORT` message.log:7753 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_TELEPORT` message.log:8311 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_TELEPORT` message.log:8869 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_TELEPORT` message.log:9427 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_TELEPORT` message.log:9986 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'sv', 'cmd', 1, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')
- warning `W_TIME_BACKWARDS` script.log:717 t 28.35 -> 28.11334 in ('HSD', 'sv', 'evt', 1.0, 'aa5011c8-d9ca-471b-84f0-b3c9b9d527f7')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 7379 | 0 | - | - |
| MT | cl | r90 | 394 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 162 | 0 | - | - |
| MT | cl | r27101 | 393 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 165 | 0 | - | - |
| MT | cl | r27102 | 394 | 299.15 | first_order (no) | friction (no) |
| MT | cl | b3 | 163 | 0 | - | - |
| MT | cl | r27103 | 393 | 299.147 | first_order (no) | friction (no) |
| MT | cl | b4 | 166 | 0 | - | - |
| MT | cl | r27104 | 393 | 299.15 | first_order (no) | friction (no) |
| MT | cl | b5 | 164 | 0 | - | - |
| MT | cl | r27105 | 437 | 199.764 | first_order (yes) | linear (yes) |
| MT | cl | b6 | 146 | 0 | - | - |
| MT | cl | r27106 | 436 | 199.767 | first_order (yes) | linear (yes) |
| MT | cl | b7 | 146 | 0 | - | - |
| MT | cl | r27107 | 367 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b8 | 166 | 0 | - | - |
| MT | cl | r27108 | 366 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b9 | 132 | 0 | - | - |
| HSD | cl | r0 | 8759 | 0 | - | - |
| HSD | cl | r90 | 451 | 299.151 | first_order (no) | - |
| HSD | cl | r27101 | 450 | 299.151 | first_order (no) | - |
| HSD | cl | r27102 | 451 | 299.15 | first_order (no) | - |
| HSD | cl | r27103 | 450 | 299.147 | first_order (no) | - |
| HSD | cl | r27104 | 450 | 299.15 | first_order (no) | - |
| HSD | cl | r27105 | 494 | 199.764 | first_order (yes) | - |
| HSD | cl | r27106 | 494 | 199.767 | first_order (yes) | - |
| HSD | cl | r27107 | 449 | 299.15 | first_order (no) | - |
| HSD | cl | r27108 | 450 | 299.151 | first_order (no) | - |
| MT | sv | b0 | 7392 | 0 | - | - |
| MT | sv | r90 | 394 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 162 | 0 | - | - |
| MT | sv | r27101 | 393 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 165 | 0 | - | - |
| MT | sv | r27102 | 394 | 299.15 | first_order (no) | friction (no) |
| MT | sv | b3 | 163 | 0 | - | - |
| MT | sv | r27103 | 393 | 299.147 | first_order (no) | friction (no) |
| MT | sv | b4 | 166 | 0 | - | - |
| MT | sv | r27104 | 393 | 299.15 | first_order (no) | friction (no) |
| MT | sv | b5 | 164 | 0 | - | - |
| MT | sv | r27105 | 436 | 199.764 | first_order (yes) | linear (yes) |
| MT | sv | b6 | 146 | 0 | - | - |
| MT | sv | r27106 | 436 | 199.767 | first_order (yes) | linear (yes) |
| MT | sv | b7 | 146 | 0 | - | - |
| MT | sv | r27107 | 367 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b8 | 166 | 0 | - | - |
| MT | sv | r27108 | 366 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b9 | 124 | 0 | - | - |

Events: 156. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
