# hsd_tel report

Inputs: 16 file(s); rows: 20235 (MT 13814, HSD 6419)

Validation: 0 error(s), 14 warning(s), 2 info

- warning `W_TELEPORT` message.log:3591 teleport in stream ('MT', 'cl', 'cmd', 1, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` message.log:4697 teleport in stream ('MT', 'cl', 'cmd', 1, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` message.log:5804 teleport in stream ('MT', 'cl', 'cmd', 1, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` message.log:6911 teleport in stream ('MT', 'cl', 'cmd', 1, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` script.log:3241 teleport in stream ('HSD', 'cl', 'frame', None, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` script.log:4111 teleport in stream ('HSD', 'cl', 'frame', None, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` script.log:4984 teleport in stream ('HSD', 'cl', 'frame', None, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` script.log:5856 teleport in stream ('HSD', 'cl', 'frame', None, '9294b7be-90e3-4abc-ae1e-11509bac6afa')
- warning `W_TELEPORT` message.log:3368 teleport in stream ('MT', 'sv', 'cmd', 1, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')
- warning `W_TELEPORT` message.log:4229 teleport in stream ('MT', 'sv', 'cmd', 1, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')
- warning `W_TELEPORT` message.log:5088 teleport in stream ('MT', 'sv', 'cmd', 1, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')
- warning `W_TELEPORT` message.log:5946 teleport in stream ('MT', 'sv', 'cmd', 1, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')
- warning `W_TELEPORT` script.log:772 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')
- warning `W_TIME_BACKWARDS` script.log:718 t 22.85 -> 22.70533 in ('HSD', 'sv', 'evt', 1.0, 'c621afe3-980a-4f2a-bda1-fc1b8dd0a8f6')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3650 | 0 | - | - |
| MT | cl | r90 | 685 | 378.946 | - | linear (yes) |
| MT | cl | r2201 | 685 | 379.012 | - | linear (yes) |
| MT | cl | r2202 | 685 | 379.046 | - | linear (yes) |
| MT | cl | r2203 | 685 | 379.253 | - | linear (yes) |
| HSD | cl | r0 | 3639 | 0 | - | - |
| HSD | cl | r90 | 685 | 378.94 | - | linear (yes) |
| HSD | cl | r2201 | 685 | 379.006 | - | linear (yes) |
| HSD | cl | r2202 | 685 | 379.04 | - | linear (yes) |
| HSD | cl | r2203 | 685 | 379.246 | - | linear (yes) |
| MT | sv | b0 | 3651 | 0 | - | - |
| MT | sv | r90 | 685 | 378.946 | - | linear (yes) |
| MT | sv | r2201 | 685 | 379.012 | - | linear (yes) |
| MT | sv | r2202 | 685 | 379.046 | - | linear (yes) |
| MT | sv | r2203 | 685 | 379.253 | - | linear (yes) |

Events: 54. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
