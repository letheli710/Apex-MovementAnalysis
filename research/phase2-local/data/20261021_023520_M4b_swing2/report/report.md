# hsd_tel report

Inputs: 16 file(s); rows: 26379 (MT 17597, HSD 8780)

Validation: 0 error(s), 23 warning(s), 6 info

- warning `W_TELEPORT` message.log:3905 teleport in stream ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` message.log:4906 teleport in stream ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` message.log:5912 teleport in stream ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` message.log:6925 teleport in stream ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` message.log:7915 teleport in stream ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:3543 teleport in stream ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:4452 teleport in stream ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:5376 teleport in stream ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:6271 teleport in stream ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:7199 teleport in stream ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:3851 teleport in stream ('HSD', 'cl', 'edge', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:4716 teleport in stream ('HSD', 'cl', 'edge', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` script.log:5688 teleport in stream ('HSD', 'cl', 'edge', None, '768d7e65-06ff-4320-9597-a457967f2eab')
- warning `W_TELEPORT` message.log:3685 teleport in stream ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TELEPORT` message.log:4519 teleport in stream ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TELEPORT` message.log:5379 teleport in stream ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TELEPORT` message.log:6196 teleport in stream ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TELEPORT` message.log:7043 teleport in stream ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TELEPORT` script.log:772 teleport in stream ('HSD', 'sv', 'evt', 1.0, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')
- warning `W_TIME_BACKWARDS` script.log:718 t 24.75 -> 24.52072 in ('HSD', 'sv', 'evt', 1.0, '2b894f0e-2e9f-4ebe-b25e-e7ca2bd886ee')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3310 | 0 | - | - |
| MT | cl | r90 | 653 | 592.716 | - | - |
| MT | cl | b1 | 179 | 0 | - | - |
| MT | cl | r2531 | 679 | 600.898 | - | - |
| MT | cl | b2 | 192 | 0 | - | - |
| MT | cl | r2532 | 649 | 595.54 | - | - |
| MT | cl | b3 | 166 | 0 | - | - |
| MT | cl | r2533 | 658 | 612.747 | first_order (yes) | friction (no) |
| MT | cl | b4 | 187 | 0 | - | - |
| MT | cl | r2534 | 656 | 611.764 | first_order (yes) | friction (no) |
| MT | cl | b5 | 190 | 0 | - | - |
| MT | cl | r2535 | 656 | 612.395 | first_order (yes) | linear (no) |
| MT | cl | b6 | 153 | 0 | - | - |
| HSD | cl | r0 | 4358 | 0 | - | - |
| HSD | cl | r90 | 721 | 592.716 | - | - |
| HSD | cl | r2531 | 721 | 600.898 | - | - |
| HSD | cl | r2532 | 721 | 595.54 | - | - |
| HSD | cl | r2533 | 727 | 612.747 | first_order (yes) | linear (no) |
| HSD | cl | r2534 | 727 | 611.764 | first_order (yes) | linear (no) |
| HSD | cl | r2535 | 727 | 612.395 | first_order (yes) | linear (no) |
| MT | sv | b0 | 3321 | 0 | - | - |
| MT | sv | r90 | 653 | 592.701 | - | - |
| MT | sv | b1 | 179 | 0 | - | - |
| MT | sv | r2531 | 666 | 600.902 | - | - |
| MT | sv | b2 | 192 | 0 | - | - |
| MT | sv | r2532 | 649 | 595.523 | - | - |
| MT | sv | b3 | 166 | 0 | - | - |
| MT | sv | r2533 | 658 | 612.736 | first_order (yes) | friction (no) |
| MT | sv | b4 | 187 | 0 | - | - |
| MT | sv | r2534 | 656 | 611.76 | first_order (yes) | friction (no) |
| MT | sv | b5 | 190 | 0 | - | - |
| MT | sv | r2535 | 656 | 612.401 | first_order (yes) | linear (no) |
| MT | sv | b6 | 149 | 0 | - | - |

Events: 76. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
