# hsd_tel report

Inputs: 16 file(s); rows: 42854 (MT 28565, HSD 14287)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3691 teleport in stream ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` message.log:5498 teleport in stream ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` message.log:7308 teleport in stream ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` message.log:9225 teleport in stream ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` message.log:11145 teleport in stream ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` script.log:3332 teleport in stream ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` script.log:6742 teleport in stream ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` script.log:10156 teleport in stream ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` script.log:13813 teleport in stream ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` script.log:17475 teleport in stream ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '67aaa346-4e9a-4bfa-887d-9e20343cb8de')
- warning `W_TELEPORT` message.log:3481 teleport in stream ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_TELEPORT` message.log:7848 teleport in stream ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_TELEPORT` message.log:12089 teleport in stream ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_TELEPORT` message.log:17087 teleport in stream ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_TELEPORT` message.log:21124 teleport in stream ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.0 -> 22.80939 in ('HSD', 'sv', 'evt', 1.0, '766f9082-fbcb-4e29-b9d8-7fea0866a4a8')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4170 | 0 | - | - |
| MT | cl | r90 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| MT | cl | r8861 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| MT | cl | r8862 | 1730 | 173.846 | first_order (yes) | linear (yes) |
| MT | cl | r8863 | 1723 | 173.856 | first_order (yes) | linear (yes) |
| MT | cl | r8864 | 1706 | 173.858 | first_order (yes) | linear (yes) |
| MT | cl | r8865 | 1706 | 173.853 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 4141 | 0 | - | - |
| HSD | cl | r90 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| HSD | cl | r8861 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| HSD | cl | r8862 | 1730 | 173.846 | first_order (yes) | linear (yes) |
| HSD | cl | r8863 | 1730 | 173.856 | first_order (yes) | linear (yes) |
| HSD | cl | r8864 | 1706 | 173.858 | first_order (yes) | linear (yes) |
| HSD | cl | r8865 | 1706 | 173.853 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 4179 | 0 | - | - |
| MT | sv | r90 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| MT | sv | r8861 | 1599 | 199.904 | first_order (yes) | linear (yes) |
| MT | sv | r8862 | 1730 | 173.846 | first_order (yes) | linear (yes) |
| MT | sv | r8863 | 1723 | 173.856 | first_order (yes) | linear (yes) |
| MT | sv | r8864 | 1706 | 173.858 | first_order (yes) | linear (yes) |
| MT | sv | r8865 | 1706 | 173.853 | first_order (yes) | linear (yes) |

Events: 98. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
