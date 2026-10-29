# hsd_tel report

Inputs: 16 file(s); rows: 32210 (MT 21572, HSD 10636)

Validation: 0 error(s), 28 warning(s), 2 info

- warning `W_TELEPORT` message.log:4190 teleport in stream ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` message.log:4905 teleport in stream ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` message.log:5568 teleport in stream ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` message.log:6243 teleport in stream ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` message.log:6951 teleport in stream ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:3851 teleport in stream ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:5021 teleport in stream ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:6157 teleport in stream ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:7295 teleport in stream ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:8455 teleport in stream ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:5597 teleport in stream ('HSD', 'cl', 'edge', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:8968 teleport in stream ('HSD', 'cl', 'edge', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` script.log:10105 teleport in stream ('HSD', 'cl', 'edge', None, '66da846c-49a2-49c6-a37e-fa6d55ada2bc')
- warning `W_TELEPORT` message.log:3988 teleport in stream ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` message.log:4672 teleport in stream ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` message.log:5321 teleport in stream ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` message.log:5969 teleport in stream ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` message.log:6640 teleport in stream ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` script.log:777 teleport in stream ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` script.log:851 teleport in stream ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` script.log:925 teleport in stream ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` script.log:1000 teleport in stream ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TELEPORT` script.log:1076 teleport in stream ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_MORE` script.log:0 4 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')
- warning `W_TIME_BACKWARDS` script.log:713 t 31.55 -> 31.26945 in ('HSD', 'sv', 'evt', 1.0, '5d9b58a2-a0aa-493a-a7db-b778de9349d8')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5372 | 0 | - | - |
| MT | cl | r90 | 481 | 604.888 | - | linear (yes) |
| MT | cl | r23101 | 481 | 605.938 | - | linear (yes) |
| MT | cl | r23102 | 481 | 606.916 | - | linear (yes) |
| MT | cl | r23103 | 481 | 608.314 | - | linear (yes) |
| MT | cl | r23104 | 481 | 721.804 | - | linear (yes) |
| MT | cl | r23105 | 481 | 721.199 | - | linear (yes) |
| MT | cl | r23106 | 601 | 722.848 | first_order (no) | linear (yes) |
| MT | cl | r23107 | 601 | 725.875 | first_order (no) | linear (yes) |
| MT | cl | r23108 | 541 | 517.966 | linear (no) | linear (yes) |
| MT | cl | r23109 | 541 | 526.452 | linear (no) | linear (yes) |
| HSD | cl | r0 | 5350 | 0 | - | - |
| HSD | cl | r90 | 481 | 604.888 | - | linear (yes) |
| HSD | cl | r23101 | 481 | 605.938 | - | linear (yes) |
| HSD | cl | r23102 | 481 | 606.916 | - | linear (yes) |
| HSD | cl | r23103 | 481 | 608.314 | - | linear (yes) |
| HSD | cl | r23104 | 481 | 721.804 | - | linear (yes) |
| HSD | cl | r23105 | 481 | 721.199 | - | linear (yes) |
| HSD | cl | r23106 | 601 | 722.848 | first_order (no) | linear (yes) |
| HSD | cl | r23107 | 601 | 725.875 | first_order (no) | linear (yes) |
| HSD | cl | r23108 | 541 | 517.966 | linear (no) | linear (yes) |
| HSD | cl | r23109 | 541 | 526.452 | linear (no) | linear (yes) |
| MT | sv | b0 | 5378 | 0 | - | - |
| MT | sv | r90 | 481 | 604.888 | - | linear (yes) |
| MT | sv | r23101 | 481 | 605.938 | - | linear (yes) |
| MT | sv | r23102 | 481 | 606.916 | - | linear (yes) |
| MT | sv | r23103 | 481 | 608.314 | - | linear (yes) |
| MT | sv | r23104 | 481 | 721.804 | - | linear (yes) |
| MT | sv | r23105 | 481 | 721.199 | - | linear (yes) |
| MT | sv | r23106 | 601 | 722.848 | first_order (no) | linear (yes) |
| MT | sv | r23107 | 601 | 725.875 | first_order (no) | linear (yes) |
| MT | sv | r23108 | 541 | 517.966 | linear (no) | linear (yes) |
| MT | sv | r23109 | 541 | 526.452 | linear (no) | linear (yes) |

Events: 114. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
