#!/bin/sh
# usage: run.sh cmds.txt out.c
export GHIDRA_HEADLESS_MAXMEM=16G
D="${SCRIPT_DIR:?set SCRIPT_DIR}"
analyzeHeadless "${GHIDRA_PROJECTS:?set GHIDRA_PROJECTS}" r5apex_dx12 -process r5apex_dx12.exe -noanalysis -readOnly -scriptPath "$D" -postScript Probe.java "$D/$1" "$D/$2" < /dev/null > "$D/$2.log" 2>&1
tail -3 "$D/$2.log"
