# hsd_tel report

> Input contains SYNTHETIC test data (hsdtel.synth, '# SYNTHETIC' header). Not Apex measurements.

Inputs: 4 file(s); rows: 6302 (MT 4181, HSD 2117)

Validation: 0 error(s), 0 warning(s), 3 info


## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | r1 | 619 | 300 | linear (yes) | friction (yes) |
| MT | cl | r2 | 630 | 556.224 | linear (no) | friction (yes) |
| MT | cl | r3 | 821 | 300 | linear (yes) | friction (no) |
| HSD | cl | r1 | 619 | 300 | linear (yes) | friction (yes) |
| HSD | cl | r2 | 630 | 556.224 | linear (no) | friction (yes) |
| HSD | cl | r3 | 821 | 300 | linear (yes) | friction (no) |
| MT | sv | r1 | 619 | 300 | linear (yes) | friction (yes) |
| MT | sv | r2 | 630 | 556.224 | linear (no) | friction (yes) |
| MT | sv | r3 | 821 | 300 | linear (yes) | friction (no) |

Events: 74. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
