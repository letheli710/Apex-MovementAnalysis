# hsd_tel report

Inputs: 16 file(s); rows: 23102 (MT 15416, HSD 7684)

Validation: 0 error(s), 16 warning(s), 2 info

- warning `W_TELEPORT` message.log:3674 teleport in stream ('MT', 'cl', 'cmd', 1, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` message.log:4627 teleport in stream ('MT', 'cl', 'cmd', 1, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` message.log:5583 teleport in stream ('MT', 'cl', 'cmd', 1, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` message.log:6538 teleport in stream ('MT', 'cl', 'cmd', 1, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` message.log:7432 teleport in stream ('MT', 'cl', 'cmd', 1, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` script.log:3333 teleport in stream ('HSD', 'cl', 'frame', None, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` script.log:4287 teleport in stream ('HSD', 'cl', 'frame', None, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` script.log:5244 teleport in stream ('HSD', 'cl', 'frame', None, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` script.log:6201 teleport in stream ('HSD', 'cl', 'frame', None, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` script.log:7099 teleport in stream ('HSD', 'cl', 'frame', None, 'cd4420ca-fafc-43ed-ba6e-3f955f110096')
- warning `W_TELEPORT` message.log:3476 teleport in stream ('MT', 'sv', 'cmd', 1, '93a850c1-9cc9-4b70-8a58-c3b69f326398')
- warning `W_TELEPORT` message.log:4425 teleport in stream ('MT', 'sv', 'cmd', 1, '93a850c1-9cc9-4b70-8a58-c3b69f326398')
- warning `W_TELEPORT` message.log:5373 teleport in stream ('MT', 'sv', 'cmd', 1, '93a850c1-9cc9-4b70-8a58-c3b69f326398')
- warning `W_TELEPORT` message.log:6322 teleport in stream ('MT', 'sv', 'cmd', 1, '93a850c1-9cc9-4b70-8a58-c3b69f326398')
- warning `W_TELEPORT` message.log:7211 teleport in stream ('MT', 'sv', 'cmd', 1, '93a850c1-9cc9-4b70-8a58-c3b69f326398')
- warning `W_TIME_BACKWARDS` script.log:714 t 23.8 -> 23.61158 in ('HSD', 'sv', 'evt', 1.0, '93a850c1-9cc9-4b70-8a58-c3b69f326398')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3961 | 0 | - | - |
| MT | cl | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8841 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8842 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r8843 | 708 | 299 | first_order (no) | linear (yes) |
| MT | cl | r8844 | 708 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 3940 | 0 | - | - |
| HSD | cl | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8841 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8842 | 768 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r8843 | 708 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r8844 | 708 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 3974 | 0 | - | - |
| MT | sv | r90 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8841 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8842 | 768 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r8843 | 708 | 299 | first_order (no) | linear (yes) |
| MT | sv | r8844 | 708 | 299 | first_order (no) | linear (yes) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
