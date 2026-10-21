# hsd_tel report

Inputs: 16 file(s); rows: 15021 (MT 10023, HSD 4996)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4175 teleport in stream ('MT', 'cl', 'cmd', 1, 'd991264a-4715-4ce2-9fcd-c74eab27c6a0')
- warning `W_TELEPORT` script.log:3851 teleport in stream ('HSD', 'cl', 'frame', None, 'd991264a-4715-4ce2-9fcd-c74eab27c6a0')
- warning `W_TELEPORT` message.log:3994 teleport in stream ('MT', 'sv', 'cmd', 1, '82497c0b-b9ab-4241-a9ca-ef09512aa85e')
- warning `W_TELEPORT` script.log:732 teleport in stream ('HSD', 'sv', 'evt', 1.0, '82497c0b-b9ab-4241-a9ca-ef09512aa85e')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.1 -> 22.9304 in ('HSD', 'sv', 'evt', 1.0, '82497c0b-b9ab-4241-a9ca-ef09512aa85e')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2553 | 0 | - | - |
| MT | cl | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r46 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 2524 | 0 | - | - |
| HSD | cl | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r46 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 2564 | 0 | - | - |
| MT | sv | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r46 | 1225 | 199.525 | first_order (yes) | linear (yes) |

Events: 24. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
