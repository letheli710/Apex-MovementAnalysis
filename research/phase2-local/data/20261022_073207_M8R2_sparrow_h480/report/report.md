# hsd_tel report

Inputs: 16 file(s); rows: 40239 (MT 26680, HSD 13499)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:4226 teleport in stream ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` message.log:5198 teleport in stream ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` message.log:6168 teleport in stream ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` message.log:7137 teleport in stream ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` message.log:8105 teleport in stream ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` script.log:3862 teleport in stream ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` script.log:5593 teleport in stream ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` script.log:7328 teleport in stream ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` script.log:9063 teleport in stream ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` script.log:10797 teleport in stream ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_MORE` script.log:0 4 more teleport rows in ('HSD', 'cl', 'frame', None, 'f143bf45-c13a-439d-9c32-a4fe5eb57740')
- warning `W_TELEPORT` message.log:3954 teleport in stream ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_TELEPORT` message.log:4900 teleport in stream ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_TELEPORT` message.log:5850 teleport in stream ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_TELEPORT` message.log:6799 teleport in stream ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_TELEPORT` message.log:7749 teleport in stream ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_MORE` message.log:0 4 more teleport rows in ('MT', 'sv', 'cmd', 1, 'a449e15a-5633-4947-b055-3fa7d2986633')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.55 -> 23.27322 in ('HSD', 'sv', 'evt', 1.0, 'a449e15a-5633-4947-b055-3fa7d2986633')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5113 | 0 | - | - |
| MT | cl | r90 | 770 | 443.342 | - | linear (yes) |
| MT | cl | r9801 | 770 | 443.341 | - | linear (yes) |
| MT | cl | r9802 | 770 | 443.341 | - | linear (yes) |
| MT | cl | r9803 | 770 | 443.34 | - | linear (yes) |
| MT | cl | r9804 | 770 | 443.339 | - | linear (yes) |
| MT | cl | r9805 | 770 | 443.235 | - | linear (yes) |
| MT | cl | r9806 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9807 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9808 | 1165 | 299.148 | first_order (no) | - |
| HSD | cl | r0 | 5087 | 0 | - | - |
| HSD | cl | r90 | 770 | 443.342 | first_order (no) | - |
| HSD | cl | r9801 | 770 | 443.341 | first_order (no) | - |
| HSD | cl | r9802 | 770 | 443.341 | first_order (no) | - |
| HSD | cl | r9803 | 770 | 443.34 | first_order (no) | - |
| HSD | cl | r9804 | 770 | 443.339 | first_order (no) | - |
| HSD | cl | r9805 | 770 | 443.235 | first_order (no) | - |
| HSD | cl | r9806 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9807 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9808 | 1165 | 299.148 | first_order (no) | - |
| MT | sv | b0 | 5121 | 0 | - | - |
| MT | sv | r90 | 770 | 443.342 | - | linear (yes) |
| MT | sv | r9801 | 770 | 443.341 | - | linear (no) |
| MT | sv | r9802 | 770 | 443.341 | - | linear (no) |
| MT | sv | r9803 | 770 | 443.34 | - | linear (no) |
| MT | sv | r9804 | 770 | 443.339 | - | linear (no) |
| MT | sv | r9805 | 770 | 443.235 | - | linear (no) |
| MT | sv | r9806 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9807 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9808 | 1165 | 299.148 | first_order (no) | - |

Events: 259. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
