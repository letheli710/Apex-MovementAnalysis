# hsd_tel report

Inputs: 20 file(s); rows: 124564 (MT 83052, HSD 41510)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.1.log:3683 teleport in stream ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` message.1.log:4650 teleport in stream ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` message.1.log:5617 teleport in stream ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` message.1.log:6582 teleport in stream ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` message.1.log:7554 teleport in stream ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_MORE` message.1.log:0 25 more teleport rows in ('MT', 'cl', 'cmd', 1, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` script.2.log:3314 teleport in stream ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` script.2.log:5931 teleport in stream ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` script.2.log:8539 teleport in stream ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` script.2.log:11146 teleport in stream ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` script.2.log:13754 teleport in stream ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_MORE` script.2.log:0 25 more teleport rows in ('HSD', 'cl', 'frame', None, 'c2efb680-1642-415b-b893-d3c84bfccc55')
- warning `W_TELEPORT` message.1.log:3450 teleport in stream ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_TELEPORT` message.1.log:4404 teleport in stream ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_TELEPORT` message.1.log:5351 teleport in stream ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_TELEPORT` message.1.log:6298 teleport in stream ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_TELEPORT` message.1.log:7245 teleport in stream ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_MORE` message.1.log:0 25 more teleport rows in ('MT', 'sv', 'cmd', 1, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')
- warning `W_TIME_BACKWARDS` script.log:715 t 24.25 -> 24.00601 in ('HSD', 'sv', 'evt', 1.0, '3a02fb88-99dd-4d23-bc57-03c01d23e14b')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 9704 | 0 | - | - |
| MT | cl | r90 | 758 | 514.467 | first_order (no) | linear (no) |
| MT | cl | r16901 | 758 | 533.667 | first_order (no) | linear (no) |
| MT | cl | r16902 | 757 | 514.467 | first_order (no) | linear (no) |
| MT | cl | r16903 | 758 | 533.667 | first_order (no) | linear (no) |
| MT | cl | r16904 | 991 | 817.381 | linear (no) | linear (no) |
| MT | cl | r16905 | 992 | 817.381 | linear (no) | linear (no) |
| MT | cl | r16906 | 991 | 817.369 | linear (no) | linear (no) |
| MT | cl | r16907 | 758 | 520.813 | first_order (no) | friction (no) |
| MT | cl | r16908 | 757 | 520.814 | first_order (no) | friction (no) |
| MT | cl | r16909 | 758 | 520.814 | first_order (no) | friction (no) |
| MT | cl | r16910 | 990 | 832.035 | linear (no) | linear (no) |
| MT | cl | r16911 | 992 | 832.036 | linear (no) | linear (no) |
| MT | cl | r16912 | 991 | 832.037 | linear (no) | linear (no) |
| MT | cl | r16913 | 757 | 539.507 | first_order (no) | friction (yes) |
| MT | cl | r16914 | 705 | 539.492 | first_order (no) | friction (no) |
| MT | cl | r16915 | 733 | 539.452 | linear (no) | friction (no) |
| MT | cl | r16916 | 992 | 813.842 | linear (no) | friction (no) |
| MT | cl | r16917 | 986 | 813.845 | linear (no) | friction (no) |
| MT | cl | r16918 | 991 | 813.846 | linear (no) | friction (no) |
| MT | cl | r16919 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | cl | r16920 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | cl | r16921 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | cl | r16922 | 727 | 523.359 | first_order (no) | linear (yes) |
| MT | cl | r16923 | 728 | 523.36 | first_order (no) | linear (yes) |
| MT | cl | r16924 | 728 | 523.36 | first_order (no) | linear (yes) |
| MT | cl | r16925 | 757 | 520.089 | first_order (no) | linear (yes) |
| MT | cl | r16926 | 757 | 520.088 | first_order (no) | linear (yes) |
| MT | cl | r16927 | 757 | 520.083 | first_order (no) | linear (yes) |
| MT | cl | r16928 | 301 | 5.94089 | - | - |
| MT | cl | r16929 | 301 | 5.93989 | - | - |
| MT | cl | r16930 | 301 | 5.94289 | - | - |
| MT | cl | r16931 | 1322 | 0 | - | - |
| MT | cl | r16932 | 1322 | 0 | - | - |
| MT | cl | r16933 | 1326 | 0 | - | - |
| MT | cl | r16934 | 1322 | 0 | - | - |
| MT | cl | r16935 | 1322 | 0 | - | - |
| MT | cl | r16936 | 1322 | 0 | - | - |
| HSD | cl | r0 | 9683 | 0 | - | - |
| HSD | cl | r90 | 758 | 514.467 | first_order (yes) | linear (no) |
| HSD | cl | r16901 | 758 | 533.667 | first_order (yes) | linear (no) |
| HSD | cl | r16902 | 757 | 514.467 | first_order (yes) | linear (no) |
| HSD | cl | r16903 | 758 | 533.667 | first_order (yes) | linear (no) |
| HSD | cl | r16904 | 991 | 817.381 | linear (no) | linear (yes) |
| HSD | cl | r16905 | 992 | 817.381 | linear (no) | linear (yes) |
| HSD | cl | r16906 | 992 | 817.369 | linear (no) | linear (yes) |
| HSD | cl | r16907 | 758 | 520.813 | first_order (no) | friction (no) |
| HSD | cl | r16908 | 757 | 520.814 | first_order (no) | friction (no) |
| HSD | cl | r16909 | 758 | 520.814 | first_order (no) | friction (no) |
| HSD | cl | r16910 | 992 | 832.035 | linear (no) | linear (yes) |
| HSD | cl | r16911 | 992 | 832.036 | linear (no) | linear (yes) |
| HSD | cl | r16912 | 991 | 832.037 | linear (no) | linear (yes) |
| HSD | cl | r16913 | 758 | 539.507 | first_order (no) | friction (yes) |
| HSD | cl | r16914 | 708 | 539.492 | first_order (no) | friction (no) |
| HSD | cl | r16915 | 733 | 539.452 | linear (no) | friction (no) |
| HSD | cl | r16916 | 992 | 813.842 | linear (no) | linear (yes) |
| HSD | cl | r16917 | 986 | 813.845 | linear (no) | linear (yes) |
| HSD | cl | r16918 | 991 | 813.846 | linear (no) | linear (yes) |
| HSD | cl | r16919 | 612 | 514.296 | linear (yes) | linear (no) |
| HSD | cl | r16920 | 612 | 514.296 | linear (yes) | linear (no) |
| HSD | cl | r16921 | 612 | 514.296 | linear (yes) | linear (no) |
| HSD | cl | r16922 | 727 | 523.359 | first_order (no) | linear (yes) |
| HSD | cl | r16923 | 728 | 523.36 | first_order (no) | linear (yes) |
| HSD | cl | r16924 | 728 | 523.36 | first_order (no) | linear (yes) |
| HSD | cl | r16925 | 758 | 520.089 | first_order (no) | linear (yes) |
| HSD | cl | r16926 | 757 | 520.088 | first_order (no) | linear (yes) |
| HSD | cl | r16927 | 757 | 520.083 | first_order (no) | linear (yes) |
| HSD | cl | r16928 | 301 | 5.94089 | - | - |
| HSD | cl | r16929 | 301 | 5.93989 | - | - |
| HSD | cl | r16930 | 301 | 5.94289 | - | - |
| HSD | cl | r16931 | 1322 | 0 | - | - |
| HSD | cl | r16932 | 1322 | 0 | - | - |
| HSD | cl | r16933 | 1322 | 0 | - | - |
| HSD | cl | r16934 | 1322 | 0 | - | - |
| HSD | cl | r16935 | 1322 | 0 | - | - |
| HSD | cl | r16936 | 1322 | 0 | - | - |
| MT | sv | b0 | 9709 | 0 | - | - |
| MT | sv | r90 | 758 | 514.467 | first_order (no) | linear (no) |
| MT | sv | r16901 | 758 | 514.467 | first_order (no) | linear (no) |
| MT | sv | r16902 | 757 | 514.467 | first_order (no) | linear (no) |
| MT | sv | r16903 | 758 | 514.467 | first_order (no) | linear (no) |
| MT | sv | r16904 | 991 | 817.381 | linear (no) | linear (no) |
| MT | sv | r16905 | 992 | 817.381 | linear (no) | linear (no) |
| MT | sv | r16906 | 991 | 817.369 | linear (no) | linear (no) |
| MT | sv | r16907 | 758 | 520.813 | first_order (no) | friction (no) |
| MT | sv | r16908 | 757 | 520.814 | first_order (no) | friction (no) |
| MT | sv | r16909 | 758 | 520.814 | first_order (no) | friction (no) |
| MT | sv | r16910 | 990 | 832.035 | linear (no) | linear (no) |
| MT | sv | r16911 | 992 | 832.036 | linear (no) | linear (no) |
| MT | sv | r16912 | 991 | 832.037 | linear (no) | linear (no) |
| MT | sv | r16913 | 757 | 539.507 | first_order (no) | friction (yes) |
| MT | sv | r16914 | 705 | 539.492 | first_order (no) | friction (no) |
| MT | sv | r16915 | 733 | 539.452 | linear (no) | friction (no) |
| MT | sv | r16916 | 992 | 813.842 | linear (no) | friction (no) |
| MT | sv | r16917 | 986 | 813.845 | linear (no) | friction (no) |
| MT | sv | r16918 | 991 | 813.846 | linear (no) | friction (no) |
| MT | sv | r16919 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | sv | r16920 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | sv | r16921 | 612 | 514.296 | linear (no) | linear (yes) |
| MT | sv | r16922 | 727 | 523.359 | first_order (no) | linear (yes) |
| MT | sv | r16923 | 728 | 523.36 | first_order (no) | linear (yes) |
| MT | sv | r16924 | 728 | 523.36 | first_order (no) | linear (yes) |
| MT | sv | r16925 | 757 | 520.089 | first_order (no) | linear (yes) |
| MT | sv | r16926 | 757 | 520.088 | first_order (no) | linear (yes) |
| MT | sv | r16927 | 757 | 520.083 | first_order (no) | linear (yes) |
| MT | sv | r16928 | 301 | 5.94089 | - | - |
| MT | sv | r16929 | 301 | 5.93989 | - | - |
| MT | sv | r16930 | 301 | 5.94289 | - | - |
| MT | sv | r16931 | 1322 | 0 | - | - |
| MT | sv | r16932 | 1322 | 0 | - | - |
| MT | sv | r16933 | 1326 | 0 | - | - |
| MT | sv | r16934 | 1322 | 0 | - | - |
| MT | sv | r16935 | 1322 | 0 | - | - |
| MT | sv | r16936 | 1322 | 0 | - | - |

Events: 295. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
