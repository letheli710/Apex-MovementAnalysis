# hsd_tel report

Inputs: 16 file(s); rows: 39816 (MT 26495, HSD 13261)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:3587 teleport in stream ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` message.log:4372 teleport in stream ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` message.log:4379 teleport in stream ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` message.log:5223 teleport in stream ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` message.log:5389 teleport in stream ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_MORE` message.log:0 12 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` script.log:3237 teleport in stream ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` script.log:4010 teleport in stream ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` script.log:4015 teleport in stream ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` script.log:4861 teleport in stream ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` script.log:5027 teleport in stream ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_MORE` script.log:0 12 more teleport rows in ('HSD', 'cl', 'frame', None, 'f2619719-f843-4e6d-aad3-6ca2cb69b586')
- warning `W_TELEPORT` message.log:3294 teleport in stream ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_TELEPORT` message.log:4072 teleport in stream ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_TELEPORT` message.log:4075 teleport in stream ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_TELEPORT` message.log:4908 teleport in stream ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_TELEPORT` message.log:5078 teleport in stream ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_MORE` message.log:0 12 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')
- warning `W_TIME_BACKWARDS` script.log:717 t 27.8 -> 27.51828 in ('HSD', 'sv', 'evt', 1.0, 'b7a0edf7-a901-40c8-ad65-72da728e8a23')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5158 | 0 | - | - |
| MT | cl | r90 | 661 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2621 | 661 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2622 | 661 | 299 | first_order (no) | - |
| MT | cl | r2623 | 662 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2624 | 661 | 324.831 | first_order (no) | linear (no) |
| MT | cl | r2625 | 661 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2626 | 661 | 323.522 | first_order (no) | friction (no) |
| MT | cl | r2627 | 541 | 0 | - | - |
| MT | cl | r2628 | 541 | 0 | - | - |
| MT | cl | r2629 | 541 | 0 | - | - |
| MT | cl | r2630 | 541 | 0 | - | - |
| MT | cl | r2631 | 541 | 0 | - | - |
| MT | cl | r2632 | 541 | 0 | - | - |
| HSD | cl | r0 | 5138 | 0 | - | - |
| HSD | cl | r90 | 661 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2621 | 661 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2622 | 661 | 299 | first_order (no) | - |
| HSD | cl | r2623 | 661 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2624 | 661 | 324.831 | first_order (no) | linear (no) |
| HSD | cl | r2625 | 661 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2626 | 661 | 323.522 | first_order (no) | friction (no) |
| HSD | cl | r2627 | 541 | 0 | - | - |
| HSD | cl | r2628 | 541 | 0 | - | - |
| HSD | cl | r2629 | 541 | 0 | - | - |
| HSD | cl | r2630 | 541 | 0 | - | - |
| HSD | cl | r2631 | 541 | 0 | - | - |
| HSD | cl | r2632 | 541 | 0 | - | - |
| MT | sv | b0 | 5162 | 0 | - | - |
| MT | sv | r90 | 661 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2621 | 661 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2622 | 661 | 299 | first_order (no) | - |
| MT | sv | r2623 | 662 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2624 | 661 | 324.831 | first_order (no) | linear (no) |
| MT | sv | r2625 | 661 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2626 | 661 | 323.522 | first_order (no) | friction (no) |
| MT | sv | r2627 | 541 | 0 | - | - |
| MT | sv | r2628 | 541 | 0 | - | - |
| MT | sv | r2629 | 541 | 0 | - | - |
| MT | sv | r2630 | 541 | 0 | - | - |
| MT | sv | r2631 | 541 | 0 | - | - |
| MT | sv | r2632 | 541 | 0 | - | - |

Events: 154. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
