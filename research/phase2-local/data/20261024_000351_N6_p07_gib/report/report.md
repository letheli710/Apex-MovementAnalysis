# hsd_tel report

Inputs: 16 file(s); rows: 27609 (MT 18616, HSD 8991)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3611 teleport in stream ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` message.log:4247 teleport in stream ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` message.log:4885 teleport in stream ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` message.log:5553 teleport in stream ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` message.log:6197 teleport in stream ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` script.log:3254 teleport in stream ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` script.log:4268 teleport in stream ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` script.log:5286 teleport in stream ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` script.log:6333 teleport in stream ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` script.log:7351 teleport in stream ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, 'c435d0db-0f2e-4406-bf34-edec4e80de2c')
- warning `W_TELEPORT` message.log:3394 teleport in stream ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_TELEPORT` message.log:3984 teleport in stream ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_TELEPORT` message.log:4572 teleport in stream ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_TELEPORT` message.log:5189 teleport in stream ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_TELEPORT` message.log:5776 teleport in stream ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.0 -> 23.84692 in ('HSD', 'sv', 'evt', 1.0, 'a2f91cb1-5e08-427f-9c9e-2c5a8931dc00')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4742 | 0 | - | - |
| MT | cl | r90 | 421 | 800.565 | - | linear (yes) |
| MT | cl | r20371 | 421 | 800.594 | - | linear (yes) |
| MT | cl | r20372 | 421 | 800.679 | - | linear (yes) |
| MT | cl | r20373 | 421 | 800.542 | - | linear (yes) |
| MT | cl | r20374 | 421 | 800.672 | - | linear (yes) |
| MT | cl | r20375 | 421 | 800.658 | - | linear (yes) |
| MT | cl | r20376 | 421 | 800.575 | - | linear (yes) |
| MT | cl | r20377 | 421 | 785.107 | - | linear (yes) |
| MT | cl | r20378 | 421 | 789.826 | - | linear (yes) |
| MT | cl | r20379 | 421 | 797.957 | - | linear (yes) |
| HSD | cl | r0 | 4717 | 0 | - | - |
| HSD | cl | r90 | 421 | 800.565 | - | linear (yes) |
| HSD | cl | r20371 | 421 | 800.594 | - | linear (yes) |
| HSD | cl | r20372 | 421 | 800.679 | - | linear (yes) |
| HSD | cl | r20373 | 421 | 800.542 | - | linear (yes) |
| HSD | cl | r20374 | 421 | 800.672 | - | linear (yes) |
| HSD | cl | r20375 | 421 | 800.658 | - | linear (yes) |
| HSD | cl | r20376 | 421 | 800.575 | - | linear (yes) |
| HSD | cl | r20377 | 421 | 785.107 | - | linear (yes) |
| HSD | cl | r20378 | 421 | 789.826 | - | linear (yes) |
| HSD | cl | r20379 | 421 | 797.957 | - | linear (yes) |
| MT | sv | b0 | 4746 | 0 | - | - |
| MT | sv | r90 | 421 | 800.565 | - | linear (yes) |
| MT | sv | r20371 | 421 | 800.594 | - | linear (yes) |
| MT | sv | r20372 | 421 | 800.679 | - | linear (yes) |
| MT | sv | r20373 | 421 | 800.542 | - | linear (yes) |
| MT | sv | r20374 | 421 | 800.672 | - | linear (yes) |
| MT | sv | r20375 | 421 | 800.658 | - | linear (yes) |
| MT | sv | r20376 | 421 | 800.575 | - | linear (yes) |
| MT | sv | r20377 | 421 | 785.107 | - | linear (yes) |
| MT | sv | r20378 | 421 | 789.826 | - | linear (yes) |
| MT | sv | r20379 | 421 | 797.957 | - | linear (yes) |

Events: 62. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
