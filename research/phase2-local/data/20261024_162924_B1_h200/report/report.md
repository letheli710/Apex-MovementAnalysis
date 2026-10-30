# hsd_tel report

Inputs: 16 file(s); rows: 38549 (MT 24652, HSD 13895)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:4057 teleport in stream ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` message.log:4838 teleport in stream ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` message.log:5616 teleport in stream ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` message.log:6400 teleport in stream ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` message.log:9707 teleport in stream ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` script.log:3711 teleport in stream ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` script.log:5131 teleport in stream ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` script.log:6552 teleport in stream ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` script.log:7972 teleport in stream ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` script.log:11621 teleport in stream ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '0da6b913-8f44-44ff-9dde-933588ae3e2d')
- warning `W_TELEPORT` message.log:3851 teleport in stream ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_TELEPORT` message.log:4579 teleport in stream ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_TELEPORT` message.log:5307 teleport in stream ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_TELEPORT` message.log:6037 teleport in stream ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_TELEPORT` message.log:7950 teleport in stream ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.95 -> 24.71031 in ('HSD', 'sv', 'evt', 1.0, '4002aac3-6b12-48e1-b2d9-47b2a60a094a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3484 | 0 | - | - |
| MT | cl | r90 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 186 | 0 | - | - |
| MT | cl | r9600 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 188 | 0 | - | - |
| MT | cl | r9601 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b3 | 557 | 0 | - | - |
| MT | cl | r9602 | 1717 | 299.151 | first_order (no) | - |
| MT | cl | r9603 | 1714 | 299.148 | first_order (no) | - |
| MT | cl | r9604 | 536 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b4 | 190 | 0 | - | - |
| MT | cl | r9605 | 593 | 199.768 | first_order (yes) | friction (no) |
| MT | cl | b5 | 159 | 0 | - | - |
| HSD | cl | r0 | 4741 | 0 | - | - |
| HSD | cl | r90 | 609 | 299.151 | first_order (no) | - |
| HSD | cl | r9600 | 609 | 299.151 | first_order (no) | - |
| HSD | cl | r9601 | 606 | 299.151 | first_order (no) | - |
| HSD | cl | r9602 | 1717 | 299.151 | first_order (no) | - |
| HSD | cl | r9603 | 1717 | 299.148 | first_order (no) | - |
| HSD | cl | r9604 | 608 | 299.151 | first_order (no) | - |
| HSD | cl | r9605 | 664 | 199.768 | first_order (yes) | - |
| MT | sv | b0 | 3493 | 0 | - | - |
| MT | sv | r90 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 186 | 0 | - | - |
| MT | sv | r9600 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 188 | 0 | - | - |
| MT | sv | r9601 | 537 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b3 | 557 | 0 | - | - |
| MT | sv | r9602 | 1717 | 299.151 | first_order (no) | - |
| MT | sv | r9603 | 1714 | 299.148 | first_order (no) | - |
| MT | sv | r9604 | 536 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b4 | 190 | 0 | - | - |
| MT | sv | r9605 | 593 | 199.768 | first_order (yes) | friction (no) |
| MT | sv | b5 | 151 | 0 | - | - |

Events: 5174. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
