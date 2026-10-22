# hsd_tel report

Inputs: 23 file(s); rows: 262205 (MT 169102, HSD 93101)

Validation: 0 error(s), 25 warning(s), 6 info

- warning `W_TELEPORT` message.2.log:3818 teleport in stream ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` message.2.log:4495 teleport in stream ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` message.2.log:5140 teleport in stream ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` message.2.log:5786 teleport in stream ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` message.2.log:6432 teleport in stream ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_MORE` message.2.log:0 106 more teleport rows in ('MT', 'cl', 'cmd', 1, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` script.3.log:3462 teleport in stream ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` script.3.log:4752 teleport in stream ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` script.3.log:6014 teleport in stream ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` script.3.log:7277 teleport in stream ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` script.3.log:8540 teleport in stream ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_MORE` script.3.log:0 106 more teleport rows in ('HSD', 'cl', 'frame', None, '97ad79f1-a67e-4e82-9641-8de02256011d')
- warning `W_TELEPORT` message.2.log:3604 teleport in stream ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` message.2.log:4274 teleport in stream ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` message.2.log:4913 teleport in stream ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` message.2.log:5552 teleport in stream ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` message.2.log:6192 teleport in stream ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_MORE` message.2.log:0 106 more teleport rows in ('MT', 'sv', 'cmd', 1, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` script.log:819 teleport in stream ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` script.log:832 teleport in stream ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` script.log:857 teleport in stream ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` script.log:901 teleport in stream ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TELEPORT` script.log:953 teleport in stream ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_MORE` script.log:0 37 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')
- warning `W_TIME_BACKWARDS` script.log:719 t 24.2 -> 24.03314 in ('HSD', 'sv', 'evt', 1.0, '20a4a511-473c-48fc-9b77-d78ee990651d')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3231 | 0 | - | - |
| MT | cl | r90 | 475 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b1 | 193 | 0 | - | - |
| MT | cl | r8601 | 471 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 168 | 0 | - | - |
| MT | cl | r8602 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b3 | 169 | 0 | - | - |
| MT | cl | r8603 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b4 | 166 | 0 | - | - |
| MT | cl | r8604 | 541 | 299.363 | first_order (no) | linear (yes) |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r8605 | 540 | 343.975 | first_order (no) | friction (no) |
| MT | cl | b6 | 172 | 0 | - | - |
| MT | cl | r8606 | 539 | 299.374 | first_order (no) | linear (yes) |
| MT | cl | b7 | 174 | 0 | - | - |
| MT | cl | r8607 | 541 | 412.982 | first_order (no) | linear (no) |
| MT | cl | b8 | 170 | 0 | - | - |
| MT | cl | r8608 | 540 | 299.374 | first_order (no) | linear (yes) |
| MT | cl | b9 | 170 | 0 | - | - |
| MT | cl | r8609 | 539 | 299.375 | first_order (no) | linear (yes) |
| MT | cl | b10 | 171 | 0 | - | - |
| MT | cl | r8610 | 539 | 421.125 | first_order (no) | linear (no) |
| MT | cl | b11 | 170 | 0 | - | - |
| MT | cl | r8611 | 541 | 460.029 | first_order (no) | linear (no) |
| MT | cl | b12 | 168 | 0 | - | - |
| MT | cl | r8612 | 539 | 424.904 | first_order (no) | linear (no) |
| MT | cl | b13 | 169 | 0 | - | - |
| MT | cl | r8613 | 539 | 460.417 | first_order (no) | linear (no) |
| MT | cl | b14 | 166 | 0 | - | - |
| MT | cl | r8614 | 539 | 460.418 | first_order (no) | linear (no) |
| MT | cl | b15 | 168 | 0 | - | - |
| MT | cl | r8615 | 538 | 460.418 | first_order (no) | linear (no) |
| MT | cl | b16 | 168 | 0 | - | - |
| MT | cl | r8616 | 541 | 460.419 | first_order (no) | linear (no) |
| MT | cl | b17 | 166 | 0 | - | - |
| MT | cl | r8617 | 539 | 460.418 | first_order (no) | friction (no) |
| MT | cl | b18 | 166 | 0 | - | - |
| MT | cl | r8618 | 540 | 460.429 | first_order (no) | friction (no) |
| MT | cl | b19 | 194 | 0 | - | - |
| MT | cl | r8619 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b20 | 194 | 0 | - | - |
| MT | cl | r8620 | 541 | 460.431 | first_order (no) | friction (no) |
| MT | cl | b21 | 193 | 0 | - | - |
| MT | cl | r8621 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b22 | 193 | 0 | - | - |
| MT | cl | r8622 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b23 | 192 | 0 | - | - |
| MT | cl | r8623 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b24 | 194 | 0 | - | - |
| MT | cl | r8624 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b25 | 194 | 0 | - | - |
| MT | cl | r8625 | 539 | 460.429 | first_order (no) | friction (no) |
| MT | cl | b26 | 193 | 0 | - | - |
| MT | cl | r8626 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b27 | 193 | 0 | - | - |
| MT | cl | r8627 | 540 | 460.43 | first_order (no) | friction (no) |
| MT | cl | b28 | 192 | 0 | - | - |
| MT | cl | r8628 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b29 | 190 | 0 | - | - |
| MT | cl | r8629 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b30 | 190 | 0 | - | - |
| MT | cl | r8630 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b31 | 189 | 0 | - | - |
| MT | cl | r8631 | 539 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b32 | 190 | 0 | - | - |
| MT | cl | r8632 | 540 | 299.704 | first_order (no) | linear (yes) |
| MT | cl | b33 | 189 | 0 | - | - |
| MT | cl | r8633 | 541 | 299.704 | first_order (no) | linear (yes) |
| MT | cl | b34 | 189 | 0 | - | - |
| MT | cl | r8634 | 543 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b35 | 187 | 0 | - | - |
| MT | cl | r8635 | 542 | 299.703 | first_order (no) | linear (yes) |
| MT | cl | b36 | 186 | 0 | - | - |
| MT | cl | r8636 | 544 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b37 | 186 | 0 | - | - |
| MT | cl | r8637 | 546 | 299.705 | first_order (no) | friction (no) |
| MT | cl | b38 | 183 | 0 | - | - |
| MT | cl | r8638 | 547 | 299.704 | first_order (no) | friction (no) |
| MT | cl | b39 | 183 | 0 | - | - |
| MT | cl | r8639 | 547 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b40 | 182 | 0 | - | - |
| MT | cl | r8640 | 538 | 299.705 | first_order (no) | linear (yes) |
| MT | cl | b41 | 167 | 0 | - | - |
| MT | cl | r8641 | 540 | 329.622 | first_order (no) | friction (no) |
| MT | cl | b42 | 193 | 0 | - | - |
| MT | cl | r8642 | 539 | 299.704 | first_order (no) | linear (yes) |
| MT | cl | b43 | 166 | 0 | - | - |
| MT | cl | r8643 | 525 | 199.77 | first_order (yes) | linear (yes) |
| MT | cl | b44 | 174 | 0 | - | - |
| MT | cl | r8644 | 524 | 199.768 | first_order (yes) | linear (yes) |
| MT | cl | b45 | 174 | 0 | - | - |
| MT | cl | r8645 | 596 | 200.01 | first_order (yes) | friction (no) |
| MT | cl | b46 | 173 | 0 | - | - |
| MT | cl | r8646 | 594 | 200.001 | first_order (yes) | friction (no) |
| MT | cl | b47 | 174 | 0 | - | - |
| MT | cl | r8647 | 593 | 199.988 | first_order (yes) | friction (no) |
| MT | cl | b48 | 176 | 0 | - | - |
| MT | cl | r8648 | 594 | 200.009 | first_order (yes) | friction (no) |
| MT | cl | b49 | 173 | 0 | - | - |
| MT | cl | r8649 | 596 | 460 | first_order (no) | linear (no) |
| MT | cl | b50 | 170 | 0 | - | - |
| MT | cl | r8650 | 595 | 402.508 | first_order (no) | linear (no) |
| MT | cl | b51 | 172 | 0 | - | - |
| MT | cl | r8651 | 593 | 200.021 | first_order (yes) | friction (no) |
| MT | cl | b52 | 171 | 0 | - | - |
| MT | cl | r8652 | 595 | 402.518 | first_order (no) | linear (no) |
| MT | cl | b53 | 169 | 0 | - | - |
| MT | cl | r8653 | 594 | 200.021 | first_order (yes) | friction (no) |
| MT | cl | b54 | 170 | 0 | - | - |
| MT | cl | r8654 | 590 | 200.024 | first_order (yes) | friction (no) |
| MT | cl | b55 | 169 | 0 | - | - |
| MT | cl | r8655 | 595 | 200.022 | first_order (yes) | friction (no) |
| MT | cl | b56 | 167 | 0 | - | - |
| MT | cl | r8656 | 594 | 200.022 | first_order (yes) | friction (no) |
| MT | cl | b57 | 168 | 0 | - | - |
| MT | cl | r8657 | 593 | 200.026 | first_order (yes) | friction (no) |
| MT | cl | b58 | 166 | 0 | - | - |
| MT | cl | r8658 | 593 | 402.518 | first_order (no) | linear (no) |
| MT | cl | b59 | 165 | 0 | - | - |
| MT | cl | r8659 | 594 | 200.02 | first_order (yes) | friction (no) |
| MT | cl | b60 | 167 | 0 | - | - |
| MT | cl | r8660 | 503 | 457.801 | first_order (no) | - |
| MT | cl | b61 | 192 | 0 | - | - |
| MT | cl | r8661 | 508 | 457.805 | first_order (no) | - |
| MT | cl | b62 | 189 | 0 | - | - |
| MT | cl | r8662 | 574 | 457.801 | first_order (no) | - |
| MT | cl | b63 | 195 | 0 | - | - |
| MT | cl | r8663 | 575 | 457.804 | first_order (no) | - |
| MT | cl | b64 | 192 | 0 | - | - |
| MT | cl | r8664 | 575 | 457.803 | first_order (no) | - |
| MT | cl | b65 | 193 | 0 | - | - |
| MT | cl | r8665 | 574 | 457.803 | first_order (no) | - |
| MT | cl | b66 | 191 | 0 | - | - |
| MT | cl | r8666 | 574 | 457.806 | first_order (no) | - |
| MT | cl | b67 | 192 | 0 | - | - |
| MT | cl | r8667 | 577 | 457.804 | first_order (no) | - |
| MT | cl | b68 | 183 | 0 | - | - |
| MT | cl | r8668 | 575 | 457.803 | first_order (no) | - |
| MT | cl | b69 | 179 | 0 | - | - |
| MT | cl | r8669 | 577 | 457.801 | first_order (no) | - |
| MT | cl | b70 | 187 | 0 | - | - |
| MT | cl | r8670 | 576 | 457.803 | first_order (no) | - |
| MT | cl | b71 | 189 | 0 | - | - |
| MT | cl | r8671 | 577 | 457.803 | first_order (no) | - |
| MT | cl | b72 | 185 | 0 | - | - |
| MT | cl | r8672 | 573 | 457.804 | first_order (no) | friction (no) |
| MT | cl | b73 | 190 | 0 | - | - |
| MT | cl | r8673 | 578 | 457.809 | first_order (no) | - |
| MT | cl | b74 | 185 | 0 | - | - |
| MT | cl | r8674 | 576 | 457.806 | first_order (no) | - |
| MT | cl | b75 | 184 | 0 | - | - |
| MT | cl | r8675 | 578 | 457.803 | first_order (no) | - |
| MT | cl | b76 | 183 | 0 | - | - |
| MT | cl | r8676 | 576 | 457.812 | first_order (no) | - |
| MT | cl | b77 | 185 | 0 | - | - |
| MT | cl | r8677 | 495 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b78 | 174 | 0 | - | - |
| MT | cl | r8678 | 495 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b79 | 172 | 0 | - | - |
| MT | cl | r8679 | 563 | 429.081 | first_order (no) | linear (no) |
| MT | cl | b80 | 175 | 0 | - | - |
| MT | cl | r8680 | 564 | 434.284 | first_order (no) | linear (no) |
| MT | cl | b81 | 175 | 0 | - | - |
| MT | cl | r8681 | 564 | 434.896 | first_order (no) | linear (no) |
| MT | cl | b82 | 173 | 0 | - | - |
| MT | cl | r8682 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b83 | 174 | 0 | - | - |
| MT | cl | r8683 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b84 | 174 | 0 | - | - |
| MT | cl | r8684 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b85 | 174 | 0 | - | - |
| MT | cl | r8685 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b86 | 171 | 0 | - | - |
| MT | cl | r8686 | 564 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b87 | 171 | 0 | - | - |
| MT | cl | r8687 | 564 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b88 | 170 | 0 | - | - |
| MT | cl | r8688 | 565 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b89 | 168 | 0 | - | - |
| MT | cl | r8689 | 565 | 460.432 | first_order (no) | friction (no) |
| MT | cl | b90 | 167 | 0 | - | - |
| MT | cl | r8690 | 566 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b91 | 167 | 0 | - | - |
| MT | cl | r8691 | 566 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b92 | 195 | 0 | - | - |
| MT | cl | r8692 | 564 | 460.425 | first_order (no) | friction (no) |
| MT | cl | b93 | 166 | 0 | - | - |
| MT | cl | r8693 | 565 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b94 | 166 | 0 | - | - |
| MT | cl | r8694 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b95 | 166 | 0 | - | - |
| MT | cl | r8695 | 473 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b96 | 167 | 0 | - | - |
| MT | cl | r8696 | 540 | 427.836 | first_order (no) | linear (no) |
| MT | cl | b97 | 168 | 0 | - | - |
| MT | cl | r8697 | 540 | 299.363 | first_order (no) | linear (yes) |
| MT | cl | b98 | 169 | 0 | - | - |
| MT | cl | r8698 | 542 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b99 | 166 | 0 | - | - |
| MT | cl | r8699 | 541 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b100 | 166 | 0 | - | - |
| MT | cl | r8700 | 540 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b101 | 167 | 0 | - | - |
| MT | cl | r8701 | 542 | 460.425 | first_order (no) | linear (no) |
| MT | cl | b102 | 194 | 0 | - | - |
| MT | cl | r8702 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b103 | 192 | 0 | - | - |
| MT | cl | r8703 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b104 | 192 | 0 | - | - |
| MT | cl | r8704 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b105 | 192 | 0 | - | - |
| MT | cl | r8705 | 543 | 460.434 | first_order (no) | linear (no) |
| MT | cl | b106 | 189 | 0 | - | - |
| MT | cl | r8706 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b107 | 193 | 0 | - | - |
| MT | cl | r8707 | 540 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b108 | 193 | 0 | - | - |
| MT | cl | r8708 | 540 | 460.426 | first_order (no) | friction (no) |
| MT | cl | b109 | 191 | 0 | - | - |
| MT | cl | r8709 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b110 | 190 | 0 | - | - |
| MT | cl | r8710 | 541 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b111 | 158 | 0 | - | - |
| HSD | cl | r0 | 23055 | 0 | - | - |
| HSD | cl | r90 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r8601 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r8602 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r8603 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r8604 | 596 | 299.363 | first_order (no) | - |
| HSD | cl | r8605 | 595 | 343.975 | - | linear (no) |
| HSD | cl | r8606 | 594 | 299.374 | first_order (no) | - |
| HSD | cl | r8607 | 598 | 412.982 | - | linear (no) |
| HSD | cl | r8608 | 597 | 299.374 | first_order (no) | - |
| HSD | cl | r8609 | 596 | 299.375 | first_order (no) | - |
| HSD | cl | r8610 | 598 | 421.125 | - | linear (no) |
| HSD | cl | r8611 | 600 | 460.029 | - | linear (no) |
| HSD | cl | r8612 | 598 | 424.904 | - | linear (no) |
| HSD | cl | r8613 | 600 | 460.417 | - | linear (no) |
| HSD | cl | r8614 | 600 | 460.418 | - | linear (no) |
| HSD | cl | r8615 | 599 | 460.418 | - | linear (no) |
| HSD | cl | r8616 | 602 | 460.419 | - | linear (no) |
| HSD | cl | r8617 | 600 | 460.418 | - | friction (no) |
| HSD | cl | r8618 | 603 | 460.429 | - | friction (no) |
| HSD | cl | r8619 | 604 | 460.428 | - | friction (no) |
| HSD | cl | r8620 | 604 | 460.431 | - | friction (no) |
| HSD | cl | r8621 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r8622 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r8623 | 604 | 460.428 | - | friction (no) |
| HSD | cl | r8624 | 604 | 460.428 | - | friction (no) |
| HSD | cl | r8625 | 604 | 460.429 | - | friction (no) |
| HSD | cl | r8626 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r8627 | 605 | 460.43 | - | friction (no) |
| HSD | cl | r8628 | 608 | 460.428 | - | friction (no) |
| HSD | cl | r8629 | 608 | 460.428 | - | friction (no) |
| HSD | cl | r8630 | 608 | 460.428 | - | friction (no) |
| HSD | cl | r8631 | 608 | 460.427 | - | friction (no) |
| HSD | cl | r8632 | 608 | 299.704 | first_order (no) | - |
| HSD | cl | r8633 | 609 | 299.704 | first_order (no) | - |
| HSD | cl | r8634 | 611 | 299.151 | first_order (no) | - |
| HSD | cl | r8635 | 611 | 299.703 | first_order (no) | - |
| HSD | cl | r8636 | 612 | 299.152 | first_order (no) | - |
| HSD | cl | r8637 | 614 | 299.705 | first_order (no) | - |
| HSD | cl | r8638 | 615 | 299.704 | first_order (no) | - |
| HSD | cl | r8639 | 615 | 299.152 | first_order (no) | - |
| HSD | cl | r8640 | 601 | 299.705 | first_order (no) | - |
| HSD | cl | r8641 | 603 | 329.622 | - | linear (no) |
| HSD | cl | r8642 | 602 | 299.704 | first_order (no) | - |
| HSD | cl | r8643 | 594 | 199.77 | first_order (yes) | - |
| HSD | cl | r8644 | 593 | 199.768 | first_order (yes) | - |
| HSD | cl | r8645 | 655 | 200.01 | first_order (yes) | - |
| HSD | cl | r8646 | 653 | 200.001 | first_order (yes) | - |
| HSD | cl | r8647 | 652 | 199.988 | first_order (yes) | - |
| HSD | cl | r8648 | 655 | 200.009 | first_order (yes) | - |
| HSD | cl | r8649 | 657 | 460 | - | linear (no) |
| HSD | cl | r8650 | 656 | 402.508 | - | linear (no) |
| HSD | cl | r8651 | 656 | 200.021 | first_order (yes) | - |
| HSD | cl | r8652 | 658 | 402.518 | - | linear (no) |
| HSD | cl | r8653 | 657 | 200.021 | first_order (yes) | - |
| HSD | cl | r8654 | 655 | 200.024 | first_order (yes) | - |
| HSD | cl | r8655 | 660 | 200.022 | first_order (yes) | - |
| HSD | cl | r8656 | 659 | 200.022 | first_order (yes) | - |
| HSD | cl | r8657 | 660 | 200.026 | first_order (yes) | - |
| HSD | cl | r8658 | 660 | 402.518 | - | linear (no) |
| HSD | cl | r8659 | 661 | 200.02 | first_order (yes) | - |
| HSD | cl | r8660 | 575 | 457.801 | first_order (no) | - |
| HSD | cl | r8661 | 578 | 457.805 | first_order (no) | - |
| HSD | cl | r8662 | 633 | 457.801 | first_order (no) | - |
| HSD | cl | r8663 | 634 | 457.804 | first_order (no) | - |
| HSD | cl | r8664 | 634 | 457.803 | first_order (no) | - |
| HSD | cl | r8665 | 635 | 457.803 | first_order (no) | - |
| HSD | cl | r8666 | 635 | 457.806 | first_order (no) | - |
| HSD | cl | r8667 | 638 | 457.804 | first_order (no) | - |
| HSD | cl | r8668 | 638 | 457.803 | first_order (no) | - |
| HSD | cl | r8669 | 640 | 457.801 | first_order (no) | - |
| HSD | cl | r8670 | 639 | 457.803 | first_order (no) | - |
| HSD | cl | r8671 | 642 | 457.803 | first_order (no) | - |
| HSD | cl | r8672 | 638 | 457.804 | first_order (no) | - |
| HSD | cl | r8673 | 643 | 457.809 | first_order (no) | - |
| HSD | cl | r8674 | 643 | 457.806 | first_order (no) | - |
| HSD | cl | r8675 | 645 | 457.803 | first_order (no) | - |
| HSD | cl | r8676 | 643 | 457.812 | first_order (no) | - |
| HSD | cl | r8677 | 564 | 299.152 | first_order (no) | - |
| HSD | cl | r8678 | 564 | 299.151 | first_order (no) | - |
| HSD | cl | r8679 | 622 | 429.081 | - | linear (no) |
| HSD | cl | r8680 | 623 | 434.284 | - | linear (no) |
| HSD | cl | r8681 | 623 | 434.896 | - | linear (no) |
| HSD | cl | r8682 | 624 | 460.426 | - | friction (no) |
| HSD | cl | r8683 | 624 | 460.426 | - | friction (no) |
| HSD | cl | r8684 | 624 | 460.426 | - | friction (no) |
| HSD | cl | r8685 | 626 | 460.426 | - | friction (no) |
| HSD | cl | r8686 | 627 | 460.426 | - | friction (no) |
| HSD | cl | r8687 | 627 | 460.428 | - | friction (no) |
| HSD | cl | r8688 | 630 | 460.427 | - | friction (no) |
| HSD | cl | r8689 | 630 | 460.432 | - | friction (no) |
| HSD | cl | r8690 | 631 | 460.426 | - | friction (no) |
| HSD | cl | r8691 | 633 | 460.426 | - | friction (no) |
| HSD | cl | r8692 | 631 | 460.425 | - | friction (no) |
| HSD | cl | r8693 | 632 | 460.426 | - | friction (no) |
| HSD | cl | r8694 | 540 | 299.151 | first_order (no) | - |
| HSD | cl | r8695 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r8696 | 599 | 427.836 | - | linear (no) |
| HSD | cl | r8697 | 599 | 299.363 | first_order (no) | - |
| HSD | cl | r8698 | 601 | 460.427 | - | friction (no) |
| HSD | cl | r8699 | 602 | 460.427 | - | friction (no) |
| HSD | cl | r8700 | 601 | 460.427 | - | friction (no) |
| HSD | cl | r8701 | 603 | 460.425 | - | linear (no) |
| HSD | cl | r8702 | 606 | 460.426 | - | friction (no) |
| HSD | cl | r8703 | 606 | 460.426 | - | friction (no) |
| HSD | cl | r8704 | 606 | 460.426 | - | friction (no) |
| HSD | cl | r8705 | 608 | 460.434 | - | linear (no) |
| HSD | cl | r8706 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r8707 | 605 | 460.426 | - | friction (no) |
| HSD | cl | r8708 | 607 | 460.426 | - | friction (no) |
| HSD | cl | r8709 | 607 | 460.428 | - | friction (no) |
| HSD | cl | r8710 | 608 | 460.427 | - | friction (no) |
| MT | sv | b0 | 3246 | 0 | - | - |
| MT | sv | r90 | 475 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b1 | 193 | 0 | - | - |
| MT | sv | r8601 | 471 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 168 | 0 | - | - |
| MT | sv | r8602 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b3 | 169 | 0 | - | - |
| MT | sv | r8603 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b4 | 166 | 0 | - | - |
| MT | sv | r8604 | 541 | 299.363 | first_order (no) | linear (yes) |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r8605 | 540 | 342.641 | first_order (no) | friction (no) |
| MT | sv | b6 | 172 | 0 | - | - |
| MT | sv | r8606 | 539 | 299.374 | first_order (no) | linear (yes) |
| MT | sv | b7 | 174 | 0 | - | - |
| MT | sv | r8607 | 541 | 412.839 | first_order (no) | linear (no) |
| MT | sv | b8 | 170 | 0 | - | - |
| MT | sv | r8608 | 540 | 299.374 | first_order (no) | linear (yes) |
| MT | sv | b9 | 170 | 0 | - | - |
| MT | sv | r8609 | 539 | 299.375 | first_order (no) | linear (yes) |
| MT | sv | b10 | 171 | 0 | - | - |
| MT | sv | r8610 | 539 | 421.025 | first_order (no) | linear (no) |
| MT | sv | b11 | 170 | 0 | - | - |
| MT | sv | r8611 | 541 | 431.763 | first_order (no) | linear (no) |
| MT | sv | b12 | 168 | 0 | - | - |
| MT | sv | r8612 | 539 | 424.819 | first_order (no) | linear (no) |
| MT | sv | b13 | 169 | 0 | - | - |
| MT | sv | r8613 | 539 | 460.417 | first_order (no) | linear (no) |
| MT | sv | b14 | 166 | 0 | - | - |
| MT | sv | r8614 | 539 | 460.418 | first_order (no) | linear (no) |
| MT | sv | b15 | 168 | 0 | - | - |
| MT | sv | r8615 | 538 | 460.418 | first_order (no) | linear (no) |
| MT | sv | b16 | 168 | 0 | - | - |
| MT | sv | r8616 | 541 | 460.419 | first_order (no) | linear (no) |
| MT | sv | b17 | 166 | 0 | - | - |
| MT | sv | r8617 | 539 | 460.418 | first_order (no) | friction (no) |
| MT | sv | b18 | 166 | 0 | - | - |
| MT | sv | r8618 | 540 | 460.429 | first_order (no) | friction (no) |
| MT | sv | b19 | 194 | 0 | - | - |
| MT | sv | r8619 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b20 | 194 | 0 | - | - |
| MT | sv | r8620 | 541 | 460.431 | first_order (no) | friction (no) |
| MT | sv | b21 | 193 | 0 | - | - |
| MT | sv | r8621 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b22 | 193 | 0 | - | - |
| MT | sv | r8622 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b23 | 192 | 0 | - | - |
| MT | sv | r8623 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b24 | 194 | 0 | - | - |
| MT | sv | r8624 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b25 | 194 | 0 | - | - |
| MT | sv | r8625 | 539 | 460.429 | first_order (no) | friction (no) |
| MT | sv | b26 | 193 | 0 | - | - |
| MT | sv | r8626 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b27 | 193 | 0 | - | - |
| MT | sv | r8627 | 540 | 460.43 | first_order (no) | friction (no) |
| MT | sv | b28 | 192 | 0 | - | - |
| MT | sv | r8628 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b29 | 190 | 0 | - | - |
| MT | sv | r8629 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b30 | 190 | 0 | - | - |
| MT | sv | r8630 | 541 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b31 | 189 | 0 | - | - |
| MT | sv | r8631 | 539 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b32 | 190 | 0 | - | - |
| MT | sv | r8632 | 540 | 299.704 | first_order (no) | linear (yes) |
| MT | sv | b33 | 189 | 0 | - | - |
| MT | sv | r8633 | 541 | 299.704 | first_order (no) | linear (yes) |
| MT | sv | b34 | 189 | 0 | - | - |
| MT | sv | r8634 | 543 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b35 | 187 | 0 | - | - |
| MT | sv | r8635 | 542 | 299.703 | first_order (no) | linear (yes) |
| MT | sv | b36 | 186 | 0 | - | - |
| MT | sv | r8636 | 544 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b37 | 186 | 0 | - | - |
| MT | sv | r8637 | 546 | 299.705 | first_order (no) | friction (no) |
| MT | sv | b38 | 183 | 0 | - | - |
| MT | sv | r8638 | 547 | 299.704 | first_order (no) | friction (no) |
| MT | sv | b39 | 183 | 0 | - | - |
| MT | sv | r8639 | 547 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b40 | 182 | 0 | - | - |
| MT | sv | r8640 | 538 | 299.705 | first_order (no) | linear (yes) |
| MT | sv | b41 | 167 | 0 | - | - |
| MT | sv | r8641 | 540 | 329.622 | first_order (no) | friction (no) |
| MT | sv | b42 | 193 | 0 | - | - |
| MT | sv | r8642 | 539 | 299.704 | first_order (no) | linear (yes) |
| MT | sv | b43 | 166 | 0 | - | - |
| MT | sv | r8643 | 525 | 199.77 | first_order (yes) | linear (yes) |
| MT | sv | b44 | 174 | 0 | - | - |
| MT | sv | r8644 | 524 | 199.768 | first_order (yes) | linear (yes) |
| MT | sv | b45 | 174 | 0 | - | - |
| MT | sv | r8645 | 596 | 199.999 | first_order (yes) | friction (no) |
| MT | sv | b46 | 173 | 0 | - | - |
| MT | sv | r8646 | 594 | 200.001 | first_order (yes) | friction (no) |
| MT | sv | b47 | 174 | 0 | - | - |
| MT | sv | r8647 | 593 | 199.988 | first_order (yes) | friction (no) |
| MT | sv | b48 | 176 | 0 | - | - |
| MT | sv | r8648 | 594 | 200.009 | first_order (yes) | friction (no) |
| MT | sv | b49 | 173 | 0 | - | - |
| MT | sv | r8649 | 596 | 402.509 | first_order (no) | linear (no) |
| MT | sv | b50 | 170 | 0 | - | - |
| MT | sv | r8650 | 595 | 402.508 | first_order (no) | linear (no) |
| MT | sv | b51 | 172 | 0 | - | - |
| MT | sv | r8651 | 593 | 200.021 | first_order (yes) | friction (no) |
| MT | sv | b52 | 171 | 0 | - | - |
| MT | sv | r8652 | 595 | 402.518 | first_order (no) | linear (no) |
| MT | sv | b53 | 169 | 0 | - | - |
| MT | sv | r8653 | 594 | 200.021 | first_order (yes) | friction (no) |
| MT | sv | b54 | 170 | 0 | - | - |
| MT | sv | r8654 | 590 | 200.024 | first_order (yes) | friction (no) |
| MT | sv | b55 | 169 | 0 | - | - |
| MT | sv | r8655 | 595 | 200.022 | first_order (yes) | friction (no) |
| MT | sv | b56 | 167 | 0 | - | - |
| MT | sv | r8656 | 594 | 200.022 | first_order (yes) | friction (no) |
| MT | sv | b57 | 168 | 0 | - | - |
| MT | sv | r8657 | 593 | 200.026 | first_order (yes) | friction (no) |
| MT | sv | b58 | 166 | 0 | - | - |
| MT | sv | r8658 | 593 | 402.518 | first_order (no) | linear (no) |
| MT | sv | b59 | 165 | 0 | - | - |
| MT | sv | r8659 | 594 | 200.02 | first_order (yes) | friction (no) |
| MT | sv | b60 | 167 | 0 | - | - |
| MT | sv | r8660 | 503 | 457.801 | first_order (no) | - |
| MT | sv | b61 | 192 | 0 | - | - |
| MT | sv | r8661 | 508 | 457.805 | first_order (no) | - |
| MT | sv | b62 | 189 | 0 | - | - |
| MT | sv | r8662 | 574 | 457.801 | first_order (no) | - |
| MT | sv | b63 | 195 | 0 | - | - |
| MT | sv | r8663 | 575 | 457.804 | first_order (no) | - |
| MT | sv | b64 | 192 | 0 | - | - |
| MT | sv | r8664 | 575 | 457.803 | first_order (no) | - |
| MT | sv | b65 | 193 | 0 | - | - |
| MT | sv | r8665 | 574 | 457.803 | first_order (no) | - |
| MT | sv | b66 | 191 | 0 | - | - |
| MT | sv | r8666 | 574 | 457.806 | first_order (no) | - |
| MT | sv | b67 | 192 | 0 | - | - |
| MT | sv | r8667 | 577 | 457.804 | first_order (no) | - |
| MT | sv | b68 | 183 | 0 | - | - |
| MT | sv | r8668 | 575 | 457.803 | first_order (no) | - |
| MT | sv | b69 | 179 | 0 | - | - |
| MT | sv | r8669 | 577 | 457.801 | first_order (no) | - |
| MT | sv | b70 | 187 | 0 | - | - |
| MT | sv | r8670 | 576 | 457.803 | first_order (no) | - |
| MT | sv | b71 | 189 | 0 | - | - |
| MT | sv | r8671 | 577 | 457.803 | first_order (no) | - |
| MT | sv | b72 | 185 | 0 | - | - |
| MT | sv | r8672 | 573 | 457.804 | first_order (no) | friction (no) |
| MT | sv | b73 | 190 | 0 | - | - |
| MT | sv | r8673 | 578 | 457.809 | first_order (no) | - |
| MT | sv | b74 | 185 | 0 | - | - |
| MT | sv | r8674 | 576 | 457.806 | first_order (no) | - |
| MT | sv | b75 | 184 | 0 | - | - |
| MT | sv | r8675 | 578 | 457.803 | first_order (no) | - |
| MT | sv | b76 | 183 | 0 | - | - |
| MT | sv | r8676 | 576 | 457.812 | first_order (no) | - |
| MT | sv | b77 | 185 | 0 | - | - |
| MT | sv | r8677 | 495 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b78 | 174 | 0 | - | - |
| MT | sv | r8678 | 495 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b79 | 172 | 0 | - | - |
| MT | sv | r8679 | 563 | 429.002 | first_order (no) | linear (no) |
| MT | sv | b80 | 175 | 0 | - | - |
| MT | sv | r8680 | 564 | 434.224 | first_order (no) | linear (no) |
| MT | sv | b81 | 175 | 0 | - | - |
| MT | sv | r8681 | 564 | 434.837 | first_order (no) | linear (no) |
| MT | sv | b82 | 173 | 0 | - | - |
| MT | sv | r8682 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b83 | 174 | 0 | - | - |
| MT | sv | r8683 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b84 | 174 | 0 | - | - |
| MT | sv | r8684 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b85 | 174 | 0 | - | - |
| MT | sv | r8685 | 563 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b86 | 171 | 0 | - | - |
| MT | sv | r8686 | 564 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b87 | 171 | 0 | - | - |
| MT | sv | r8687 | 564 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b88 | 170 | 0 | - | - |
| MT | sv | r8688 | 565 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b89 | 168 | 0 | - | - |
| MT | sv | r8689 | 565 | 460.432 | first_order (no) | friction (no) |
| MT | sv | b90 | 167 | 0 | - | - |
| MT | sv | r8690 | 566 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b91 | 167 | 0 | - | - |
| MT | sv | r8691 | 566 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b92 | 195 | 0 | - | - |
| MT | sv | r8692 | 564 | 460.425 | first_order (no) | friction (no) |
| MT | sv | b93 | 166 | 0 | - | - |
| MT | sv | r8693 | 565 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b94 | 166 | 0 | - | - |
| MT | sv | r8694 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b95 | 166 | 0 | - | - |
| MT | sv | r8695 | 473 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b96 | 167 | 0 | - | - |
| MT | sv | r8696 | 540 | 427.76 | first_order (no) | linear (no) |
| MT | sv | b97 | 168 | 0 | - | - |
| MT | sv | r8697 | 540 | 299.363 | first_order (no) | linear (yes) |
| MT | sv | b98 | 169 | 0 | - | - |
| MT | sv | r8698 | 542 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b99 | 166 | 0 | - | - |
| MT | sv | r8699 | 541 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b100 | 166 | 0 | - | - |
| MT | sv | r8700 | 540 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b101 | 167 | 0 | - | - |
| MT | sv | r8701 | 542 | 460.425 | first_order (no) | linear (no) |
| MT | sv | b102 | 194 | 0 | - | - |
| MT | sv | r8702 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b103 | 192 | 0 | - | - |
| MT | sv | r8703 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b104 | 192 | 0 | - | - |
| MT | sv | r8704 | 543 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b105 | 192 | 0 | - | - |
| MT | sv | r8705 | 543 | 460.434 | first_order (no) | linear (no) |
| MT | sv | b106 | 189 | 0 | - | - |
| MT | sv | r8706 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b107 | 193 | 0 | - | - |
| MT | sv | r8707 | 540 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b108 | 193 | 0 | - | - |
| MT | sv | r8708 | 540 | 460.426 | first_order (no) | friction (no) |
| MT | sv | b109 | 191 | 0 | - | - |
| MT | sv | r8709 | 540 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b110 | 190 | 0 | - | - |
| MT | sv | r8710 | 541 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b111 | 154 | 0 | - | - |

Events: 2934. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
