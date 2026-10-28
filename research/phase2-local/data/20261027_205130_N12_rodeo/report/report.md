# hsd_tel report

Inputs: 16 file(s); rows: 38106 (MT 25604, HSD 12500)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3826 teleport in stream ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` message.log:4713 teleport in stream ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` message.log:5655 teleport in stream ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` message.log:6578 teleport in stream ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` message.log:7487 teleport in stream ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'cl', 'cmd', 1, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` script.log:3464 teleport in stream ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` script.log:4990 teleport in stream ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` script.log:6504 teleport in stream ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` script.log:8029 teleport in stream ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` script.log:9547 teleport in stream ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'cl', 'frame', None, '1b801647-6b27-4d78-b118-8df5842bfbc1')
- warning `W_TELEPORT` message.log:3613 teleport in stream ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_TELEPORT` message.log:4462 teleport in stream ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_TELEPORT` message.log:5296 teleport in stream ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_TELEPORT` message.log:6138 teleport in stream ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_TELEPORT` message.log:6977 teleport in stream ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'sv', 'cmd', 1, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.25 -> 24.97576 in ('HSD', 'sv', 'evt', 1.0, '6ab0dfcc-62b7-4fd0-82c7-315fbe9d8862')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5186 | 0 | - | - |
| MT | cl | r90 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21201 | 661 | 452.676 | first_order (no) | linear (yes) |
| MT | cl | r21202 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21203 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21204 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21205 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21206 | 661 | 299 | first_order (no) | linear (no) |
| MT | cl | r21207 | 660 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r21208 | 661 | 299 | first_order (no) | linear (no) |
| MT | cl | r21209 | 661 | 299 | first_order (no) | linear (no) |
| MT | cl | r21210 | 661 | 299 | first_order (no) | linear (no) |
| HSD | cl | r0 | 5157 | 0 | - | - |
| HSD | cl | r90 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21201 | 661 | 452.676 | first_order (no) | linear (yes) |
| HSD | cl | r21202 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21203 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21204 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21205 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21206 | 661 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21207 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r21208 | 661 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21209 | 661 | 299 | first_order (no) | linear (no) |
| HSD | cl | r21210 | 661 | 299 | first_order (no) | linear (no) |
| MT | sv | b0 | 5195 | 0 | - | - |
| MT | sv | r90 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21201 | 661 | 452.674 | first_order (no) | linear (yes) |
| MT | sv | r21202 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21203 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21204 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21205 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21206 | 661 | 299 | first_order (no) | linear (no) |
| MT | sv | r21207 | 660 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r21208 | 661 | 299 | first_order (no) | linear (no) |
| MT | sv | r21209 | 661 | 299 | first_order (no) | linear (no) |
| MT | sv | r21210 | 661 | 299 | first_order (no) | linear (no) |

Events: 50. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
