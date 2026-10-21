# hsd_tel report

Inputs: 16 file(s); rows: 8498 (MT 5569, HSD 2869)

Validation: 0 error(s), 1 warning(s), 24 info

- warning `W_TIME_BACKWARDS` script.log:713 t 27.3 -> 27.04663 in ('HSD', 'sv', 'evt', 1.0, '2eb9142b-d3b5-41c3-84af-a4ba2cb54311')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2772 | 0 | - | - |
| HSD | cl | r0 | 2746 | 0 | - | - |
| MT | sv | b0 | 2778 | 0 | - | - |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
