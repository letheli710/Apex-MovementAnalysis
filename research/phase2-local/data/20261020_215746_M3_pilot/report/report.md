# hsd_tel report

Inputs: 19 file(s); rows: 187345 (MT 123146, HSD 64139)

Validation: 0 error(s), 19 warning(s), 28 info

- warning `W_TELEPORT` message.1.log:5611 teleport in stream ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` message.1.log:21780 teleport in stream ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` message.1.log:22418 teleport in stream ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` message.1.log:23053 teleport in stream ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` message.1.log:23687 teleport in stream ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_MORE` message.1.log:0 45 more teleport rows in ('MT', 'cl', 'cmd', 1, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` script.1.log:5259 teleport in stream ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` script.1.log:21497 teleport in stream ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` script.1.log:22145 teleport in stream ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` script.1.log:22793 teleport in stream ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` script.1.log:23440 teleport in stream ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_MORE` script.1.log:0 45 more teleport rows in ('HSD', 'cl', 'frame', None, 'a0d87e6c-680c-4705-be77-7f5e8f9c8de9')
- warning `W_TELEPORT` message.1.log:5393 teleport in stream ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_TELEPORT` message.1.log:21466 teleport in stream ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_TELEPORT` message.1.log:22099 teleport in stream ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_TELEPORT` message.1.log:22732 teleport in stream ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_TELEPORT` message.1.log:23366 teleport in stream ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_MORE` message.1.log:0 45 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b955ca06-a714-4581-9827-24b0188978b7')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.2 -> 23.04365 in ('HSD', 'sv', 'evt', 1.0, 'b955ca06-a714-4581-9827-24b0188978b7')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5027 | 0 | - | - |
| MT | cl | r401 | 810 | 299.151 | first_order (no) | - |
| MT | cl | b1 | 19633 | 0 | - | - |
| MT | cl | r90 | 420 | 297.329 | first_order (no) | friction (no) |
| MT | cl | r501 | 420 | 295.647 | first_order (no) | friction (no) |
| MT | cl | r502 | 421 | 295.982 | first_order (no) | friction (no) |
| MT | cl | r503 | 422 | 296.888 | first_order (no) | friction (no) |
| MT | cl | r504 | 424 | 295.746 | first_order (no) | friction (no) |
| MT | cl | r505 | 427 | 297.098 | first_order (no) | friction (no) |
| MT | cl | r506 | 431 | 296.907 | first_order (no) | friction (no) |
| MT | cl | r507 | 437 | 296.983 | first_order (no) | friction (no) |
| MT | cl | r508 | 444 | 297.449 | first_order (no) | friction (no) |
| MT | cl | r509 | 454 | 296.975 | first_order (no) | friction (no) |
| MT | cl | r510 | 469 | 297.129 | first_order (no) | friction (no) |
| MT | cl | r511 | 489 | 305.552 | first_order (no) | linear (no) |
| MT | cl | r512 | 509 | 303.965 | first_order (no) | linear (no) |
| MT | cl | r513 | 422 | 295.9 | first_order (no) | friction (no) |
| MT | cl | r514 | 423 | 297.073 | first_order (no) | friction (no) |
| MT | cl | r515 | 431 | 296.948 | first_order (no) | linear (no) |
| MT | cl | r516 | 432 | 296.889 | first_order (no) | friction (no) |
| MT | cl | r517 | 454 | 297.436 | first_order (no) | linear (no) |
| MT | cl | r518 | 455 | 296.874 | first_order (no) | friction (no) |
| MT | cl | r519 | 424 | 199.579 | first_order (yes) | friction (no) |
| MT | cl | r520 | 654 | 458.169 | first_order (no) | friction (no) |
| MT | cl | r521 | 882 | 299.15 | first_order (no) | - |
| MT | cl | b2 | 1479 | 0 | - | - |
| MT | cl | r522 | 669 | 299.151 | first_order (no) | linear (no) |
| MT | cl | r523 | 669 | 299.151 | first_order (no) | friction (no) |
| MT | cl | r524 | 669 | 299.151 | first_order (no) | linear (no) |
| MT | cl | r525 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | cl | r526 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | cl | r527 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | cl | r528 | 692 | 299.506 | first_order (no) | - |
| MT | cl | b3 | 213 | 0 | - | - |
| MT | cl | r529 | 691 | 299.506 | first_order (no) | - |
| MT | cl | b4 | 214 | 0 | - | - |
| MT | cl | r530 | 699 | 299.551 | first_order (no) | - |
| MT | cl | b5 | 208 | 0 | - | - |
| MT | cl | r531 | 697 | 299.543 | first_order (no) | - |
| MT | cl | b6 | 208 | 0 | - | - |
| MT | cl | r532 | 706 | 299.67 | first_order (no) | - |
| MT | cl | b7 | 189 | 0 | - | - |
| MT | cl | r533 | 704 | 299.62 | first_order (no) | - |
| MT | cl | b8 | 199 | 0 | - | - |
| MT | cl | r534 | 706 | 299.629 | first_order (no) | - |
| MT | cl | b9 | 202 | 0 | - | - |
| MT | cl | r535 | 705 | 299.62 | first_order (no) | - |
| MT | cl | b10 | 202 | 0 | - | - |
| MT | cl | r536 | 711 | 299.67 | first_order (no) | - |
| MT | cl | b11 | 197 | 0 | - | - |
| MT | cl | r537 | 709 | 299.638 | first_order (no) | - |
| MT | cl | b12 | 198 | 0 | - | - |
| MT | cl | r538 | 715 | 299.692 | first_order (no) | - |
| MT | cl | b13 | 193 | 0 | - | - |
| MT | cl | r539 | 713 | 299.701 | first_order (no) | - |
| MT | cl | b14 | 195 | 0 | - | - |
| MT | cl | r540 | 718 | 299.753 | first_order (no) | - |
| MT | cl | b15 | 225 | 0 | - | - |
| MT | cl | r541 | 721 | 299.744 | first_order (no) | - |
| MT | cl | b16 | 225 | 0 | - | - |
| MT | cl | r542 | 726 | 299.785 | first_order (no) | - |
| MT | cl | b17 | 221 | 0 | - | - |
| MT | cl | r543 | 721 | 299.775 | first_order (no) | - |
| MT | cl | b18 | 222 | 0 | - | - |
| MT | cl | r544 | 733 | 299.973 | first_order (no) | - |
| MT | cl | b19 | 206 | 0 | - | - |
| MT | cl | r545 | 732 | 299.875 | first_order (no) | - |
| MT | cl | b20 | 643 | 0 | - | - |
| MT | cl | r546 | 1031 | 458.193 | first_order (no) | linear (no) |
| MT | cl | r547 | 954 | 531.733 | first_order (no) | linear (yes) |
| MT | cl | r548 | 955 | 299.696 | first_order (no) | - |
| MT | cl | b21 | 186 | 0 | - | - |
| HSD | cl | r0 | 30463 | 0 | - | - |
| HSD | cl | r401 | 894 | 299.151 | first_order (no) | - |
| HSD | cl | r90 | 420 | 297.329 | first_order (no) | friction (no) |
| HSD | cl | r501 | 420 | 295.647 | first_order (no) | friction (no) |
| HSD | cl | r502 | 421 | 295.982 | first_order (no) | friction (no) |
| HSD | cl | r503 | 422 | 296.888 | first_order (no) | friction (no) |
| HSD | cl | r504 | 424 | 295.746 | first_order (no) | friction (no) |
| HSD | cl | r505 | 427 | 297.098 | first_order (no) | friction (no) |
| HSD | cl | r506 | 431 | 296.907 | first_order (no) | friction (no) |
| HSD | cl | r507 | 437 | 296.983 | first_order (no) | friction (no) |
| HSD | cl | r508 | 444 | 297.449 | first_order (no) | friction (no) |
| HSD | cl | r509 | 454 | 296.975 | first_order (no) | friction (no) |
| HSD | cl | r510 | 469 | 297.129 | first_order (no) | linear (no) |
| HSD | cl | r511 | 489 | 305.552 | first_order (no) | linear (no) |
| HSD | cl | r512 | 509 | 303.965 | first_order (no) | linear (no) |
| HSD | cl | r513 | 422 | 295.9 | first_order (no) | linear (no) |
| HSD | cl | r514 | 423 | 297.073 | first_order (no) | linear (yes) |
| HSD | cl | r515 | 431 | 296.948 | first_order (no) | linear (no) |
| HSD | cl | r516 | 432 | 296.889 | first_order (no) | linear (yes) |
| HSD | cl | r517 | 454 | 297.436 | first_order (no) | linear (no) |
| HSD | cl | r518 | 455 | 296.874 | first_order (no) | linear (yes) |
| HSD | cl | r519 | 424 | 199.579 | first_order (yes) | friction (no) |
| HSD | cl | r520 | 654 | 458.169 | first_order (no) | linear (no) |
| HSD | cl | r521 | 966 | 299.15 | first_order (no) | - |
| HSD | cl | r522 | 669 | 299.151 | first_order (no) | linear (no) |
| HSD | cl | r523 | 669 | 299.151 | first_order (no) | friction (no) |
| HSD | cl | r524 | 669 | 299.151 | first_order (no) | friction (no) |
| HSD | cl | r525 | 705 | 299.151 | first_order (no) | linear (no) |
| HSD | cl | r526 | 705 | 299.151 | first_order (no) | friction (no) |
| HSD | cl | r527 | 705 | 299.151 | first_order (no) | linear (no) |
| HSD | cl | r528 | 778 | 299.506 | first_order (no) | - |
| HSD | cl | r529 | 777 | 299.506 | first_order (no) | - |
| HSD | cl | r530 | 784 | 299.551 | first_order (no) | - |
| HSD | cl | r531 | 783 | 299.543 | first_order (no) | - |
| HSD | cl | r532 | 788 | 299.67 | first_order (no) | - |
| HSD | cl | r533 | 787 | 299.62 | first_order (no) | - |
| HSD | cl | r534 | 792 | 299.629 | first_order (no) | - |
| HSD | cl | r535 | 791 | 299.62 | first_order (no) | - |
| HSD | cl | r536 | 796 | 299.67 | first_order (no) | - |
| HSD | cl | r537 | 795 | 299.638 | first_order (no) | - |
| HSD | cl | r538 | 800 | 299.692 | first_order (no) | - |
| HSD | cl | r539 | 799 | 299.701 | first_order (no) | - |
| HSD | cl | r540 | 804 | 299.753 | first_order (no) | - |
| HSD | cl | r541 | 803 | 299.744 | first_order (no) | - |
| HSD | cl | r542 | 808 | 299.785 | first_order (no) | - |
| HSD | cl | r543 | 807 | 299.775 | first_order (no) | - |
| HSD | cl | r544 | 818 | 299.973 | first_order (no) | - |
| HSD | cl | r545 | 817 | 299.875 | first_order (no) | - |
| HSD | cl | r546 | 1031 | 458.193 | first_order (no) | linear (no) |
| HSD | cl | r547 | 954 | 531.733 | first_order (no) | - |
| HSD | cl | r548 | 1038 | 299.696 | first_order (no) | - |
| MT | sv | b0 | 5035 | 0 | - | - |
| MT | sv | r401 | 810 | 299.151 | first_order (no) | - |
| MT | sv | b1 | 19633 | 0 | - | - |
| MT | sv | r90 | 420 | 297.329 | first_order (no) | friction (no) |
| MT | sv | r501 | 420 | 295.647 | first_order (no) | friction (no) |
| MT | sv | r502 | 421 | 295.982 | first_order (no) | friction (no) |
| MT | sv | r503 | 422 | 296.888 | first_order (no) | friction (no) |
| MT | sv | r504 | 424 | 295.746 | first_order (no) | friction (no) |
| MT | sv | r505 | 427 | 297.098 | first_order (no) | friction (no) |
| MT | sv | r506 | 431 | 296.907 | first_order (no) | friction (no) |
| MT | sv | r507 | 437 | 296.983 | first_order (no) | friction (no) |
| MT | sv | r508 | 444 | 297.449 | first_order (no) | friction (no) |
| MT | sv | r509 | 454 | 296.975 | first_order (no) | friction (no) |
| MT | sv | r510 | 469 | 297.129 | first_order (no) | friction (no) |
| MT | sv | r511 | 489 | 305.552 | first_order (no) | linear (no) |
| MT | sv | r512 | 509 | 303.965 | first_order (no) | linear (no) |
| MT | sv | r513 | 422 | 295.9 | first_order (no) | friction (no) |
| MT | sv | r514 | 423 | 297.073 | first_order (no) | friction (no) |
| MT | sv | r515 | 431 | 296.948 | first_order (no) | linear (no) |
| MT | sv | r516 | 432 | 296.889 | first_order (no) | friction (no) |
| MT | sv | r517 | 454 | 297.436 | first_order (no) | linear (no) |
| MT | sv | r518 | 455 | 296.874 | first_order (no) | friction (no) |
| MT | sv | r519 | 424 | 199.579 | first_order (yes) | friction (no) |
| MT | sv | r520 | 654 | 458.169 | first_order (no) | friction (no) |
| MT | sv | r521 | 881 | 299.15 | first_order (no) | - |
| MT | sv | b2 | 1479 | 0 | - | - |
| MT | sv | r522 | 669 | 299.151 | first_order (no) | linear (no) |
| MT | sv | r523 | 669 | 299.151 | first_order (no) | friction (no) |
| MT | sv | r524 | 669 | 299.151 | first_order (no) | linear (no) |
| MT | sv | r525 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | sv | r526 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | sv | r527 | 705 | 299.151 | first_order (no) | linear (no) |
| MT | sv | r528 | 692 | 299.506 | first_order (no) | - |
| MT | sv | b3 | 213 | 0 | - | - |
| MT | sv | r529 | 691 | 299.506 | first_order (no) | - |
| MT | sv | b4 | 214 | 0 | - | - |
| MT | sv | r530 | 699 | 299.551 | first_order (no) | - |
| MT | sv | b5 | 208 | 0 | - | - |
| MT | sv | r531 | 697 | 299.543 | first_order (no) | - |
| MT | sv | b6 | 208 | 0 | - | - |
| MT | sv | r532 | 706 | 299.67 | first_order (no) | - |
| MT | sv | b7 | 189 | 0 | - | - |
| MT | sv | r533 | 704 | 299.62 | first_order (no) | - |
| MT | sv | b8 | 199 | 0 | - | - |
| MT | sv | r534 | 706 | 299.629 | first_order (no) | - |
| MT | sv | b9 | 202 | 0 | - | - |
| MT | sv | r535 | 705 | 299.62 | first_order (no) | - |
| MT | sv | b10 | 202 | 0 | - | - |
| MT | sv | r536 | 711 | 299.67 | first_order (no) | - |
| MT | sv | b11 | 197 | 0 | - | - |
| MT | sv | r537 | 709 | 299.638 | first_order (no) | - |
| MT | sv | b12 | 198 | 0 | - | - |
| MT | sv | r538 | 715 | 299.692 | first_order (no) | - |
| MT | sv | b13 | 193 | 0 | - | - |
| MT | sv | r539 | 713 | 299.701 | first_order (no) | - |
| MT | sv | b14 | 195 | 0 | - | - |
| MT | sv | r540 | 718 | 299.753 | first_order (no) | - |
| MT | sv | b15 | 225 | 0 | - | - |
| MT | sv | r541 | 721 | 299.744 | first_order (no) | - |
| MT | sv | b16 | 225 | 0 | - | - |
| MT | sv | r542 | 726 | 299.785 | first_order (no) | - |
| MT | sv | b17 | 221 | 0 | - | - |
| MT | sv | r543 | 721 | 299.775 | first_order (no) | - |
| MT | sv | b18 | 222 | 0 | - | - |
| MT | sv | r544 | 733 | 299.973 | first_order (no) | - |
| MT | sv | b19 | 206 | 0 | - | - |
| MT | sv | r545 | 732 | 299.875 | first_order (no) | - |
| MT | sv | b20 | 643 | 0 | - | - |
| MT | sv | r546 | 1031 | 458.193 | first_order (no) | linear (no) |
| MT | sv | r547 | 954 | 531.733 | first_order (no) | linear (yes) |
| MT | sv | r548 | 955 | 299.696 | first_order (no) | - |
| MT | sv | b21 | 182 | 0 | - | - |

Events: 1048. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
