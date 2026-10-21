# hsd_tel report

Inputs: 16 file(s); rows: 78247 (MT 52136, HSD 26051)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:2748 teleport in stream ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` message.log:3959 teleport in stream ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` message.log:5147 teleport in stream ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` message.log:6332 teleport in stream ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` message.log:7520 teleport in stream ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_MORE` message.log:0 16 more teleport rows in ('MT', 'cl', 'cmd', 1, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` script.log:2396 teleport in stream ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` script.log:3550 teleport in stream ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` script.log:4718 teleport in stream ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` script.log:5885 teleport in stream ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` script.log:7053 teleport in stream ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_MORE` script.log:0 16 more teleport rows in ('HSD', 'cl', 'frame', None, '256eb8be-dbeb-4bf3-af7f-fe46cfbb4e06')
- warning `W_TELEPORT` message.log:2474 teleport in stream ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_TELEPORT` message.log:3615 teleport in stream ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_TELEPORT` message.log:4773 teleport in stream ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_TELEPORT` message.log:5931 teleport in stream ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_TELEPORT` message.log:7089 teleport in stream ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_MORE` message.log:0 16 more teleport rows in ('MT', 'sv', 'cmd', 1, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.3 -> 24.06417 in ('HSD', 'sv', 'evt', 1.0, 'ea13fdd8-1413-499b-80e7-3cfaa8e06161')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6847 | 400 | - | linear (yes) |
| MT | cl | r90 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1601 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1602 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1603 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1604 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1605 | 972 | 400 | first_order (no) | linear (yes) |
| MT | cl | r1606 | 793 | 400 | first_order (yes) | - |
| MT | cl | r1607 | 793 | 400 | first_order (yes) | - |
| MT | cl | r1608 | 793 | 400 | first_order (yes) | - |
| MT | cl | r1609 | 793 | 400 | first_order (yes) | - |
| MT | cl | r1610 | 793 | 400 | first_order (yes) | - |
| MT | cl | r1611 | 972 | 400.283 | first_order (no) | linear (yes) |
| MT | cl | r1612 | 972 | 400.295 | first_order (no) | linear (yes) |
| MT | cl | r1613 | 972 | 400.285 | first_order (no) | linear (yes) |
| MT | cl | r1614 | 972 | 400.296 | first_order (no) | linear (yes) |
| MT | cl | r1615 | 972 | 400.285 | first_order (no) | linear (yes) |
| MT | cl | r1616 | 301 | 0 | - | - |
| MT | cl | r1617 | 301 | 0 | - | - |
| MT | cl | r1618 | 301 | 0 | - | - |
| MT | cl | r1619 | 301 | 0 | - | - |
| MT | cl | r1620 | 301 | 0 | - | - |
| MT | cl | r1621 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1622 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1623 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1624 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1625 | 544 | 299.031 | first_order (no) | friction (no) |
| HSD | cl | r0 | 6829 | 400 | - | linear (yes) |
| HSD | cl | r90 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1601 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1602 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1603 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1604 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1605 | 972 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r1606 | 793 | 400 | first_order (yes) | - |
| HSD | cl | r1607 | 793 | 400 | first_order (yes) | - |
| HSD | cl | r1608 | 793 | 400 | first_order (yes) | - |
| HSD | cl | r1609 | 793 | 400 | first_order (yes) | - |
| HSD | cl | r1610 | 793 | 400 | first_order (yes) | - |
| HSD | cl | r1611 | 972 | 400.283 | first_order (no) | linear (yes) |
| HSD | cl | r1612 | 972 | 400.295 | first_order (no) | linear (yes) |
| HSD | cl | r1613 | 972 | 400.285 | first_order (no) | linear (yes) |
| HSD | cl | r1614 | 972 | 400.296 | first_order (no) | linear (yes) |
| HSD | cl | r1615 | 972 | 400.285 | first_order (no) | linear (yes) |
| HSD | cl | r1616 | 301 | 0 | - | - |
| HSD | cl | r1617 | 301 | 0 | - | - |
| HSD | cl | r1618 | 301 | 0 | - | - |
| HSD | cl | r1619 | 301 | 0 | - | - |
| HSD | cl | r1620 | 301 | 0 | - | - |
| HSD | cl | r1621 | 544 | 299.03 | first_order (no) | linear (yes) |
| HSD | cl | r1622 | 544 | 299.03 | first_order (no) | linear (yes) |
| HSD | cl | r1623 | 544 | 299.03 | first_order (no) | linear (yes) |
| HSD | cl | r1624 | 544 | 299.03 | first_order (no) | linear (yes) |
| HSD | cl | r1625 | 544 | 299.031 | first_order (no) | linear (yes) |
| MT | sv | b0 | 6853 | 400 | - | linear (yes) |
| MT | sv | r90 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1601 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1602 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1603 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1604 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1605 | 972 | 400 | first_order (no) | linear (yes) |
| MT | sv | r1606 | 793 | 400 | first_order (yes) | - |
| MT | sv | r1607 | 793 | 400 | first_order (yes) | - |
| MT | sv | r1608 | 793 | 400 | first_order (yes) | - |
| MT | sv | r1609 | 793 | 400 | first_order (yes) | - |
| MT | sv | r1610 | 793 | 400 | first_order (yes) | - |
| MT | sv | r1611 | 972 | 400.283 | first_order (no) | linear (yes) |
| MT | sv | r1612 | 972 | 400.295 | first_order (no) | linear (yes) |
| MT | sv | r1613 | 972 | 400.285 | first_order (no) | linear (yes) |
| MT | sv | r1614 | 972 | 400.296 | first_order (no) | linear (yes) |
| MT | sv | r1615 | 972 | 400.285 | first_order (no) | linear (yes) |
| MT | sv | r1616 | 301 | 0 | - | - |
| MT | sv | r1617 | 301 | 0 | - | - |
| MT | sv | r1618 | 301 | 0 | - | - |
| MT | sv | r1619 | 301 | 0 | - | - |
| MT | sv | r1620 | 301 | 0 | - | - |
| MT | sv | r1621 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1622 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1623 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1624 | 544 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1625 | 544 | 299.031 | first_order (no) | friction (no) |

Events: 250. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
