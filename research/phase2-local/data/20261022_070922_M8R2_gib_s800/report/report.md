# hsd_tel report

Inputs: 16 file(s); rows: 34846 (MT 23083, HSD 11703)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:4165 teleport in stream ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` message.log:5514 teleport in stream ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` message.log:6859 teleport in stream ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` message.log:8205 teleport in stream ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` message.log:9558 teleport in stream ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` script.log:3795 teleport in stream ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` script.log:6319 teleport in stream ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` script.log:8836 teleport in stream ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` script.log:11354 teleport in stream ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` script.log:13873 teleport in stream ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '7589f15d-e9ba-489d-9839-13f7c91d1f07')
- warning `W_TELEPORT` message.log:3890 teleport in stream ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_TELEPORT` message.log:5236 teleport in stream ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_TELEPORT` message.log:6574 teleport in stream ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_TELEPORT` message.log:7913 teleport in stream ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_TELEPORT` message.log:9252 teleport in stream ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')
- warning `W_TIME_BACKWARDS` script.log:716 t 23.9 -> 23.6304 in ('HSD', 'sv', 'evt', 1.0, '3e06d869-0e97-4dd7-8d93-5ef7cf814a59')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4511 | 0 | - | - |
| MT | cl | r90 | 1165 | 299.149 | first_order (no) | - |
| MT | cl | r9661 | 1165 | 299.149 | first_order (no) | - |
| MT | cl | r9662 | 1165 | 299.149 | first_order (no) | - |
| MT | cl | r9663 | 1165 | 299.149 | first_order (no) | - |
| MT | cl | r9664 | 1165 | 299.147 | first_order (no) | - |
| MT | cl | r9665 | 1165 | 299.149 | first_order (no) | - |
| HSD | cl | r0 | 4483 | 0 | - | - |
| HSD | cl | r90 | 1165 | 299.149 | first_order (no) | - |
| HSD | cl | r9661 | 1165 | 299.149 | first_order (no) | - |
| HSD | cl | r9662 | 1165 | 299.149 | first_order (no) | - |
| HSD | cl | r9663 | 1165 | 299.149 | first_order (no) | - |
| HSD | cl | r9664 | 1165 | 299.147 | first_order (no) | - |
| HSD | cl | r9665 | 1165 | 299.149 | first_order (no) | - |
| MT | sv | b0 | 4518 | 0 | - | - |
| MT | sv | r90 | 1165 | 299.149 | first_order (no) | - |
| MT | sv | r9661 | 1165 | 299.149 | first_order (no) | - |
| MT | sv | r9662 | 1165 | 299.149 | first_order (no) | - |
| MT | sv | r9663 | 1165 | 299.149 | first_order (no) | - |
| MT | sv | r9664 | 1165 | 299.147 | first_order (no) | - |
| MT | sv | r9665 | 1165 | 299.149 | first_order (no) | - |

Events: 152. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
