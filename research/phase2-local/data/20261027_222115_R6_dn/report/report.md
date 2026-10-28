# hsd_tel report

Inputs: 20 file(s); rows: 126480 (MT 84355, HSD 42123)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.1.log:3961 teleport in stream ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` message.1.log:4915 teleport in stream ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` message.1.log:5867 teleport in stream ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` message.1.log:6818 teleport in stream ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` message.1.log:7774 teleport in stream ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_MORE` message.1.log:0 36 more teleport rows in ('MT', 'cl', 'cmd', 1, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` script.2.log:3608 teleport in stream ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` script.2.log:5350 teleport in stream ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` script.2.log:7088 teleport in stream ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` script.2.log:8825 teleport in stream ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` script.2.log:10564 teleport in stream ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_MORE` script.2.log:0 36 more teleport rows in ('HSD', 'cl', 'frame', None, 'afd708c0-cb4b-4f23-93d0-8a870295e188')
- warning `W_TELEPORT` message.1.log:3779 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_TELEPORT` message.1.log:4732 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_TELEPORT` message.1.log:5680 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_TELEPORT` message.1.log:6626 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_TELEPORT` message.1.log:7573 teleport in stream ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_MORE` message.1.log:0 36 more teleport rows in ('MT', 'sv', 'cmd', 1, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')
- warning `W_TIME_BACKWARDS` script.log:713 t 25.35 -> 25.00753 in ('HSD', 'sv', 'evt', 1.0, 'aa45712f-faa3-4858-a91a-1a8803fe9a2a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 10306 | 0 | - | - |
| MT | cl | r90 | 780 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r671 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r672 | 781 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r673 | 781 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r674 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r675 | 780 | 457.813 | first_order (no) | linear (no) |
| MT | cl | r676 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r677 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r678 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | cl | r679 | 780 | 458.871 | first_order (no) | linear (no) |
| MT | cl | r680 | 779 | 457.809 | first_order (no) | linear (no) |
| MT | cl | r681 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r682 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r683 | 780 | 461.783 | first_order (no) | linear (yes) |
| MT | cl | r684 | 781 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r685 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | cl | r686 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | cl | r687 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | cl | r688 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | cl | r689 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | cl | r690 | 780 | 461.002 | first_order (no) | linear (yes) |
| MT | cl | r691 | 780 | 493.051 | first_order (no) | linear (yes) |
| MT | cl | r692 | 779 | 493.1 | first_order (no) | linear (yes) |
| MT | cl | r693 | 780 | 493.049 | first_order (no) | linear (yes) |
| MT | cl | r694 | 780 | 493.042 | first_order (no) | linear (yes) |
| MT | cl | r695 | 780 | 493.18 | first_order (no) | linear (yes) |
| MT | cl | r696 | 779 | 565.788 | first_order (no) | linear (yes) |
| MT | cl | r697 | 779 | 565.73 | first_order (no) | linear (yes) |
| MT | cl | r698 | 780 | 565.903 | first_order (no) | linear (yes) |
| MT | cl | r699 | 780 | 565.878 | first_order (no) | linear (yes) |
| MT | cl | r700 | 781 | 565.794 | first_order (no) | linear (yes) |
| MT | cl | r701 | 804 | 467.638 | first_order (no) | linear (no) |
| MT | cl | r702 | 804 | 467.779 | first_order (no) | linear (no) |
| MT | cl | r703 | 805 | 468.093 | first_order (no) | linear (no) |
| MT | cl | r704 | 803 | 467.559 | first_order (no) | linear (no) |
| MT | cl | r705 | 803 | 467.947 | first_order (no) | linear (no) |
| MT | cl | r706 | 695 | 457.802 | first_order (no) | linear (no) |
| MT | cl | r707 | 696 | 457.807 | first_order (no) | linear (no) |
| MT | cl | r708 | 696 | 457.801 | first_order (no) | linear (no) |
| MT | cl | r709 | 697 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r710 | 696 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r0 | 10275 | 0 | - | - |
| HSD | cl | r90 | 780 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r671 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r672 | 780 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r673 | 780 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r674 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r675 | 780 | 457.813 | first_order (no) | linear (no) |
| HSD | cl | r676 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r677 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r678 | 780 | 457.804 | first_order (no) | linear (no) |
| HSD | cl | r679 | 780 | 458.871 | first_order (no) | linear (no) |
| HSD | cl | r680 | 780 | 457.809 | first_order (no) | linear (no) |
| HSD | cl | r681 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r682 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r683 | 780 | 461.783 | first_order (no) | linear (yes) |
| HSD | cl | r684 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r685 | 780 | 460.781 | first_order (no) | linear (yes) |
| HSD | cl | r686 | 780 | 461.005 | first_order (no) | linear (yes) |
| HSD | cl | r687 | 780 | 461.005 | first_order (no) | linear (yes) |
| HSD | cl | r688 | 780 | 461.005 | first_order (no) | linear (yes) |
| HSD | cl | r689 | 780 | 461.005 | first_order (no) | linear (yes) |
| HSD | cl | r690 | 780 | 461.002 | first_order (no) | linear (yes) |
| HSD | cl | r691 | 780 | 493.051 | first_order (no) | linear (yes) |
| HSD | cl | r692 | 780 | 493.1 | first_order (no) | linear (yes) |
| HSD | cl | r693 | 780 | 493.049 | first_order (no) | linear (yes) |
| HSD | cl | r694 | 780 | 493.042 | first_order (no) | linear (yes) |
| HSD | cl | r695 | 780 | 493.18 | first_order (no) | linear (yes) |
| HSD | cl | r696 | 780 | 565.788 | first_order (no) | linear (yes) |
| HSD | cl | r697 | 780 | 565.73 | first_order (no) | linear (yes) |
| HSD | cl | r698 | 780 | 565.903 | first_order (no) | linear (yes) |
| HSD | cl | r699 | 780 | 565.878 | first_order (no) | linear (yes) |
| HSD | cl | r700 | 780 | 565.794 | first_order (no) | linear (yes) |
| HSD | cl | r701 | 804 | 467.638 | first_order (no) | linear (no) |
| HSD | cl | r702 | 804 | 467.779 | first_order (no) | linear (no) |
| HSD | cl | r703 | 804 | 468.093 | first_order (no) | linear (no) |
| HSD | cl | r704 | 804 | 467.559 | first_order (no) | linear (no) |
| HSD | cl | r705 | 804 | 467.947 | first_order (no) | linear (no) |
| HSD | cl | r706 | 696 | 457.802 | first_order (no) | linear (no) |
| HSD | cl | r707 | 696 | 457.807 | first_order (no) | linear (no) |
| HSD | cl | r708 | 696 | 457.801 | first_order (no) | linear (no) |
| HSD | cl | r709 | 696 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r710 | 696 | 457.804 | first_order (no) | linear (no) |
| MT | sv | b0 | 10336 | 0 | - | - |
| MT | sv | r90 | 780 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r671 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r672 | 781 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r673 | 781 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r674 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r675 | 780 | 457.813 | first_order (no) | linear (no) |
| MT | sv | r676 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r677 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r678 | 780 | 457.804 | first_order (no) | linear (no) |
| MT | sv | r679 | 780 | 458.806 | first_order (no) | linear (no) |
| MT | sv | r680 | 779 | 457.809 | first_order (no) | linear (no) |
| MT | sv | r681 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | sv | r682 | 780 | 460.782 | first_order (no) | linear (yes) |
| MT | sv | r683 | 780 | 460.781 | first_order (no) | linear (yes) |
| MT | sv | r684 | 781 | 460.782 | first_order (no) | linear (yes) |
| MT | sv | r685 | 780 | 460.782 | first_order (no) | linear (yes) |
| MT | sv | r686 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | sv | r687 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | sv | r688 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | sv | r689 | 780 | 461.005 | first_order (no) | linear (yes) |
| MT | sv | r690 | 780 | 461.002 | first_order (no) | linear (yes) |
| MT | sv | r691 | 780 | 492.974 | first_order (no) | linear (yes) |
| MT | sv | r692 | 779 | 493.023 | first_order (no) | linear (yes) |
| MT | sv | r693 | 780 | 492.972 | first_order (no) | linear (yes) |
| MT | sv | r694 | 780 | 492.965 | first_order (no) | linear (yes) |
| MT | sv | r695 | 780 | 493.103 | first_order (no) | linear (yes) |
| MT | sv | r696 | 779 | 565.63 | first_order (no) | linear (yes) |
| MT | sv | r697 | 779 | 565.805 | first_order (no) | linear (yes) |
| MT | sv | r698 | 780 | 565.747 | first_order (no) | linear (yes) |
| MT | sv | r699 | 780 | 565.723 | first_order (no) | linear (yes) |
| MT | sv | r700 | 781 | 565.638 | first_order (no) | linear (yes) |
| MT | sv | r701 | 804 | 467.655 | first_order (no) | linear (no) |
| MT | sv | r702 | 804 | 467.796 | first_order (no) | linear (no) |
| MT | sv | r703 | 805 | 468.151 | first_order (no) | linear (no) |
| MT | sv | r704 | 803 | 467.576 | first_order (no) | linear (no) |
| MT | sv | r705 | 803 | 467.908 | first_order (no) | linear (no) |
| MT | sv | r706 | 695 | 457.802 | first_order (no) | linear (no) |
| MT | sv | r707 | 696 | 457.807 | first_order (no) | linear (no) |
| MT | sv | r708 | 696 | 457.801 | first_order (no) | linear (no) |
| MT | sv | r709 | 697 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r710 | 696 | 457.804 | first_order (no) | linear (no) |

Events: 248. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
