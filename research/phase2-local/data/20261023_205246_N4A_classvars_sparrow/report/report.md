# hsd_tel report

Inputs: 16 file(s); rows: 13383 (MT 8504, HSD 4208)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4318 teleport in stream ('MT', 'cl', 'cmd', 1, 'd14fad08-e400-47cb-bf19-e772a5490d5f')
- warning `W_TELEPORT` script.log:3298 teleport in stream ('HSD', 'cl', 'frame', None, 'd14fad08-e400-47cb-bf19-e772a5490d5f')
- warning `W_TELEPORT` message.log:3467 teleport in stream ('MT', 'sv', 'cmd', 1, '2b76a81a-3d3c-4d83-ab00-db92162f8520')
- warning `W_TELEPORT` script.log:778 teleport in stream ('HSD', 'sv', 'evt', 1.0, '2b76a81a-3d3c-4d83-ab00-db92162f8520')
- warning `W_TIME_BACKWARDS` script.log:716 t 23.3 -> 23.05078 in ('HSD', 'sv', 'evt', 1.0, '2b76a81a-3d3c-4d83-ab00-db92162f8520')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3206 | 0 | - | - |
| MT | cl | r20111 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3174 | 0 | - | - |
| HSD | cl | r20111 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3233 | 0 | - | - |
| MT | sv | r20111 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
