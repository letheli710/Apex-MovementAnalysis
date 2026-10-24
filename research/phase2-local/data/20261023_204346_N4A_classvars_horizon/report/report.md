# hsd_tel report

Inputs: 16 file(s); rows: 13615 (MT 8655, HSD 4289)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4418 teleport in stream ('MT', 'cl', 'cmd', 1, '43174a26-6b0c-4c67-8589-f0d7281ab398')
- warning `W_TELEPORT` script.log:3381 teleport in stream ('HSD', 'cl', 'frame', None, '43174a26-6b0c-4c67-8589-f0d7281ab398')
- warning `W_TELEPORT` message.log:3521 teleport in stream ('MT', 'sv', 'cmd', 1, 'b11f320c-7d98-4a19-891d-f1fc39e3ad4f')
- warning `W_TELEPORT` script.log:776 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'b11f320c-7d98-4a19-891d-f1fc39e3ad4f')
- warning `W_TIME_BACKWARDS` script.log:714 t 22.7 -> 22.54731 in ('HSD', 'sv', 'evt', 1.0, 'b11f320c-7d98-4a19-891d-f1fc39e3ad4f')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3275 | 0 | - | - |
| MT | cl | r20104 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3255 | 0 | - | - |
| HSD | cl | r20104 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3287 | 0 | - | - |
| MT | sv | r20104 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
