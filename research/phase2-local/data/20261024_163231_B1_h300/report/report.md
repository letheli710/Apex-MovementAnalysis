# hsd_tel report

Inputs: 17 file(s); rows: 66504 (MT 41914, HSD 24588)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3667 teleport in stream ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` message.log:6777 teleport in stream ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` message.log:10073 teleport in stream ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` message.log:13436 teleport in stream ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` message.log:16884 teleport in stream ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` script.1.log:3309 teleport in stream ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` script.1.log:6910 teleport in stream ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` script.1.log:10514 teleport in stream ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` script.1.log:14119 teleport in stream ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` script.1.log:19054 teleport in stream ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_MORE` script.1.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, 'ea325ac5-3db1-480a-9916-6ef3f0a2d3e2')
- warning `W_TELEPORT` message.log:3447 teleport in stream ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_TELEPORT` message.log:5330 teleport in stream ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_TELEPORT` message.log:7214 teleport in stream ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_TELEPORT` message.log:9099 teleport in stream ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_TELEPORT` message.log:11014 teleport in stream ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '7347e241-7f9d-45b2-91b1-68af3eece195')
- warning `W_TIME_BACKWARDS` script.log:719 t 25.7 -> 25.41334 in ('HSD', 'sv', 'evt', 1.0, '7347e241-7f9d-45b2-91b1-68af3eece195')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4328 | 0 | - | - |
| MT | cl | r90 | 1705 | 299.149 | first_order (no) | - |
| MT | cl | r9700 | 1705 | 299.15 | first_order (no) | - |
| MT | cl | r9701 | 1705 | 299.15 | first_order (no) | - |
| MT | cl | r9702 | 1717 | 299.15 | first_order (no) | - |
| MT | cl | r9703 | 1717 | 299.15 | first_order (no) | - |
| MT | cl | r9704 | 1705 | 299.149 | first_order (no) | - |
| MT | cl | r9705 | 1759 | 199.764 | first_order (yes) | - |
| HSD | cl | r0 | 4310 | 0 | - | - |
| HSD | cl | r90 | 1705 | 299.149 | first_order (no) | - |
| HSD | cl | r9700 | 1705 | 299.15 | first_order (no) | - |
| HSD | cl | r9701 | 1705 | 299.15 | first_order (no) | - |
| HSD | cl | r9702 | 1717 | 299.15 | first_order (no) | - |
| HSD | cl | r9703 | 1717 | 299.15 | first_order (no) | - |
| HSD | cl | r9704 | 1705 | 299.149 | first_order (no) | - |
| HSD | cl | r9705 | 1759 | 199.764 | first_order (yes) | - |
| MT | sv | b0 | 4333 | 0 | - | - |
| MT | sv | r90 | 1705 | 299.149 | first_order (no) | - |
| MT | sv | r9700 | 1705 | 299.15 | first_order (no) | - |
| MT | sv | r9701 | 1705 | 299.15 | first_order (no) | - |
| MT | sv | r9702 | 1717 | 299.15 | first_order (no) | - |
| MT | sv | r9703 | 1717 | 299.15 | first_order (no) | - |
| MT | sv | r9704 | 1705 | 299.149 | first_order (no) | - |
| MT | sv | r9705 | 1759 | 199.764 | first_order (yes) | - |

Events: 16379. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
