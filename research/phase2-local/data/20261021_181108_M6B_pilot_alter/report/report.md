# hsd_tel report

Inputs: 16 file(s); rows: 33730 (MT 21955, HSD 11773)

Validation: 0 error(s), 20 warning(s), 2 info

- warning `W_TELEPORT` message.log:4054 teleport in stream ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` message.log:5232 teleport in stream ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` message.log:6405 teleport in stream ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` message.log:7569 teleport in stream ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` message.log:8783 teleport in stream ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` script.log:3700 teleport in stream ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` script.log:5707 teleport in stream ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` script.log:7712 teleport in stream ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` script.log:9717 teleport in stream ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` script.log:11713 teleport in stream ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, 'f31af98d-4f60-430f-b8e9-9730c97b65bc')
- warning `W_TELEPORT` message.log:3823 teleport in stream ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TELEPORT` message.log:5736 teleport in stream ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TELEPORT` message.log:7503 teleport in stream ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TELEPORT` message.log:9273 teleport in stream ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TELEPORT` message.log:10771 teleport in stream ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TELEPORT` script.log:768 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')
- warning `W_TIME_BACKWARDS` script.log:714 t 22.7 -> 22.55787 in ('HSD', 'sv', 'evt', 1.0, 'b5bb82b6-da29-43b3-8fb5-40c5316d799a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4637 | 0 | - | - |
| MT | cl | r90 | 804 | 199.525 | first_order (yes) | - |
| MT | cl | r4401 | 804 | 199.525 | first_order (yes) | - |
| MT | cl | r4402 | 804 | 199.525 | first_order (yes) | - |
| MT | cl | r4403 | 793 | 199.525 | first_order (yes) | - |
| MT | cl | r4404 | 793 | 199.525 | first_order (yes) | - |
| MT | cl | r4405 | 782 | 199.525 | first_order (yes) | - |
| MT | cl | r4406 | 782 | 199.525 | first_order (yes) | - |
| HSD | cl | r0 | 4613 | 0 | - | - |
| HSD | cl | r90 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r4401 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r4402 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r4403 | 793 | 199.525 | first_order (yes) | - |
| HSD | cl | r4404 | 793 | 199.525 | first_order (yes) | - |
| HSD | cl | r4405 | 782 | 199.525 | first_order (yes) | - |
| HSD | cl | r4406 | 782 | 199.525 | first_order (yes) | - |
| MT | sv | b0 | 4641 | 0 | - | - |
| MT | sv | r90 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | r4401 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | r4402 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | r4403 | 793 | 199.525 | first_order (yes) | - |
| MT | sv | r4404 | 793 | 199.525 | first_order (yes) | - |
| MT | sv | r4405 | 782 | 199.525 | first_order (yes) | - |
| MT | sv | r4406 | 782 | 199.525 | first_order (yes) | - |

Events: 3120. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
