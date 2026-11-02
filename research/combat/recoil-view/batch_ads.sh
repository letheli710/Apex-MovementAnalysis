#!/usr/bin/env bash
# ADS in and out: R-301, Wingman, Spitfire, no shots. 4 full runs each, then interrupted runs. Marks go to $1.
M="$1"; cd "$(cd "$(dirname "$0")" && pwd)" || exit 1
run() { timeout 60 py -3 -I ads_run.py "$M" "$@" secs=4 2>&1 | tail -1 | cut -c1-120; }
for rep in 1 2 3 4; do
  run r301_full_$rep mp_weapon_rspn101 ADS_CENTER_SIGHT_R301 "wait 0.5; down zoom; wait 1.2; up zoom; wait 1"
  run wing_full_$rep mp_weapon_wingman ADS_CENTER_SIGHT_WINGMAN "wait 0.5; down zoom; wait 1.2; up zoom; wait 1"
  run spit_full_$rep mp_weapon_lmg ADS_CENTER_SIGHT_SPITFIRE "wait 0.5; down zoom; wait 1.2; up zoom; wait 1"
done
for rep in 1 2; do
  run r301_cut_$rep mp_weapon_rspn101 ADS_CENTER_SIGHT_R301 "wait 0.5; down zoom; wait 0.12; up zoom; wait 0.05; down zoom; wait 0.6; up zoom; wait 1"
  run spit_cut_$rep mp_weapon_lmg ADS_CENTER_SIGHT_SPITFIRE "wait 0.5; down zoom; wait 0.15; up zoom; wait 0.05; down zoom; wait 0.6; up zoom; wait 1"
done
echo BATCH_DONE
