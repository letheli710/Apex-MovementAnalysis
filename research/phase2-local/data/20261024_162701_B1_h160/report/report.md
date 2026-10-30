# hsd_tel report

Inputs: 16 file(s); rows: 38224 (MT 24467, HSD 13755)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:4101 teleport in stream ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` message.log:4852 teleport in stream ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` message.log:5571 teleport in stream ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` message.log:6315 teleport in stream ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` message.log:9679 teleport in stream ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` script.log:3716 teleport in stream ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` script.log:5069 teleport in stream ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` script.log:6394 teleport in stream ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` script.log:7742 teleport in stream ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` script.log:12696 teleport in stream ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, 'f1fb2991-9555-46d1-b07e-f155432613b9')
- warning `W_TELEPORT` message.log:3852 teleport in stream ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_TELEPORT` message.log:4552 teleport in stream ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_TELEPORT` message.log:5221 teleport in stream ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_TELEPORT` message.log:5914 teleport in stream ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_TELEPORT` message.log:7814 teleport in stream ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'c22dada5-9757-4111-aa07-5c58306d8343')
- warning `W_TIME_BACKWARDS` script.log:715 t 25.15 -> 24.87801 in ('HSD', 'sv', 'evt', 1.0, 'c22dada5-9757-4111-aa07-5c58306d8343')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3484 | 0 | - | - |
| MT | cl | r90 | 504 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 191 | 0 | - | - |
| MT | cl | r9500 | 500 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b2 | 166 | 0 | - | - |
| MT | cl | r9501 | 504 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b3 | 565 | 0 | - | - |
| MT | cl | r9502 | 1717 | 299.053 | first_order (no) | - |
| MT | cl | r9503 | 1717 | 299.151 | first_order (no) | - |
| MT | cl | r9504 | 502 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b4 | 166 | 0 | - | - |
| MT | cl | r9505 | 558 | 199.77 | first_order (yes) | friction (no) |
| MT | cl | b5 | 135 | 0 | - | - |
| HSD | cl | r0 | 4687 | 0 | - | - |
| HSD | cl | r90 | 573 | 299.151 | first_order (no) | - |
| HSD | cl | r9500 | 572 | 299.152 | first_order (no) | - |
| HSD | cl | r9501 | 573 | 299.151 | first_order (no) | - |
| HSD | cl | r9502 | 1717 | 299.053 | first_order (no) | - |
| HSD | cl | r9503 | 1717 | 299.151 | first_order (no) | - |
| HSD | cl | r9504 | 572 | 299.151 | first_order (no) | - |
| HSD | cl | r9505 | 628 | 199.77 | first_order (yes) | - |
| MT | sv | b0 | 3494 | 0 | - | - |
| MT | sv | r90 | 504 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 191 | 0 | - | - |
| MT | sv | r9500 | 500 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b2 | 166 | 0 | - | - |
| MT | sv | r9501 | 504 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b3 | 565 | 0 | - | - |
| MT | sv | r9502 | 1717 | 299.053 | first_order (no) | - |
| MT | sv | r9503 | 1717 | 299.151 | first_order (no) | - |
| MT | sv | r9504 | 502 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b4 | 166 | 0 | - | - |
| MT | sv | r9505 | 558 | 199.77 | first_order (yes) | friction (no) |
| MT | sv | b5 | 127 | 0 | - | - |

Events: 5358. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
