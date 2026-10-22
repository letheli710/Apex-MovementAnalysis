# hsd_tel report

Inputs: 16 file(s); rows: 56370 (MT 37524, HSD 18844)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3712 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` message.log:4299 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` message.log:4890 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` message.log:5479 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` message.log:6071 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_MORE` message.log:0 17 more teleport rows in ('MT', 'cl', 'cmd', 1, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` script.log:3361 teleport in stream ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` script.log:4370 teleport in stream ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` script.log:5383 teleport in stream ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` script.log:6395 teleport in stream ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` script.log:7408 teleport in stream ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_MORE` script.log:0 17 more teleport rows in ('HSD', 'cl', 'frame', None, 'd9c9674f-f92f-4123-9e57-47b9253b4fea')
- warning `W_TELEPORT` message.log:3508 teleport in stream ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_TELEPORT` message.log:4101 teleport in stream ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_TELEPORT` message.log:4693 teleport in stream ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_TELEPORT` message.log:5284 teleport in stream ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_TELEPORT` message.log:5876 teleport in stream ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_MORE` message.log:0 17 more teleport rows in ('MT', 'sv', 'cmd', 1, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')
- warning `W_TIME_BACKWARDS` script.log:719 t 22.95 -> 22.77888 in ('HSD', 'sv', 'evt', 1.0, '92ef1c61-c1af-4069-a0b4-5fb74e9c46e9')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 7788 | 0 | - | - |
| MT | cl | r90 | 410 | 285.81 | first_order (no) | friction (no) |
| MT | cl | r13001 | 410 | 286.071 | first_order (no) | friction (no) |
| MT | cl | r13002 | 410 | 286.044 | first_order (no) | friction (no) |
| MT | cl | r13003 | 410 | 286.066 | first_order (no) | friction (no) |
| MT | cl | r13004 | 410 | 286.11 | first_order (no) | friction (no) |
| MT | cl | r13005 | 410 | 286.114 | first_order (no) | friction (no) |
| MT | cl | r13006 | 411 | 287.072 | first_order (no) | friction (no) |
| MT | cl | r13007 | 411 | 287.083 | first_order (no) | friction (no) |
| MT | cl | r13008 | 411 | 287.151 | first_order (no) | friction (no) |
| MT | cl | r13009 | 411 | 287.067 | first_order (no) | friction (no) |
| MT | cl | r13010 | 411 | 286.363 | first_order (no) | friction (no) |
| MT | cl | r13011 | 409 | 286.146 | first_order (no) | linear (yes) |
| MT | cl | r13012 | 409 | 286.108 | first_order (no) | linear (yes) |
| MT | cl | r13013 | 409 | 286.077 | first_order (no) | linear (yes) |
| MT | cl | r13014 | 409 | 286.104 | first_order (no) | linear (yes) |
| MT | cl | r13015 | 409 | 286.116 | first_order (no) | linear (yes) |
| MT | cl | r13016 | 397 | 0 | - | - |
| MT | cl | r13017 | 397 | 0 | - | - |
| MT | cl | r13018 | 397 | 0 | - | - |
| MT | cl | r13019 | 397 | 0 | - | - |
| MT | cl | r13020 | 397 | 0 | - | - |
| MT | cl | r13021 | 475 | 457.803 | first_order (no) | linear (yes) |
| MT | cl | r13022 | 475 | 457.81 | first_order (no) | linear (yes) |
| MT | cl | r13023 | 477 | 457.804 | first_order (no) | linear (yes) |
| MT | cl | r13024 | 475 | 457.804 | first_order (no) | linear (yes) |
| MT | cl | r13025 | 475 | 457.808 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 7761 | 0 | - | - |
| HSD | cl | r90 | 410 | 285.81 | first_order (no) | linear (yes) |
| HSD | cl | r13001 | 410 | 286.071 | first_order (no) | linear (yes) |
| HSD | cl | r13002 | 410 | 286.044 | first_order (no) | linear (yes) |
| HSD | cl | r13003 | 410 | 286.066 | first_order (no) | linear (yes) |
| HSD | cl | r13004 | 410 | 286.11 | first_order (no) | linear (yes) |
| HSD | cl | r13005 | 410 | 286.114 | first_order (no) | linear (yes) |
| HSD | cl | r13006 | 411 | 287.072 | first_order (no) | linear (yes) |
| HSD | cl | r13007 | 411 | 287.083 | first_order (no) | linear (yes) |
| HSD | cl | r13008 | 411 | 287.151 | first_order (no) | linear (yes) |
| HSD | cl | r13009 | 411 | 287.067 | first_order (no) | linear (yes) |
| HSD | cl | r13010 | 411 | 286.363 | first_order (no) | linear (yes) |
| HSD | cl | r13011 | 409 | 286.146 | first_order (no) | linear (yes) |
| HSD | cl | r13012 | 409 | 286.108 | first_order (no) | linear (yes) |
| HSD | cl | r13013 | 409 | 286.077 | first_order (no) | linear (yes) |
| HSD | cl | r13014 | 409 | 286.104 | first_order (no) | linear (yes) |
| HSD | cl | r13015 | 409 | 286.116 | first_order (no) | linear (yes) |
| HSD | cl | r13016 | 397 | 0 | - | - |
| HSD | cl | r13017 | 397 | 0 | - | - |
| HSD | cl | r13018 | 397 | 0 | - | - |
| HSD | cl | r13019 | 397 | 0 | - | - |
| HSD | cl | r13020 | 397 | 0 | - | - |
| HSD | cl | r13021 | 475 | 457.803 | first_order (no) | linear (yes) |
| HSD | cl | r13022 | 475 | 457.81 | first_order (no) | linear (yes) |
| HSD | cl | r13023 | 475 | 457.804 | first_order (no) | linear (yes) |
| HSD | cl | r13024 | 475 | 457.804 | first_order (no) | linear (yes) |
| HSD | cl | r13025 | 475 | 457.808 | first_order (no) | linear (yes) |
| MT | sv | b0 | 7792 | 0 | - | - |
| MT | sv | r90 | 410 | 285.81 | first_order (no) | friction (no) |
| MT | sv | r13001 | 410 | 286.071 | first_order (no) | friction (no) |
| MT | sv | r13002 | 410 | 286.044 | first_order (no) | friction (no) |
| MT | sv | r13003 | 410 | 286.066 | first_order (no) | friction (no) |
| MT | sv | r13004 | 410 | 286.11 | first_order (no) | friction (no) |
| MT | sv | r13005 | 410 | 286.114 | first_order (no) | friction (no) |
| MT | sv | r13006 | 411 | 287.072 | first_order (no) | friction (no) |
| MT | sv | r13007 | 411 | 287.083 | first_order (no) | friction (no) |
| MT | sv | r13008 | 411 | 287.151 | first_order (no) | friction (no) |
| MT | sv | r13009 | 411 | 287.067 | first_order (no) | friction (no) |
| MT | sv | r13010 | 411 | 286.363 | first_order (no) | friction (no) |
| MT | sv | r13011 | 409 | 286.146 | first_order (no) | linear (yes) |
| MT | sv | r13012 | 409 | 286.108 | first_order (no) | linear (yes) |
| MT | sv | r13013 | 409 | 286.077 | first_order (no) | linear (yes) |
| MT | sv | r13014 | 409 | 286.104 | first_order (no) | linear (yes) |
| MT | sv | r13015 | 409 | 286.116 | first_order (no) | linear (yes) |
| MT | sv | r13016 | 397 | 0 | - | - |
| MT | sv | r13017 | 397 | 0 | - | - |
| MT | sv | r13018 | 397 | 0 | - | - |
| MT | sv | r13019 | 397 | 0 | - | - |
| MT | sv | r13020 | 397 | 0 | - | - |
| MT | sv | r13021 | 475 | 457.803 | first_order (no) | linear (yes) |
| MT | sv | r13022 | 475 | 457.81 | first_order (no) | linear (yes) |
| MT | sv | r13023 | 477 | 457.804 | first_order (no) | linear (yes) |
| MT | sv | r13024 | 475 | 457.804 | first_order (no) | linear (yes) |
| MT | sv | r13025 | 475 | 457.808 | first_order (no) | linear (yes) |

Events: 153. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
