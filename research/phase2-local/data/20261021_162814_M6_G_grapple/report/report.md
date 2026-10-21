# hsd_tel report

Inputs: 16 file(s); rows: 58154 (MT 38368, HSD 19784)

Validation: 0 error(s), 27 warning(s), 6 info

- warning `W_TELEPORT` message.log:4049 teleport in stream ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` message.log:4725 teleport in stream ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` message.log:5395 teleport in stream ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` message.log:6079 teleport in stream ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` message.log:6757 teleport in stream ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'cl', 'cmd', 1, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:3685 teleport in stream ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:4747 teleport in stream ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:5808 teleport in stream ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:6872 teleport in stream ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:7934 teleport in stream ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_MORE` script.log:0 21 more teleport rows in ('HSD', 'cl', 'frame', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:10807 teleport in stream ('HSD', 'cl', 'edge', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` script.log:11877 teleport in stream ('HSD', 'cl', 'edge', None, '6314cc81-e4c5-4e43-b648-7dc2f90ed650')
- warning `W_TELEPORT` message.log:3833 teleport in stream ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` message.log:4451 teleport in stream ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` message.log:5069 teleport in stream ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` message.log:5687 teleport in stream ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` message.log:6304 teleport in stream ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'sv', 'cmd', 1, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` script.log:771 teleport in stream ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` script.log:822 teleport in stream ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` script.log:831 teleport in stream ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` script.log:840 teleport in stream ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TELEPORT` script.log:849 teleport in stream ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.3 -> 23.17043 in ('HSD', 'sv', 'evt', 1.0, '836a87d3-f266-447c-bfa0-b9f79b774547')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6343 | 0 | - | - |
| MT | cl | r90 | 434 | 144.046 | - | linear (yes) |
| MT | cl | r3801 | 434 | 145.532 | - | linear (yes) |
| MT | cl | r3802 | 434 | 147.547 | - | linear (yes) |
| MT | cl | r3803 | 434 | 147.77 | - | linear (yes) |
| MT | cl | r3804 | 434 | 147.549 | - | linear (yes) |
| MT | cl | r3805 | 434 | 147.797 | - | linear (yes) |
| MT | cl | r3806 | 434 | 573.615 | linear (yes) | - |
| MT | cl | r3807 | 434 | 573.371 | linear (yes) | - |
| MT | cl | r3808 | 434 | 574.676 | linear (yes) | - |
| MT | cl | r3809 | 434 | 574.448 | linear (yes) | - |
| MT | cl | r3810 | 434 | 574.085 | linear (yes) | - |
| MT | cl | r3811 | 421 | 573.57 | linear (yes) | - |
| MT | cl | r3812 | 421 | 574.474 | linear (yes) | - |
| MT | cl | r3813 | 421 | 575.123 | linear (yes) | - |
| MT | cl | r3814 | 421 | 574.68 | linear (yes) | - |
| MT | cl | r3815 | 421 | 574.47 | linear (yes) | - |
| MT | cl | r3816 | 226 | 600 | - | - |
| MT | cl | b1 | 167 | 318.604 | - | - |
| MT | cl | r3817 | 226 | 600 | - | - |
| MT | cl | b2 | 167 | 318.639 | - | - |
| MT | cl | r3818 | 225 | 600 | - | - |
| MT | cl | b3 | 167 | 339.309 | - | - |
| MT | cl | r3819 | 227 | 600 | - | - |
| MT | cl | b4 | 167 | 309.591 | - | - |
| MT | cl | r3820 | 226 | 600 | - | - |
| MT | cl | b5 | 196 | 329.389 | - | - |
| MT | cl | r3821 | 287 | 600 | - | linear (yes) |
| MT | cl | b6 | 195 | 0 | - | - |
| MT | cl | r3822 | 287 | 600 | - | linear (yes) |
| MT | cl | b7 | 195 | 0 | - | - |
| MT | cl | r3823 | 287 | 600 | - | linear (yes) |
| MT | cl | b8 | 196 | 0 | - | - |
| MT | cl | r3824 | 287 | 600 | - | linear (yes) |
| MT | cl | b9 | 166 | 0 | - | - |
| MT | cl | r3825 | 287 | 600 | - | linear (yes) |
| MT | cl | b10 | 156 | 0 | - | - |
| HSD | cl | r0 | 8088 | 350.477 | - | linear (yes) |
| HSD | cl | r90 | 434 | 144.046 | - | linear (yes) |
| HSD | cl | r3801 | 434 | 145.532 | - | linear (yes) |
| HSD | cl | r3802 | 434 | 147.547 | - | linear (yes) |
| HSD | cl | r3803 | 434 | 147.77 | - | linear (yes) |
| HSD | cl | r3804 | 434 | 147.549 | - | linear (yes) |
| HSD | cl | r3805 | 434 | 147.797 | - | linear (yes) |
| HSD | cl | r3806 | 434 | 573.615 | linear (yes) | - |
| HSD | cl | r3807 | 434 | 573.371 | linear (yes) | - |
| HSD | cl | r3808 | 434 | 574.676 | linear (yes) | - |
| HSD | cl | r3809 | 434 | 574.448 | linear (yes) | - |
| HSD | cl | r3810 | 434 | 574.085 | linear (yes) | - |
| HSD | cl | r3811 | 421 | 573.57 | linear (yes) | - |
| HSD | cl | r3812 | 421 | 574.474 | linear (yes) | - |
| HSD | cl | r3813 | 421 | 575.123 | linear (yes) | - |
| HSD | cl | r3814 | 421 | 574.68 | linear (yes) | - |
| HSD | cl | r3815 | 421 | 574.47 | linear (yes) | - |
| HSD | cl | r3816 | 421 | 600 | - | - |
| HSD | cl | r3817 | 421 | 600 | - | - |
| HSD | cl | r3818 | 421 | 600 | - | - |
| HSD | cl | r3819 | 421 | 600 | - | - |
| HSD | cl | r3820 | 421 | 600 | - | - |
| HSD | cl | r3821 | 482 | 600 | - | linear (yes) |
| HSD | cl | r3822 | 482 | 600 | - | linear (yes) |
| HSD | cl | r3823 | 482 | 600 | - | linear (yes) |
| HSD | cl | r3824 | 482 | 600 | - | linear (yes) |
| HSD | cl | r3825 | 482 | 600 | - | linear (yes) |
| MT | sv | b0 | 6355 | 0 | - | - |
| MT | sv | r90 | 434 | 144.046 | - | linear (yes) |
| MT | sv | r3801 | 434 | 145.532 | - | linear (yes) |
| MT | sv | r3802 | 434 | 147.547 | - | linear (yes) |
| MT | sv | r3803 | 434 | 147.77 | - | linear (yes) |
| MT | sv | r3804 | 434 | 147.549 | - | linear (yes) |
| MT | sv | r3805 | 434 | 147.797 | - | linear (yes) |
| MT | sv | r3806 | 434 | 573.613 | linear (yes) | - |
| MT | sv | r3807 | 434 | 573.357 | linear (yes) | - |
| MT | sv | r3808 | 434 | 574.667 | linear (yes) | - |
| MT | sv | r3809 | 434 | 574.443 | linear (yes) | - |
| MT | sv | r3810 | 434 | 574.065 | linear (yes) | - |
| MT | sv | r3811 | 421 | 573.556 | linear (yes) | - |
| MT | sv | r3812 | 421 | 574.457 | linear (yes) | - |
| MT | sv | r3813 | 421 | 575.117 | linear (yes) | - |
| MT | sv | r3814 | 421 | 574.659 | linear (yes) | - |
| MT | sv | r3815 | 421 | 574.454 | linear (yes) | - |
| MT | sv | r3816 | 226 | 600 | - | - |
| MT | sv | b1 | 167 | 318.604 | - | - |
| MT | sv | r3817 | 226 | 600 | - | - |
| MT | sv | b2 | 167 | 318.639 | - | - |
| MT | sv | r3818 | 225 | 600 | - | - |
| MT | sv | b3 | 167 | 339.309 | - | - |
| MT | sv | r3819 | 227 | 600 | - | - |
| MT | sv | b4 | 167 | 309.591 | - | - |
| MT | sv | r3820 | 226 | 600 | - | - |
| MT | sv | b5 | 196 | 329.389 | - | - |
| MT | sv | r3821 | 287 | 600 | - | linear (yes) |
| MT | sv | b6 | 195 | 0 | - | - |
| MT | sv | r3822 | 287 | 600 | - | linear (yes) |
| MT | sv | b7 | 195 | 0 | - | - |
| MT | sv | r3823 | 287 | 600 | - | linear (yes) |
| MT | sv | b8 | 196 | 0 | - | - |
| MT | sv | r3824 | 287 | 600 | - | linear (yes) |
| MT | sv | b9 | 166 | 0 | - | - |
| MT | sv | r3825 | 287 | 600 | - | linear (yes) |
| MT | sv | b10 | 147 | 0 | - | - |

Events: 318. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
