# hsd_tel report

Inputs: 19 file(s); rows: 189775 (MT 126538, HSD 63237)

Validation: 0 error(s), 2 warning(s), 2 info

- warning `W_TELEPORT` script.log:734 teleport in stream ('HSD', 'sv', 'evt', 1.0)
- warning `W_TIME_BACKWARDS` script.log:717 t 23.75 -> 23.51931 in ('HSD', 'sv', 'evt', 1.0)

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 61977 | 0 | - | - |
| MT | cl | r16 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 61950 | 0 | - | - |
| HSD | cl | r16 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 61985 | 0 | - | - |
| MT | sv | r16 | 1281 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
