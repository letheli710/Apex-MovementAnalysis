# hsd_tel report

Inputs: 16 file(s); rows: 56465 (MT 37556, HSD 18907)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3025 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` message.log:4017 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` message.log:5009 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` message.log:6002 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` message.log:6996 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` script.log:2674 teleport in stream ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` script.log:3667 teleport in stream ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` script.log:4662 teleport in stream ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` script.log:5657 teleport in stream ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` script.log:6653 teleport in stream ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_MORE` script.log:0 11 more teleport rows in ('HSD', 'cl', 'frame', None, '72fb7bfb-678e-40f5-8284-91e06e1bc38e')
- warning `W_TELEPORT` message.log:2809 teleport in stream ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_TELEPORT` message.log:3798 teleport in stream ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_TELEPORT` message.log:4787 teleport in stream ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_TELEPORT` message.log:5775 teleport in stream ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_TELEPORT` message.log:6764 teleport in stream ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, 'd297b885-f448-4964-b208-deef2a4a36f1')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.1 -> 23.92106 in ('HSD', 'sv', 'evt', 1.0, 'd297b885-f448-4964-b208-deef2a4a36f1')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5563 | 0 | - | - |
| MT | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r801 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r802 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r803 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r804 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r805 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r806 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | cl | r807 | 653 | 299.032 | first_order (no) | friction (no) |
| MT | cl | r808 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | cl | r809 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | cl | r810 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | cl | r811 | 1031 | 458.101 | first_order (no) | linear (no) |
| MT | cl | r812 | 1031 | 458.104 | first_order (no) | linear (no) |
| MT | cl | r813 | 1031 | 458.109 | first_order (no) | linear (no) |
| MT | cl | r814 | 1031 | 458.058 | first_order (no) | linear (no) |
| MT | cl | r815 | 1031 | 458.105 | first_order (no) | linear (no) |
| HSD | cl | r0 | 5542 | 0 | - | - |
| HSD | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r801 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r802 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r803 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r804 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r805 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r806 | 653 | 299.033 | first_order (no) | linear (yes) |
| HSD | cl | r807 | 653 | 299.032 | first_order (no) | linear (yes) |
| HSD | cl | r808 | 653 | 299.033 | first_order (no) | linear (yes) |
| HSD | cl | r809 | 653 | 299.033 | first_order (no) | linear (yes) |
| HSD | cl | r810 | 653 | 299.033 | first_order (no) | linear (yes) |
| HSD | cl | r811 | 1031 | 458.101 | first_order (no) | linear (no) |
| HSD | cl | r812 | 1031 | 458.104 | first_order (no) | linear (no) |
| HSD | cl | r813 | 1031 | 458.109 | first_order (no) | linear (no) |
| HSD | cl | r814 | 1031 | 458.058 | first_order (no) | linear (no) |
| HSD | cl | r815 | 1031 | 458.105 | first_order (no) | linear (no) |
| MT | sv | b0 | 5567 | 0 | - | - |
| MT | sv | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r801 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r802 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r803 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r804 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r805 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r806 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | sv | r807 | 653 | 299.032 | first_order (no) | friction (no) |
| MT | sv | r808 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | sv | r809 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | sv | r810 | 653 | 299.033 | first_order (no) | friction (no) |
| MT | sv | r811 | 1031 | 458.101 | first_order (no) | linear (no) |
| MT | sv | r812 | 1031 | 458.104 | first_order (no) | linear (no) |
| MT | sv | r813 | 1031 | 458.109 | first_order (no) | linear (no) |
| MT | sv | r814 | 1031 | 458.058 | first_order (no) | linear (no) |
| MT | sv | r815 | 1031 | 458.105 | first_order (no) | linear (no) |

Events: 307. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
