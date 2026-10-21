# hsd_tel report

Inputs: 16 file(s); rows: 69377 (MT 46438, HSD 22834)

Validation: 0 error(s), 5 warning(s), 24 info

- warning `W_TELEPORT` message.log:4310 teleport in stream ('MT', 'cl', 'cmd', 1, 'ed37fd56-9097-43c1-8fc0-6c4ac99d1839')
- warning `W_TELEPORT` script.log:3895 teleport in stream ('HSD', 'cl', 'frame', None, 'ed37fd56-9097-43c1-8fc0-6c4ac99d1839')
- warning `W_TELEPORT` message.log:3977 teleport in stream ('MT', 'sv', 'cmd', 1, 'bbdf6b34-553a-4e7f-a5fe-87aec95f76d0')
- warning `W_TELEPORT` script.log:862 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'bbdf6b34-553a-4e7f-a5fe-87aec95f76d0')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.9 -> 23.61065 in ('HSD', 'sv', 'evt', 1.0, 'bbdf6b34-553a-4e7f-a5fe-87aec95f76d0')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5564 | 0 | - | - |
| MT | cl | r90 | 2076 | 0 | - | - |
| MT | cl | r4331 | 2076 | 0 | - | - |
| MT | cl | r4332 | 2076 | 0 | - | - |
| MT | cl | r4333 | 2076 | 0 | - | - |
| MT | cl | r4334 | 2069 | 0 | - | - |
| MT | cl | r4335 | 2076 | 0 | - | - |
| MT | cl | r4336 | 924 | 0 | - | - |
| MT | cl | r4337 | 924 | 0 | - | - |
| MT | cl | r4338 | 924 | 0 | - | - |
| MT | cl | r4339 | 924 | 0 | - | - |
| MT | cl | r4340 | 924 | 0 | - | - |
| HSD | cl | r0 | 5544 | 0 | - | - |
| HSD | cl | r90 | 2076 | 0 | - | - |
| HSD | cl | r4331 | 2076 | 0 | - | - |
| HSD | cl | r4332 | 2076 | 0 | - | - |
| HSD | cl | r4333 | 2076 | 0 | - | - |
| HSD | cl | r4334 | 2069 | 0 | - | - |
| HSD | cl | r4335 | 2076 | 0 | - | - |
| HSD | cl | r4336 | 924 | 0 | - | - |
| HSD | cl | r4337 | 924 | 0 | - | - |
| HSD | cl | r4338 | 924 | 0 | - | - |
| HSD | cl | r4339 | 924 | 0 | - | - |
| HSD | cl | r4340 | 924 | 0 | - | - |
| MT | sv | b0 | 5573 | 0 | - | - |
| MT | sv | r90 | 2076 | 0 | - | - |
| MT | sv | r4331 | 2076 | 0 | - | - |
| MT | sv | r4332 | 2076 | 0 | - | - |
| MT | sv | r4333 | 2076 | 0 | - | - |
| MT | sv | r4334 | 2069 | 0 | - | - |
| MT | sv | r4335 | 2076 | 0 | - | - |
| MT | sv | r4336 | 924 | 0 | - | - |
| MT | sv | r4337 | 924 | 0 | - | - |
| MT | sv | r4338 | 924 | 0 | - | - |
| MT | sv | r4339 | 924 | 0 | - | - |
| MT | sv | r4340 | 924 | 0 | - | - |

Events: 175. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
