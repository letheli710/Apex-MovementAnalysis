# M4 P3: teleport and phase transitions (transitions only)

Plan scope: Wraith, Ash and Loba, transitions only. Question: is speed kept across a teleport, and is there a stun or
control lock? All numbers come from the dedi MOVE-TRACE, which is authoritative.

- Script: `p3_analysis.py`. Output in `analysis_output.txt` and `results.json`.
- Rerun:
  `py -3 p3_analysis.py --wraith ../../data/20261021_031128_M4_wraith ../../data/20261021_032958_M4_wraith2 --loba ../../data/20261021_031416_M4_loba --json results.json > analysis_output.txt`
- Setup: 120 fps, kit equipped (`--kit`). Start at (-14900, 6650, 294.92), the longest clear lane in `m3/map/field_fine.json`.

## Wraith, Into the Void (tactical)

Data: `m4_wraith_void` n = 7 (session 1: 4/6 valid; top-up: 3/3); control `m4_wraith_ctrl` n = 5. Sprint starts, and the
tactical is pressed after 0.5 s.

| Phase | Measured (n = 7) |
|---|---|
| Deploy | msc 0.80 for 140–141 commands (1.17 s). Sprint drops from 254 to about 155 u/s. |
| Boost | msc 1.5961 = 1.388 × 1.15, constant for 323–336 commands (2.77 s). Sprint speed 414.98 = 260 × msc. |
| Fade | Back to 1.15 over 94–96 commands (0.79 s). |
| Control | Sprint cap 299.0 = 260 × 1.15. |

So the phase is a pure movescale modifier. It drops into the M4 `StimAbility` speed-multiplier primitive with different
numbers: a deploy slow of 0.8 for 1.17 s, ×1.388 for 2.77 s, then a 0.79 s fade. The 260·msc sprint cap matches the pad
re-jump cap (`m4b/pad_rejump`).

## Loba, Translocation (tactical)

Data: `m4_loba_tele` (sprinting throw, 4/6 valid) and `m4_loba_tele_still` (standing throw, 6/6 valid). A single tap
throws the bracelet at pitch −15.

- **Teleport happened in 6 of 10 valid trials.** In the other 4 the bracelet never produced a teleport within 3 s.
- **Range:** the 6 teleports jumped 2600–3900 u, landing on lower terrain off the test field. The throw is far longer than
  the field.
- **Speed is not kept.** Speed after the teleport is 0.0–5.5 u/s. In the one trial with forward held, speed dropped from
  248.5 to 23.9, which is one command of acceleration from rest.
- **No control lock.** With forward held, speed rises again from the first or second command.

This matches the server script: `TeleportPlayerNoInterp` plus velocity set to zero
(`loba_tactical_translocation.nut:1103-1114`, see `../ABILITY-TRIGGERS.md`).

**Limit:** landing spot and throw arc were not studied. They depend on terrain and are not a movement primitive.

## Wraith Portal, Ash Phase Breach, Vantage (from source, not measured)

- **Wraith Portal / Ash Phase Breach.**
  - They are server-scripted path replays: prediction disabled, controls frozen, `SetVelocity(node.velocity)` at exit. The
    breach travels at 1200 u/s.
  - The client trace is not physics truth here, so a measurement would only confirm "exit velocity = recorded node velocity".
  - Unity version: an "instant impulse / replace velocity" primitive at exit, plus a control-lock duration.
- **Ash passive dash.** Not measured: the setfile mod values are unknown, and the plan lists only teleports for Ash.
- **Vantage (P2, "as needed").** Not measured. On the dedi its Echo jet-drive is an SDK reimplementation (`jetdrive.cpp`),
  not original S21 code. The motion pattern (thrust toward a target, plus an optional double jump) is already covered by
  the jets and impulse primitives.

## Design reading

- Teleports either zero velocity (Loba) or impose a fixed exit velocity under a control lock (Portal, Breach).
- None of them carries speed across.
- For HSD, "keeps speed through a teleport" would therefore be an original design choice, not Apex behaviour.
