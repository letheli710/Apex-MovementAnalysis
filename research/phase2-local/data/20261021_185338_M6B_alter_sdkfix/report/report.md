# hsd_tel report

Inputs: 16 file(s); rows: 54900 (MT 35845, HSD 19053)

Validation: 0 error(s), 20 warning(s), 2 info

- warning `W_TELEPORT` message.log:3979 teleport in stream ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` message.log:5095 teleport in stream ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` message.log:6235 teleport in stream ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` message.log:7412 teleport in stream ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` message.log:8591 teleport in stream ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'cl', 'cmd', 1, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` script.log:3608 teleport in stream ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` script.log:5538 teleport in stream ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` script.log:7472 teleport in stream ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` script.log:9405 teleport in stream ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` script.log:11344 teleport in stream ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_MORE` script.log:0 9 more teleport rows in ('HSD', 'cl', 'frame', None, '9dc12c59-f6f5-4977-bdf8-f05b29c6cd50')
- warning `W_TELEPORT` message.log:3754 teleport in stream ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TELEPORT` message.log:5848 teleport in stream ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TELEPORT` message.log:7632 teleport in stream ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TELEPORT` message.log:9103 teleport in stream ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TELEPORT` message.log:10552 teleport in stream ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'sv', 'cmd', 1, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TELEPORT` script.log:797 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ee527903-8f57-4f1a-a505-e277633c53b9')
- warning `W_TIME_BACKWARDS` script.log:719 t 30.3 -> 30.02859 in ('HSD', 'sv', 'evt', 1.0, 'ee527903-8f57-4f1a-a505-e277633c53b9')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5796 | 0 | - | - |
| MT | cl | r90 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4501 | 769 | 199.525 | first_order (yes) | - |
| MT | cl | r4502 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4503 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4504 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4505 | 768 | 199.525 | first_order (yes) | - |
| MT | cl | r4506 | 708 | 299 | first_order (no) | - |
| MT | cl | r4507 | 713 | 299 | first_order (no) | - |
| MT | cl | r4508 | 708 | 299 | first_order (no) | - |
| MT | cl | r4509 | 709 | 299 | first_order (no) | - |
| MT | cl | r4510 | 708 | 299 | first_order (no) | - |
| MT | cl | r4511 | 804 | 199.525 | first_order (yes) | - |
| MT | cl | r4512 | 804 | 199.525 | first_order (yes) | - |
| MT | cl | r4513 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r0 | 5771 | 0 | - | - |
| HSD | cl | r90 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4501 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4502 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4503 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4504 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4505 | 768 | 199.525 | first_order (yes) | - |
| HSD | cl | r4506 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4507 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4508 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4509 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4510 | 708 | 299 | first_order (no) | - |
| HSD | cl | r4511 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r4512 | 804 | 199.525 | first_order (yes) | - |
| HSD | cl | r4513 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | b0 | 5806 | 0 | - | - |
| MT | sv | r90 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4501 | 769 | 199.525 | first_order (yes) | - |
| MT | sv | r4502 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4503 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4504 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4505 | 768 | 199.525 | first_order (yes) | - |
| MT | sv | r4506 | 708 | 299 | first_order (no) | - |
| MT | sv | r4507 | 713 | 299 | first_order (no) | - |
| MT | sv | r4508 | 708 | 299 | first_order (no) | - |
| MT | sv | r4509 | 709 | 299 | first_order (no) | - |
| MT | sv | r4510 | 708 | 299 | first_order (no) | - |
| MT | sv | r4511 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | r4512 | 804 | 199.525 | first_order (yes) | - |
| MT | sv | r4513 | 804 | 199.525 | first_order (yes) | - |

Events: 5294. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
