# hsd_tel report

Inputs: 16 file(s); rows: 13512 (MT 8576, HSD 4265)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4338 teleport in stream ('MT', 'cl', 'cmd', 1, '9da13b37-1d5b-4934-a9a3-78dfeb76333b')
- warning `W_TELEPORT` script.log:3324 teleport in stream ('HSD', 'cl', 'frame', None, '9da13b37-1d5b-4934-a9a3-78dfeb76333b')
- warning `W_TELEPORT` message.log:3457 teleport in stream ('MT', 'sv', 'cmd', 1, '00986d91-c4e0-4a06-a1dd-f8e9056780da')
- warning `W_TELEPORT` script.log:773 teleport in stream ('HSD', 'sv', 'evt', 1.0, '00986d91-c4e0-4a06-a1dd-f8e9056780da')
- warning `W_TIME_BACKWARDS` script.log:711 t 23.15 -> 22.96271 in ('HSD', 'sv', 'evt', 1.0, '00986d91-c4e0-4a06-a1dd-f8e9056780da')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3249 | 0 | - | - |
| MT | cl | r20106 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3231 | 0 | - | - |
| HSD | cl | r20106 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3256 | 0 | - | - |
| MT | sv | r20106 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
