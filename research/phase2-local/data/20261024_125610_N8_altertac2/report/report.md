# hsd_tel report

Inputs: 16 file(s); rows: 20568 (MT 13731, HSD 6835)

Validation: 0 error(s), 13 warning(s), 2 info

- warning `W_TELEPORT` message.log:3715 teleport in stream ('MT', 'cl', 'cmd', 1, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` message.log:4666 teleport in stream ('MT', 'cl', 'cmd', 1, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` message.log:5619 teleport in stream ('MT', 'cl', 'cmd', 1, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` message.log:6571 teleport in stream ('MT', 'cl', 'cmd', 1, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` script.log:3353 teleport in stream ('HSD', 'cl', 'frame', None, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` script.log:4307 teleport in stream ('HSD', 'cl', 'frame', None, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` script.log:5264 teleport in stream ('HSD', 'cl', 'frame', None, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` script.log:6221 teleport in stream ('HSD', 'cl', 'frame', None, '7680e5e7-35b5-4bff-9280-3cdb6ae8eeff')
- warning `W_TELEPORT` message.log:3497 teleport in stream ('MT', 'sv', 'cmd', 1, '8d415221-d377-4511-b2a6-bbfd97112a2c')
- warning `W_TELEPORT` message.log:4447 teleport in stream ('MT', 'sv', 'cmd', 1, '8d415221-d377-4511-b2a6-bbfd97112a2c')
- warning `W_TELEPORT` message.log:5397 teleport in stream ('MT', 'sv', 'cmd', 1, '8d415221-d377-4511-b2a6-bbfd97112a2c')
- warning `W_TELEPORT` message.log:6347 teleport in stream ('MT', 'sv', 'cmd', 1, '8d415221-d377-4511-b2a6-bbfd97112a2c')
- warning `W_TIME_BACKWARDS` script.log:714 t 23.05 -> 22.87918 in ('HSD', 'sv', 'evt', 1.0, '8d415221-d377-4511-b2a6-bbfd97112a2c')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3825 | 0 | - | - |
| MT | cl | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8851 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8852 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8853 | 708 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 3803 | 0 | - | - |
| HSD | cl | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8851 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8852 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8853 | 708 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 3833 | 0 | - | - |
| MT | sv | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8851 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8852 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8853 | 708 | 299 | first_order (no) | linear (yes) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
