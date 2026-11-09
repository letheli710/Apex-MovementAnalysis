#!/bin/sh
# usage: dig.sh <out name> <cmd>...   (writes <workspace>/TF2-Research/local/ai-live/<out name>.txt)
# Set HSD_WS to the workspace root (Windows form, e.g. D:\work\ReApex-DataAnalysis) and GHIDRA to the
# Ghidra 12.1.4 install. The local copy used on 11-08 had both paths written in; see HSD-RawData.
W="${HSD_WS:?set HSD_WS to the workspace root}"
G="${GHIDRA:?set GHIDRA to the Ghidra install dir}"
out="$1"; shift
GHIDRA_HEADLESS_MAXMEM=16G MAXMEM=16G "$G/support/analyzeHeadless.bat" "$W\\ghidra-projects\\tf2" tf2 -process server.dll -noanalysis -readOnly \
  -scriptPath "$W\\TF2-Research\\pve\\live\\ghidra" -postScript AiDig.java "$W/TF2-Research/local/ai-live/$out.txt" "$@" \
  > "$out.stdout.txt" 2>&1
tail -2 "$out.stdout.txt"
