# hsd_tel report

Inputs: 16 file(s); rows: 24713 (MT 16236, HSD 8475)

Validation: 0 error(s), 19 warning(s), 4 info

- warning `W_TELEPORT` message.log:4006 teleport in stream ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` message.log:4724 teleport in stream ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` message.log:5441 teleport in stream ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` message.log:6160 teleport in stream ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` message.log:6858 teleport in stream ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` script.log:3654 teleport in stream ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` script.log:4915 teleport in stream ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` script.log:6180 teleport in stream ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` script.log:7444 teleport in stream ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` script.log:8708 teleport in stream ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '5fa04d6d-9e9b-4ece-a34a-30e2c341d5ba')
- warning `W_TELEPORT` message.log:3805 teleport in stream ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_TELEPORT` message.log:4475 teleport in stream ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_TELEPORT` message.log:5147 teleport in stream ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_TELEPORT` message.log:5818 teleport in stream ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_TELEPORT` message.log:6464 teleport in stream ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')
- warning `W_TIME_BACKWARDS` script.log:717 t 25.45 -> 25.17405 in ('HSD', 'sv', 'evt', 1.0, 'a72a48ed-8314-4a23-9e55-07e3e6f90c42')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3432 | 0 | - | - |
| MT | cl | r90 | 501 | 299.23 | first_order (no) | friction (no) |
| MT | cl | b1 | 165 | 0 | - | - |
| MT | cl | r9300 | 504 | 299.239 | first_order (no) | friction (no) |
| MT | cl | b2 | 166 | 0 | - | - |
| MT | cl | r9301 | 503 | 299.247 | first_order (no) | friction (no) |
| MT | cl | b3 | 166 | 0 | - | - |
| MT | cl | r9302 | 478 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b4 | 167 | 0 | - | - |
| MT | cl | r9303 | 477 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b5 | 168 | 0 | - | - |
| MT | cl | r9304 | 501 | 299.23 | first_order (no) | friction (no) |
| MT | cl | b6 | 168 | 0 | - | - |
| MT | cl | r9305 | 555 | 199.77 | first_order (yes) | friction (no) |
| MT | cl | b7 | 139 | 0 | - | - |
| HSD | cl | r0 | 4543 | 0 | - | - |
| HSD | cl | r90 | 540 | 299.23 | first_order (no) | - |
| HSD | cl | r9300 | 542 | 299.239 | first_order (no) | - |
| HSD | cl | r9301 | 541 | 299.247 | first_order (no) | - |
| HSD | cl | r9302 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r9303 | 540 | 299.152 | first_order (no) | - |
| HSD | cl | r9304 | 540 | 299.23 | first_order (no) | - |
| HSD | cl | r9305 | 594 | 199.77 | first_order (yes) | - |
| MT | sv | b0 | 3447 | 0 | - | - |
| MT | sv | r90 | 501 | 299.23 | first_order (no) | friction (no) |
| MT | sv | b1 | 165 | 0 | - | - |
| MT | sv | r9300 | 504 | 299.239 | first_order (no) | friction (no) |
| MT | sv | b2 | 166 | 0 | - | - |
| MT | sv | r9301 | 503 | 299.247 | first_order (no) | friction (no) |
| MT | sv | b3 | 166 | 0 | - | - |
| MT | sv | r9302 | 478 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b4 | 167 | 0 | - | - |
| MT | sv | r9303 | 477 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b5 | 168 | 0 | - | - |
| MT | sv | r9304 | 501 | 299.23 | first_order (no) | friction (no) |
| MT | sv | b6 | 168 | 0 | - | - |
| MT | sv | r9305 | 555 | 199.77 | first_order (yes) | friction (no) |
| MT | sv | b7 | 131 | 0 | - | - |

Events: 126. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
