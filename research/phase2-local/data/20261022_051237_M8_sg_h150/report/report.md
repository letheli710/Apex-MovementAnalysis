# hsd_tel report

Inputs: 17 file(s); rows: 108251 (MT 69906, HSD 38343)

Validation: 0 error(s), 25 warning(s), 6 info

- warning `W_TELEPORT` message.log:3831 teleport in stream ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` message.log:4499 teleport in stream ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` message.log:5171 teleport in stream ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` message.log:5841 teleport in stream ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` message.log:6513 teleport in stream ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_MORE` message.log:0 38 more teleport rows in ('MT', 'cl', 'cmd', 1, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` script.1.log:3473 teleport in stream ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` script.1.log:4787 teleport in stream ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` script.1.log:6106 teleport in stream ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` script.1.log:7424 teleport in stream ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` script.1.log:8741 teleport in stream ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_MORE` script.1.log:0 38 more teleport rows in ('HSD', 'cl', 'frame', None, '8e2758ff-d581-447a-bc07-937aa466c3f9')
- warning `W_TELEPORT` message.log:3622 teleport in stream ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` message.log:4289 teleport in stream ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` message.log:4959 teleport in stream ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` message.log:5624 teleport in stream ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` message.log:6290 teleport in stream ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_MORE` message.log:0 38 more teleport rows in ('MT', 'sv', 'cmd', 1, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` script.log:821 teleport in stream ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` script.log:834 teleport in stream ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` script.log:847 teleport in stream ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` script.log:860 teleport in stream ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TELEPORT` script.log:872 teleport in stream ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_MORE` script.log:0 28 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')
- warning `W_TIME_BACKWARDS` script.log:717 t 25.55 -> 25.29008 in ('HSD', 'sv', 'evt', 1.0, '69d74eaf-a658-48ca-b819-10296a0c5c23')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3247 | 0 | - | - |
| MT | cl | r90 | 491 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 173 | 0 | - | - |
| MT | cl | r9001 | 498 | 299.15 | first_order (no) | friction (no) |
| MT | cl | b2 | 171 | 0 | - | - |
| MT | cl | r9002 | 491 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b3 | 174 | 0 | - | - |
| MT | cl | r9003 | 492 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b4 | 174 | 0 | - | - |
| MT | cl | r9004 | 565 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b5 | 176 | 0 | - | - |
| MT | cl | r9005 | 566 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b6 | 176 | 0 | - | - |
| MT | cl | r9006 | 566 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b7 | 173 | 0 | - | - |
| MT | cl | r9007 | 565 | 377.403 | first_order (no) | linear (no) |
| MT | cl | b8 | 174 | 0 | - | - |
| MT | cl | r9008 | 559 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b9 | 181 | 0 | - | - |
| MT | cl | r9009 | 566 | 376.412 | first_order (no) | linear (no) |
| MT | cl | b10 | 173 | 0 | - | - |
| MT | cl | r9010 | 564 | 299.468 | first_order (no) | friction (no) |
| MT | cl | b11 | 174 | 0 | - | - |
| MT | cl | r9011 | 564 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b12 | 174 | 0 | - | - |
| MT | cl | r9012 | 564 | 299.473 | first_order (no) | friction (no) |
| MT | cl | b13 | 173 | 0 | - | - |
| MT | cl | r9013 | 565 | 460.485 | first_order (no) | friction (no) |
| MT | cl | b14 | 171 | 0 | - | - |
| MT | cl | r9014 | 565 | 460.486 | first_order (no) | friction (no) |
| MT | cl | b15 | 171 | 0 | - | - |
| MT | cl | r9015 | 561 | 299.455 | first_order (no) | friction (no) |
| MT | cl | b16 | 174 | 0 | - | - |
| MT | cl | r9016 | 566 | 460.496 | first_order (no) | friction (no) |
| MT | cl | b17 | 168 | 0 | - | - |
| MT | cl | r9017 | 562 | 460.494 | first_order (no) | friction (no) |
| MT | cl | b18 | 168 | 0 | - | - |
| MT | cl | r9018 | 563 | 460.485 | first_order (no) | friction (no) |
| MT | cl | b19 | 171 | 0 | - | - |
| MT | cl | r9019 | 563 | 460.487 | first_order (no) | friction (no) |
| MT | cl | b20 | 170 | 0 | - | - |
| MT | cl | r9020 | 564 | 460.485 | first_order (no) | friction (no) |
| MT | cl | b21 | 170 | 0 | - | - |
| MT | cl | r9021 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b22 | 168 | 0 | - | - |
| MT | cl | r9022 | 564 | 460.492 | first_order (no) | friction (no) |
| MT | cl | b23 | 167 | 0 | - | - |
| MT | cl | r9023 | 565 | 460.496 | first_order (no) | friction (no) |
| MT | cl | b24 | 167 | 0 | - | - |
| MT | cl | r9024 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b25 | 167 | 0 | - | - |
| MT | cl | r9025 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b26 | 166 | 0 | - | - |
| MT | cl | r9026 | 566 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b27 | 194 | 0 | - | - |
| MT | cl | r9027 | 564 | 460.496 | first_order (no) | friction (no) |
| MT | cl | b28 | 195 | 0 | - | - |
| MT | cl | r9028 | 563 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b29 | 167 | 0 | - | - |
| MT | cl | r9029 | 563 | 460.496 | first_order (no) | friction (no) |
| MT | cl | b30 | 166 | 0 | - | - |
| MT | cl | r9030 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b31 | 166 | 0 | - | - |
| MT | cl | r9031 | 564 | 460.496 | first_order (no) | friction (no) |
| MT | cl | b32 | 194 | 0 | - | - |
| MT | cl | r9032 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b33 | 192 | 0 | - | - |
| MT | cl | r9033 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | cl | b34 | 194 | 0 | - | - |
| MT | cl | r9034 | 569 | 299.793 | first_order (no) | friction (no) |
| MT | cl | b35 | 190 | 0 | - | - |
| MT | cl | r9035 | 566 | 299.793 | first_order (no) | friction (no) |
| MT | cl | b36 | 189 | 0 | - | - |
| MT | cl | r9036 | 567 | 299.793 | first_order (no) | friction (no) |
| MT | cl | b37 | 190 | 0 | - | - |
| MT | cl | r9037 | 567 | 299.794 | first_order (no) | friction (no) |
| MT | cl | b38 | 189 | 0 | - | - |
| MT | cl | r9038 | 565 | 299.794 | first_order (no) | friction (no) |
| MT | cl | b39 | 190 | 0 | - | - |
| MT | cl | r9039 | 569 | 299.794 | first_order (no) | friction (no) |
| MT | cl | b40 | 189 | 0 | - | - |
| MT | cl | r9040 | 566 | 299.794 | first_order (no) | friction (no) |
| MT | cl | b41 | 194 | 0 | - | - |
| MT | cl | r9041 | 562 | 299.78 | first_order (no) | friction (no) |
| MT | cl | b42 | 168 | 0 | - | - |
| MT | cl | r9042 | 564 | 299.793 | first_order (no) | friction (no) |
| MT | cl | b43 | 132 | 0 | - | - |
| HSD | cl | r0 | 10784 | 0 | - | - |
| HSD | cl | r90 | 563 | 299.151 | first_order (no) | - |
| HSD | cl | r9001 | 566 | 299.15 | first_order (no) | - |
| HSD | cl | r9002 | 564 | 299.152 | first_order (no) | - |
| HSD | cl | r9003 | 564 | 299.152 | first_order (no) | - |
| HSD | cl | r9004 | 621 | 299.467 | first_order (no) | - |
| HSD | cl | r9005 | 622 | 299.467 | first_order (no) | - |
| HSD | cl | r9006 | 622 | 299.467 | first_order (no) | - |
| HSD | cl | r9007 | 623 | 377.403 | - | linear (no) |
| HSD | cl | r9008 | 617 | 299.467 | first_order (no) | - |
| HSD | cl | r9009 | 624 | 376.412 | - | linear (no) |
| HSD | cl | r9010 | 624 | 299.468 | first_order (no) | - |
| HSD | cl | r9011 | 624 | 299.467 | first_order (no) | - |
| HSD | cl | r9012 | 624 | 299.473 | first_order (no) | - |
| HSD | cl | r9013 | 627 | 460.485 | - | friction (no) |
| HSD | cl | r9014 | 627 | 460.486 | - | friction (no) |
| HSD | cl | r9015 | 623 | 299.455 | first_order (no) | - |
| HSD | cl | r9016 | 630 | 460.496 | - | friction (no) |
| HSD | cl | r9017 | 626 | 460.494 | - | friction (no) |
| HSD | cl | r9018 | 627 | 460.485 | - | friction (no) |
| HSD | cl | r9019 | 627 | 460.487 | - | friction (no) |
| HSD | cl | r9020 | 628 | 460.485 | - | friction (no) |
| HSD | cl | r9021 | 630 | 460.495 | - | friction (no) |
| HSD | cl | r9022 | 630 | 460.492 | - | friction (no) |
| HSD | cl | r9023 | 631 | 460.496 | - | friction (no) |
| HSD | cl | r9024 | 631 | 460.495 | - | friction (no) |
| HSD | cl | r9025 | 631 | 460.495 | - | friction (no) |
| HSD | cl | r9026 | 634 | 460.495 | - | friction (no) |
| HSD | cl | r9027 | 632 | 460.496 | - | friction (no) |
| HSD | cl | r9028 | 631 | 460.495 | - | friction (no) |
| HSD | cl | r9029 | 631 | 460.496 | - | friction (no) |
| HSD | cl | r9030 | 632 | 460.495 | - | friction (no) |
| HSD | cl | r9031 | 634 | 460.496 | - | friction (no) |
| HSD | cl | r9032 | 635 | 460.495 | - | friction (no) |
| HSD | cl | r9033 | 634 | 460.495 | - | friction (no) |
| HSD | cl | r9034 | 638 | 299.793 | first_order (no) | - |
| HSD | cl | r9035 | 636 | 299.793 | first_order (no) | - |
| HSD | cl | r9036 | 637 | 299.793 | first_order (no) | - |
| HSD | cl | r9037 | 638 | 299.794 | first_order (no) | - |
| HSD | cl | r9038 | 637 | 299.794 | first_order (no) | - |
| HSD | cl | r9039 | 639 | 299.794 | first_order (no) | - |
| HSD | cl | r9040 | 632 | 299.794 | first_order (no) | - |
| HSD | cl | r9041 | 628 | 299.78 | first_order (no) | - |
| HSD | cl | r9042 | 630 | 299.793 | first_order (no) | - |
| MT | sv | b0 | 3259 | 0 | - | - |
| MT | sv | r90 | 491 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 173 | 0 | - | - |
| MT | sv | r9001 | 498 | 299.15 | first_order (no) | friction (no) |
| MT | sv | b2 | 171 | 0 | - | - |
| MT | sv | r9002 | 491 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b3 | 174 | 0 | - | - |
| MT | sv | r9003 | 492 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b4 | 174 | 0 | - | - |
| MT | sv | r9004 | 565 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b5 | 176 | 0 | - | - |
| MT | sv | r9005 | 566 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b6 | 176 | 0 | - | - |
| MT | sv | r9006 | 566 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b7 | 173 | 0 | - | - |
| MT | sv | r9007 | 565 | 377.3 | first_order (no) | linear (no) |
| MT | sv | b8 | 174 | 0 | - | - |
| MT | sv | r9008 | 559 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b9 | 181 | 0 | - | - |
| MT | sv | r9009 | 566 | 376.31 | first_order (no) | linear (no) |
| MT | sv | b10 | 173 | 0 | - | - |
| MT | sv | r9010 | 564 | 299.468 | first_order (no) | friction (no) |
| MT | sv | b11 | 174 | 0 | - | - |
| MT | sv | r9011 | 564 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b12 | 174 | 0 | - | - |
| MT | sv | r9012 | 564 | 299.473 | first_order (no) | friction (no) |
| MT | sv | b13 | 173 | 0 | - | - |
| MT | sv | r9013 | 565 | 460.485 | first_order (no) | friction (no) |
| MT | sv | b14 | 171 | 0 | - | - |
| MT | sv | r9014 | 565 | 460.486 | first_order (no) | friction (no) |
| MT | sv | b15 | 171 | 0 | - | - |
| MT | sv | r9015 | 561 | 299.455 | first_order (no) | friction (no) |
| MT | sv | b16 | 174 | 0 | - | - |
| MT | sv | r9016 | 566 | 460.496 | first_order (no) | friction (no) |
| MT | sv | b17 | 168 | 0 | - | - |
| MT | sv | r9017 | 562 | 460.494 | first_order (no) | friction (no) |
| MT | sv | b18 | 168 | 0 | - | - |
| MT | sv | r9018 | 563 | 460.485 | first_order (no) | friction (no) |
| MT | sv | b19 | 171 | 0 | - | - |
| MT | sv | r9019 | 563 | 460.487 | first_order (no) | friction (no) |
| MT | sv | b20 | 170 | 0 | - | - |
| MT | sv | r9020 | 564 | 460.485 | first_order (no) | friction (no) |
| MT | sv | b21 | 170 | 0 | - | - |
| MT | sv | r9021 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b22 | 168 | 0 | - | - |
| MT | sv | r9022 | 564 | 460.492 | first_order (no) | friction (no) |
| MT | sv | b23 | 167 | 0 | - | - |
| MT | sv | r9023 | 565 | 460.496 | first_order (no) | friction (no) |
| MT | sv | b24 | 167 | 0 | - | - |
| MT | sv | r9024 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b25 | 167 | 0 | - | - |
| MT | sv | r9025 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b26 | 166 | 0 | - | - |
| MT | sv | r9026 | 566 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b27 | 194 | 0 | - | - |
| MT | sv | r9027 | 564 | 460.496 | first_order (no) | friction (no) |
| MT | sv | b28 | 195 | 0 | - | - |
| MT | sv | r9028 | 563 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b29 | 167 | 0 | - | - |
| MT | sv | r9029 | 563 | 460.496 | first_order (no) | friction (no) |
| MT | sv | b30 | 166 | 0 | - | - |
| MT | sv | r9030 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b31 | 166 | 0 | - | - |
| MT | sv | r9031 | 564 | 460.496 | first_order (no) | friction (no) |
| MT | sv | b32 | 194 | 0 | - | - |
| MT | sv | r9032 | 565 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b33 | 192 | 0 | - | - |
| MT | sv | r9033 | 564 | 460.495 | first_order (no) | friction (no) |
| MT | sv | b34 | 194 | 0 | - | - |
| MT | sv | r9034 | 569 | 299.793 | first_order (no) | friction (no) |
| MT | sv | b35 | 190 | 0 | - | - |
| MT | sv | r9035 | 566 | 299.793 | first_order (no) | friction (no) |
| MT | sv | b36 | 189 | 0 | - | - |
| MT | sv | r9036 | 567 | 299.793 | first_order (no) | friction (no) |
| MT | sv | b37 | 190 | 0 | - | - |
| MT | sv | r9037 | 567 | 299.794 | first_order (no) | friction (no) |
| MT | sv | b38 | 189 | 0 | - | - |
| MT | sv | r9038 | 565 | 299.794 | first_order (no) | friction (no) |
| MT | sv | b39 | 190 | 0 | - | - |
| MT | sv | r9039 | 569 | 299.794 | first_order (no) | friction (no) |
| MT | sv | b40 | 189 | 0 | - | - |
| MT | sv | r9040 | 566 | 299.794 | first_order (no) | friction (no) |
| MT | sv | b41 | 194 | 0 | - | - |
| MT | sv | r9041 | 562 | 299.78 | first_order (no) | friction (no) |
| MT | sv | b42 | 168 | 0 | - | - |
| MT | sv | r9042 | 564 | 299.793 | first_order (no) | friction (no) |
| MT | sv | b43 | 128 | 0 | - | - |

Events: 1187. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
