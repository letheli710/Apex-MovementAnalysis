# hsd_tel report

Inputs: 16 file(s); rows: 6563 (MT 4397, HSD 2164)

Validation: 0 error(s), 2 warning(s), 2 info

- warning `W_TELEPORT` script.log:730 teleport in stream ('HSD', 'sv', 'evt', 1.0, '97fc9877-df72-4717-9feb-f39fb09e42a4')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.45 -> 25.28612 in ('HSD', 'sv', 'evt', 1.0, '97fc9877-df72-4717-9feb-f39fb09e42a4')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 895 | 0 | - | - |
| MT | cl | r26 | 1280 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 871 | 0 | - | - |
| HSD | cl | r26 | 1280 | 199.525 | first_order (yes) | friction (no) |
| MT | sv | b0 | 905 | 0 | - | - |
| MT | sv | r26 | 1280 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
