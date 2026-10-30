# hsd_tel report

Inputs: 16 file(s); rows: 24401 (MT 15955, HSD 8444)

Validation: 0 error(s), 19 warning(s), 4 info

- warning `W_TELEPORT` message.log:3991 teleport in stream ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` message.log:4691 teleport in stream ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` message.log:5392 teleport in stream ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` message.log:6098 teleport in stream ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` message.log:6795 teleport in stream ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` script.log:3623 teleport in stream ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` script.log:4881 teleport in stream ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` script.log:6144 teleport in stream ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` script.log:7410 teleport in stream ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` script.log:8669 teleport in stream ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '44f6aad8-dd40-44a8-a0b6-2494e2937867')
- warning `W_TELEPORT` message.log:3760 teleport in stream ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_TELEPORT` message.log:4412 teleport in stream ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_TELEPORT` message.log:5065 teleport in stream ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_TELEPORT` message.log:5720 teleport in stream ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_TELEPORT` message.log:6351 teleport in stream ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.55 -> 25.32439 in ('HSD', 'sv', 'evt', 1.0, 'b9af7025-bc53-43c1-8977-25f00a1a7a7f')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3393 | 0 | - | - |
| MT | cl | r90 | 483 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 165 | 0 | - | - |
| MT | cl | r9400 | 482 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 169 | 0 | - | - |
| MT | cl | r9401 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b3 | 168 | 0 | - | - |
| MT | cl | r9402 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b4 | 166 | 0 | - | - |
| MT | cl | r9403 | 466 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b5 | 167 | 0 | - | - |
| MT | cl | r9404 | 475 | 299.145 | first_order (no) | friction (no) |
| MT | cl | b6 | 172 | 0 | - | - |
| MT | cl | r9405 | 538 | 199.77 | first_order (yes) | linear (no) |
| MT | cl | b7 | 140 | 0 | - | - |
| HSD | cl | r0 | 4519 | 0 | - | - |
| HSD | cl | r90 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9400 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9401 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r9402 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9403 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r9404 | 534 | 299.145 | first_order (no) | - |
| HSD | cl | r9405 | 594 | 199.77 | first_order (yes) | - |
| MT | sv | b0 | 3402 | 0 | - | - |
| MT | sv | r90 | 483 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 165 | 0 | - | - |
| MT | sv | r9400 | 482 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 169 | 0 | - | - |
| MT | sv | r9401 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b3 | 168 | 0 | - | - |
| MT | sv | r9402 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b4 | 166 | 0 | - | - |
| MT | sv | r9403 | 466 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b5 | 167 | 0 | - | - |
| MT | sv | r9404 | 475 | 299.145 | first_order (no) | friction (no) |
| MT | sv | b6 | 172 | 0 | - | - |
| MT | sv | r9405 | 538 | 199.77 | first_order (yes) | linear (no) |
| MT | sv | b7 | 131 | 0 | - | - |

Events: 130. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
