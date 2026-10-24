# hsd_tel report

Inputs: 16 file(s); rows: 44990 (MT 30004, HSD 14984)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3657 teleport in stream ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` message.log:5373 teleport in stream ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` message.log:7178 teleport in stream ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` message.log:8991 teleport in stream ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` message.log:10713 teleport in stream ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` script.log:3285 teleport in stream ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` script.log:6601 teleport in stream ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` script.log:10007 teleport in stream ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` script.log:13417 teleport in stream ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` script.log:16642 teleport in stream ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '8b54cefe-7634-437f-9c5e-00c5aecc1092')
- warning `W_TELEPORT` message.log:3437 teleport in stream ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_TELEPORT` message.log:7716 teleport in stream ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_TELEPORT` message.log:11775 teleport in stream ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_TELEPORT` message.log:15187 teleport in stream ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_TELEPORT` message.log:18232 teleport in stream ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '6851a30b-0535-47d2-bca2-c1f170ec8977')
- warning `W_TIME_BACKWARDS` script.log:715 t 27.2 -> 26.89995 in ('HSD', 'sv', 'evt', 1.0, '6851a30b-0535-47d2-bca2-c1f170ec8977')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4275 | 0 | - | - |
| MT | cl | r90 | 1599 | 199.9 | first_order (yes) | linear (yes) |
| MT | cl | r8821 | 1599 | 199.898 | first_order (yes) | linear (yes) |
| MT | cl | r8822 | 1599 | 199.896 | first_order (yes) | linear (yes) |
| MT | cl | r8823 | 1504 | 199.899 | first_order (yes) | linear (yes) |
| MT | cl | r8824 | 1504 | 199.9 | first_order (yes) | linear (yes) |
| MT | cl | r8825 | 1419 | 199.865 | first_order (yes) | friction (no) |
| MT | cl | r8826 | 1419 | 199.878 | first_order (yes) | friction (no) |
| HSD | cl | r0 | 4245 | 0 | - | - |
| HSD | cl | r90 | 1599 | 199.9 | first_order (yes) | linear (yes) |
| HSD | cl | r8821 | 1599 | 199.898 | first_order (yes) | linear (yes) |
| HSD | cl | r8822 | 1599 | 199.896 | first_order (yes) | linear (yes) |
| HSD | cl | r8823 | 1504 | 199.899 | first_order (yes) | linear (yes) |
| HSD | cl | r8824 | 1504 | 199.9 | first_order (yes) | linear (yes) |
| HSD | cl | r8825 | 1419 | 199.865 | first_order (yes) | linear (yes) |
| HSD | cl | r8826 | 1419 | 199.878 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 4282 | 0 | - | - |
| MT | sv | r90 | 1599 | 199.9 | first_order (yes) | linear (yes) |
| MT | sv | r8821 | 1599 | 199.898 | first_order (yes) | linear (yes) |
| MT | sv | r8822 | 1599 | 199.896 | first_order (yes) | linear (yes) |
| MT | sv | r8823 | 1504 | 199.899 | first_order (yes) | linear (yes) |
| MT | sv | r8824 | 1504 | 199.9 | first_order (yes) | linear (yes) |
| MT | sv | r8825 | 1419 | 199.865 | first_order (yes) | friction (no) |
| MT | sv | r8826 | 1419 | 199.878 | first_order (yes) | friction (no) |

Events: 130. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
