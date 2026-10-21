# hsd_tel report

Inputs: 16 file(s); rows: 16111 (MT 10761, HSD 5348)

Validation: 0 error(s), 4 warning(s), 2 info

- warning `W_TELEPORT` message.log:3368 teleport in stream ('MT', 'cl', 'cmd', 1, 'f280cea7-dc60-4728-8b69-27675df8d432')
- warning `W_TELEPORT` script.log:3004 teleport in stream ('HSD', 'cl', 'frame', None, 'f280cea7-dc60-4728-8b69-27675df8d432')
- warning `W_TELEPORT` message.log:3160 teleport in stream ('MT', 'sv', 'cmd', 1, '61ccc10f-a099-45ca-91a5-b7bd23adae0a')
- warning `W_TIME_BACKWARDS` script.log:712 t 27.5 -> 27.22229 in ('HSD', 'sv', 'evt', 1.0, '61ccc10f-a099-45ca-91a5-b7bd23adae0a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3603 | 0 | - | - |
| MT | cl | r90 | 360 | 0 | - | - |
| MT | cl | r2431 | 360 | 0 | - | - |
| MT | cl | r2432 | 360 | 0 | - | - |
| MT | cl | r2433 | 336 | 0 | - | - |
| MT | cl | r2434 | 336 | 0 | - | - |
| HSD | cl | r0 | 3572 | 0 | - | - |
| HSD | cl | r90 | 360 | 0 | - | - |
| HSD | cl | r2431 | 360 | 0 | - | - |
| HSD | cl | r2432 | 360 | 0 | - | - |
| HSD | cl | r2433 | 336 | 0 | - | - |
| HSD | cl | r2434 | 336 | 0 | - | - |
| MT | sv | b0 | 3618 | 0 | - | - |
| MT | sv | r90 | 360 | 0 | - | - |
| MT | sv | r2431 | 360 | 0 | - | - |
| MT | sv | r2432 | 360 | 0 | - | - |
| MT | sv | r2433 | 336 | 0 | - | - |
| MT | sv | r2434 | 336 | 0 | - | - |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
