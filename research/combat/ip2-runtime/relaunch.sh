#!/usr/bin/env bash
# Restart dedi + client (bounded) and wait until both VMs answer. PY = a python 3 interpreter.
PY="${PY:-python}"
cd "$(cd "$(dirname "$0")" && pwd)/../w2-runtime" || exit 1
(timeout 900 powershell.exe -NoProfile -ExecutionPolicy Bypass -File ../../phase2-local/tools/hsd_launch.ps1 > /dev/null 2>&1 &)
sleep 20
for i in $(seq 1 80); do
  r=$(timeout 20 "$PY" -I ping.py 2>&1 | grep -c "'ran': True")
  [ "$r" = "2" ] && { echo "up after $((i * 8)) s"; sleep 15; exit 0; }
  sleep 8
done
echo "NOT up"; exit 1
