# hsd_tel report

Inputs: 16 file(s); rows: 13401 (MT 8511, HSD 4219)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4333 teleport in stream ('MT', 'cl', 'cmd', 1, '439f8ca5-193e-4c3a-bb25-a986db99fe61')
- warning `W_TELEPORT` script.log:3310 teleport in stream ('HSD', 'cl', 'frame', None, '439f8ca5-193e-4c3a-bb25-a986db99fe61')
- warning `W_TELEPORT` message.log:3461 teleport in stream ('MT', 'sv', 'cmd', 1, 'cd0fe3f6-8aca-43ce-9350-905fe00dec85')
- warning `W_TELEPORT` script.log:777 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'cd0fe3f6-8aca-43ce-9350-905fe00dec85')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.4 -> 23.20821 in ('HSD', 'sv', 'evt', 1.0, 'cd0fe3f6-8aca-43ce-9350-905fe00dec85')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3211 | 0 | - | - |
| MT | cl | r20108 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3185 | 0 | - | - |
| HSD | cl | r20108 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3228 | 0 | - | - |
| MT | sv | r20108 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
