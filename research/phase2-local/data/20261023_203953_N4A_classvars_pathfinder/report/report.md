# hsd_tel report

Inputs: 16 file(s); rows: 15162 (MT 9691, HSD 4800)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4939 teleport in stream ('MT', 'cl', 'cmd', 1, '86d217cb-9d9a-46d7-9948-07a67139fa0a')
- warning `W_TELEPORT` script.log:3892 teleport in stream ('HSD', 'cl', 'frame', None, '86d217cb-9d9a-46d7-9948-07a67139fa0a')
- warning `W_TELEPORT` message.log:4039 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae711007-bb89-4d41-bb61-4b8d4a515acf')
- warning `W_TELEPORT` script.log:775 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ae711007-bb89-4d41-bb61-4b8d4a515acf')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.35 -> 25.15508 in ('HSD', 'sv', 'evt', 1.0, 'ae711007-bb89-4d41-bb61-4b8d4a515acf')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3787 | 0 | - | - |
| MT | cl | r20101 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3766 | 0 | - | - |
| HSD | cl | r20101 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3805 | 0 | - | - |
| MT | sv | r20101 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
