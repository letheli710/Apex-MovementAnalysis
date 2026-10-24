# hsd_tel report

Inputs: 16 file(s); rows: 43154 (MT 28815, HSD 14337)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3577 teleport in stream ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` message.log:4602 teleport in stream ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` message.log:5622 teleport in stream ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` message.log:6642 teleport in stream ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` message.log:7670 teleport in stream ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` script.log:3215 teleport in stream ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` script.log:5077 teleport in stream ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` script.log:6935 teleport in stream ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` script.log:8794 teleport in stream ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` script.log:10652 teleport in stream ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, '495cddc0-e2af-4873-b0aa-6791b3e8bb9a')
- warning `W_TELEPORT` message.log:3351 teleport in stream ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_TELEPORT` message.log:4371 teleport in stream ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_TELEPORT` message.log:5379 teleport in stream ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_TELEPORT` message.log:6386 teleport in stream ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_TELEPORT` message.log:7392 teleport in stream ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')
- warning `W_TIME_BACKWARDS` script.log:718 t 28.15 -> 28.07253 in ('HSD', 'sv', 'evt', 1.0, '2efd076a-a2e8-4d64-bee1-2899c7e1bd9d')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4698 | 0 | - | - |
| MT | cl | r90 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | cl | r8801 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | cl | r8802 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | cl | r8803 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | cl | r8804 | 840 | 515.826 | first_order (no) | linear (no) |
| MT | cl | r8805 | 840 | 515.827 | first_order (no) | linear (no) |
| MT | cl | r8806 | 840 | 515.826 | first_order (no) | linear (no) |
| MT | cl | r8807 | 1237 | 515.828 | first_order (no) | linear (no) |
| MT | cl | r8808 | 1237 | 515.829 | first_order (no) | linear (no) |
| MT | cl | r8809 | 1237 | 515.83 | first_order (no) | linear (no) |
| HSD | cl | r0 | 4674 | 0 | - | - |
| HSD | cl | r90 | 841 | 414.98 | first_order (no) | linear (yes) |
| HSD | cl | r8801 | 841 | 414.98 | first_order (no) | linear (yes) |
| HSD | cl | r8802 | 841 | 414.98 | first_order (no) | linear (yes) |
| HSD | cl | r8803 | 841 | 414.98 | first_order (no) | linear (yes) |
| HSD | cl | r8804 | 840 | 515.826 | first_order (yes) | linear (no) |
| HSD | cl | r8805 | 840 | 515.827 | first_order (yes) | linear (no) |
| HSD | cl | r8806 | 840 | 515.826 | first_order (yes) | linear (no) |
| HSD | cl | r8807 | 1237 | 515.828 | first_order (no) | linear (no) |
| HSD | cl | r8808 | 1237 | 515.829 | first_order (no) | linear (no) |
| HSD | cl | r8809 | 1237 | 515.83 | first_order (no) | linear (no) |
| MT | sv | b0 | 4699 | 0 | - | - |
| MT | sv | r90 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | sv | r8801 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | sv | r8802 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | sv | r8803 | 841 | 414.98 | first_order (no) | linear (yes) |
| MT | sv | r8804 | 840 | 515.826 | first_order (no) | linear (no) |
| MT | sv | r8805 | 840 | 515.827 | first_order (no) | linear (no) |
| MT | sv | r8806 | 840 | 515.826 | first_order (no) | linear (no) |
| MT | sv | r8807 | 1237 | 515.828 | first_order (no) | linear (no) |
| MT | sv | r8808 | 1237 | 515.829 | first_order (no) | linear (no) |
| MT | sv | r8809 | 1237 | 515.83 | first_order (no) | linear (no) |

Events: 50. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
