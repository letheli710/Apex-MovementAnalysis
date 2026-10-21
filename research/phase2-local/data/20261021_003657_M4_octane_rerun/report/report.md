# hsd_tel report

Inputs: 16 file(s); rows: 53051 (MT 35362, HSD 17687)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3669 teleport in stream ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` message.log:4689 teleport in stream ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` message.log:5711 teleport in stream ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` message.log:6544 teleport in stream ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` message.log:7385 teleport in stream ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` script.log:3285 teleport in stream ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` script.log:4307 teleport in stream ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` script.log:5330 teleport in stream ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` script.log:6175 teleport in stream ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` script.log:7023 teleport in stream ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_MORE` script.log:0 11 more teleport rows in ('HSD', 'cl', 'frame', None, '73e8ad53-450a-47de-b027-b209e065d8d6')
- warning `W_TELEPORT` message.log:3435 teleport in stream ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_TELEPORT` message.log:4449 teleport in stream ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_TELEPORT` message.log:5457 teleport in stream ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_TELEPORT` message.log:6283 teleport in stream ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_TELEPORT` message.log:7111 teleport in stream ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, '916dd91f-09be-4f59-ac5b-e279babc13f4')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.85 -> 23.45738 in ('HSD', 'sv', 'evt', 1.0, '916dd91f-09be-4f59-ac5b-e279babc13f4')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5932 | 0 | - | - |
| MT | cl | r90 | 817 | 258.991 | first_order (yes) | linear (yes) |
| MT | cl | r1551 | 817 | 258.991 | first_order (yes) | linear (yes) |
| MT | cl | r1552 | 641 | 420.974 | first_order (no) | friction (no) |
| MT | cl | r1553 | 640 | 320.903 | first_order (no) | friction (no) |
| MT | cl | r1554 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1555 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1556 | 640 | 299.028 | first_order (no) | friction (no) |
| MT | cl | r1557 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | cl | r1558 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | cl | r1559 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | cl | r1560 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | cl | r1561 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | cl | r1562 | 780 | 515.721 | first_order (no) | linear (no) |
| MT | cl | r1563 | 757 | 299 | first_order (no) | linear (yes) |
| MT | cl | r1564 | 757 | 299 | first_order (no) | linear (yes) |
| MT | cl | r1565 | 757 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 5908 | 0 | - | - |
| HSD | cl | r90 | 817 | 258.991 | first_order (yes) | linear (yes) |
| HSD | cl | r1551 | 817 | 258.991 | first_order (yes) | linear (yes) |
| HSD | cl | r1552 | 641 | 420.974 | first_order (no) | friction (no) |
| HSD | cl | r1553 | 640 | 320.903 | first_order (no) | friction (no) |
| HSD | cl | r1554 | 640 | 299.03 | first_order (no) | friction (no) |
| HSD | cl | r1555 | 640 | 299.03 | first_order (no) | friction (no) |
| HSD | cl | r1556 | 640 | 299.028 | first_order (no) | friction (no) |
| HSD | cl | r1557 | 640 | 299.03 | first_order (no) | friction (no) |
| HSD | cl | r1558 | 780 | 515.72 | first_order (yes) | linear (no) |
| HSD | cl | r1559 | 780 | 515.72 | first_order (yes) | linear (no) |
| HSD | cl | r1560 | 780 | 515.72 | first_order (yes) | linear (no) |
| HSD | cl | r1561 | 780 | 515.72 | first_order (yes) | linear (no) |
| HSD | cl | r1562 | 780 | 515.721 | first_order (yes) | linear (no) |
| HSD | cl | r1563 | 757 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r1564 | 757 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r1565 | 757 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 5945 | 0 | - | - |
| MT | sv | r90 | 817 | 258.991 | first_order (yes) | linear (yes) |
| MT | sv | r1551 | 817 | 258.991 | first_order (yes) | linear (yes) |
| MT | sv | r1552 | 641 | 420.974 | first_order (no) | friction (no) |
| MT | sv | r1553 | 640 | 320.903 | first_order (no) | friction (no) |
| MT | sv | r1554 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1555 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1556 | 640 | 299.028 | first_order (no) | friction (no) |
| MT | sv | r1557 | 640 | 299.03 | first_order (no) | friction (no) |
| MT | sv | r1558 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | sv | r1559 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | sv | r1560 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | sv | r1561 | 780 | 515.72 | first_order (no) | linear (no) |
| MT | sv | r1562 | 780 | 515.721 | first_order (no) | linear (no) |
| MT | sv | r1563 | 757 | 299 | first_order (no) | linear (yes) |
| MT | sv | r1564 | 757 | 299 | first_order (no) | linear (yes) |
| MT | sv | r1565 | 757 | 299 | first_order (no) | linear (yes) |

Events: 141. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
