# hsd_tel report

Inputs: 16 file(s); rows: 13384 (MT 8503, HSD 4210)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4324 teleport in stream ('MT', 'cl', 'cmd', 1, '8527c9a8-0508-4e2b-9d94-ef426a83ac34')
- warning `W_TELEPORT` script.log:3295 teleport in stream ('HSD', 'cl', 'frame', None, '8527c9a8-0508-4e2b-9d94-ef426a83ac34')
- warning `W_TELEPORT` message.log:3452 teleport in stream ('MT', 'sv', 'cmd', 1, '7d7409ea-7557-4838-823b-7f3cced52467')
- warning `W_TELEPORT` script.log:777 teleport in stream ('HSD', 'sv', 'evt', 1.0, '7d7409ea-7557-4838-823b-7f3cced52467')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.9 -> 23.73514 in ('HSD', 'sv', 'evt', 1.0, '7d7409ea-7557-4838-823b-7f3cced52467')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3203 | 0 | - | - |
| MT | cl | r20102 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3176 | 0 | - | - |
| HSD | cl | r20102 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3223 | 0 | - | - |
| MT | sv | r20102 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
