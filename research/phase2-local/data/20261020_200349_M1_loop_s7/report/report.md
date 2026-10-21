# hsd_tel report

Inputs: 16 file(s); rows: 32291 (MT 21519, HSD 10770)

Validation: 0 error(s), 17 warning(s), 2 info

- warning `W_TELEPORT` message.log:4232 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` message.log:5662 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` message.log:7088 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` message.log:8517 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` message.log:9946 teleport in stream ('MT', 'cl', 'cmd', 1, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` script.log:3899 teleport in stream ('HSD', 'cl', 'frame', None, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` script.log:5334 teleport in stream ('HSD', 'cl', 'frame', None, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` script.log:6765 teleport in stream ('HSD', 'cl', 'frame', None, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` script.log:8200 teleport in stream ('HSD', 'cl', 'frame', None, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` script.log:9636 teleport in stream ('HSD', 'cl', 'frame', None, '72fb3f24-f55e-458a-ba46-e5d10cc552d3')
- warning `W_TELEPORT` message.log:4033 teleport in stream ('MT', 'sv', 'cmd', 1, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TELEPORT` message.log:5457 teleport in stream ('MT', 'sv', 'cmd', 1, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TELEPORT` message.log:6878 teleport in stream ('MT', 'sv', 'cmd', 1, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TELEPORT` message.log:8303 teleport in stream ('MT', 'sv', 'cmd', 1, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TELEPORT` message.log:9728 teleport in stream ('MT', 'sv', 'cmd', 1, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TELEPORT` script.log:732 teleport in stream ('HSD', 'sv', 'evt', 1.0, '496754ef-336e-4dff-bb10-79a1c6e90712')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.8 -> 24.58387 in ('HSD', 'sv', 'evt', 1.0, '496754ef-336e-4dff-bb10-79a1c6e90712')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3389 | 0 | - | - |
| MT | cl | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r41 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r42 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r43 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r44 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r45 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3362 | 0 | - | - |
| HSD | cl | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r41 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r42 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r43 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r44 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r45 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3400 | 0 | - | - |
| MT | sv | r90 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r41 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r42 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r43 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r44 | 1225 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r45 | 1225 | 199.525 | first_order (yes) | linear (yes) |

Events: 68. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
