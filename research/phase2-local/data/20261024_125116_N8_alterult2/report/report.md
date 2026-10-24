# hsd_tel report

Inputs: 16 file(s); rows: 24805 (MT 16548, HSD 8255)

Validation: 0 error(s), 10 warning(s), 2 info

- warning `W_TELEPORT` message.log:3585 teleport in stream ('MT', 'cl', 'cmd', 1, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` message.log:5334 teleport in stream ('MT', 'cl', 'cmd', 1, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` message.log:7128 teleport in stream ('MT', 'cl', 'cmd', 1, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` script.log:3229 teleport in stream ('HSD', 'cl', 'frame', None, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` script.log:6562 teleport in stream ('HSD', 'cl', 'frame', None, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` script.log:9953 teleport in stream ('HSD', 'cl', 'frame', None, '71d0cc4c-4231-486a-b3f9-afd6b274a6ef')
- warning `W_TELEPORT` message.log:3351 teleport in stream ('MT', 'sv', 'cmd', 1, '1175bf59-9c8b-4a94-a3ea-64742b16dc71')
- warning `W_TELEPORT` message.log:7225 teleport in stream ('MT', 'sv', 'cmd', 1, '1175bf59-9c8b-4a94-a3ea-64742b16dc71')
- warning `W_TELEPORT` message.log:10878 teleport in stream ('MT', 'sv', 'cmd', 1, '1175bf59-9c8b-4a94-a3ea-64742b16dc71')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.35 -> 23.24976 in ('HSD', 'sv', 'evt', 1.0, '1175bf59-9c8b-4a94-a3ea-64742b16dc71')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3429 | 0 | - | - |
| MT | cl | r90 | 1596 | 199.902 | first_order (yes) | linear (yes) |
| MT | cl | r8831 | 1599 | 199.894 | first_order (yes) | linear (yes) |
| MT | cl | r8832 | 1599 | 199.897 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3418 | 0 | - | - |
| HSD | cl | r90 | 1599 | 199.902 | first_order (yes) | linear (yes) |
| HSD | cl | r8831 | 1599 | 199.894 | first_order (yes) | linear (yes) |
| HSD | cl | r8832 | 1599 | 199.897 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3425 | 0 | - | - |
| MT | sv | r90 | 1596 | 199.902 | first_order (yes) | linear (yes) |
| MT | sv | r8831 | 1599 | 199.894 | first_order (yes) | linear (yes) |
| MT | sv | r8832 | 1599 | 199.897 | first_order (yes) | linear (yes) |

Events: 50. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
