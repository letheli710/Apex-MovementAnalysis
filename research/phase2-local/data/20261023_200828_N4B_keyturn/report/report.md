# hsd_tel report

Inputs: 16 file(s); rows: 65498 (MT 43527, HSD 21911)

Validation: 0 error(s), 19 warning(s), 24 info

- warning `W_TELEPORT` message.log:3735 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` message.log:4627 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` message.log:5520 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` message.log:6412 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` message.log:7308 teleport in stream ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'cl', 'cmd', 1, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` script.log:3374 teleport in stream ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` script.log:4270 teleport in stream ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` script.log:5169 teleport in stream ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` script.log:6067 teleport in stream ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` script.log:6966 teleport in stream ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_MORE` script.log:0 11 more teleport rows in ('HSD', 'cl', 'frame', None, 'd9dc6a0c-0059-4baa-8572-144e880546a7')
- warning `W_TELEPORT` message.log:3474 teleport in stream ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_TELEPORT` message.log:4361 teleport in stream ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_TELEPORT` message.log:5248 teleport in stream ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_TELEPORT` message.log:6135 teleport in stream ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_TELEPORT` message.log:7022 teleport in stream ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, '90e79015-db9f-4ece-8fad-606505907f81')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.15 -> 24.96115 in ('HSD', 'sv', 'evt', 1.0, '90e79015-db9f-4ece-8fad-606505907f81')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 6573 | 0 | - | - |
| MT | cl | r90 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20011 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20012 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20013 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20014 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20015 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20016 | 720 | 299 | first_order (no) | friction (no) |
| MT | cl | r20017 | 720 | 299 | first_order (no) | friction (no) |
| MT | cl | r20018 | 720 | 299 | first_order (no) | friction (no) |
| MT | cl | r20019 | 720 | 299 | first_order (no) | friction (no) |
| MT | cl | r20020 | 720 | 299 | first_order (no) | friction (no) |
| MT | cl | r20021 | 720 | 199.773 | first_order (yes) | linear (no) |
| MT | cl | r20022 | 720 | 199.776 | first_order (yes) | linear (no) |
| MT | cl | r20023 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | cl | r20024 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | cl | r20025 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | cl | r20026 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20027 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20028 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20029 | 720 | 299 | first_order (no) | linear (no) |
| MT | cl | r20030 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r0 | 6545 | 0 | - | - |
| HSD | cl | r90 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20011 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20012 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20013 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20014 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20015 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20016 | 720 | 299 | first_order (no) | friction (no) |
| HSD | cl | r20017 | 720 | 299 | first_order (no) | friction (no) |
| HSD | cl | r20018 | 720 | 299 | first_order (no) | friction (no) |
| HSD | cl | r20019 | 720 | 299 | first_order (no) | friction (no) |
| HSD | cl | r20020 | 720 | 299 | first_order (no) | friction (no) |
| HSD | cl | r20021 | 720 | 199.773 | first_order (yes) | linear (no) |
| HSD | cl | r20022 | 720 | 199.776 | first_order (yes) | linear (no) |
| HSD | cl | r20023 | 720 | 199.74 | first_order (yes) | linear (no) |
| HSD | cl | r20024 | 720 | 199.74 | first_order (yes) | linear (no) |
| HSD | cl | r20025 | 720 | 199.74 | first_order (yes) | linear (no) |
| HSD | cl | r20026 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20027 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20028 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20029 | 720 | 299 | first_order (no) | linear (no) |
| HSD | cl | r20030 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | b0 | 6584 | 0 | - | - |
| MT | sv | r90 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20011 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20012 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20013 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20014 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20015 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20016 | 720 | 299 | first_order (no) | friction (no) |
| MT | sv | r20017 | 720 | 299 | first_order (no) | friction (no) |
| MT | sv | r20018 | 720 | 299 | first_order (no) | friction (no) |
| MT | sv | r20019 | 720 | 299 | first_order (no) | friction (no) |
| MT | sv | r20020 | 720 | 299 | first_order (no) | friction (no) |
| MT | sv | r20021 | 720 | 199.773 | first_order (yes) | linear (no) |
| MT | sv | r20022 | 720 | 199.776 | first_order (yes) | linear (no) |
| MT | sv | r20023 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | sv | r20024 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | sv | r20025 | 720 | 199.74 | first_order (yes) | linear (no) |
| MT | sv | r20026 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20027 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20028 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20029 | 720 | 299 | first_order (no) | linear (no) |
| MT | sv | r20030 | 720 | 299 | first_order (no) | linear (no) |

Events: 82. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
