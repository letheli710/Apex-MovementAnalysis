# hsd_tel report

Inputs: 16 file(s); rows: 15776 (MT 9472, HSD 6302)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3604 teleport in stream ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` message.log:3915 teleport in stream ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` message.log:4197 teleport in stream ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` message.log:4500 teleport in stream ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` message.log:4805 teleport in stream ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` script.log:3219 teleport in stream ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` script.log:3786 teleport in stream ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` script.log:4335 teleport in stream ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` script.log:4900 teleport in stream ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` script.log:5469 teleport in stream ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, 'e768febd-19e9-4dcb-abdd-78584d2349e7')
- warning `W_TELEPORT` message.log:3370 teleport in stream ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_TELEPORT` message.log:3698 teleport in stream ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_TELEPORT` message.log:3983 teleport in stream ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_TELEPORT` message.log:4273 teleport in stream ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_TELEPORT` message.log:4572 teleport in stream ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '507ae49d-8976-46a3-b605-1189a5163644')
- warning `W_TIME_BACKWARDS` script.log:718 t 29.4 -> 29.22458 in ('HSD', 'sv', 'evt', 1.0, '507ae49d-8976-46a3-b605-1189a5163644')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2994 | 0 | - | - |
| MT | cl | r90 | 120 | 600 | - | - |
| MT | cl | b1 | 171 | 402.077 | - | - |
| MT | cl | r8881 | 121 | 600 | - | - |
| MT | cl | b2 | 151 | 399.525 | - | - |
| MT | cl | r8882 | 121 | 600 | - | - |
| MT | cl | b3 | 169 | 391.645 | - | - |
| MT | cl | r8883 | 120 | 600 | - | - |
| MT | cl | b4 | 173 | 402.06 | - | - |
| MT | cl | r8884 | 120 | 600 | - | - |
| MT | cl | b5 | 173 | 402.048 | - | - |
| MT | cl | r8885 | 120 | 600 | - | - |
| MT | cl | b6 | 134 | 402.039 | - | - |
| HSD | cl | r0 | 3940 | 412.494 | - | linear (yes) |
| HSD | cl | r90 | 385 | 600 | - | - |
| HSD | cl | r8881 | 385 | 600 | - | - |
| HSD | cl | r8882 | 385 | 600 | - | - |
| HSD | cl | r8883 | 385 | 600 | - | - |
| HSD | cl | r8884 | 385 | 600 | - | - |
| HSD | cl | r8885 | 385 | 600 | - | - |
| MT | sv | b0 | 3009 | 0 | - | - |
| MT | sv | r90 | 120 | 600 | - | - |
| MT | sv | b1 | 171 | 402.077 | - | - |
| MT | sv | r8881 | 121 | 600 | - | - |
| MT | sv | b2 | 151 | 399.525 | - | - |
| MT | sv | r8882 | 121 | 600 | - | - |
| MT | sv | b3 | 169 | 391.645 | - | - |
| MT | sv | r8883 | 120 | 600 | - | - |
| MT | sv | b4 | 173 | 402.06 | - | - |
| MT | sv | r8884 | 120 | 600 | - | - |
| MT | sv | b5 | 173 | 402.048 | - | - |
| MT | sv | r8885 | 120 | 600 | - | - |
| MT | sv | b6 | 130 | 402.039 | - | - |

Events: 50. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
