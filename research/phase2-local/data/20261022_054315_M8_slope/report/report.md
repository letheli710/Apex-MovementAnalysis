# hsd_tel report

Inputs: 16 file(s); rows: 48809 (MT 32567, HSD 16240)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3558 teleport in stream ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` message.log:4396 teleport in stream ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` message.log:5227 teleport in stream ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` message.log:6060 teleport in stream ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` message.log:6895 teleport in stream ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` script.log:3203 teleport in stream ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` script.log:4705 teleport in stream ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` script.log:6201 teleport in stream ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` script.log:7699 teleport in stream ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` script.log:9197 teleport in stream ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_MORE` script.log:0 11 more teleport rows in ('HSD', 'cl', 'frame', None, '2e5bab2a-e8ef-4c9b-b692-5a633b78e01f')
- warning `W_TELEPORT` message.log:3336 teleport in stream ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_TELEPORT` message.log:4170 teleport in stream ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_TELEPORT` message.log:4995 teleport in stream ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_TELEPORT` message.log:5822 teleport in stream ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_TELEPORT` message.log:6649 teleport in stream ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, '5adf97ef-50d7-4df1-9291-d7b234934607')
- warning `W_TIME_BACKWARDS` script.log:715 t 25.3 -> 25.04301 in ('HSD', 'sv', 'evt', 1.0, '5adf97ef-50d7-4df1-9291-d7b234934607')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5626 | 159.956 | - | linear (yes) |
| MT | cl | r90 | 660 | 553.702 | first_order (no) | - |
| MT | cl | r9601 | 660 | 554.25 | first_order (no) | - |
| MT | cl | r9602 | 660 | 553.267 | first_order (no) | - |
| MT | cl | r9603 | 660 | 553.314 | first_order (no) | - |
| MT | cl | r9604 | 660 | 553.336 | first_order (no) | - |
| MT | cl | r9605 | 660 | 553.579 | first_order (no) | - |
| MT | cl | r9606 | 660 | 296.63 | first_order (no) | linear (yes) |
| MT | cl | r9607 | 660 | 296.646 | first_order (no) | linear (yes) |
| MT | cl | r9608 | 660 | 296.624 | first_order (no) | linear (yes) |
| MT | cl | r9609 | 660 | 296.607 | first_order (no) | linear (yes) |
| MT | cl | r9610 | 660 | 296.577 | first_order (no) | linear (yes) |
| MT | cl | r9611 | 660 | 299 | first_order (no) | linear (yes) |
| MT | cl | r9612 | 660 | 299 | first_order (no) | linear (yes) |
| MT | cl | r9613 | 660 | 299 | first_order (no) | linear (yes) |
| MT | cl | r9614 | 660 | 299 | first_order (no) | linear (yes) |
| MT | cl | r9615 | 660 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 5612 | 170.733 | - | linear (yes) |
| HSD | cl | r90 | 660 | 553.702 | first_order (no) | - |
| HSD | cl | r9601 | 660 | 554.25 | first_order (no) | - |
| HSD | cl | r9602 | 660 | 553.267 | first_order (no) | - |
| HSD | cl | r9603 | 660 | 553.314 | first_order (no) | - |
| HSD | cl | r9604 | 660 | 553.336 | first_order (no) | - |
| HSD | cl | r9605 | 660 | 553.579 | first_order (no) | - |
| HSD | cl | r9606 | 660 | 296.63 | first_order (no) | linear (yes) |
| HSD | cl | r9607 | 660 | 296.646 | first_order (no) | linear (yes) |
| HSD | cl | r9608 | 660 | 296.624 | first_order (no) | linear (yes) |
| HSD | cl | r9609 | 660 | 296.607 | first_order (no) | linear (yes) |
| HSD | cl | r9610 | 660 | 296.577 | first_order (no) | linear (yes) |
| HSD | cl | r9611 | 660 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r9612 | 660 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r9613 | 660 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r9614 | 660 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r9615 | 660 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 5630 | 159.956 | - | linear (yes) |
| MT | sv | r90 | 660 | 553.702 | first_order (no) | - |
| MT | sv | r9601 | 660 | 554.25 | first_order (no) | - |
| MT | sv | r9602 | 660 | 553.267 | first_order (no) | - |
| MT | sv | r9603 | 660 | 553.314 | first_order (no) | - |
| MT | sv | r9604 | 660 | 553.336 | first_order (no) | - |
| MT | sv | r9605 | 660 | 553.579 | first_order (no) | - |
| MT | sv | r9606 | 660 | 296.63 | first_order (no) | linear (yes) |
| MT | sv | r9607 | 660 | 296.646 | first_order (no) | linear (yes) |
| MT | sv | r9608 | 660 | 296.624 | first_order (no) | linear (yes) |
| MT | sv | r9609 | 660 | 296.607 | first_order (no) | linear (yes) |
| MT | sv | r9610 | 660 | 296.577 | first_order (no) | linear (yes) |
| MT | sv | r9611 | 660 | 299 | first_order (no) | linear (yes) |
| MT | sv | r9612 | 660 | 299 | first_order (no) | linear (yes) |
| MT | sv | r9613 | 660 | 299 | first_order (no) | linear (yes) |
| MT | sv | r9614 | 660 | 299 | first_order (no) | linear (yes) |
| MT | sv | r9615 | 660 | 299 | first_order (no) | linear (yes) |

Events: 38. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
