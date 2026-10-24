# hsd_tel report

Inputs: 16 file(s); rows: 28788 (MT 19407, HSD 9379)

Validation: 0 error(s), 21 warning(s), 2 info

- warning `W_TELEPORT` message.log:3959 teleport in stream ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` message.log:4578 teleport in stream ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` message.log:5196 teleport in stream ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` message.log:5835 teleport in stream ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` message.log:6501 teleport in stream ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:3603 teleport in stream ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:4617 teleport in stream ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:5635 teleport in stream ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:6652 teleport in stream ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:7700 teleport in stream ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` script.log:12009 teleport in stream ('HSD', 'cl', 'edge', None, 'c699b180-883c-467b-bb57-4f85b23bb80b')
- warning `W_TELEPORT` message.log:3750 teleport in stream ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TELEPORT` message.log:4340 teleport in stream ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TELEPORT` message.log:4928 teleport in stream ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TELEPORT` message.log:5515 teleport in stream ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TELEPORT` message.log:6132 teleport in stream ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TELEPORT` script.log:1338 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd6655187-e926-4eee-839b-b018b0c54065')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.9 -> 23.63529 in ('HSD', 'sv', 'evt', 1.0, 'd6655187-e926-4eee-839b-b018b0c54065')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5090 | 383.673 | - | linear (yes) |
| MT | cl | r90 | 421 | 599.018 | - | linear (yes) |
| MT | cl | r20321 | 421 | 599.763 | - | linear (yes) |
| MT | cl | r20322 | 421 | 597.499 | - | linear (yes) |
| MT | cl | r20323 | 421 | 604.167 | - | linear (yes) |
| MT | cl | r20324 | 421 | 597.22 | - | linear (yes) |
| MT | cl | r20325 | 421 | 600.164 | - | linear (yes) |
| MT | cl | r20326 | 421 | 596.295 | - | linear (yes) |
| MT | cl | r20327 | 421 | 862.989 | - | - |
| MT | cl | r20328 | 421 | 377.975 | - | linear (no) |
| MT | cl | r20329 | 421 | 393.551 | - | linear (no) |
| HSD | cl | r0 | 5067 | 383.673 | - | linear (yes) |
| HSD | cl | r90 | 421 | 599.018 | - | linear (yes) |
| HSD | cl | r20321 | 421 | 599.763 | - | linear (yes) |
| HSD | cl | r20322 | 421 | 597.499 | - | linear (yes) |
| HSD | cl | r20323 | 421 | 604.167 | - | linear (yes) |
| HSD | cl | r20324 | 421 | 597.22 | - | linear (yes) |
| HSD | cl | r20325 | 421 | 600.164 | - | linear (yes) |
| HSD | cl | r20326 | 421 | 596.295 | - | linear (yes) |
| HSD | cl | r20327 | 421 | 862.989 | - | - |
| HSD | cl | r20328 | 421 | 377.975 | - | linear (no) |
| HSD | cl | r20329 | 421 | 393.551 | - | linear (no) |
| MT | sv | b0 | 5101 | 383.673 | - | linear (yes) |
| MT | sv | r90 | 421 | 599.023 | - | linear (yes) |
| MT | sv | r20321 | 421 | 599.783 | - | linear (yes) |
| MT | sv | r20322 | 421 | 597.543 | - | linear (yes) |
| MT | sv | r20323 | 421 | 604.197 | - | linear (yes) |
| MT | sv | r20324 | 421 | 597.238 | - | linear (yes) |
| MT | sv | r20325 | 421 | 600.179 | - | linear (yes) |
| MT | sv | r20326 | 421 | 596.315 | - | linear (yes) |
| MT | sv | r20327 | 421 | 862.92 | - | - |
| MT | sv | r20328 | 421 | 377.939 | - | linear (no) |
| MT | sv | r20329 | 421 | 393.52 | - | linear (no) |

Events: 114. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
