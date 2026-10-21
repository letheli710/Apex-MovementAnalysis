# hsd_tel report

Inputs: 17 file(s); rows: 91139 (MT 60529, HSD 30608)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3822 teleport in stream ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` message.log:4811 teleport in stream ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` message.log:5790 teleport in stream ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` message.log:6782 teleport in stream ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` message.log:7766 teleport in stream ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` script.1.log:3474 teleport in stream ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` script.1.log:5282 teleport in stream ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` script.1.log:7078 teleport in stream ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` script.1.log:8880 teleport in stream ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` script.1.log:10678 teleport in stream ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_MORE` script.1.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, 'bf2c13d9-705a-4c88-b0dd-09d096fa8ace')
- warning `W_TELEPORT` message.log:3615 teleport in stream ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_TELEPORT` message.log:4600 teleport in stream ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_TELEPORT` message.log:5580 teleport in stream ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_TELEPORT` message.log:6556 teleport in stream ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_TELEPORT` message.log:7535 teleport in stream ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.85 -> 23.57463 in ('HSD', 'sv', 'evt', 1.0, '514284bb-7ae0-46dc-b3a2-c77c1e012d34')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 8763 | 0 | - | - |
| MT | cl | r90 | 805 | 299.146 | first_order (no) | - |
| MT | cl | r3421 | 805 | 299.149 | first_order (no) | - |
| MT | cl | r3422 | 805 | 299.148 | first_order (no) | - |
| MT | cl | r3423 | 805 | 299.148 | first_order (no) | - |
| MT | cl | r3424 | 805 | 299.147 | first_order (no) | - |
| MT | cl | r3425 | 805 | 299.149 | first_order (no) | - |
| MT | cl | r3426 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | cl | r3427 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | cl | r3428 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | cl | r3429 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | cl | r3430 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | cl | r3431 | 553 | 299.147 | first_order (no) | - |
| MT | cl | r3432 | 553 | 299.147 | first_order (no) | - |
| MT | cl | r3433 | 553 | 299.149 | first_order (no) | - |
| MT | cl | r3434 | 553 | 299.148 | first_order (no) | - |
| MT | cl | r3435 | 553 | 299.147 | first_order (no) | - |
| MT | cl | r3436 | 673 | 299.147 | first_order (no) | - |
| MT | cl | r3437 | 673 | 299.146 | first_order (no) | - |
| MT | cl | r3438 | 673 | 299.149 | first_order (no) | - |
| MT | cl | r3439 | 673 | 299.149 | first_order (no) | - |
| MT | cl | r3440 | 673 | 299.146 | first_order (no) | - |
| MT | cl | r3441 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3442 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3443 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3444 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3445 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3446 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3447 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3448 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3449 | 734 | 299.147 | first_order (no) | - |
| MT | cl | r3450 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r0 | 8744 | 0 | - | - |
| HSD | cl | r90 | 805 | 299.146 | first_order (no) | - |
| HSD | cl | r3421 | 805 | 299.149 | first_order (no) | - |
| HSD | cl | r3422 | 805 | 299.148 | first_order (no) | - |
| HSD | cl | r3423 | 805 | 299.148 | first_order (no) | - |
| HSD | cl | r3424 | 805 | 299.147 | first_order (no) | - |
| HSD | cl | r3425 | 805 | 299.149 | first_order (no) | - |
| HSD | cl | r3426 | 600 | 199.525 | first_order (yes) | linear (no) |
| HSD | cl | r3427 | 600 | 199.525 | first_order (yes) | linear (no) |
| HSD | cl | r3428 | 600 | 199.525 | first_order (yes) | linear (no) |
| HSD | cl | r3429 | 600 | 199.525 | first_order (yes) | linear (no) |
| HSD | cl | r3430 | 600 | 199.525 | first_order (yes) | linear (no) |
| HSD | cl | r3431 | 553 | 299.147 | first_order (no) | - |
| HSD | cl | r3432 | 553 | 299.147 | first_order (no) | - |
| HSD | cl | r3433 | 553 | 299.149 | first_order (no) | - |
| HSD | cl | r3434 | 553 | 299.148 | first_order (no) | - |
| HSD | cl | r3435 | 553 | 299.147 | first_order (no) | - |
| HSD | cl | r3436 | 673 | 299.147 | first_order (no) | - |
| HSD | cl | r3437 | 673 | 299.146 | first_order (no) | - |
| HSD | cl | r3438 | 673 | 299.149 | first_order (no) | - |
| HSD | cl | r3439 | 673 | 299.149 | first_order (no) | - |
| HSD | cl | r3440 | 673 | 299.146 | first_order (no) | - |
| HSD | cl | r3441 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3442 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3443 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3444 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3445 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3446 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3447 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3448 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3449 | 734 | 299.147 | first_order (no) | - |
| HSD | cl | r3450 | 734 | 299.147 | first_order (no) | - |
| MT | sv | b0 | 8772 | 0 | - | - |
| MT | sv | r90 | 805 | 299.146 | first_order (no) | - |
| MT | sv | r3421 | 805 | 299.149 | first_order (no) | - |
| MT | sv | r3422 | 805 | 299.148 | first_order (no) | - |
| MT | sv | r3423 | 805 | 299.148 | first_order (no) | - |
| MT | sv | r3424 | 805 | 299.147 | first_order (no) | - |
| MT | sv | r3425 | 805 | 299.149 | first_order (no) | - |
| MT | sv | r3426 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | sv | r3427 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | sv | r3428 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | sv | r3429 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | sv | r3430 | 600 | 199.525 | first_order (yes) | linear (no) |
| MT | sv | r3431 | 553 | 299.147 | first_order (no) | - |
| MT | sv | r3432 | 553 | 299.147 | first_order (no) | - |
| MT | sv | r3433 | 553 | 299.149 | first_order (no) | - |
| MT | sv | r3434 | 553 | 299.148 | first_order (no) | - |
| MT | sv | r3435 | 553 | 299.147 | first_order (no) | - |
| MT | sv | r3436 | 673 | 299.147 | first_order (no) | - |
| MT | sv | r3437 | 673 | 299.146 | first_order (no) | - |
| MT | sv | r3438 | 673 | 299.149 | first_order (no) | - |
| MT | sv | r3439 | 673 | 299.149 | first_order (no) | - |
| MT | sv | r3440 | 673 | 299.146 | first_order (no) | - |
| MT | sv | r3441 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3442 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3443 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3444 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3445 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3446 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3447 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3448 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3449 | 734 | 299.147 | first_order (no) | - |
| MT | sv | r3450 | 734 | 299.147 | first_order (no) | - |

Events: 842. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
