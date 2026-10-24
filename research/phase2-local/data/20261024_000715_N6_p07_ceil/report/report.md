# hsd_tel report

Inputs: 16 file(s); rows: 25967 (MT 17422, HSD 8543)

Validation: 0 error(s), 4 warning(s), 2 info

- warning `W_TELEPORT` message.log:3726 teleport in stream ('MT', 'cl', 'cmd', 1, 'd5a9c673-894d-4174-bc22-650a5243829d')
- warning `W_TELEPORT` script.log:3368 teleport in stream ('HSD', 'cl', 'frame', None, 'd5a9c673-894d-4174-bc22-650a5243829d')
- warning `W_TELEPORT` message.log:3526 teleport in stream ('MT', 'sv', 'cmd', 1, 'e41294a0-8e93-45ab-aebc-5a952ce299b2')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.4 -> 23.23891 in ('HSD', 'sv', 'evt', 1.0, 'e41294a0-8e93-45ab-aebc-5a952ce299b2')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4726 | 0 | - | - |
| MT | cl | r90 | 421 | 91.6721 | - | - |
| MT | cl | r20381 | 421 | 91.7691 | - | - |
| MT | cl | r20382 | 421 | 91.7181 | - | - |
| MT | cl | r20383 | 421 | 91.6951 | - | - |
| MT | cl | r20384 | 421 | 91.7711 | - | - |
| MT | cl | r20385 | 421 | 91.799 | - | - |
| MT | cl | r20386 | 421 | 91.795 | - | - |
| MT | cl | r20387 | 421 | 91.718 | - | - |
| MT | cl | r20388 | 421 | 91.795 | - | - |
| HSD | cl | r0 | 4696 | 0 | - | - |
| HSD | cl | r90 | 421 | 91.6721 | - | - |
| HSD | cl | r20381 | 421 | 91.7691 | - | - |
| HSD | cl | r20382 | 421 | 91.7181 | - | - |
| HSD | cl | r20383 | 421 | 91.6951 | - | - |
| HSD | cl | r20384 | 421 | 91.7711 | - | - |
| HSD | cl | r20385 | 421 | 91.799 | - | - |
| HSD | cl | r20386 | 421 | 91.795 | - | - |
| HSD | cl | r20387 | 421 | 91.718 | - | - |
| HSD | cl | r20388 | 421 | 91.795 | - | - |
| MT | sv | b0 | 4736 | 0 | - | - |
| MT | sv | r90 | 421 | 91.6721 | - | - |
| MT | sv | r20381 | 421 | 91.7691 | - | - |
| MT | sv | r20382 | 421 | 91.7181 | - | - |
| MT | sv | r20383 | 421 | 91.6951 | - | - |
| MT | sv | r20384 | 421 | 91.7711 | - | - |
| MT | sv | r20385 | 421 | 91.799 | - | - |
| MT | sv | r20386 | 421 | 91.795 | - | - |
| MT | sv | r20387 | 421 | 91.718 | - | - |
| MT | sv | r20388 | 421 | 91.795 | - | - |

Events: 56. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
