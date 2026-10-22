# hsd_tel report

Inputs: 16 file(s); rows: 33556 (MT 22247, HSD 11307)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3811 teleport in stream ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` message.log:5124 teleport in stream ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` message.log:6426 teleport in stream ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` message.log:7767 teleport in stream ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` message.log:9166 teleport in stream ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` script.log:3469 teleport in stream ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` script.log:5991 teleport in stream ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` script.log:8508 teleport in stream ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` script.log:11026 teleport in stream ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` script.log:13543 teleport in stream ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '40882908-b5d5-436b-888a-23a08371e812')
- warning `W_TELEPORT` message.log:3611 teleport in stream ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_TELEPORT` message.log:4886 teleport in stream ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_TELEPORT` message.log:6154 teleport in stream ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_TELEPORT` message.log:7421 teleport in stream ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_TELEPORT` message.log:8688 teleport in stream ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')
- warning `W_TIME_BACKWARDS` script.log:713 t 24.4 -> 24.15181 in ('HSD', 'sv', 'evt', 1.0, '96c053ac-d9dc-47df-a45b-cce91c37ab3c')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3236 | 0 | - | - |
| MT | cl | r90 | 1094 | 300.319 | first_order (no) | - |
| MT | cl | b1 | 177 | 0 | - | - |
| MT | cl | r9641 | 1093 | 300.319 | first_order (no) | - |
| MT | cl | b2 | 172 | 0 | - | - |
| MT | cl | r9642 | 1093 | 300.304 | first_order (no) | - |
| MT | cl | b3 | 173 | 0 | - | - |
| MT | cl | r9643 | 1093 | 300.318 | first_order (no) | - |
| MT | cl | b4 | 172 | 0 | - | - |
| MT | cl | r9644 | 1096 | 300.303 | first_order (no) | - |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r9645 | 1096 | 300.304 | first_order (no) | - |
| MT | cl | b6 | 134 | 0 | - | - |
| HSD | cl | r0 | 4217 | 0 | - | - |
| HSD | cl | r90 | 1165 | 300.319 | first_order (no) | - |
| HSD | cl | r9641 | 1165 | 300.319 | first_order (no) | - |
| HSD | cl | r9642 | 1165 | 300.304 | first_order (no) | - |
| HSD | cl | r9643 | 1165 | 300.318 | first_order (no) | - |
| HSD | cl | r9644 | 1165 | 300.303 | first_order (no) | - |
| HSD | cl | r9645 | 1165 | 300.304 | first_order (no) | - |
| MT | sv | b0 | 3250 | 0 | - | - |
| MT | sv | r90 | 1094 | 300.319 | first_order (no) | - |
| MT | sv | b1 | 177 | 0 | - | - |
| MT | sv | r9641 | 1093 | 300.319 | first_order (no) | - |
| MT | sv | b2 | 172 | 0 | - | - |
| MT | sv | r9642 | 1093 | 300.304 | first_order (no) | - |
| MT | sv | b3 | 173 | 0 | - | - |
| MT | sv | r9643 | 1093 | 300.318 | first_order (no) | - |
| MT | sv | b4 | 172 | 0 | - | - |
| MT | sv | r9644 | 1096 | 300.303 | first_order (no) | - |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r9645 | 1095 | 300.304 | first_order (no) | - |
| MT | sv | b6 | 130 | 0 | - | - |

Events: 134. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
