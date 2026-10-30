# hsd_tel report

Inputs: 16 file(s); rows: 8269 (MT 5529, HSD 2738)

Validation: 0 error(s), 1 warning(s), 2 info

- warning `W_TIME_BACKWARDS` script.log:715 t 26.05 -> 25.78392 in ('HSD', 'sv', 'evt', 1.0, '8e9b9317-9e26-40ae-bdc5-2225085f110e')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2756 | 0 | - | - |
| HSD | cl | r0 | 2734 | 0 | - | - |
| MT | sv | b0 | 2763 | 0 | - | - |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
