# M5.5 grapple range: Unity's 850 u, and what R5 actually does

Question from the user: the Unity grapple has a range of 850 u. Where does that number come from, and has it been verified?
Do not treat a config value as a full measurement.

## 1. Where 850 comes from (config, not a measurement)

- **R5 weapon settings:** `mp_ability_grapple.txt` lines 49–50 set `"grapple_maxLength" "850"` and
  `"grapple_maxLengthVert" "850"`. The file is the same in the pinned source clone (`s21-platform@9b21dc9`) and in the
  installed game (`platform/scripts/weapons/`, after line-ending normalisation).
- **Unity:** `GrappleAbility.range = 850` copies that setting. Its doc comment already said "not exercised".
- **M4/M4b data:** the longest measured hook was 705 u (104 hooks), so the range limit was never reached.

## 2. Finding: every M4/M4b grapple trial ran with a doubled range

- `DevAbilities_RefillWeapon` (`_weapon_utility.nut:3810-3841`) always calls `DevAbilities_ApplyGrappleRange(weapon, true)`
  for a grapple weapon. That function adds the mod `infinite_abilities_grapple`, which sets `grapple_maxLength` and
  `grapple_maxLengthVert` to ×2 (`mp_ability_grapple.txt:136-141`).
- The runner's `--kit` refill (`DevAbilities_RefillPlayer`) therefore put this mod on the grapple in every M4/M4b trial.
  `ABILITY-TRIGGERS.md` warned only about the cheat `infinite_abilities`; the refill path was missed.
- **The mod changes only the two range values** (it is the whole mod block).
- **Impact on M4/M4b results: none found.**
  - Every M4/M4b hook was at most 705 u, below even the normal range.
  - Control `m55_nomod_hold` (mod removed after the refill; the reset log confirms `grapple_mod=false`) against the M4
    `m4_grapple_hold` trials, aligned on the hop:

    | | Speed 40 commands later (u/s) | Speed 80 commands later (u/s) |
    |---|---|---|
    | With mod | 112.5 / 116.4–116.9 | 280.5 / 284.7–285.2 |
    | Without mod | 112.4–112.6 / 116.7–116.8 / 122.7 | 281.2–283.5 / 285.0–285.1 / 291.8 |

    The values fall in the same set; the one high trial (r2773) hopped 4 commands earlier, which is timing, not dynamics.
    The pull law (RF) is unaffected. Data: `grapple_mod_pull_compare_output.txt`.
- **Runner fix:** schedules with the prefix `m55_nomod` remove the mod after the refill. Any future grapple experiment
  should do the same.

## 3. Measured range (pitch 0, straight at the test wall face x −13706, 120 fps, Pathfinder)

Attach = the grapple hop, a pre-command vz of 200 u/s. `d` = horizontal distance from the start to the face, which at
pitch 0 is also the aim distance.

| d (u) | Mod present (as in M4) | Mod removed (normal game) |
|---|---|---|
| 800 | 5/5 | 3/3 |
| 810 / 820 / 830 | – | 3/3 each |
| 840 | 5/5 | **0/3** |
| 860 / 900 | 5/5 each | 0/3 each |
| 950 … 1200 | 3/3 each (the player stops short of the wall from 1000 u on) | – |

- **Effective range, normal game: 830–840 u** from the start position at pitch 0. That is 10–20 u short of the configured 850.
  The likely reason is where the trace starts and the hook's size; this was not separated.
- **Out of range:** no hop and no pull. Nothing happens to the player's movement.
- **Hook flight time** matches the M4 model t = 0.004 + L / 2035 u/s to within one command, up to 1200 u.
- **Not measured:**
  - the vertical limit `maxLengthVert` (only pitch 0 was tested);
  - the exact behaviour of a miss (hook visuals, cooldown spent or not);
  - why the player stops short beyond 1000 u with the mod.

## 4. Consequence for Unity

- **Keep `range = 850` as a design setting**, now labelled as "R5 config; measured effective range 830–840 u at pitch 0".
- **Range check:** the aim ray is measured from origin + 60. The gap to the measured value is small enough that 850 stays
  the game setting.
- **Show it in the game:** the M5.5 grapple visuals show the range and an out-of-range state.
  - **Out of range:** no attach, no movement.
  - **Charge:** Unity keeps its own rule. That a miss spends no charge is a design rule, since R5 was not measured.

Rerun:

- `py -3 grapple_range_check.py <session>` for `../data/20261021_110539_M55_grapple_range`,
  `../data/20261021_110904_M55_grapple_range2`, `../data/20261021_111248_M55_grapple_nomod` and
  `../data/20261021_111609_M55_grapple_nomod2`.
- `py -3 grapple_mod_pull_compare.py ../data/20261021_003330_M4_pathfinder ../data/20261021_111609_M55_grapple_nomod2`
