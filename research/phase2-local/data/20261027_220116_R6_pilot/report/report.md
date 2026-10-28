# hsd_tel report

Inputs: 16 file(s); rows: 41492 (MT 27678, HSD 13812)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3940 teleport in stream ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` message.log:4898 teleport in stream ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` message.log:5851 teleport in stream ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` message.log:6836 teleport in stream ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` message.log:7823 teleport in stream ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'cl', 'cmd', 1, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` script.log:3567 teleport in stream ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` script.log:5310 teleport in stream ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` script.log:7048 teleport in stream ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` script.log:8846 teleport in stream ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` script.log:10638 teleport in stream ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'cl', 'frame', None, '8580a3ee-d031-46a1-965d-583a79001257')
- warning `W_TELEPORT` message.log:3695 teleport in stream ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_TELEPORT` message.log:4650 teleport in stream ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_TELEPORT` message.log:5597 teleport in stream ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_TELEPORT` message.log:6574 teleport in stream ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_TELEPORT` message.log:7551 teleport in stream ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'sv', 'cmd', 1, '368ec968-7a21-4f47-9a82-fdeb0e378910')
- warning `W_TIME_BACKWARDS` script.log:715 t 26.45 -> 26.20865 in ('HSD', 'sv', 'evt', 1.0, '368ec968-7a21-4f47-9a82-fdeb0e378910')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5230 | 0 | - | - |
| MT | cl | r90 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r601 | 780 | 457.806 | first_order (no) | linear (no) |
| MT | cl | r602 | 809 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r603 | 799 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r604 | 780 | 461.004 | first_order (no) | linear (yes) |
| MT | cl | r605 | 900 | 458.995 | first_order (no) | linear (no) |
| MT | cl | r606 | 937 | 461.005 | first_order (no) | linear (yes) |
| MT | cl | r607 | 779 | 299 | first_order (no) | linear (yes) |
| MT | cl | r608 | 660 | 457.77 | first_order (no) | linear (no) |
| MT | cl | r609 | 660 | 459.224 | first_order (no) | linear (yes) |
| MT | cl | r610 | 660 | 456.378 | first_order (no) | linear (no) |
| HSD | cl | r0 | 5214 | 0 | - | - |
| HSD | cl | r90 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r601 | 780 | 457.806 | first_order (no) | linear (no) |
| HSD | cl | r602 | 810 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r603 | 799 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r604 | 780 | 461.004 | first_order (no) | linear (yes) |
| HSD | cl | r605 | 900 | 458.995 | first_order (no) | linear (no) |
| HSD | cl | r606 | 936 | 461.005 | first_order (no) | linear (yes) |
| HSD | cl | r607 | 780 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r608 | 660 | 457.77 | first_order (no) | linear (no) |
| HSD | cl | r609 | 660 | 459.224 | first_order (no) | linear (yes) |
| HSD | cl | r610 | 660 | 456.378 | first_order (no) | linear (no) |
| MT | sv | b0 | 5235 | 0 | - | - |
| MT | sv | r90 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r601 | 780 | 457.806 | first_order (no) | linear (no) |
| MT | sv | r602 | 809 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r603 | 799 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r604 | 780 | 461.004 | first_order (no) | linear (yes) |
| MT | sv | r605 | 900 | 458.995 | first_order (no) | linear (no) |
| MT | sv | r606 | 937 | 461.005 | first_order (no) | linear (yes) |
| MT | sv | r607 | 779 | 299 | first_order (no) | linear (yes) |
| MT | sv | r608 | 660 | 457.77 | first_order (no) | linear (no) |
| MT | sv | r609 | 660 | 459.224 | first_order (no) | linear (yes) |
| MT | sv | r610 | 660 | 456.378 | first_order (no) | linear (no) |

Events: 79. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
