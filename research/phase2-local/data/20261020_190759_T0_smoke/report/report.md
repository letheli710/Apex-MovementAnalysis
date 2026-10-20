# hsd_tel report

Inputs: 16 file(s); rows: 23589 (MT 15619, HSD 7912)

Validation: 0 error(s), 2 warning(s), 24 info

- warning `W_TELEPORT` script.log:706 teleport in stream ('HSD', 'sv', 'evt', 1.0)
- warning `W_TIME_BACKWARDS` script.log:690 t 324.45001 -> 324.18283 in ('HSD', 'sv', 'evt', 1.0)

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | r1 | 2811 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | b0 | 4992 | 0 | - | - |
| HSD | cl | r1 | 2788 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 4993 | 0 | - | - |
| MT | sv | b0 | 5 | 0 | - | - |
| MT | sv | r1 | 7797 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
