# hsd_tel report

Inputs: 16 file(s); rows: 58837 (MT 39075, HSD 19702)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:3997 teleport in stream ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` message.log:5159 teleport in stream ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` message.log:6325 teleport in stream ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` message.log:7490 teleport in stream ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` message.log:8660 teleport in stream ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'cl', 'cmd', 1, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` script.log:3613 teleport in stream ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` script.log:4962 teleport in stream ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` script.log:6315 teleport in stream ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` script.log:7667 teleport in stream ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` script.log:9019 teleport in stream ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_MORE` script.log:0 9 more teleport rows in ('HSD', 'cl', 'frame', None, '6f66cc5e-c47e-413a-8933-57f4a9de0c6f')
- warning `W_TELEPORT` message.log:3705 teleport in stream ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_TELEPORT` message.log:4862 teleport in stream ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_TELEPORT` message.log:6019 teleport in stream ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_TELEPORT` message.log:7177 teleport in stream ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_TELEPORT` message.log:8334 teleport in stream ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'sv', 'cmd', 1, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')
- warning `W_TIME_BACKWARDS` script.log:715 t 25.15 -> 24.87825 in ('HSD', 'sv', 'evt', 1.0, '6fc53a0c-938d-41dc-a79d-812238ed1bf6')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6800 | 515.533 | - | - |
| MT | cl | r90 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2441 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2442 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2443 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2444 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2445 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | cl | r2446 | 964 | 517.34 | first_order (no) | friction (no) |
| MT | cl | r2447 | 964 | 517.341 | first_order (no) | friction (no) |
| MT | cl | r2448 | 964 | 517.341 | first_order (no) | friction (no) |
| MT | cl | r2449 | 360 | 0 | - | - |
| MT | cl | r2450 | 360 | 0 | - | - |
| MT | cl | r2451 | 360 | 0 | - | - |
| MT | cl | r2452 | 360 | 0 | - | - |
| MT | cl | r2453 | 360 | 0 | - | - |
| MT | cl | r2454 | 432 | 515.531 | first_order (no) | - |
| MT | cl | r2455 | 432 | 515.532 | first_order (no) | - |
| MT | cl | r2456 | 432 | 515.532 | first_order (no) | - |
| MT | cl | r2457 | 432 | 515.533 | first_order (no) | - |
| MT | cl | r2458 | 432 | 515.532 | first_order (no) | - |
| HSD | cl | r0 | 6769 | 515.533 | - | - |
| HSD | cl | r90 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2441 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2442 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2443 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2444 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2445 | 964 | 514.946 | first_order (no) | linear (no) |
| HSD | cl | r2446 | 964 | 517.34 | first_order (no) | - |
| HSD | cl | r2447 | 964 | 517.341 | first_order (no) | - |
| HSD | cl | r2448 | 964 | 517.341 | first_order (no) | - |
| HSD | cl | r2449 | 360 | 0 | - | - |
| HSD | cl | r2450 | 360 | 0 | - | - |
| HSD | cl | r2451 | 360 | 0 | - | - |
| HSD | cl | r2452 | 360 | 0 | - | - |
| HSD | cl | r2453 | 360 | 0 | - | - |
| HSD | cl | r2454 | 432 | 515.531 | first_order (no) | - |
| HSD | cl | r2455 | 432 | 515.532 | first_order (no) | - |
| HSD | cl | r2456 | 432 | 515.532 | first_order (no) | - |
| HSD | cl | r2457 | 432 | 515.533 | first_order (no) | - |
| HSD | cl | r2458 | 432 | 515.532 | first_order (no) | - |
| MT | sv | b0 | 6812 | 515.533 | - | - |
| MT | sv | r90 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2441 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2442 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2443 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2444 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2445 | 964 | 514.946 | first_order (no) | linear (no) |
| MT | sv | r2446 | 964 | 517.34 | first_order (no) | friction (no) |
| MT | sv | r2447 | 964 | 517.341 | first_order (no) | friction (no) |
| MT | sv | r2448 | 964 | 517.341 | first_order (no) | friction (no) |
| MT | sv | r2449 | 360 | 0 | - | - |
| MT | sv | r2450 | 360 | 0 | - | - |
| MT | sv | r2451 | 360 | 0 | - | - |
| MT | sv | r2452 | 360 | 0 | - | - |
| MT | sv | r2453 | 360 | 0 | - | - |
| MT | sv | r2454 | 432 | 515.531 | first_order (no) | - |
| MT | sv | r2455 | 432 | 515.532 | first_order (no) | - |
| MT | sv | r2456 | 432 | 515.532 | first_order (no) | - |
| MT | sv | r2457 | 432 | 515.533 | first_order (no) | - |
| MT | sv | r2458 | 432 | 515.532 | first_order (no) | - |

Events: 209. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
