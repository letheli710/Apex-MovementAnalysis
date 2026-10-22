# hsd_tel report

Inputs: 18 file(s); rows: 104416 (MT 72329, HSD 32027)

Validation: 0 error(s), 31 warning(s), 25 info

- warning `W_TELEPORT` message.1.log:4315 teleport in stream ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` message.1.log:5899 teleport in stream ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` message.1.log:7547 teleport in stream ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` message.1.log:9313 teleport in stream ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` message.1.log:11031 teleport in stream ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_MORE` message.1.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:3941 teleport in stream ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:6463 teleport in stream ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:8980 teleport in stream ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:11499 teleport in stream ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:14017 teleport in stream ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_MORE` script.1.log:0 10 more teleport rows in ('HSD', 'cl', 'frame', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:6260 teleport in stream ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:8784 teleport in stream ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:11301 teleport in stream ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:13820 teleport in stream ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` script.1.log:16162 teleport in stream ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_MORE` script.1.log:0 19 more teleport rows in ('HSD', 'cl', 'edge', None, '700cc65e-bf2d-4132-b18c-c65d97d140ff')
- warning `W_TELEPORT` message.log:4018 teleport in stream ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` message.log:5363 teleport in stream ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` message.log:6701 teleport in stream ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` message.log:8040 teleport in stream ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` message.log:9378 teleport in stream ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'sv', 'cmd', 1, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` script.log:891 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` script.log:893 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` script.log:900 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` script.log:902 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TELEPORT` script.log:909 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.6 -> 24.35166 in ('HSD', 'sv', 'evt', 1.0, 'f92d4864-f5d0-4985-9721-c18fd034a906')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 7860 | 70.366 | - | - |
| MT | cl | r90 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9601 | 1165 | 299.146 | first_order (no) | - |
| MT | cl | r9602 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9603 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9604 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9605 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9606 | 1115 | 450.872 | - | - |
| MT | cl | r9607 | 955 | 452.071 | - | - |
| MT | cl | r9608 | 955 | 451.997 | - | - |
| MT | cl | r9609 | 955 | 451.983 | - | - |
| MT | cl | r9610 | 955 | 452.075 | - | - |
| MT | cl | r9611 | 955 | 452.172 | - | - |
| MT | cl | r9612 | 955 | 450.654 | - | - |
| MT | cl | r9613 | 955 | 452.135 | - | - |
| MT | cl | r9614 | 955 | 450.447 | - | - |
| MT | cl | r9615 | 955 | 450.98 | - | - |
| MT | cl | r9616 | 877 | 199.788 | first_order (yes) | - |
| MT | cl | r9617 | 877 | 199.788 | first_order (yes) | - |
| MT | cl | r9618 | 877 | 199.788 | first_order (yes) | - |
| MT | cl | r9619 | 877 | 199.788 | first_order (yes) | - |
| MT | cl | r9620 | 877 | 199.788 | first_order (yes) | - |
| MT | cl | r9621 | 925 | 299.147 | first_order (no) | - |
| MT | cl | r9622 | 925 | 299.149 | first_order (no) | - |
| MT | cl | r9623 | 925 | 299.147 | first_order (no) | - |
| HSD | cl | r0 | 7845 | 70.366 | - | - |
| HSD | cl | r90 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9601 | 1165 | 299.146 | first_order (no) | - |
| HSD | cl | r9602 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9603 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9604 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9605 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9606 | 955 | 450.872 | linear (no) | friction (no) |
| HSD | cl | r9607 | 955 | 452.071 | linear (no) | friction (no) |
| HSD | cl | r9608 | 955 | 451.997 | linear (no) | - |
| HSD | cl | r9609 | 955 | 451.983 | linear (no) | - |
| HSD | cl | r9610 | 955 | 452.075 | linear (no) | - |
| HSD | cl | r9611 | 955 | 452.172 | first_order (no) | friction (no) |
| HSD | cl | r9612 | 955 | 450.654 | first_order (no) | friction (no) |
| HSD | cl | r9613 | 955 | 452.135 | linear (no) | - |
| HSD | cl | r9614 | 955 | 450.447 | first_order (no) | friction (no) |
| HSD | cl | r9615 | 955 | 450.98 | first_order (no) | friction (no) |
| HSD | cl | r9616 | 877 | 199.788 | first_order (yes) | - |
| HSD | cl | r9617 | 877 | 199.788 | first_order (yes) | - |
| HSD | cl | r9618 | 877 | 199.788 | first_order (yes) | - |
| HSD | cl | r9619 | 877 | 199.788 | first_order (yes) | - |
| HSD | cl | r9620 | 877 | 199.788 | first_order (yes) | - |
| HSD | cl | r9621 | 925 | 299.147 | first_order (no) | - |
| HSD | cl | r9622 | 925 | 299.149 | first_order (no) | - |
| HSD | cl | r9623 | 925 | 299.147 | first_order (no) | - |
| MT | sv | b0 | 7865 | 70.37 | - | - |
| MT | sv | r90 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9601 | 1165 | 299.146 | first_order (no) | - |
| MT | sv | r9602 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9603 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9604 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9605 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9606 | 980 | 450.88 | - | - |
| MT | sv | r9607 | 955 | 452.071 | - | - |
| MT | sv | r9608 | 955 | 451.997 | - | - |
| MT | sv | r9609 | 955 | 451.983 | - | - |
| MT | sv | r9610 | 955 | 452.075 | - | - |
| MT | sv | r9611 | 955 | 452.172 | - | - |
| MT | sv | r9612 | 955 | 450.654 | - | - |
| MT | sv | r9613 | 955 | 452.135 | - | - |
| MT | sv | r9614 | 955 | 450.447 | - | - |
| MT | sv | r9615 | 955 | 450.98 | - | - |
| MT | sv | r9616 | 877 | 199.788 | first_order (yes) | - |
| MT | sv | r9617 | 877 | 199.788 | first_order (yes) | - |
| MT | sv | r9618 | 877 | 199.788 | first_order (yes) | - |
| MT | sv | r9619 | 877 | 199.788 | first_order (yes) | - |
| MT | sv | r9620 | 877 | 199.788 | first_order (yes) | - |
| MT | sv | r9621 | 925 | 299.147 | first_order (no) | - |
| MT | sv | r9622 | 925 | 299.149 | first_order (no) | - |
| MT | sv | r9623 | 925 | 299.147 | first_order (no) | - |

Events: 498. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
