# hsd_tel report

Inputs: 16 file(s); rows: 39833 (MT 26303, HSD 13528)

Validation: 0 error(s), 20 warning(s), 2 info

- warning `W_TELEPORT` message.log:3521 teleport in stream ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` message.log:5165 teleport in stream ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` message.log:5792 teleport in stream ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` message.log:6417 teleport in stream ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` message.log:7041 teleport in stream ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` script.log:3192 teleport in stream ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` script.log:4862 teleport in stream ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` script.log:5492 teleport in stream ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` script.log:6121 teleport in stream ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` script.log:6750 teleport in stream ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, 'e4958dbb-f726-4ba9-b94d-6be7c2b86cd4')
- warning `W_TELEPORT` message.log:3301 teleport in stream ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TELEPORT` message.log:4939 teleport in stream ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TELEPORT` message.log:5556 teleport in stream ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TELEPORT` message.log:6173 teleport in stream ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TELEPORT` message.log:6791 teleport in stream ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TELEPORT` script.log:768 teleport in stream ('HSD', 'sv', 'evt', 1.0, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')
- warning `W_TIME_BACKWARDS` script.log:714 t 27.3 -> 27.06388 in ('HSD', 'sv', 'evt', 1.0, '372c3d73-3c94-4f8d-97d2-4d50faf2d435')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5825 | 0 | - | - |
| MT | cl | r90 | 241 | 0 | - | - |
| MT | cl | r27201 | 241 | 0 | - | - |
| MT | cl | r27202 | 241 | 0 | - | - |
| MT | cl | r27203 | 241 | 0 | - | - |
| MT | cl | r27204 | 434 | 200.863 | first_order (yes) | linear (no) |
| MT | cl | r27205 | 434 | 200.864 | first_order (yes) | linear (no) |
| MT | cl | r27206 | 433 | 200.864 | first_order (yes) | linear (no) |
| MT | cl | r27207 | 434 | 200.863 | first_order (yes) | linear (no) |
| MT | cl | r27208 | 733 | 457.804 | first_order (no) | - |
| MT | cl | r27209 | 733 | 457.804 | first_order (no) | - |
| MT | cl | r27210 | 733 | 457.803 | first_order (no) | - |
| MT | cl | r27211 | 733 | 457.804 | first_order (no) | - |
| MT | cl | r27212 | 332 | 0 | - | - |
| MT | cl | r27213 | 332 | 0 | - | - |
| MT | cl | r27214 | 332 | 0 | - | - |
| MT | cl | r27215 | 332 | 0 | - | - |
| HSD | cl | r0 | 5811 | 0 | - | - |
| HSD | cl | r90 | 241 | 0 | - | - |
| HSD | cl | r27201 | 241 | 0 | - | - |
| HSD | cl | r27202 | 241 | 0 | - | - |
| HSD | cl | r27203 | 241 | 0 | - | - |
| HSD | cl | r27204 | 434 | 200.863 | first_order (yes) | linear (yes) |
| HSD | cl | r27205 | 434 | 200.864 | first_order (yes) | linear (yes) |
| HSD | cl | r27206 | 433 | 200.864 | first_order (yes) | linear (yes) |
| HSD | cl | r27207 | 434 | 200.863 | first_order (yes) | linear (yes) |
| HSD | cl | r27208 | 733 | 457.804 | first_order (no) | - |
| HSD | cl | r27209 | 733 | 457.804 | first_order (no) | - |
| HSD | cl | r27210 | 733 | 457.803 | first_order (no) | - |
| HSD | cl | r27211 | 733 | 457.804 | first_order (no) | - |
| HSD | cl | r27212 | 332 | 0 | - | - |
| HSD | cl | r27213 | 332 | 0 | - | - |
| HSD | cl | r27214 | 332 | 0 | - | - |
| HSD | cl | r27215 | 332 | 0 | - | - |
| MT | sv | b0 | 5825 | 0 | - | - |
| MT | sv | r90 | 241 | 0 | - | - |
| MT | sv | r27201 | 241 | 0 | - | - |
| MT | sv | r27202 | 241 | 0 | - | - |
| MT | sv | r27203 | 241 | 0 | - | - |
| MT | sv | r27204 | 434 | 200.863 | first_order (yes) | linear (no) |
| MT | sv | r27205 | 434 | 200.864 | first_order (yes) | linear (no) |
| MT | sv | r27206 | 433 | 200.864 | first_order (yes) | linear (no) |
| MT | sv | r27207 | 434 | 200.863 | first_order (yes) | linear (no) |
| MT | sv | r27208 | 733 | 457.804 | first_order (no) | - |
| MT | sv | r27209 | 733 | 457.804 | first_order (no) | - |
| MT | sv | r27210 | 733 | 457.803 | first_order (no) | - |
| MT | sv | r27211 | 733 | 457.804 | first_order (no) | - |
| MT | sv | r27212 | 332 | 0 | - | - |
| MT | sv | r27213 | 332 | 0 | - | - |
| MT | sv | r27214 | 332 | 0 | - | - |
| MT | sv | r27215 | 332 | 0 | - | - |

Events: 1446. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
