# hsd_tel report

Inputs: 16 file(s); rows: 19371 (MT 12776, HSD 6535)

Validation: 0 error(s), 5 warning(s), 24 info

- warning `W_TELEPORT` message.log:3863 teleport in stream ('MT', 'cl', 'cmd', 1, '3cc70eba-377d-4d4a-b2c6-df78b80a4c8d')
- warning `W_TELEPORT` script.log:3517 teleport in stream ('HSD', 'cl', 'frame', None, '3cc70eba-377d-4d4a-b2c6-df78b80a4c8d')
- warning `W_TELEPORT` message.log:3604 teleport in stream ('MT', 'sv', 'cmd', 1, 'c7408eb7-9519-451e-91fd-2d49b2ec4646')
- warning `W_TELEPORT` script.log:830 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'c7408eb7-9519-451e-91fd-2d49b2ec4646')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.35 -> 23.08944 in ('HSD', 'sv', 'evt', 1.0, 'c7408eb7-9519-451e-91fd-2d49b2ec4646')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4474 | 0 | - | - |
| MT | cl | r90 | 241 | 0 | - | - |
| MT | cl | r20231 | 241 | 0 | - | - |
| MT | cl | r20232 | 241 | 0 | - | - |
| MT | cl | r20233 | 241 | 0 | - | - |
| MT | cl | r20234 | 311 | 0 | - | - |
| MT | cl | r20235 | 311 | 0 | - | - |
| MT | cl | r20236 | 311 | 0 | - | - |
| HSD | cl | r0 | 4453 | 0 | - | - |
| HSD | cl | r90 | 241 | 0 | - | - |
| HSD | cl | r20231 | 241 | 0 | - | - |
| HSD | cl | r20232 | 241 | 0 | - | - |
| HSD | cl | r20233 | 241 | 0 | - | - |
| HSD | cl | r20234 | 311 | 0 | - | - |
| HSD | cl | r20235 | 311 | 0 | - | - |
| HSD | cl | r20236 | 311 | 0 | - | - |
| MT | sv | b0 | 4486 | 0 | - | - |
| MT | sv | r90 | 241 | 0 | - | - |
| MT | sv | r20231 | 241 | 0 | - | - |
| MT | sv | r20232 | 241 | 0 | - | - |
| MT | sv | r20233 | 241 | 0 | - | - |
| MT | sv | r20234 | 311 | 0 | - | - |
| MT | sv | r20235 | 311 | 0 | - | - |
| MT | sv | r20236 | 311 | 0 | - | - |

Events: 79. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
