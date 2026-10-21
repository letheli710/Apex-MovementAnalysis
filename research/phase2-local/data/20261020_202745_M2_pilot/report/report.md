# hsd_tel report

Inputs: 16 file(s); rows: 66381 (MT 44035, HSD 22286)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:4217 teleport in stream ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` message.log:5214 teleport in stream ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` message.log:6210 teleport in stream ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` message.log:7422 teleport in stream ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` message.log:9413 teleport in stream ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_MORE` message.log:0 10 more teleport rows in ('MT', 'cl', 'cmd', 1, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` script.log:3883 teleport in stream ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` script.log:4883 teleport in stream ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` script.log:5884 teleport in stream ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` script.log:7101 teleport in stream ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` script.log:9097 teleport in stream ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_MORE` script.log:0 10 more teleport rows in ('HSD', 'cl', 'frame', None, '129c3e8c-6498-43f2-911d-373b6f3cf92c')
- warning `W_TELEPORT` message.log:3968 teleport in stream ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_TELEPORT` message.log:4961 teleport in stream ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_TELEPORT` message.log:5954 teleport in stream ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_TELEPORT` message.log:7162 teleport in stream ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_TELEPORT` message.log:9144 teleport in stream ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_MORE` message.log:0 10 more teleport rows in ('MT', 'sv', 'cmd', 1, '022caf80-5eee-4036-9151-00d4979d3ef6')
- warning `W_TIME_BACKWARDS` script.log:717 t 27.7 -> 27.43866 in ('HSD', 'sv', 'evt', 1.0, '022caf80-5eee-4036-9151-00d4979d3ef6')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6213 | 0 | - | - |
| MT | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r101 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r102 | 792 | 299 | first_order (no) | linear (yes) |
| MT | cl | r103 | 1008 | 92 | linear (yes) | linear (yes) |
| MT | cl | r104 | 792 | 0 | - | - |
| MT | cl | r105 | 792 | 199.525 | first_order (yes) | - |
| MT | cl | r106 | 792 | 199.524 | first_order (yes) | friction (no) |
| MT | cl | r107 | 936 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r108 | 753 | 299.031 | first_order (no) | friction (no) |
| MT | cl | r109 | 653 | 299.031 | first_order (no) | friction (no) |
| MT | cl | r110 | 793 | 299.296 | first_order (no) | linear (yes) |
| MT | cl | r111 | 361 | 0 | - | - |
| MT | cl | r112 | 1233 | 299.647 | first_order (no) | linear (yes) |
| MT | cl | r113 | 1245 | 299.669 | first_order (no) | linear (yes) |
| MT | cl | r114 | 1405 | 299.991 | first_order (no) | linear (yes) |
| MT | cl | r115 | 936 | 458.169 | first_order (no) | linear (no) |
| MT | cl | r116 | 822 | 458.221 | first_order (no) | linear (no) |
| MT | cl | r117 | 879 | 458.169 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 6186 | 0 | - | - |
| HSD | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r101 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r102 | 792 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r103 | 1008 | 92 | linear (yes) | linear (yes) |
| HSD | cl | r104 | 792 | 0 | - | - |
| HSD | cl | r105 | 792 | 199.525 | first_order (yes) | - |
| HSD | cl | r106 | 792 | 199.524 | first_order (yes) | friction (no) |
| HSD | cl | r107 | 936 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r108 | 753 | 299.031 | first_order (no) | friction (no) |
| HSD | cl | r109 | 653 | 299.031 | first_order (no) | linear (yes) |
| HSD | cl | r110 | 793 | 299.296 | first_order (no) | linear (yes) |
| HSD | cl | r111 | 361 | 0 | - | - |
| HSD | cl | r112 | 1233 | 299.647 | first_order (no) | linear (yes) |
| HSD | cl | r113 | 1245 | 299.669 | first_order (no) | linear (yes) |
| HSD | cl | r114 | 1405 | 299.991 | first_order (no) | linear (yes) |
| HSD | cl | r115 | 936 | 458.169 | first_order (no) | linear (no) |
| HSD | cl | r116 | 822 | 458.221 | first_order (no) | linear (no) |
| HSD | cl | r117 | 879 | 458.169 | first_order (no) | linear (yes) |
| MT | sv | b0 | 6223 | 0 | - | - |
| MT | sv | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r101 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r102 | 792 | 299 | first_order (no) | linear (yes) |
| MT | sv | r103 | 1008 | 92 | linear (yes) | linear (yes) |
| MT | sv | r104 | 792 | 0 | - | - |
| MT | sv | r105 | 792 | 199.525 | first_order (yes) | - |
| MT | sv | r106 | 792 | 199.524 | first_order (yes) | linear (no) |
| MT | sv | r107 | 936 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r108 | 753 | 299.031 | first_order (no) | friction (no) |
| MT | sv | r109 | 653 | 299.031 | first_order (no) | friction (no) |
| MT | sv | r110 | 793 | 299.296 | first_order (no) | linear (yes) |
| MT | sv | r111 | 361 | 0 | - | - |
| MT | sv | r112 | 1233 | 299.647 | first_order (no) | linear (yes) |
| MT | sv | r113 | 1245 | 299.669 | first_order (no) | linear (yes) |
| MT | sv | r114 | 1405 | 299.991 | first_order (no) | linear (yes) |
| MT | sv | r115 | 936 | 458.169 | first_order (no) | linear (no) |
| MT | sv | r116 | 822 | 458.221 | first_order (no) | linear (no) |
| MT | sv | r117 | 879 | 458.169 | first_order (no) | linear (yes) |

Events: 316. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
