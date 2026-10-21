# hsd_tel report

Inputs: 19 file(s); rows: 124435 (MT 82735, HSD 41640)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.1.log:15472 teleport in stream ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` message.1.log:16964 teleport in stream ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` message.1.log:23227 teleport in stream ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` message.1.log:24249 teleport in stream ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` message.1.log:25244 teleport in stream ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_MORE` message.1.log:0 14 more teleport rows in ('MT', 'cl', 'cmd', 1, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` script.1.log:15120 teleport in stream ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` script.1.log:16639 teleport in stream ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` script.1.log:22898 teleport in stream ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` script.1.log:23923 teleport in stream ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` script.1.log:24922 teleport in stream ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_MORE` script.1.log:0 14 more teleport rows in ('HSD', 'cl', 'frame', None, 'd792523b-adcd-4665-934a-eefd0bb36924')
- warning `W_TELEPORT` message.1.log:15266 teleport in stream ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_TELEPORT` message.1.log:16756 teleport in stream ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_TELEPORT` message.1.log:22945 teleport in stream ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_TELEPORT` message.1.log:23963 teleport in stream ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_TELEPORT` message.1.log:24956 teleport in stream ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_MORE` message.1.log:0 14 more teleport rows in ('MT', 'sv', 'cmd', 1, 'd67a6684-94d9-454a-b749-36c3e0c03800')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.45 -> 25.18485 in ('HSD', 'sv', 'evt', 1.0, 'd67a6684-94d9-454a-b749-36c3e0c03800')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 24277 | 488.108 | - | linear (yes) |
| MT | cl | r190 | 1233 | 344.875 | first_order (no) | - |
| MT | cl | r191 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r121 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r122 | 792 | 299 | first_order (no) | linear (yes) |
| MT | cl | r123 | 1008 | 92 | linear (yes) | linear (yes) |
| MT | cl | r124 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r125 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r126 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | cl | r127 | 936 | 299.001 | first_order (no) | linear (yes) |
| MT | cl | r128 | 753 | 299.031 | first_order (no) | friction (no) |
| MT | cl | r129 | 653 | 299.032 | first_order (no) | friction (no) |
| MT | cl | r130 | 793 | 299.308 | first_order (no) | linear (yes) |
| MT | cl | r131 | 361 | 0 | - | - |
| MT | cl | r132 | 983 | 299.309 | first_order (no) | linear (yes) |
| MT | cl | r133 | 995 | 299.148 | first_order (no) | linear (yes) |
| MT | cl | r134 | 1155 | 299.26 | first_order (no) | linear (yes) |
| MT | cl | r135 | 936 | 458.002 | first_order (no) | linear (no) |
| MT | cl | r136 | 822 | 458.169 | first_order (no) | linear (no) |
| MT | cl | r137 | 879 | 458.169 | first_order (no) | linear (no) |
| HSD | cl | r0 | 24253 | 488.108 | - | linear (yes) |
| HSD | cl | r190 | 1233 | 342.576 | first_order (no) | - |
| HSD | cl | r191 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r121 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r122 | 792 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r123 | 1008 | 92 | linear (yes) | linear (yes) |
| HSD | cl | r124 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r125 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r126 | 792 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r127 | 936 | 299.001 | first_order (no) | linear (yes) |
| HSD | cl | r128 | 753 | 299.031 | first_order (no) | friction (no) |
| HSD | cl | r129 | 653 | 299.032 | first_order (no) | linear (yes) |
| HSD | cl | r130 | 793 | 299.308 | first_order (no) | linear (yes) |
| HSD | cl | r131 | 361 | 0 | - | - |
| HSD | cl | r132 | 983 | 299.309 | first_order (no) | linear (yes) |
| HSD | cl | r133 | 995 | 299.148 | first_order (no) | linear (yes) |
| HSD | cl | r134 | 1155 | 299.26 | first_order (no) | linear (yes) |
| HSD | cl | r135 | 936 | 458.002 | first_order (no) | linear (no) |
| HSD | cl | r136 | 822 | 458.169 | first_order (no) | linear (no) |
| HSD | cl | r137 | 879 | 458.169 | first_order (no) | linear (no) |
| MT | sv | b0 | 24302 | 488.108 | - | linear (yes) |
| MT | sv | r190 | 1233 | 344.875 | first_order (no) | - |
| MT | sv | r191 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r90 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r121 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r122 | 792 | 299 | first_order (no) | linear (yes) |
| MT | sv | r123 | 1008 | 92 | linear (yes) | linear (yes) |
| MT | sv | r124 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r125 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r126 | 792 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | r127 | 936 | 299.001 | first_order (no) | linear (yes) |
| MT | sv | r128 | 753 | 299.031 | first_order (no) | friction (no) |
| MT | sv | r129 | 653 | 299.032 | first_order (no) | friction (no) |
| MT | sv | r130 | 793 | 299.308 | first_order (no) | linear (yes) |
| MT | sv | r131 | 361 | 0 | - | - |
| MT | sv | r132 | 983 | 299.309 | first_order (no) | linear (yes) |
| MT | sv | r133 | 995 | 299.148 | first_order (no) | linear (yes) |
| MT | sv | r134 | 1155 | 299.26 | first_order (no) | linear (yes) |
| MT | sv | r135 | 936 | 458.002 | first_order (no) | linear (no) |
| MT | sv | r136 | 822 | 458.169 | first_order (no) | linear (no) |
| MT | sv | r137 | 879 | 458.169 | first_order (no) | linear (no) |

Events: 326. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
