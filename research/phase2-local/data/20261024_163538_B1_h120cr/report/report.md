# hsd_tel report

Inputs: 16 file(s); rows: 32167 (MT 20795, HSD 11370)

Validation: 0 error(s), 21 warning(s), 6 info

- warning `W_TELEPORT` message.log:4039 teleport in stream ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` message.log:4806 teleport in stream ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` message.log:5550 teleport in stream ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` message.log:6311 teleport in stream ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` message.log:7106 teleport in stream ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` script.log:3672 teleport in stream ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` script.log:5047 teleport in stream ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` script.log:6425 teleport in stream ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` script.log:7812 teleport in stream ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` script.log:9234 teleport in stream ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, '8ef5e0bd-e029-4963-aa80-dc586930b9c4')
- warning `W_TELEPORT` message.log:3819 teleport in stream ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` message.log:4495 teleport in stream ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` message.log:5194 teleport in stream ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` message.log:5870 teleport in stream ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` message.log:6577 teleport in stream ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` script.log:787 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TELEPORT` script.log:859 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')
- warning `W_TIME_BACKWARDS` script.log:717 t 26.55 -> 26.387 in ('HSD', 'sv', 'evt', 1.0, 'c65de9da-d4bd-4684-bbe0-4dbd0369eb2c')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3443 | 0 | - | - |
| MT | cl | r90 | 492 | 389.225 | first_order (no) | linear (yes) |
| MT | cl | b1 | 175 | 0 | - | - |
| MT | cl | r9800 | 513 | 460 | first_order (no) | linear (yes) |
| MT | cl | b2 | 175 | 0 | - | - |
| MT | cl | r9801 | 500 | 389.307 | first_order (no) | linear (yes) |
| MT | cl | b3 | 169 | 0 | - | - |
| MT | cl | r9802 | 506 | 389.383 | first_order (no) | linear (yes) |
| MT | cl | b4 | 194 | 0 | - | - |
| MT | cl | r9803 | 512 | 389.406 | first_order (no) | linear (yes) |
| MT | cl | b5 | 188 | 0 | - | - |
| MT | cl | r9804 | 518 | 389.41 | first_order (no) | linear (yes) |
| MT | cl | b6 | 181 | 0 | - | - |
| MT | cl | r9805 | 524 | 389.406 | first_order (no) | linear (yes) |
| MT | cl | b7 | 175 | 0 | - | - |
| MT | cl | r9806 | 524 | 389.406 | first_order (no) | linear (yes) |
| MT | cl | b8 | 175 | 0 | - | - |
| MT | cl | r9807 | 533 | 389.406 | first_order (no) | friction (no) |
| MT | cl | b9 | 167 | 0 | - | - |
| MT | cl | r9808 | 536 | 389.406 | first_order (no) | friction (no) |
| MT | cl | b10 | 159 | 0 | - | - |
| HSD | cl | r0 | 5179 | 0 | - | - |
| HSD | cl | r90 | 590 | 389.225 | - | linear (yes) |
| HSD | cl | r9800 | 592 | 460 | - | linear (yes) |
| HSD | cl | r9801 | 599 | 389.307 | - | linear (yes) |
| HSD | cl | r9802 | 604 | 389.383 | - | linear (yes) |
| HSD | cl | r9803 | 610 | 389.406 | - | linear (yes) |
| HSD | cl | r9804 | 616 | 389.41 | - | linear (yes) |
| HSD | cl | r9805 | 623 | 389.406 | - | linear (yes) |
| HSD | cl | r9806 | 593 | 389.406 | - | linear (yes) |
| HSD | cl | r9807 | 601 | 389.406 | - | friction (no) |
| HSD | cl | r9808 | 605 | 389.406 | - | friction (no) |
| MT | sv | b0 | 3458 | 0 | - | - |
| MT | sv | r90 | 491 | 389.225 | first_order (no) | linear (yes) |
| MT | sv | b1 | 175 | 0 | - | - |
| MT | sv | r9800 | 513 | 460 | first_order (no) | linear (yes) |
| MT | sv | b2 | 175 | 0 | - | - |
| MT | sv | r9801 | 500 | 389.307 | first_order (no) | linear (yes) |
| MT | sv | b3 | 169 | 0 | - | - |
| MT | sv | r9802 | 506 | 389.383 | first_order (no) | linear (yes) |
| MT | sv | b4 | 194 | 0 | - | - |
| MT | sv | r9803 | 512 | 389.406 | first_order (no) | linear (yes) |
| MT | sv | b5 | 188 | 0 | - | - |
| MT | sv | r9804 | 518 | 389.41 | first_order (no) | linear (yes) |
| MT | sv | b6 | 181 | 0 | - | - |
| MT | sv | r9805 | 524 | 389.406 | first_order (no) | linear (yes) |
| MT | sv | b7 | 175 | 0 | - | - |
| MT | sv | r9806 | 524 | 389.406 | first_order (no) | linear (yes) |
| MT | sv | b8 | 175 | 0 | - | - |
| MT | sv | r9807 | 533 | 389.406 | first_order (no) | friction (no) |
| MT | sv | b9 | 167 | 0 | - | - |
| MT | sv | r9808 | 536 | 389.406 | first_order (no) | friction (no) |
| MT | sv | b10 | 150 | 0 | - | - |

Events: 240. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
