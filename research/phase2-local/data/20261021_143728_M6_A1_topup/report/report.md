# hsd_tel report

Inputs: 16 file(s); rows: 23920 (MT 15916, HSD 8002)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3524 teleport in stream ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` message.log:4082 teleport in stream ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` message.log:4643 teleport in stream ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` message.log:5202 teleport in stream ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` message.log:5762 teleport in stream ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'cl', 'cmd', 1, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` script.log:3188 teleport in stream ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` script.log:3762 teleport in stream ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` script.log:4338 teleport in stream ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` script.log:4914 teleport in stream ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` script.log:5490 teleport in stream ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_MORE` script.log:0 4 more teleport rows in ('HSD', 'cl', 'frame', None, 'df9ea06f-0123-4d78-9414-11de38330e99')
- warning `W_TELEPORT` message.log:3327 teleport in stream ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_TELEPORT` message.log:3885 teleport in stream ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_TELEPORT` message.log:4442 teleport in stream ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_TELEPORT` message.log:5000 teleport in stream ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_TELEPORT` message.log:5558 teleport in stream ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'sv', 'cmd', 1, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')
- warning `W_TIME_BACKWARDS` script.log:716 t 24.9 -> 24.76554 in ('HSD', 'sv', 'evt', 1.0, '84fdd5d2-6257-41cc-8bfb-9be3a3ca3e2e')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4617 | 0 | - | - |
| MT | cl | r90 | 370 | 297.105 | first_order (no) | friction (no) |
| MT | cl | r2801 | 370 | 296.63 | first_order (no) | friction (no) |
| MT | cl | r2802 | 370 | 295.868 | first_order (no) | friction (no) |
| MT | cl | r2803 | 370 | 297.59 | first_order (no) | friction (no) |
| MT | cl | r2804 | 370 | 296.664 | first_order (no) | friction (no) |
| MT | cl | r2805 | 370 | 296.595 | first_order (no) | friction (no) |
| MT | cl | r2806 | 370 | 296.659 | first_order (no) | friction (no) |
| MT | cl | r2807 | 365 | 296.665 | first_order (no) | linear (no) |
| MT | cl | r2808 | 365 | 296.662 | first_order (no) | linear (no) |
| HSD | cl | r0 | 4597 | 0 | - | - |
| HSD | cl | r90 | 370 | 297.105 | first_order (no) | friction (no) |
| HSD | cl | r2801 | 370 | 296.63 | first_order (no) | friction (no) |
| HSD | cl | r2802 | 370 | 295.868 | first_order (no) | friction (no) |
| HSD | cl | r2803 | 370 | 297.59 | first_order (no) | friction (no) |
| HSD | cl | r2804 | 370 | 296.664 | first_order (no) | friction (no) |
| HSD | cl | r2805 | 370 | 296.595 | first_order (no) | friction (no) |
| HSD | cl | r2806 | 370 | 296.659 | first_order (no) | friction (no) |
| HSD | cl | r2807 | 365 | 296.665 | first_order (no) | linear (no) |
| HSD | cl | r2808 | 365 | 296.662 | first_order (no) | linear (no) |
| MT | sv | b0 | 4628 | 0 | - | - |
| MT | sv | r90 | 370 | 297.105 | first_order (no) | friction (no) |
| MT | sv | r2801 | 370 | 296.63 | first_order (no) | friction (no) |
| MT | sv | r2802 | 370 | 295.868 | first_order (no) | friction (no) |
| MT | sv | r2803 | 370 | 297.59 | first_order (no) | friction (no) |
| MT | sv | r2804 | 370 | 296.664 | first_order (no) | friction (no) |
| MT | sv | r2805 | 370 | 296.595 | first_order (no) | friction (no) |
| MT | sv | r2806 | 370 | 296.659 | first_order (no) | friction (no) |
| MT | sv | r2807 | 365 | 296.665 | first_order (no) | linear (no) |
| MT | sv | r2808 | 365 | 296.662 | first_order (no) | linear (no) |

Events: 101. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
