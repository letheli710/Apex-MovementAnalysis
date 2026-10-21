# hsd_tel report

Inputs: 16 file(s); rows: 44993 (MT 29969, HSD 14964)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:4487 teleport in stream ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` message.log:5429 teleport in stream ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` message.log:6378 teleport in stream ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` message.log:7330 teleport in stream ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` message.log:8285 teleport in stream ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_MORE` message.log:0 7 more teleport rows in ('MT', 'cl', 'cmd', 1, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` script.log:4100 teleport in stream ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` script.log:5024 teleport in stream ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` script.log:5953 teleport in stream ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` script.log:6888 teleport in stream ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` script.log:7823 teleport in stream ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_MORE` script.log:0 7 more teleport rows in ('HSD', 'cl', 'frame', None, '98b750db-57ff-4056-a281-1490fa72fa54')
- warning `W_TELEPORT` message.log:4203 teleport in stream ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_TELEPORT` message.log:5123 teleport in stream ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_TELEPORT` message.log:6040 teleport in stream ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_TELEPORT` message.log:6963 teleport in stream ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_TELEPORT` message.log:7887 teleport in stream ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_MORE` message.log:0 7 more teleport rows in ('MT', 'sv', 'cmd', 1, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')
- warning `W_TIME_BACKWARDS` script.log:713 t 30.35 -> 30.01501 in ('HSD', 'sv', 'evt', 1.0, '2bef3f6a-7f4a-4829-8ae8-ce19fc87ee63')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5884 | 0 | - | - |
| MT | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2601 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2602 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2603 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2604 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2605 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2606 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r2607 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2608 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2609 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2610 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r2611 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 5859 | 0 | - | - |
| HSD | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2601 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2602 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2603 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2604 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2605 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2606 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r2607 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2608 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2609 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2610 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r2611 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 5911 | 0 | - | - |
| MT | sv | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2601 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2602 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2603 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2604 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2605 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2606 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r2607 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2608 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2609 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2610 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r2611 | 744 | 299 | first_order (no) | linear (yes) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
