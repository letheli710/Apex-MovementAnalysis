# hsd_tel report

Inputs: 16 file(s); rows: 16549 (MT 11023, HSD 5524)

Validation: 0 error(s), 10 warning(s), 2 info

- warning `W_TELEPORT` message.log:3808 teleport in stream ('MT', 'cl', 'cmd', 1, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` message.log:4580 teleport in stream ('MT', 'cl', 'cmd', 1, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` message.log:5349 teleport in stream ('MT', 'cl', 'cmd', 1, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` script.log:3463 teleport in stream ('HSD', 'cl', 'frame', None, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` script.log:4823 teleport in stream ('HSD', 'cl', 'frame', None, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` script.log:6185 teleport in stream ('HSD', 'cl', 'frame', None, '7ac5b486-6883-429e-b0f3-4879186c7455')
- warning `W_TELEPORT` message.log:3608 teleport in stream ('MT', 'sv', 'cmd', 1, 'ac752daf-016b-4598-8d71-068ed1b88159')
- warning `W_TELEPORT` message.log:4376 teleport in stream ('MT', 'sv', 'cmd', 1, 'ac752daf-016b-4598-8d71-068ed1b88159')
- warning `W_TELEPORT` message.log:5145 teleport in stream ('MT', 'sv', 'cmd', 1, 'ac752daf-016b-4598-8d71-068ed1b88159')
- warning `W_TIME_BACKWARDS` script.log:714 t 23.4 -> 23.26931 in ('HSD', 'sv', 'evt', 1.0, 'ac752daf-016b-4598-8d71-068ed1b88159')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3761 | 0 | - | - |
| MT | cl | r90 | 578 | 299.15 | first_order (no) | - |
| MT | cl | r4081 | 578 | 299.15 | first_order (no) | - |
| MT | cl | r4082 | 578 | 299.15 | first_order (no) | - |
| HSD | cl | r0 | 3738 | 0 | - | - |
| HSD | cl | r90 | 578 | 299.15 | first_order (no) | - |
| HSD | cl | r4081 | 578 | 299.15 | first_order (no) | - |
| HSD | cl | r4082 | 578 | 299.15 | first_order (no) | - |
| MT | sv | b0 | 3768 | 0 | - | - |
| MT | sv | r90 | 578 | 299.15 | first_order (no) | - |
| MT | sv | r4081 | 578 | 299.15 | first_order (no) | - |
| MT | sv | r4082 | 578 | 299.15 | first_order (no) | - |

Events: 74. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
