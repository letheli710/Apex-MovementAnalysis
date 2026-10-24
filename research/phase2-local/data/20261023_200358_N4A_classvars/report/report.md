# hsd_tel report

Inputs: 16 file(s); rows: 14020 (MT 8809, HSD 4482)

Validation: 0 error(s), 5 warning(s), 24 info

- warning `W_TELEPORT` message.log:4540 teleport in stream ('MT', 'cl', 'cmd', 1, '754ff315-c367-4521-bb17-cfb795cd0d97')
- warning `W_TELEPORT` script.log:3516 teleport in stream ('HSD', 'cl', 'frame', None, '754ff315-c367-4521-bb17-cfb795cd0d97')
- warning `W_TELEPORT` message.log:3615 teleport in stream ('MT', 'sv', 'cmd', 1, '7b6fd98d-f22b-4857-b493-c583c7c4dc32')
- warning `W_TELEPORT` script.log:835 teleport in stream ('HSD', 'sv', 'evt', 1.0, '7b6fd98d-f22b-4857-b493-c583c7c4dc32')
- warning `W_TIME_BACKWARDS` script.log:714 t 33.25 -> 33.0433 in ('HSD', 'sv', 'evt', 1.0, '7b6fd98d-f22b-4857-b493-c583c7c4dc32')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3358 | 0 | - | - |
| MT | cl | r20001 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3330 | 0 | - | - |
| HSD | cl | r20001 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3380 | 0 | - | - |
| MT | sv | r20001 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
