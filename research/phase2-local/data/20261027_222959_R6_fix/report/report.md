# hsd_tel report

Inputs: 16 file(s); rows: 38671 (MT 25795, HSD 12874)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3993 teleport in stream ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` message.log:4945 teleport in stream ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` message.log:5897 teleport in stream ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` message.log:6849 teleport in stream ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` message.log:7806 teleport in stream ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'cl', 'cmd', 1, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` script.log:3647 teleport in stream ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` script.log:5384 teleport in stream ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` script.log:7122 teleport in stream ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` script.log:8860 teleport in stream ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` script.log:10599 teleport in stream ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_MORE` script.log:0 5 more teleport rows in ('HSD', 'cl', 'frame', None, '7b99275f-15c3-421c-8397-8ad679d0f586')
- warning `W_TELEPORT` message.log:3783 teleport in stream ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_TELEPORT` message.log:4730 teleport in stream ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_TELEPORT` message.log:5678 teleport in stream ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_TELEPORT` message.log:6626 teleport in stream ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_TELEPORT` message.log:7573 teleport in stream ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, '0c302099-89a2-44ba-be0f-42a14436cbad')
- warning `W_TIME_BACKWARDS` script.log:716 t 23.35 -> 23.23128 in ('HSD', 'sv', 'evt', 1.0, '0c302099-89a2-44ba-be0f-42a14436cbad')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5047 | 0 | - | - |
| MT | cl | r90 | 780 | 457.806 | first_order (no) | linear (no) |
| MT | cl | r741 | 780 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r742 | 780 | 457.811 | first_order (no) | linear (no) |
| MT | cl | r743 | 781 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r744 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r745 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r746 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r747 | 780 | 460.791 | first_order (no) | linear (yes) |
| MT | cl | r748 | 781 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r749 | 779 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r0 | 5030 | 0 | - | - |
| HSD | cl | r90 | 780 | 457.806 | first_order (no) | linear (no) |
| HSD | cl | r741 | 780 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r742 | 780 | 457.811 | first_order (no) | linear (no) |
| HSD | cl | r743 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r744 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r745 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r746 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r747 | 780 | 460.791 | first_order (no) | linear (yes) |
| HSD | cl | r748 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r749 | 780 | 457.803 | first_order (no) | linear (no) |
| MT | sv | b0 | 5047 | 0 | - | - |
| MT | sv | r90 | 780 | 457.806 | first_order (no) | linear (no) |
| MT | sv | r741 | 780 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r742 | 780 | 457.811 | first_order (no) | linear (no) |
| MT | sv | r743 | 781 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r744 | 780 | 460.782 | first_order (no) | linear (yes) |
| MT | sv | r745 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | sv | r746 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | sv | r747 | 780 | 460.791 | first_order (no) | linear (yes) |
| MT | sv | r748 | 781 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r749 | 779 | 457.803 | first_order (no) | linear (no) |

Events: 62. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
