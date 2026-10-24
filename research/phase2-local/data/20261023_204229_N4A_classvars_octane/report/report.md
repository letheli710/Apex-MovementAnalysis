# hsd_tel report

Inputs: 16 file(s); rows: 13287 (MT 8437, HSD 4179)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4310 teleport in stream ('MT', 'cl', 'cmd', 1, 'b2974075-971a-44d9-b7fb-d94aa5717630')
- warning `W_TELEPORT` script.log:3270 teleport in stream ('HSD', 'cl', 'frame', None, 'b2974075-971a-44d9-b7fb-d94aa5717630')
- warning `W_TELEPORT` message.log:3427 teleport in stream ('MT', 'sv', 'cmd', 1, '7aa8f594-21dc-4754-aa02-2bdec5a1c29b')
- warning `W_TELEPORT` script.log:775 teleport in stream ('HSD', 'sv', 'evt', 1.0, '7aa8f594-21dc-4754-aa02-2bdec5a1c29b')
- warning `W_TIME_BACKWARDS` script.log:713 t 24.45 -> 24.25718 in ('HSD', 'sv', 'evt', 1.0, '7aa8f594-21dc-4754-aa02-2bdec5a1c29b')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3174 | 0 | - | - |
| MT | cl | r20103 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3145 | 0 | - | - |
| HSD | cl | r20103 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3195 | 0 | - | - |
| MT | sv | r20103 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
