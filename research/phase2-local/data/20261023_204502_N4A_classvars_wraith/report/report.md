# hsd_tel report

Inputs: 16 file(s); rows: 13471 (MT 8554, HSD 4246)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4358 teleport in stream ('MT', 'cl', 'cmd', 1, '20690dc3-63fc-44c3-8aca-ffff401b57f0')
- warning `W_TELEPORT` script.log:3337 teleport in stream ('HSD', 'cl', 'frame', None, '20690dc3-63fc-44c3-8aca-ffff401b57f0')
- warning `W_TELEPORT` message.log:3480 teleport in stream ('MT', 'sv', 'cmd', 1, 'd9138968-baec-4d75-89e4-7828c3779804')
- warning `W_TELEPORT` script.log:779 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd9138968-baec-4d75-89e4-7828c3779804')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.15 -> 23.0498 in ('HSD', 'sv', 'evt', 1.0, 'd9138968-baec-4d75-89e4-7828c3779804')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3239 | 0 | - | - |
| MT | cl | r20105 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3212 | 0 | - | - |
| HSD | cl | r20105 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3246 | 0 | - | - |
| MT | sv | r20105 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
