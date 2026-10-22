# hsd_tel report

Inputs: 16 file(s); rows: 33188 (MT 21884, HSD 11302)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3793 teleport in stream ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` message.log:5101 teleport in stream ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` message.log:6395 teleport in stream ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` message.log:7699 teleport in stream ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` message.log:9026 teleport in stream ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` script.log:3442 teleport in stream ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` script.log:5965 teleport in stream ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` script.log:8483 teleport in stream ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` script.log:11002 teleport in stream ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` script.log:13522 teleport in stream ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '68514cb2-4b2f-46a0-91a7-b99a87914bb8')
- warning `W_TELEPORT` message.log:3595 teleport in stream ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_TELEPORT` message.log:4873 teleport in stream ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_TELEPORT` message.log:6141 teleport in stream ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_TELEPORT` message.log:7409 teleport in stream ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_TELEPORT` message.log:8678 teleport in stream ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')
- warning `W_TIME_BACKWARDS` script.log:714 t 24.75 -> 24.43724 in ('HSD', 'sv', 'evt', 1.0, 'ecb918ff-2ddc-4255-a3df-60d5b69e2b4a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3219 | 0 | - | - |
| MT | cl | r90 | 1098 | 299.871 | first_order (no) | friction (no) |
| MT | cl | b1 | 176 | 0 | - | - |
| MT | cl | r9631 | 1094 | 299.872 | first_order (no) | friction (no) |
| MT | cl | b2 | 171 | 0 | - | - |
| MT | cl | r9632 | 1095 | 299.872 | first_order (no) | friction (no) |
| MT | cl | b3 | 172 | 0 | - | - |
| MT | cl | r9633 | 1095 | 299.871 | first_order (no) | friction (no) |
| MT | cl | b4 | 173 | 0 | - | - |
| MT | cl | r9634 | 1096 | 299.864 | first_order (no) | friction (no) |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r9635 | 1094 | 299.871 | first_order (no) | friction (no) |
| MT | cl | b6 | 133 | 0 | - | - |
| HSD | cl | r0 | 4188 | 0 | - | - |
| HSD | cl | r90 | 1165 | 299.871 | first_order (no) | - |
| HSD | cl | r9631 | 1165 | 299.872 | first_order (no) | - |
| HSD | cl | r9632 | 1165 | 299.872 | first_order (no) | - |
| HSD | cl | r9633 | 1165 | 299.871 | first_order (no) | - |
| HSD | cl | r9634 | 1165 | 299.864 | first_order (no) | - |
| HSD | cl | r9635 | 1165 | 299.871 | first_order (no) | - |
| MT | sv | b0 | 3234 | 0 | - | - |
| MT | sv | r90 | 1098 | 299.871 | first_order (no) | friction (no) |
| MT | sv | b1 | 176 | 0 | - | - |
| MT | sv | r9631 | 1094 | 299.872 | first_order (no) | friction (no) |
| MT | sv | b2 | 171 | 0 | - | - |
| MT | sv | r9632 | 1094 | 299.872 | first_order (no) | friction (no) |
| MT | sv | b3 | 172 | 0 | - | - |
| MT | sv | r9633 | 1095 | 299.871 | first_order (no) | friction (no) |
| MT | sv | b4 | 173 | 0 | - | - |
| MT | sv | r9634 | 1096 | 299.864 | first_order (no) | friction (no) |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r9635 | 1094 | 299.871 | first_order (no) | friction (no) |
| MT | sv | b6 | 129 | 0 | - | - |

Events: 182. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
