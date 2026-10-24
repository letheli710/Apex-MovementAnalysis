# hsd_tel report

Inputs: 16 file(s); rows: 13155 (MT 8363, HSD 4121)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4273 teleport in stream ('MT', 'cl', 'cmd', 1, '60ffc377-4669-463d-b1b8-33102ee471f3')
- warning `W_TELEPORT` script.log:3233 teleport in stream ('HSD', 'cl', 'frame', None, '60ffc377-4669-463d-b1b8-33102ee471f3')
- warning `W_TELEPORT` message.log:3371 teleport in stream ('MT', 'sv', 'cmd', 1, 'a5fd4b1a-ae2a-41f5-9e49-60ef065defd2')
- warning `W_TELEPORT` script.log:779 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'a5fd4b1a-ae2a-41f5-9e49-60ef065defd2')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.0 -> 23.73935 in ('HSD', 'sv', 'evt', 1.0, 'a5fd4b1a-ae2a-41f5-9e49-60ef065defd2')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3120 | 0 | - | - |
| MT | cl | r20110 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3087 | 0 | - | - |
| HSD | cl | r20110 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3140 | 0 | - | - |
| MT | sv | r20110 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
