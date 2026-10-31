# hsd_tel report

Inputs: 17 file(s); rows: 72493 (MT 45987, HSD 26504)

Validation: 0 error(s), 22 warning(s), 6 info

- warning `W_TELEPORT` message.log:3674 teleport in stream ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` message.log:4633 teleport in stream ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` message.log:5605 teleport in stream ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` message.log:6566 teleport in stream ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` message.log:7531 teleport in stream ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'cl', 'cmd', 1, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.1.log:3333 teleport in stream ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.1.log:4755 teleport in stream ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.1.log:6173 teleport in stream ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.1.log:7581 teleport in stream ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.1.log:9006 teleport in stream ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_MORE` script.1.log:0 20 more teleport rows in ('HSD', 'cl', 'frame', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.log:3668 teleport in stream ('HSD', 'cl', 'edge', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` script.log:3827 teleport in stream ('HSD', 'cl', 'edge', None, 'e70daa0c-8703-4335-914d-1d8016ef87d1')
- warning `W_TELEPORT` message.log:3479 teleport in stream ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TELEPORT` message.log:4269 teleport in stream ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TELEPORT` message.log:5059 teleport in stream ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TELEPORT` message.log:5849 teleport in stream ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TELEPORT` message.log:6639 teleport in stream ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TELEPORT` script.log:3534 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')
- warning `W_TIME_BACKWARDS` script.log:717 t 22.05 -> 21.92776 in ('HSD', 'sv', 'evt', 1.0, 'b86c5482-ce48-4d88-ae40-8146dc5b65ea')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3997 | 0 | - | - |
| MT | cl | r90 | 613 | 299.154 | first_order (no) | - |
| MT | cl | r39000 | 613 | 299.155 | first_order (no) | - |
| MT | cl | r39001 | 601 | 297.21 | first_order (no) | - |
| MT | cl | r39002 | 611 | 299.157 | first_order (no) | - |
| MT | cl | r39003 | 589 | 289.825 | first_order (no) | - |
| MT | cl | r39004 | 532 | 299.043 | first_order (no) | - |
| MT | cl | b1 | 188 | 0 | - | - |
| MT | cl | r39005 | 521 | 299 | first_order (no) | linear (no) |
| MT | cl | b2 | 171 | 0 | - | - |
| MT | cl | r39006 | 555 | 299.486 | first_order (no) | friction (no) |
| MT | cl | b3 | 877 | 0 | - | - |
| MT | cl | r39007 | 613 | 299.154 | first_order (no) | - |
| MT | cl | r39008 | 601 | 297.824 | first_order (no) | - |
| MT | cl | r39009 | 611 | 299.157 | first_order (no) | - |
| MT | cl | r39010 | 589 | 289.967 | first_order (no) | - |
| MT | cl | r39011 | 530 | 299.047 | first_order (no) | - |
| MT | cl | b4 | 189 | 0 | - | - |
| MT | cl | r39012 | 520 | 299 | first_order (no) | linear (yes) |
| MT | cl | b5 | 171 | 0 | - | - |
| MT | cl | r39013 | 557 | 299.497 | first_order (no) | friction (no) |
| MT | cl | b6 | 877 | 0 | - | - |
| MT | cl | r39014 | 613 | 299.154 | first_order (no) | - |
| MT | cl | r39015 | 601 | 299.158 | first_order (no) | - |
| MT | cl | r39016 | 611 | 299.157 | first_order (no) | - |
| MT | cl | r39017 | 589 | 285.928 | first_order (no) | - |
| MT | cl | r39018 | 530 | 299.156 | first_order (no) | - |
| MT | cl | b7 | 189 | 0 | - | - |
| MT | cl | r39019 | 522 | 299 | first_order (no) | friction (yes) |
| MT | cl | b8 | 850 | 0 | - | - |
| MT | cl | r39020 | 613 | 299.155 | first_order (no) | - |
| MT | cl | r39021 | 601 | 296.518 | first_order (no) | - |
| MT | cl | r39022 | 611 | 299.156 | first_order (no) | - |
| MT | cl | r39023 | 589 | 290.554 | first_order (no) | - |
| HSD | cl | r0 | 7484 | 0 | - | - |
| HSD | cl | r90 | 613 | 299.154 | first_order (no) | - |
| HSD | cl | r39000 | 613 | 299.155 | first_order (no) | - |
| HSD | cl | r39001 | 601 | 297.21 | first_order (no) | - |
| HSD | cl | r39002 | 611 | 299.157 | first_order (no) | - |
| HSD | cl | r39003 | 589 | 289.825 | first_order (no) | - |
| HSD | cl | r39004 | 601 | 299.043 | first_order (no) | - |
| HSD | cl | r39005 | 589 | 299 | first_order (no) | linear (no) |
| HSD | cl | r39006 | 625 | 299.486 | first_order (no) | - |
| HSD | cl | r39007 | 613 | 299.154 | first_order (no) | - |
| HSD | cl | r39008 | 601 | 297.824 | first_order (no) | - |
| HSD | cl | r39009 | 611 | 299.157 | first_order (no) | - |
| HSD | cl | r39010 | 589 | 289.967 | first_order (no) | - |
| HSD | cl | r39011 | 601 | 299.047 | first_order (no) | - |
| HSD | cl | r39012 | 589 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r39013 | 625 | 299.497 | first_order (no) | - |
| HSD | cl | r39014 | 613 | 299.154 | first_order (no) | - |
| HSD | cl | r39015 | 601 | 299.158 | first_order (no) | - |
| HSD | cl | r39016 | 611 | 299.157 | first_order (no) | - |
| HSD | cl | r39017 | 589 | 285.928 | first_order (no) | - |
| HSD | cl | r39018 | 601 | 299.156 | first_order (no) | - |
| HSD | cl | r39019 | 589 | 299 | first_order (no) | friction (yes) |
| HSD | cl | r39020 | 613 | 299.155 | first_order (no) | - |
| HSD | cl | r39021 | 601 | 296.518 | first_order (no) | - |
| HSD | cl | r39022 | 611 | 299.156 | first_order (no) | - |
| HSD | cl | r39023 | 589 | 290.554 | first_order (no) | - |
| MT | sv | b0 | 4008 | 0 | - | - |
| MT | sv | r90 | 613 | 299.154 | first_order (no) | - |
| MT | sv | r39000 | 613 | 299.155 | first_order (no) | - |
| MT | sv | r39001 | 601 | 297.21 | first_order (no) | - |
| MT | sv | r39002 | 611 | 299.157 | first_order (no) | - |
| MT | sv | r39003 | 589 | 289.825 | first_order (no) | - |
| MT | sv | r39004 | 532 | 299.043 | first_order (no) | - |
| MT | sv | b1 | 188 | 0 | - | - |
| MT | sv | r39005 | 521 | 299 | first_order (no) | linear (no) |
| MT | sv | b2 | 171 | 0 | - | - |
| MT | sv | r39006 | 555 | 299.486 | first_order (no) | friction (no) |
| MT | sv | b3 | 877 | 0 | - | - |
| MT | sv | r39007 | 613 | 299.154 | first_order (no) | - |
| MT | sv | r39008 | 601 | 297.824 | first_order (no) | - |
| MT | sv | r39009 | 611 | 299.157 | first_order (no) | - |
| MT | sv | r39010 | 589 | 289.967 | first_order (no) | - |
| MT | sv | r39011 | 530 | 299.047 | first_order (no) | - |
| MT | sv | b4 | 189 | 0 | - | - |
| MT | sv | r39012 | 520 | 299 | first_order (no) | linear (yes) |
| MT | sv | b5 | 171 | 0 | - | - |
| MT | sv | r39013 | 557 | 299.497 | first_order (no) | friction (no) |
| MT | sv | b6 | 877 | 0 | - | - |
| MT | sv | r39014 | 613 | 299.154 | first_order (no) | - |
| MT | sv | r39015 | 601 | 299.158 | first_order (no) | - |
| MT | sv | r39016 | 611 | 299.157 | first_order (no) | - |
| MT | sv | r39017 | 589 | 285.928 | first_order (no) | - |
| MT | sv | r39018 | 532 | 299.156 | first_order (no) | - |
| MT | sv | b7 | 189 | 0 | - | - |
| MT | sv | r39019 | 522 | 299 | first_order (no) | friction (yes) |
| MT | sv | b8 | 850 | 0 | - | - |
| MT | sv | r39020 | 613 | 299.155 | first_order (no) | - |
| MT | sv | r39021 | 601 | 296.518 | first_order (no) | - |
| MT | sv | r39022 | 611 | 299.156 | first_order (no) | - |
| MT | sv | r39023 | 589 | 290.554 | first_order (no) | - |

Events: 7635. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
