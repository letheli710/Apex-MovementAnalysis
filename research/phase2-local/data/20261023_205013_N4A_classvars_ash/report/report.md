# hsd_tel report

Inputs: 16 file(s); rows: 13471 (MT 8564, HSD 4236)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4332 teleport in stream ('MT', 'cl', 'cmd', 1, '95a6d4d7-884e-4ca2-befd-2fb988dce775')
- warning `W_TELEPORT` script.log:3298 teleport in stream ('HSD', 'cl', 'frame', None, '95a6d4d7-884e-4ca2-befd-2fb988dce775')
- warning `W_TELEPORT` message.log:3464 teleport in stream ('MT', 'sv', 'cmd', 1, '1781717d-7c4c-4c87-8b4f-53f379cf9df5')
- warning `W_TELEPORT` script.log:782 teleport in stream ('HSD', 'sv', 'evt', 1.0, '1781717d-7c4c-4c87-8b4f-53f379cf9df5')
- warning `W_TIME_BACKWARDS` script.log:718 t 23.65 -> 23.42908 in ('HSD', 'sv', 'evt', 1.0, '1781717d-7c4c-4c87-8b4f-53f379cf9df5')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3236 | 0 | - | - |
| MT | cl | r20109 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3202 | 0 | - | - |
| HSD | cl | r20109 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3255 | 0 | - | - |
| MT | sv | r20109 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
