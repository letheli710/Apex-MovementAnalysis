# hsd_tel report

Inputs: 16 file(s); rows: 15492 (MT 10337, HSD 5153)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4334 teleport in stream ('MT', 'cl', 'cmd', 1, '0fb590ae-ea08-4763-bbc3-14bb4360b752')
- warning `W_TELEPORT` script.log:4005 teleport in stream ('HSD', 'cl', 'frame', None, '0fb590ae-ea08-4763-bbc3-14bb4360b752')
- warning `W_TELEPORT` message.log:4138 teleport in stream ('MT', 'sv', 'cmd', 1, '8c7f8d24-3d4f-49f3-92c8-4bc7b56a8cca')
- warning `W_TELEPORT` script.log:732 teleport in stream ('HSD', 'sv', 'evt', 1.0, '8c7f8d24-3d4f-49f3-92c8-4bc7b56a8cca')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.85 -> 24.66794 in ('HSD', 'sv', 'evt', 1.0, '8c7f8d24-3d4f-49f3-92c8-4bc7b56a8cca')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2607 | 0 | - | - |
| MT | cl | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r36 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 2583 | 0 | - | - |
| HSD | cl | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r36 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 2618 | 0 | - | - |
| MT | sv | r90 | 1274 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r36 | 1274 | 199.525 | first_order (yes) | linear (yes) |

Events: 24. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
