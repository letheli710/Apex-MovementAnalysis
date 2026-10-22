# hsd_tel report

Inputs: 20 file(s); rows: 229658 (MT 153888, HSD 75768)

Validation: 0 error(s), 24 warning(s), 6 info

- warning `W_TELEPORT` message.1.log:15941 teleport in stream ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` message.1.log:18803 teleport in stream ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` message.1.log:33516 teleport in stream ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` message.1.log:34888 teleport in stream ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` message.1.log:36334 teleport in stream ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_MORE` message.1.log:0 8 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.2.log:15558 teleport in stream ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.2.log:18407 teleport in stream ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.2.log:33089 teleport in stream ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.2.log:35609 teleport in stream ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.1.log:2318 teleport in stream ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_MORE` script.2.log:0 8 more teleport rows in ('HSD', 'cl', 'frame', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` script.1.log:6386 teleport in stream ('HSD', 'cl', 'edge', None, 'f6754b86-f5d6-4276-b5b5-b48dd13cf44c')
- warning `W_TELEPORT` message.1.log:15701 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` message.1.log:18545 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` message.1.log:33218 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` message.1.log:34493 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` message.1.log:35761 teleport in stream ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_MORE` message.1.log:0 8 more teleport rows in ('MT', 'sv', 'cmd', 1, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` script.log:735 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` script.log:867 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` script.log:875 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TELEPORT` script.log:1079 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')
- warning `W_TIME_BACKWARDS` script.log:717 t 25.2 -> 24.93788 in ('HSD', 'sv', 'evt', 1.0, 'ae547c10-f2ff-4cc9-8a38-092a525595dd')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 32841 | 860.672 | - | linear (no) |
| MT | cl | r9501 | 1095 | 299.147 | first_order (no) | - |
| MT | cl | b1 | 176 | 0 | - | - |
| MT | cl | r9502 | 1095 | 299.147 | first_order (no) | - |
| MT | cl | b2 | 173 | 0 | - | - |
| MT | cl | r9503 | 908 | 450.45 | - | - |
| MT | cl | b3 | 31483 | 69.9838 | - | - |
| MT | cl | r9504 | 955 | 452.146 | - | - |
| MT | cl | r9511 | 646 | 860.711 | - | linear (no) |
| MT | cl | r9512 | 712 | 860.711 | - | linear (no) |
| MT | cl | r9513 | 649 | 860.89 | - | friction (no) |
| MT | cl | r9514 | 1022 | 0 | - | - |
| MT | cl | r9515 | 1141 | 834.89 | - | - |
| MT | cl | r9521 | 1081 | 848.838 | - | - |
| MT | cl | r9522 | 748 | 860.708 | - | friction (no) |
| MT | cl | r9523 | 762 | 860.709 | - | friction (no) |
| HSD | cl | r0 | 64644 | 860.672 | - | friction (no) |
| HSD | cl | r9501 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9502 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9503 | 955 | 450.45 | - | friction (no) |
| HSD | cl | r9504 | 955 | 452.146 | linear (no) | - |
| HSD | cl | r9511 | 646 | 860.711 | - | friction (yes) |
| HSD | cl | r9512 | 712 | 860.711 | - | friction (no) |
| HSD | cl | r9513 | 649 | 860.89 | - | friction (yes) |
| HSD | cl | r9514 | 1022 | 0 | - | - |
| HSD | cl | r9515 | 1141 | 834.89 | - | - |
| HSD | cl | r9521 | 1081 | 848.838 | - | - |
| HSD | cl | r9522 | 748 | 860.708 | - | linear (yes) |
| HSD | cl | r9523 | 762 | 860.709 | - | linear (yes) |
| MT | sv | b0 | 32856 | 860.672 | - | linear (no) |
| MT | sv | r9501 | 1095 | 299.147 | first_order (no) | - |
| MT | sv | b1 | 176 | 0 | - | - |
| MT | sv | r9502 | 1095 | 299.147 | first_order (no) | - |
| MT | sv | b2 | 173 | 0 | - | - |
| MT | sv | r9503 | 884 | 450.45 | - | linear (no) |
| MT | sv | b3 | 31481 | 69.9886 | - | - |
| MT | sv | r9504 | 955 | 452.146 | - | - |
| MT | sv | r9511 | 646 | 860.711 | - | linear (no) |
| MT | sv | r9512 | 712 | 860.711 | - | linear (no) |
| MT | sv | r9513 | 649 | 860.96 | - | friction (no) |
| MT | sv | r9514 | 1022 | 0 | - | - |
| MT | sv | r9515 | 1141 | 848.836 | - | - |
| MT | sv | r9521 | 1081 | 848.836 | - | - |
| MT | sv | r9522 | 748 | 860.708 | - | friction (no) |
| MT | sv | r9523 | 762 | 860.709 | - | friction (no) |

Events: 141. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
