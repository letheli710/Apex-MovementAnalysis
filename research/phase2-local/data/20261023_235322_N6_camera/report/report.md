# hsd_tel report

Inputs: 16 file(s); rows: 38555 (MT 25694, HSD 12859)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3361 teleport in stream ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` message.log:3983 teleport in stream ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` message.log:4608 teleport in stream ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` message.log:5230 teleport in stream ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` message.log:5856 teleport in stream ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'cl', 'cmd', 1, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` script.log:3006 teleport in stream ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` script.log:3633 teleport in stream ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` script.log:4263 teleport in stream ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` script.log:4891 teleport in stream ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` script.log:5521 teleport in stream ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'cl', 'frame', None, 'c0e01f3c-5de7-4c2e-82bf-ff658f043ddf')
- warning `W_TELEPORT` message.log:3129 teleport in stream ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_TELEPORT` message.log:3746 teleport in stream ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_TELEPORT` message.log:4363 teleport in stream ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_TELEPORT` message.log:4981 teleport in stream ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_TELEPORT` message.log:5598 teleport in stream ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'sv', 'cmd', 1, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.45 -> 23.36246 in ('HSD', 'sv', 'evt', 1.0, '9dd8f4e8-5fb5-46ad-9f72-63f23263e14f')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5809 | 0 | - | - |
| MT | cl | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20341 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20342 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20343 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20344 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20345 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20346 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r20347 | 432 | 199.526 | first_order (yes) | linear (yes) |
| MT | cl | r20348 | 432 | 199.526 | first_order (yes) | linear (yes) |
| MT | cl | r20349 | 396 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r20350 | 396 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r20351 | 385 | 0 | - | - |
| MT | cl | r20352 | 385 | 0 | - | - |
| MT | cl | r20353 | 385 | 0 | - | - |
| MT | cl | r20354 | 385 | 0 | - | - |
| MT | cl | r20355 | 385 | 0 | - | - |
| MT | cl | r20356 | 385 | 0 | - | - |
| HSD | cl | r0 | 5797 | 0 | - | - |
| HSD | cl | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20341 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20342 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20343 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20344 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20345 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20346 | 432 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r20347 | 432 | 199.526 | first_order (yes) | linear (yes) |
| HSD | cl | r20348 | 432 | 199.526 | first_order (yes) | linear (yes) |
| HSD | cl | r20349 | 396 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r20350 | 396 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r20351 | 385 | 0 | - | - |
| HSD | cl | r20352 | 385 | 0 | - | - |
| HSD | cl | r20353 | 385 | 0 | - | - |
| HSD | cl | r20354 | 385 | 0 | - | - |
| HSD | cl | r20355 | 385 | 0 | - | - |
| HSD | cl | r20356 | 385 | 0 | - | - |
| MT | sv | b0 | 5811 | 0 | - | - |
| MT | sv | r90 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20341 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20342 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20343 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20344 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20345 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20346 | 432 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r20347 | 432 | 199.526 | first_order (yes) | linear (yes) |
| MT | sv | r20348 | 432 | 199.526 | first_order (yes) | linear (yes) |
| MT | sv | r20349 | 396 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r20350 | 396 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r20351 | 385 | 0 | - | - |
| MT | sv | r20352 | 385 | 0 | - | - |
| MT | sv | r20353 | 385 | 0 | - | - |
| MT | sv | r20354 | 385 | 0 | - | - |
| MT | sv | r20355 | 385 | 0 | - | - |
| MT | sv | r20356 | 385 | 0 | - | - |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
