# hsd_tel report

Inputs: 16 file(s); rows: 60715 (MT 39252, HSD 21403)

Validation: 0 error(s), 20 warning(s), 24 info

- warning `W_TELEPORT` message.log:4094 teleport in stream ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` message.log:5029 teleport in stream ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` message.log:5979 teleport in stream ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` message.log:6925 teleport in stream ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` message.log:7875 teleport in stream ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` script.log:3724 teleport in stream ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` script.log:5422 teleport in stream ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` script.log:7165 teleport in stream ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` script.log:8917 teleport in stream ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` script.log:10669 teleport in stream ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_MORE` script.log:0 11 more teleport rows in ('HSD', 'cl', 'frame', None, '03e38ab9-3865-4eee-bb05-89fa07d1449e')
- warning `W_TELEPORT` message.log:3819 teleport in stream ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TELEPORT` message.log:5964 teleport in stream ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TELEPORT` message.log:8115 teleport in stream ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TELEPORT` message.log:10243 teleport in stream ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TELEPORT` message.log:12400 teleport in stream ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TELEPORT` script.log:828 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.05 -> 23.8542 in ('HSD', 'sv', 'evt', 1.0, 'f8421a94-8b0a-4ed6-ba1e-a9459eb1d00a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6264 | 0 | - | - |
| MT | cl | r90 | 708 | 299 | first_order (no) | - |
| MT | cl | r4201 | 708 | 299 | first_order (no) | - |
| MT | cl | r4202 | 708 | 299 | first_order (no) | - |
| MT | cl | r4203 | 708 | 299 | first_order (no) | - |
| MT | cl | r4204 | 708 | 299 | first_order (no) | - |
| MT | cl | r4205 | 708 | 299 | first_order (no) | - |
| MT | cl | r4206 | 828 | 199.525 | first_order (yes) | - |
| MT | cl | r4207 | 828 | 199.525 | first_order (yes) | - |
| MT | cl | r4208 | 828 | 199.525 | first_order (yes) | - |
| MT | cl | r4209 | 828 | 199.525 | first_order (yes) | - |
| MT | cl | r4210 | 828 | 199.525 | first_order (yes) | - |
| MT | cl | r4211 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4212 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4213 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4214 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4215 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r0 | 6237 | 0 | - | - |
| HSD | cl | r90 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4201 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4202 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4203 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4204 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4205 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4206 | 828 | 199.525 | first_order (yes) | - |
| HSD | cl | r4207 | 828 | 199.525 | first_order (yes) | - |
| HSD | cl | r4208 | 828 | 199.525 | first_order (yes) | - |
| HSD | cl | r4209 | 828 | 199.525 | first_order (yes) | - |
| HSD | cl | r4210 | 828 | 199.525 | first_order (yes) | - |
| HSD | cl | r4211 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4212 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4213 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4214 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4215 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | b0 | 6278 | 0 | - | - |
| MT | sv | r90 | 708 | 299 | first_order (no) | - |
| MT | sv | r4201 | 708 | 299 | first_order (no) | - |
| MT | sv | r4202 | 708 | 299 | first_order (no) | - |
| MT | sv | r4203 | 708 | 299 | first_order (no) | - |
| MT | sv | r4204 | 708 | 299 | first_order (no) | - |
| MT | sv | r4205 | 708 | 299 | first_order (no) | - |
| MT | sv | r4206 | 828 | 199.525 | first_order (yes) | - |
| MT | sv | r4207 | 828 | 199.525 | first_order (yes) | - |
| MT | sv | r4208 | 828 | 199.525 | first_order (yes) | - |
| MT | sv | r4209 | 828 | 199.525 | first_order (yes) | - |
| MT | sv | r4210 | 828 | 199.525 | first_order (yes) | - |
| MT | sv | r4211 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4212 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4213 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4214 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4215 | 768 | 199.525 | first_order (yes) | - |

Events: 5496. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
