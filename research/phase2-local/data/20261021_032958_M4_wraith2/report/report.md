# hsd_tel report

Inputs: 16 file(s); rows: 21541 (MT 14404, HSD 7135)

Validation: 0 error(s), 13 warning(s), 2 info

- warning `W_TELEPORT` message.log:4080 teleport in stream ('MT', 'cl', 'cmd', 1, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` message.log:5009 teleport in stream ('MT', 'cl', 'cmd', 1, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` message.log:5947 teleport in stream ('MT', 'cl', 'cmd', 1, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` message.log:6893 teleport in stream ('MT', 'cl', 'cmd', 1, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` script.log:3720 teleport in stream ('HSD', 'cl', 'frame', None, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` script.log:4644 teleport in stream ('HSD', 'cl', 'frame', None, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` script.log:5573 teleport in stream ('HSD', 'cl', 'frame', None, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` script.log:6501 teleport in stream ('HSD', 'cl', 'frame', None, '8b2f65c7-268c-49b8-bbbb-6bf3426f370b')
- warning `W_TELEPORT` message.log:3865 teleport in stream ('MT', 'sv', 'cmd', 1, '3b0b8445-9d0f-4114-b759-a576e5418c00')
- warning `W_TELEPORT` message.log:4785 teleport in stream ('MT', 'sv', 'cmd', 1, '3b0b8445-9d0f-4114-b759-a576e5418c00')
- warning `W_TELEPORT` message.log:5701 teleport in stream ('MT', 'sv', 'cmd', 1, '3b0b8445-9d0f-4114-b759-a576e5418c00')
- warning `W_TELEPORT` message.log:6617 teleport in stream ('MT', 'sv', 'cmd', 1, '3b0b8445-9d0f-4114-b759-a576e5418c00')
- warning `W_TIME_BACKWARDS` script.log:718 t 28.45 -> 28.14262 in ('HSD', 'sv', 'evt', 1.0, '3b0b8445-9d0f-4114-b759-a576e5418c00')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4160 | 0 | - | - |
| MT | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2641 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2642 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2643 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r0 | 4135 | 0 | - | - |
| HSD | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2641 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2642 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2643 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | b0 | 4171 | 0 | - | - |
| MT | sv | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2641 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2642 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2643 | 745 | 414.98 | first_order (no) | friction (no) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
