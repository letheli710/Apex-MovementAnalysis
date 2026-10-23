# hsd_tel report

Inputs: 19 file(s); rows: 127802 (MT 85096, HSD 42704)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.1.log:5673 teleport in stream ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` message.1.log:7119 teleport in stream ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` message.1.log:8565 teleport in stream ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` message.1.log:10017 teleport in stream ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` message.1.log:11484 teleport in stream ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_MORE` message.1.log:0 27 more teleport rows in ('MT', 'cl', 'cmd', 1, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` script.1.log:5307 teleport in stream ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` script.1.log:8109 teleport in stream ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` script.1.log:10915 teleport in stream ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` script.1.log:13720 teleport in stream ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` script.1.log:16532 teleport in stream ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_MORE` script.1.log:0 27 more teleport rows in ('HSD', 'cl', 'frame', None, '40877ef7-e82d-452a-ad5a-5b125f480572')
- warning `W_TELEPORT` message.1.log:5451 teleport in stream ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_TELEPORT` message.1.log:6878 teleport in stream ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_TELEPORT` message.1.log:8301 teleport in stream ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_TELEPORT` message.1.log:9729 teleport in stream ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_TELEPORT` message.1.log:11157 teleport in stream ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_MORE` message.1.log:0 27 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')
- warning `W_TIME_BACKWARDS` script.log:715 t 27.6 -> 27.26217 in ('HSD', 'sv', 'evt', 1.0, 'b4f50eb1-b1b8-4a6e-943e-8e737c2e480d')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5081 | 0 | - | - |
| MT | cl | r90 | 2444 | 514.32 | - | linear (no) |
| MT | cl | b1 | 185 | 0 | - | - |
| MT | cl | r18601 | 1227 | 364 | linear (no) | linear (yes) |
| MT | cl | b2 | 188 | 0 | - | - |
| MT | cl | r18602 | 1234 | 364 | linear (no) | linear (yes) |
| MT | cl | b3 | 188 | 0 | - | - |
| MT | cl | r18603 | 1228 | 364 | linear (no) | linear (yes) |
| MT | cl | b4 | 12687 | 0 | - | - |
| MT | cl | r18604 | 1299 | 364 | linear (no) | linear (yes) |
| MT | cl | r18605 | 1299 | 364 | linear (no) | linear (yes) |
| MT | cl | r18606 | 1299 | 364 | linear (no) | linear (yes) |
| MT | cl | r18621 | 584 | 514.32 | first_order (no) | linear (no) |
| MT | cl | r18622 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | cl | r18623 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | cl | r18624 | 602 | 514.322 | first_order (no) | linear (no) |
| MT | cl | r18625 | 602 | 514.322 | first_order (no) | linear (no) |
| MT | cl | r18626 | 602 | 514.323 | first_order (no) | linear (no) |
| MT | cl | r18627 | 602 | 514.399 | first_order (no) | linear (no) |
| MT | cl | r18628 | 602 | 514.386 | first_order (no) | linear (no) |
| MT | cl | r18629 | 602 | 514.388 | first_order (no) | linear (no) |
| MT | cl | r18630 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | cl | r18631 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | cl | r18632 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | cl | r18633 | 602 | 299.491 | first_order (no) | friction (no) |
| MT | cl | r18634 | 602 | 298.417 | first_order (no) | friction (no) |
| MT | cl | r18635 | 602 | 300.188 | first_order (no) | friction (no) |
| MT | cl | r18636 | 602 | 299 | first_order (no) | friction (no) |
| MT | cl | r18637 | 602 | 298.771 | first_order (no) | friction (no) |
| MT | cl | r18638 | 602 | 298.449 | first_order (no) | friction (no) |
| MT | cl | r18641 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | cl | r18642 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | cl | r18643 | 602 | 514.399 | first_order (no) | linear (no) |
| MT | cl | r18644 | 602 | 514.373 | first_order (no) | linear (no) |
| MT | cl | r18645 | 602 | 299.134 | first_order (no) | friction (no) |
| HSD | cl | r0 | 18302 | 0 | - | - |
| HSD | cl | r90 | 2516 | 1418.86 | - | friction (no) |
| HSD | cl | r18601 | 1298 | 1405.51 | - | linear (no) |
| HSD | cl | r18602 | 1298 | 1401.04 | - | linear (no) |
| HSD | cl | r18603 | 1298 | 1379.73 | - | linear (no) |
| HSD | cl | r18604 | 1299 | 364 | linear (no) | linear (yes) |
| HSD | cl | r18605 | 1299 | 364 | linear (no) | linear (yes) |
| HSD | cl | r18606 | 1299 | 364 | linear (no) | linear (yes) |
| HSD | cl | r18621 | 584 | 514.32 | first_order (no) | linear (no) |
| HSD | cl | r18622 | 609 | 514.32 | first_order (no) | linear (no) |
| HSD | cl | r18623 | 609 | 514.32 | first_order (no) | linear (no) |
| HSD | cl | r18624 | 602 | 514.322 | first_order (no) | linear (no) |
| HSD | cl | r18625 | 602 | 514.322 | first_order (no) | linear (no) |
| HSD | cl | r18626 | 602 | 514.323 | first_order (no) | linear (no) |
| HSD | cl | r18627 | 602 | 514.399 | first_order (no) | linear (no) |
| HSD | cl | r18628 | 602 | 514.386 | first_order (no) | linear (no) |
| HSD | cl | r18629 | 602 | 514.388 | first_order (no) | linear (no) |
| HSD | cl | r18630 | 602 | 514.333 | first_order (no) | linear (no) |
| HSD | cl | r18631 | 602 | 514.333 | first_order (no) | linear (no) |
| HSD | cl | r18632 | 602 | 514.333 | first_order (no) | linear (no) |
| HSD | cl | r18633 | 602 | 299.491 | first_order (no) | linear (yes) |
| HSD | cl | r18634 | 602 | 298.417 | first_order (no) | linear (yes) |
| HSD | cl | r18635 | 602 | 300.188 | first_order (no) | linear (yes) |
| HSD | cl | r18636 | 602 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r18637 | 602 | 298.771 | first_order (no) | linear (yes) |
| HSD | cl | r18638 | 602 | 298.449 | first_order (no) | linear (yes) |
| HSD | cl | r18641 | 609 | 514.32 | first_order (no) | linear (no) |
| HSD | cl | r18642 | 609 | 514.32 | first_order (no) | linear (no) |
| HSD | cl | r18643 | 602 | 514.399 | first_order (no) | linear (no) |
| HSD | cl | r18644 | 602 | 514.373 | first_order (no) | linear (no) |
| HSD | cl | r18645 | 602 | 299.134 | first_order (no) | linear (yes) |
| MT | sv | b0 | 5093 | 0 | - | - |
| MT | sv | r90 | 2450 | 514.32 | - | linear (no) |
| MT | sv | b1 | 185 | 0 | - | - |
| MT | sv | r18601 | 1233 | 364 | linear (no) | linear (yes) |
| MT | sv | b2 | 188 | 0 | - | - |
| MT | sv | r18602 | 1238 | 364 | linear (no) | linear (yes) |
| MT | sv | b3 | 188 | 0 | - | - |
| MT | sv | r18603 | 1232 | 364 | linear (no) | linear (yes) |
| MT | sv | b4 | 12681 | 0 | - | - |
| MT | sv | r18604 | 1299 | 364 | linear (no) | linear (yes) |
| MT | sv | r18605 | 1299 | 364 | linear (no) | linear (yes) |
| MT | sv | r18606 | 1299 | 364 | linear (no) | linear (yes) |
| MT | sv | r18621 | 584 | 514.32 | first_order (no) | linear (no) |
| MT | sv | r18622 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | sv | r18623 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | sv | r18624 | 602 | 514.322 | first_order (no) | linear (no) |
| MT | sv | r18625 | 602 | 514.322 | first_order (no) | linear (no) |
| MT | sv | r18626 | 602 | 514.323 | first_order (no) | linear (no) |
| MT | sv | r18627 | 602 | 514.399 | first_order (no) | linear (no) |
| MT | sv | r18628 | 602 | 514.386 | first_order (no) | linear (no) |
| MT | sv | r18629 | 602 | 514.388 | first_order (no) | linear (no) |
| MT | sv | r18630 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | sv | r18631 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | sv | r18632 | 602 | 514.333 | first_order (no) | linear (no) |
| MT | sv | r18633 | 602 | 299.489 | first_order (no) | friction (no) |
| MT | sv | r18634 | 602 | 298.417 | first_order (no) | friction (no) |
| MT | sv | r18635 | 602 | 300.188 | first_order (no) | friction (no) |
| MT | sv | r18636 | 602 | 299.001 | first_order (no) | friction (no) |
| MT | sv | r18637 | 602 | 298.771 | first_order (no) | friction (no) |
| MT | sv | r18638 | 602 | 298.451 | first_order (no) | friction (no) |
| MT | sv | r18641 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | sv | r18642 | 609 | 514.32 | first_order (no) | linear (no) |
| MT | sv | r18643 | 602 | 514.399 | first_order (no) | linear (no) |
| MT | sv | r18644 | 602 | 514.373 | first_order (no) | linear (no) |
| MT | sv | r18645 | 602 | 299.133 | first_order (no) | friction (no) |

Events: 245. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
