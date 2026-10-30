# hsd_tel report

Inputs: 16 file(s); rows: 16475 (MT 10853, HSD 5620)

Validation: 0 error(s), 10 warning(s), 6 info

- warning `W_TELEPORT` message.log:4015 teleport in stream ('MT', 'cl', 'cmd', 1, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` message.log:4737 teleport in stream ('MT', 'cl', 'cmd', 1, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` message.log:5424 teleport in stream ('MT', 'cl', 'cmd', 1, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` script.log:3647 teleport in stream ('HSD', 'cl', 'frame', None, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` script.log:4938 teleport in stream ('HSD', 'cl', 'frame', None, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` script.log:6200 teleport in stream ('HSD', 'cl', 'frame', None, 'cc445e3d-a2ff-408c-a255-4192931638b9')
- warning `W_TELEPORT` message.log:3801 teleport in stream ('MT', 'sv', 'cmd', 1, '530e4352-c264-4d6e-83e0-22517c54e812')
- warning `W_TELEPORT` message.log:4472 teleport in stream ('MT', 'sv', 'cmd', 1, '530e4352-c264-4d6e-83e0-22517c54e812')
- warning `W_TELEPORT` message.log:5113 teleport in stream ('MT', 'sv', 'cmd', 1, '530e4352-c264-4d6e-83e0-22517c54e812')
- warning `W_TIME_BACKWARDS` script.log:718 t 25.9 -> 25.55298 in ('HSD', 'sv', 'evt', 1.0, '530e4352-c264-4d6e-83e0-22517c54e812')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3430 | 0 | - | - |
| MT | cl | r90 | 474 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b1 | 193 | 0 | - | - |
| MT | cl | r9011 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 169 | 0 | - | - |
| MT | cl | r9012 | 520 | 299.71 | first_order (no) | linear (yes) |
| MT | cl | b3 | 144 | 0 | - | - |
| HSD | cl | r0 | 3902 | 0 | - | - |
| HSD | cl | r90 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r9011 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9012 | 589 | 299.71 | first_order (no) | - |
| MT | sv | b0 | 3442 | 0 | - | - |
| MT | sv | r90 | 474 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b1 | 193 | 0 | - | - |
| MT | sv | r9011 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 169 | 0 | - | - |
| MT | sv | r9012 | 520 | 299.71 | first_order (no) | linear (yes) |
| MT | sv | b3 | 142 | 0 | - | - |

Events: 61. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
