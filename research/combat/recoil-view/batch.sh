#!/usr/bin/env bash
# All recoil cases: R-301, Spitfire, Wingman, P2020, hip and ADS. Marks go to $1.
M="$1"; cd "$(cd "$(dirname "$0")" && pwd)" || exit 1
run() { timeout 90 py -3 -I recoil_run.py "$M" "$@" 2>&1 | tail -1; }
ADS="down zoom; wait 0.8;"; ENDA="up zoom;"
for rep in 1 2 3; do
  for g in r301:mp_weapon_rspn101 spit:mp_weapon_lmg; do
    t=${g%%:*}; w=${g##*:}
    run ${t}_hip_tap_$rep  $w "wait 0.5; tap attack; wait 2.5" secs=12
    run ${t}_hip_b03_$rep  $w "wait 0.5; hold attack 0.3; wait 2.5" secs=12
    run ${t}_hip_b08_$rep  $w "wait 0.5; hold attack 0.8; wait 3" secs=12
    run ${t}_hip_b15_$rep  $w "wait 0.5; hold attack 1.5; wait 3.5" secs=12
    run ${t}_ads_tap_$rep  $w "$ADS tap attack; wait 2; $ENDA wait 0.5" secs=12
    run ${t}_ads_b03_$rep  $w "$ADS hold attack 0.3; wait 2; $ENDA wait 0.5" secs=12
    run ${t}_ads_b08_$rep  $w "$ADS hold attack 0.8; wait 2; $ENDA wait 0.5" secs=12
    run ${t}_ads_b15_$rep  $w "$ADS hold attack 1.5; wait 2; $ENDA wait 0.5" secs=12
  done
  for g in wing:mp_weapon_wingman p20:mp_weapon_semipistol; do
    t=${g%%:*}; w=${g##*:}
    run ${t}_hip_tap_$rep  $w "wait 0.5; tap attack; wait 2; tap attack; wait 2" secs=12
    run ${t}_hip_tri_$rep  $w "wait 0.5; tap attack; wait 0.5; tap attack; wait 0.5; tap attack; wait 2.5" secs=12
    run ${t}_ads_tap_$rep  $w "$ADS tap attack; wait 2; tap attack; wait 2; $ENDA wait 0.5" secs=12
    run ${t}_ads_tri_$rep  $w "$ADS tap attack; wait 0.5; tap attack; wait 0.5; tap attack; wait 2.5; $ENDA wait 0.5" secs=12
  done
done
# Pattern restart: a burst, a gap, one more shot.
for gap in 0.05 0.1 0.15 0.2 0.3 0.5 0.8; do
  run r301_gap${gap}  mp_weapon_rspn101 "wait 0.5; hold attack 0.8; wait $gap; tap attack; wait 1.5" secs=8
  run spit_gap${gap}  mp_weapon_lmg "wait 0.5; hold attack 0.8; wait $gap; tap attack; wait 1.5" secs=8
done

# Rounds against the view: dummie at 150 u, ADS (no spread), aim re-snapped each frame so only the punch moves the rounds.
T="target=body dist=150 snap=1 secs=10"
for rep in 1 2 3 4; do
  run r301_bul_$rep  mp_weapon_rspn101 "$ADS hold attack 0.8; wait 1; $ENDA wait 0.3" $T
  run spit_bul_$rep  mp_weapon_lmg "$ADS hold attack 1.0; wait 1; $ENDA wait 0.3" $T
  run wing_bul_$rep  mp_weapon_wingman "$ADS tap attack; wait 0.35; tap attack; wait 0.35; tap attack; wait 0.35; tap attack; wait 1; $ENDA wait 0.3" $T
  run p20_bul_$rep   mp_weapon_semipistol "$ADS tap attack; wait 0.1; tap attack; wait 0.1; tap attack; wait 0.1; tap attack; wait 0.1; tap attack; wait 1; $ENDA wait 0.3" $T
done
echo BATCH_DONE
