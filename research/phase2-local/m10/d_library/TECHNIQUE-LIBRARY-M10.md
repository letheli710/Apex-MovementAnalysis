# M10 track D: technique library extension (Pathfinder grapple, Zipline Gun, Octane, Wraith, E2 candidates)

Desk research only: no game, no Unity. Date 2026-10-22. Branch `m10/plan`. This file **extends** `../../m9/d_library/TECHNIQUE-LIBRARY.md` (M9-D). It keeps M9-D's format, evidence levels and version rule, and does not repeat M9-D entries (lurch, TS, SG, zipline riding, pounce, Echo). Section numbers continue from M9-D (§3.21 onward) so the two files can be read as one library.

## 0. Method, honesty rules and evidence levels

**What I could read**
- **Apex Movement Wiki (apexmovement.tech).** I reused the M9-D extraction: the markdown page sources bundled in the site's JS chunks (`/_app/immutable/chunks/*.js`, 101 pages, extracted 2026-10-22). Pages read in full for this file: Pathfinder fundamental Grapple Tech, Pathfinder advanced Grapple Tech, Pathfinder Zipline Tech, Zipline basics, Octane Stim, Octane Jump Pad basics, Octane additional Jump Pad Tech, Octane advanced Direction Changes, Wraith Phase Tech, Wraith Portal Tech, Mad Maggie Wrecking Ball, Mad Maggie Passive, Newcastle Castle push, Generic Legend Tech (speed boosts), Removed Legend Tech, Legend Mysteries, Velocities and Timings. They are the **current (Oct 2026) wiki**. I cite them by their wiki URL path.
- **YouTube.** I read **titles, channels, publish dates and descriptions**, including the chapter timestamps that authors wrote. **Transcripts are still unreadable:** I retried the timedtext endpoint this session and it returned an empty body. **I watched no video.** Anything I say about a video comes from its title, its description or the author's own chapter names.
- **Official text:** EA patch notes for Upheaval (S21, page dated 6 May 2024) and Breakout (S20, page dated 12 Feb 2024), read through WebFetch.
- **apexlegends.wiki.gg:** curl is blocked, so I read the Pathfinder and Wraith pages (raw wikitext) through WebFetch, which returns a model summary. Its version-history lists are used for dates only; numbers from it are marked as summary-level.
- **Local source (read-only):** `C:\Workspace\Playground\ReApex-DataAnalysis\research-src\s21-platform\scripts\vscripts\...` and `...\scripts\weapons\*.txt` (S21-era scripts and weapon files), plus `...\research-src\s21-r5sdk\src\...` (the R5 SDK bridge). **These files contain post-S21 content** (Axle, Sparrow, the Jan-2026 stim delay, and so on), so every value below is checked against a dated source before I call it S21.
- **Blocked:** Reddit, Discord, ginx.tv (403), and the wiki.gg raw endpoint through curl.

**Evidence levels** (the same as M9-D)
- **A**: a source I read in text states the inputs and their order explicitly.
- **B**: described in text, but the inputs are incomplete or ambiguous.
- **C**: a name, a video title or a chapter timestamp only.
- **measured**: matches an HSD R5 measurement (file and number cited).
- **contradicted**: conflicts with an HSD R5 measurement.
- **[src]**: S21-era script, weapon file or SDK constant read locally.
- **[inf]**: my own inference from the texts and measurements. It is a hypothesis to test, not a fact.

**Version rule (unchanged).** S21 = 7 May – 6 Aug 2024. A technique is **S21-present** only if a source dates it before S21 and nothing removes it before then. Wiki numbers are current-game numbers unless an HSD measurement or a dated source agrees.

**Local files cited** (under `research/phase2-local/`):

| Short name | File |
|---|---|
| M4-LG | `m4/lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md` |
| SWING | `m4b/swing/SWING.md` |
| GZ | `m6/a3_zip/GRAPPLE-ZIP.md` |
| A3 | `m6/a3_zip/A3-ZIPLINE.md` |
| OCT | `m4/octane/OCTANE-PRIMITIVES.md` |
| RD1 | `m9/r_d1/D1.md` |
| P3 | `m4/p3_transitions/P3-TRANSITIONS.md` |
| D2 | `m9/D2-CANDIDATES.md` |
| LIB9 | `m9/d_library/TECHNIQUE-LIBRARY.md` |

Script paths are relative to `research-src/s21-platform/scripts/`: **P:** = `vscripts/`, **W:** = `weapons/`.

## 1. Top findings

1. **The wiki points to a probable detach rule for the grapple, which three R5 rounds missed: look away from the anchor.** Four separate wiki entries say or imply it.
   - Momentum carry: sometimes you have to look away from the anchor before it lets go.
   - Grapple hop: if you aim further forward, you look up afterwards to make it disconnect.
   - Rodeo: you keep looking at the anchor for the whole orbit.
   - Double-Bounce: turning away is ruled out there only because you must face the wall.

   The wiki also states two other rules:
   - The grapple disconnects when you pass the anchor (Slingshot, Drag Grapple).
   - It disconnects manually with **Crouch** or **Tactical**. Tactical is measured (GZ §1); Crouch is untested.

   SWING's turn trials turned only 54° and never released. A view–rope angle threshold, together with a passed-the-anchor rule and a near-surface trace, is the first candidate to test (spec G-3) [inf].
2. **The Slingshot and RF model need not conflict.** SWING measured two things:
   - with W held, the pull clamps only **v·ŵ** (the speed along the flat view) at 483;
   - v_h reached 609 when the view was off the rope.

   The wiki Slingshot is the same scheme as an air strafe. Turn the view 80° off, hold a diagonal (W+A), and swap the diagonal halfway through the pull. A clamp on the speed along the view lets the speed across the view grow freely, which is how air strafing gains speed. So RF plus the measured W rule probably produces Slingshot-like gains without a new swing state [inf]. Two things are still untested: the response to the A/D keys during a pull, and the 850 u maximum-range, 45° geometry (spec G-1). The wiki's figure of about 1200 (Slingshot page) and 1300 (Velocities, peak) are current-game numbers.
3. **The S21 grapple script and the weapon file give hard limits** [src]:
   - `grapple_maxLength` 850 and `grapple_maxLengthVert` 850 (≈ 21.6 m; the wiki says 21 m).
   - The cooldown is drained by distance: base cost 100 + up to 300 by distance traveled over 300–4500 u, out of a 300-unit clip refilling at 10/s. That gives **10 s minimum and 30 s maximum** (30 s reached at about 3100 u).
   - The drain is tracked while the grapple is active **or** speed > 500, for at most **5 s**, and the tracking stops on a zipline mount.

   This matches the wiki.gg history: distance-based 10–35 s from Oct 2020, max 30 s and a 5 s travel cap from Nov 2020, flat 30 s only from Jan 2025. **S21 = 1 charge, 10–30 s by distance.** The second charge (23 Jun 2026) and Landing Gear (S29) are post-S21.
   - The SDK's `GrappleData` carries `m_grapplePoints[4]` (the rope can wrap up to 4 points), `m_grappleSwinging`, `m_grappleRetracting`, `m_grappleSwingDetachLowSpeed` and `m_grappleSwingHoldTime`. So the native grapple has **swing, retract and rope-wrap states** that our RF fit (straight pulls only) never exercised. These states are the native basis for Super Grapple (connect while retracting) and pillar wrap/Rodeo [src + inf].
4. **Zipline Gun S21 rules are mostly in script** [src], and they explain a known wiki fact:
   - Range 700–8000 u (about 18–203 m; the +60 % range of Feb 2023 is included).
   - Projectile speed 2600 u/s with no gravity; snap distance 250, snap angle 10°.
   - Firing requires being **on the ground, wallrunning or wall-hanging**.
   - 3 s refund window; auto-detach 100 u from the ends; at most 10 of one player's ropes in the world; cooldown clip 180 at 1/s, so **180 s**.
   - A rope steeper than |dir.z| > 0.7 (about 44.4°) is created with `ZiplineVertical` and `ZiplinePreserveVelocity`. This is the script cause of the wiki's 45° Ziplines entry: they keep more speed (an 800 exit instead of 600) and allow a jump-off in any direction.
   - Gun-rope ride speed: wiki 1000 u/s, consistent with "+66 %" (Feb 2023) on 600. It is not set in the script, so it must be measured.
5. **Octane S21 upgrades are now pinned by the official S21 notes** (EA, 6 May 2024):
   - Level 2: **Mad Hops** (extra Launch Pad charge) or **Thick Skin** (5 less Stim damage).
   - Level 3: **Airborne Agility** (change direction with the pad double jump) or **Thick Skin** again.

   The script agrees on each part:
   - two −5 health-cost passives;
   - `upgrade_ult_one` gives a 180 clip, i.e. 2 pads;
   - `PAS_ULT_UPGRADE_THREE` selects the UPGRADED pad skin, which grants `enable_doublejump_aircontrol`.

   **Not S21:** Triple Jump, Squad Rush, Stim Surge/Daredevil, the base 2 charges, the base direction change, and removing the pad activation delay. All arrived on 6 Jan 2026.
   - **Open:** `JumpPad_GetPushVelocity` multiplies by **1.2** when the owner has `PAS_ULT_UPGRADE_ONE`. No dated source names a +20 % launch upgrade, and I could not establish which upgrade grants that passive. Treat ×1.2 as **[src, version unknown]**: do not put it in the S21 Reference until R5 shows whether Mad Hops also raises the push.
6. **Ceiling surf has a usable mechanism hypothesis and a cheap decisive test.** The wiki says:
   - you ride along the ceiling until the upward momentum is used up or the ceiling ends;
   - the duration appears to depend on the ceiling height above the pad;
   - leftover potential throws you upward when the roof ends;
   - the potential survives a zipline interaction;
   - it works better crouched, and Forward helps.

   All of this fits one rule: **the pad's vertical velocity is not zeroed by the ceiling contact and keeps decaying under the (slow-mo) gravity while the player is pinned** [inf]. In R5 the stored vz is directly visible in MOVE-TRACE (vz > 0 with z constant). One trial settles it (spec O-6). The technique is dated before 12 Jan 2021 (Mokeysniper video, chapter 01:52), so it is S21-present.
7. **Pad launch direction probably follows the movement input at contact, not the approach velocity** [inf from wiki text]:
   - A melee lunge onto the pad without input goes straight up.
   - Back or side input after the melee launches backwards or sideways.
   - Arriving with very high speed can also send you straight up.
   - Straight up reaches 884–920 hu. The formula 1150²/(2·750) = 882 matches the 884 floor (OCT's slow-mo scales time, not height).

   OCT left ĥ undetermined. Spec O-3 settles it.
8. **The wiki's Tap strafe off Pad is consistent with the D3 decision.** RD1 measured that the pad launch itself opens **no** lurch window. The wiki technique is an ordinary flat-ground 180° tap strafe, i.e. one that starts from a jump *before* the pad, timed progressively later until it happens at contact. If it works in S21, the most likely reason is that the earlier jump's lurch window survives the pad relaunch, as it survives zipline mounts and mantles (LIB9 §3.1) [inf]. This is spec O-5, a cheap R test. It does **not** re-open `pad_lurch` in the Reference.
9. **Wraith S21 rules are clear, and our M4 phase numbers match the wiki:**
   - Into the Void: 1.25 s activation, 4 s duration, +30 % speed. The cooldown was 25 s (20 s with the Level 3 upgrade, moved on 26 Mar 2024).
   - R5 measured sprint 414.98 (P3); the wiki speed-boost table gives 414 for phase.
   - Dimensional Rift in S21: max 6000 u (152 m), lifetime 45 s, path replay at 1024 u/s clamped to 0.3–2.0 s (Wraith: up to 3.5 s beyond 3000 u), exit velocity = the recorded node velocity, base speed boost severity 0.2 rising +0.1 per 20 % of max distance [src]. The ramp was compressed on 25 Mar 2025, so the S21 ramp is the 2023 one: 22 % → 39 % → 57 % → 74 % at 0/60/90/120 m.
10. **Correction to D2:** Mad Maggie's Wrecking Ball **speed pads are original S12 kit** (wiki: Maggie added 8 Feb 2022; the pads are her ultimate's core). D2 called the pads a post-S26.1 change. The post-S21 changes are the 6 s per-pad re-activation (S26.1, 16 Sep 2025) and sprint-only (23 Jun 2026). S21 script: speed severity **0.15 while inside an 88 u trigger, then 2 s after leaving** (0.25 s fade), pads lasting 60 s [src]. By the M4 stim formula that is about ×1.30 (byte-quantised 0.149 → ×1.298) [inf].

## 2. Source register (sources read for this file; date = publish date)

**Web text**

| Id | Source | Author | Date | What I read |
|---|---|---|---|---|
| W-GrF | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EPathfinder%3EFundamental%20Grapple%20Tech%3EBasic%20Grapple%20Tech%20page (Grapple basics, Jump Grapple, Drag Grapple, Slingshot, Grapple hop, Momentum carry, Slide Grapple, Landing Gear) | wiki (Mokeysniper voice) | live | full text |
| W-GrA | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EPathfinder%3EAdvanced%20Grapple%20Tech%3EAdvanced%20Grapple%20Tech%20page (Super Grapple, Rodeo, Grapple Bounce, Double-Bounce, Infinite Grapple climb, Grapple scrape) | wiki | live | full text |
| W-PZ | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EPathfinder%3EZipline%3EZipline%20article (Momentum carry exit, 45° Ziplines) | wiki | live | full text |
| W-ZipB | Zipline basics (max speeds, connecting) | wiki | live | full text |
| W-Stim | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EOctane%3EStim%3EStim%20article | wiki | live | full text |
| W-Pad | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EOctane%3EJump%20Pad%20basics%3EJump%20Pad%20basics (basics, 2nd pad, double jump, triple jump, Squad Rush, Ceiling surf) | wiki | live | full text |
| W-Pad2 | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EOctane%3EAdditional%20Jump%20Pad%20Tech%3EAdditional%20Jump%20Pad%20Tech (Jump Pad wallrunning, Shallow Pad, Mantle double jump) | wiki | live | full text |
| W-PadDir | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EOctane%3EAdvanced%20Direction%20Changes%3EAdvanced%20Direction%20Changes (Melee pad, TS off pad, Flick strafe) | wiki | live | full text |
| W-Phase | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EWraith%3EPhase%3EPhase%20Tech | wiki | live | full text |
| W-Portal | Wraith Portal Tech (Portal speed manipulation, Portal glide, oddities) | wiki | live | full text |
| W-Gen | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EGeneric%3EGeneric%20Legend%20Tech%20article (speed boosts and tables) | wiki; strafe tables by Chaosmonkey | live | full text |
| W-Mag | Mad Maggie Wrecking Ball page (Speed pads, Ball explosion boost) | wiki | live | full text |
| W-NC | Newcastle Castle push page | wiki | live | full text (its History section is truncated in the source) |
| W-RemL | Removed Legend Tech (Slide-through TS, Pad dash, Grapple Hyper jump, Zip dash, Bat bending …) | wiki | live | full text |
| W-Vel | Velocities collected in one place | Mokeysniper | 8 Jun 2025 | full text |
| EA-S21 | https://www.ea.com/games/apex-legends/apex-legends/news/upheaval-patch-notes | EA/Respawn | 6 May 2024 | Octane, Wraith, Newcastle, Maggie sections |
| EA-S20 | https://www.ea.com/games/apex-legends/apex-legends/news/breakout-patch-notes | EA/Respawn | 12 Feb 2024 | legend sections (no upgrade lists on that page) |
| WG-Path | https://apexlegends.wiki.gg/wiki/Pathfinder (raw, through a model summary) | wiki.gg editors | live | grapple and Zipline Gun version history |
| WG-Wr | https://apexlegends.wiki.gg/wiki/Wraith (raw, through a model summary) | wiki.gg editors | live | Void and Rift stats and history |

**Local source**

| Id | Source | What it gives |
|---|---|---|
| SRC-Gr | W:`mp_ability_grapple.txt`; P:`weapons/mp_ability_grapple.nut` lines 25–60, 227–380 | grapple length, power, clip and regen; distance-scaled drain; the 5 s cap |
| SRC-GrSDK | `s21-r5sdk/src/game/shared/r1/grapple.h`; `src/game/shared/s21_dt_schema.h` 3202–3223 | GrappleData fields (points[4], swinging, retracting, swing detach low speed / hold time) |
| SRC-Zg | W:`mp_weapon_zipline.txt`; P:`weapons/mp_weapon_zipline.nut` 22–37, 387–440, 600–700 | Zipline Gun range, snap, projectile, cooldown, station rules, steep flag |
| SRC-Stim | P:`weapons/mp_ability_octane_stim.nut`; P:`weapons/sh_stim.gnut` 9–100; W:`mp_ability_octane_stim.txt` | health cost 20 / −5 upgrades, 6 s, re-use block, mods |
| SRC-Pad | P:`mp/sh_jump_pads.gnut` 27–41, 140–150, 280–350, 757–860; W:`mp_weapon_jump_pad.txt` | push 1150, V 2.0, ×1.2 passive, UPGRADED skin → air-control double jump, Mad Hops clip 180 |
| SRC-PadSDK | `s21-r5sdk/src/game/server/jumppad_parity.cpp` header and lines 177–240, 717–733 | slow-mo until landing, relaunch debounce and ground reset |
| SRC-Void | P:`weapons/mp_ability_phase_walk.nut` 30–160; W:`mp_ability_phase_walk.txt` | deploy slow 0.2, speed severity 0.3, charge 4.0 (mixed version) |
| SRC-Rift | P:`weapons/mp_weapon_phase_tunnel.nut` 73–106, 252–258, 495–510, 1500–1530, 2085–2185 | portal distance, travel, speed ramp, exit velocity |
| SRC-Mag | P:`weapons/mp_ability_wrecking_ball.nut` 29–50, 1405–1500 | speed pad trigger and buff |
| SRC-NC | P:`weapons/mp_ability_armored_leap.nut` 71–127 | leap distances, speeds, hover, interrupt keep 35 % |

**Video sources (description and chapters read; not watched)**

| Id | Video | Channel | Date | Author chapters (relevant) |
|---|---|---|---|---|
| V-MokGr | https://youtu.be/R7YOuYMohNY "The most INSANE Grapple and Zipline Tricks i learned from maining Pathfinder for 2 years." | Mokeysniper | 31 Jul 2021 | 01:50 Angled Ziplines; 03:03 Random Quicktips; 03:22 Zipline Tap-Strafe; 04:02 Grapple Hop; 04:41 Super Grapple; 06:00 Backwards Slide Grapple; 07:02 Stun Cancel; 07:10 B-Hop vs Slidehop; 07:28 Grapple Tap-Strafing; 08:14 Slingshots |
| V-MokSS | https://youtu.be/hB0Wa2fCVAk "The last Grapple Slingshot Tutorial you'll need" | Mokey | 16 Jul 2019 | 00:39 Step 1 air-strafe inputs; 01:19 Step 2 air strafing; 02:37 Step 3 grapple inputs; 03:37 Step 4 grappling; 04:44 Step 5 tilting the view line; 05:25 Step 6 braking the view line; 07:05 train with the grapple; 07:42 additional tips; 09:48 the last 10 % |
| V-MokSS7 | https://youtu.be/ANCAE6oR3Cc "7min of Satisfying Grapple Slingshots" | Mokey | 20 Oct 2019 | none |
| V-Froth | https://youtu.be/xU00WXvw2V0 "Titanfall 2 - How to Grapple like a PRO" | Frothy | 5 Feb 2017 | none (TF2 origin of the Slingshot) |
| V-Norse | https://youtu.be/mD9WF_xXLgc "Grapple Tutorial With Taltallon" | MikeTheNorseman | 16 Dec 2016 | none (TF2) |
| V-Kovah | https://youtu.be/DiB9vBvjgWE "New Movement Tech! Works With Controller/Console and KBM" (Grapple Double-Bounce, per the wiki) | Kovah | 2/3 Jul 2023 | none |
| V-Gruic | https://youtu.be/zfZ6wI1KEOo "The underrated Pathfinder grapple technique: Slide Grapple" | Gruic | 4 Apr 2022 | none (58 s) |
| V-Pesky | https://youtu.be/Uv1BmQvJrfM "How to SUPER Grapple like a PRO" | PeskyFrank | 28 Feb 2023 | none |
| V-Dirk | https://youtu.be/x70w21VYtew "Rodeo Grapple Control Mode Pathfinder" | DirkFade | 15 Jan 2023 | none (32 s) |
| V-BOOL | https://youtu.be/8CpQBWnzuo4 "\"Rodeo\" Grapple 2v1" | BOOL | 28 Aug 2021 | none (31 s) |
| V-Cau1 | https://youtu.be/mlj9SBY7qq8 "ADVANCED PATHFINDER TECH 2024 (with Tutorials)" | Cau7ioN | 20 Aug 2023 | none in description (683 s) |
| V-Cau2 | https://youtu.be/_CNefm7EmpA "HOW THE #1 PATHFINDER GRAPPLES IN APEX LEGENDS..." | Cau7ioN | 1 Oct 2023 | none |
| V-Cau3 | https://youtu.be/6X8_OXUuijE "THE TOUGHEST GRAPPLE IN APEX HISTORY! (99% FAIL)" | Cau7ioN | 18 Jun 2023 | none |
| V-Cau4 | https://youtu.be/p7mz1OE8OHs "PATHFINDERS GRAPPLE HAS BECOME STRONGER!" ("Pathfinder has become meta in Season 20!") | Cau7ioN | 15 Feb 2024 | none |
| V-MokOct | https://youtu.be/uka85Jx_-yY "Ridiculous Octane 2021 Movement Tech (Wallrunning, Ceiling Surfing, Instant Direction Change)" | Mokeysniper | 12 Jan 2021 | 01:52 Ceiling Surfing; 03:24 Wallrunning; 06:02 Instant Direction Change; 07:11 Tap-Strafing |
| V-MokPadDir | https://youtu.be/ZxDwH37uT24 "5 Pro Methods to INSTANTLY change JUMP-PAD DIRECTION !!" | Mokeysniper | 19 Jul 2021 | none (the wiki links t=15 for TS off pad and slide-through TS) |
| V-MokPadWR | https://youtu.be/BEVo2RTMkq8 "You can still Jump-Pad Wallrun in Season 10" | Mok3ysnip3r | 16 Aug 2021 | none (53 s) |
| V-MokSecret | https://youtu.be/Tf2zaMzqPfA "These Legends have SECRET MOVEMENT ABILITIES !!" | Mokeysniper | 20 Nov 2021 | none; links the ceiling-surf clip and the grapple hyper jump (wiki t=158) |
| V-MokOct19 | https://youtu.be/4rp_e6Ab4TI "OCTANE IS TRASH - Let's fix that" (the earliest melee-pad mention is in its comments, per the wiki) | Mokey | 11 Dec 2019 | none |
| V-Baner | https://youtu.be/3kYoyYOGjX0 "Octane Ceiling Surfing is Busted" | MrBaner | 8 May 2022 | none (29 s) |
| V-Stras | https://youtu.be/vm1brUdu_Uo "Octane pad ceiling surfing is my favorite" | strasner | 11 Jul 2021 | none (short) |
| V-Shm | https://youtu.be/Dz83OHYw_G8 "Controller 'Tap-Strafe' Tutorial-(Flick Strafe Tutorial)" | Shmellz (wiki credits Cryo) | 20 Apr 2021 | none |
| V-MokS16 | https://youtu.be/wIrGCO7VNkg "New Movement Tech in APEX SEASON 16 !!" | Mokeysniper | 18 Feb 2023 | 00:00 Wraith; 02:52 Pathfinder; 06:45 Horizon; 07:07 Vantage |
| V-MokZD | https://youtu.be/cG13set9FwA "ZIP-DASHING - The Movement Tech that's REVOLUTIONIZING Ziplines !!" | Mokeysniper | 21 Jul 2022 | 01:16 Zipline Super-Slides; 02:41 Slideless Zip-Dash; 04:05 Zip-E-Dash / Zippydash; 06:07 Zippydash interact tangent |
| V-Mok1 | https://youtu.be/iuI1Ux7gUB4 "1 MOVEMENT TRICK for EVERY LEGEND !!" | Mokeysniper | 30 Nov 2023 | 00:00 Assault; 01:51 Skirmisher; 06:50 Recon; 08:26 Support; 11:35 Controller |
| V-Gruic2 | https://youtu.be/evlOp_SBWiY "The most creative wraith portal trick" | Gruic | 14 Jun 2023 | none (73 s) |
| V-Faide | https://youtu.be/Z9OTtG9qEeI "The Secret Portal Tech" | Faide | 18 Jul 2025 (S25, **post-S21**) | none |
| V-bobz | https://youtu.be/gp4x4iihQKI "Newcastle Tactical Shield Movement Guide" | bobz | 12 May 2022 | none |

## 3. Technique library (continues LIB9 §3)

Format per entry: **Sources**, **Inputs (only as stated by the source)**, **Conditions / failures**, **Version**, **Evidence**.

### 3.21 Pathfinder grapple: S21 rule set (the base for §3.22–3.33)

**Script and SDK [src, SRC-Gr / SRC-GrSDK]**

| Item | S21-era value | Note |
|---|---|---|
| Max rope length | `grapple_maxLength` 850, `grapple_maxLengthVert` 850 | wiki "21 m"; the M4 far trial used 705 |
| Power | `grapple_power_required` 100, `grapple_power_use_rate` 0 | a press while `SuitGrapplePower` < 100 calls `Grapple(<0,0,1>)`; read with GZ §1 (a second tactical press releases, latency 0) |
| Cooldown | clip 300, regen 10/s; drain = 100 + int(300 · clamp((d − 300)/(4500 − 300))), capped at the clip | **10 s minimum, 30 s maximum** at d ≥ 3100 u. `pathfinder_grapple_drain_max_dist` defaults to 4500 in script (2800 in the file struct) |
| Drain tracking | while `IsGrappleActive()` **or** \|v\| > 500, ≤ 5 s, polled every 0.1 s; stops when you mount a zipline; ends on `JumpPad_GiveDoubleJump` | post-release flight above 500 u/s counts as distance |
| Native states | `m_grapplePoints[4]` + count, attached, pulling, **swinging**, **retracting**, forced retracting, grace period, `m_grappleSwingDetachLowSpeed`, `m_grappleSwingHoldTime`, `m_grappleHasGoodVelocity` | TF2-heritage grapple; rope wrap up to 4 points; a swing mode exists natively |
| Disallowed surfaces | impact tables `grapple_disallowed.txt`, `DT_TriggerNoGrapple`; phase-tunnel blockers use `CONTENTS_NOGRAPPLE` | |
| NPC detach | `CodeCallback_GrappleDetachFromNPC`: detaches from a prowler when \|v\| > 400 | |
| Upgrade mod in file | `upgrade_reduced_grapple_cooldown`: clip 200 (max 20 s) | S20/S21 upgrade lists for Pathfinder are not confirmed by any official text I read; S25 coverage says a grapple cooldown upgrade was replaced then. **Version unknown**; keep it out of Reference |

**R5 measured (M4-LG, SWING, GZ)**
- Attach time 0.004 + L/2035 s (hook ≈ 2035 u/s).
- 200 u/s vertical hop at attach, also in the air; 0.20 s wind-up.
- RF pull: along-rope ramp ≈ 495–541 u/s², tangential brake ≈ 420 u/s².
- W held: accelerate along the flat view, with v·ŵ clamped at 483.
- Momentum kept exactly at release.
- Jump does **not** release the grapple (pressed 0.6 s after fire).
- A second tactical press releases on the same command.
- Detach rule unidentified.

**Wiki rules (W-GrF / W-GrA; current text, but each rule is dated or older than S21 unless noted)**
- You steer with both movement keys and the view.
- The grapple only connects if you are more than 20 hu from the wall. Between 20 and 27 hu it connects and auto-disconnects.
- It disconnects as you pass the grapple point (Slingshot, Drag Grapple).
- Looking away disconnects (Momentum carry, Grapple hop).
- Crouch or Tactical disconnects manually (Grapple Bounce, Double-Bounce).
- The grapple resets climb space (the baseline is where it disconnected) and resets fall stun.
- The two grapple charges and the 5 s hidden cooldown after grappling interactables are **2026 kit** (second charge on 23 Jun 2026; WG-Path).
- **Version (WG-Path, summary):** 35 s (May 2020) → distance-based 10–35 s (6 Oct 2020) → max 30 s and a 5 s travel cap (4 Nov 2020) → flat 30 s (7 Jan 2025) → 10–30 s (6 May 2025) → 2 charges, flat 20 s (23 Jun 2026). Projectile speed −33 % (1 Oct 2019). **S21 = 1 charge, 10–30 s.** The S21 notes (EA-S21) list no Pathfinder change.
- **Evidence:** the constants are [src]. The pull model is measured. The wiki detach rules are **A as statements**, untested in R5 except Tactical (measured GZ §1) and the fact that Jump does not release (measured; the wiki never says Jump releases).

### 3.22 Jump Grapple (and coyote after attach)
- **Sources:** W-GrF (full text). It is TF2-era: Titanfall 2 released 28 Oct 2016, and the wiki credits no single discoverer.
- **Inputs (W-GrF):**
  1. Choose a point (the floor ahead is fine); max out the range.
  2. Press Tactical.
  3. Wait for the grapple to connect.
  4. Jump.

  Tips:
  - Grappling the ground lifts you slightly and keeps you airborne until the grapple point.
  - It activates coyote time, so jumping late is safer than jumping early; most failures are early jumps.
- **Combinations:** with the Slingshot inputs; landing in a slide.
- **Mechanism reading [inf]:** the measured 200 u/s attach hop takes the player off the ground. The ground coyote window (0.2 s, LIB9 §3.9) then allows a normal jump (+289.8) during the pull. M4-LG's jump was pressed at +0.6 s after fire, about 0.4 s after attach, which is outside a 0.2 s coyote window. So M4-LG did not test this technique.
- **Version:** S21-present.
- **Evidence:** **A** (order stated; no timing beyond after-connect, inside coyote). Not measured → spec G-2.

### 3.23 Drag Grapple
- **Sources:** W-GrF.
- **Inputs:** aim at the ground in front, max range; Tactical; let the pull drag you along the ground; Jump as you pass the grapple point.
- **Failure:** passing the grapple point disconnects the grapple, and ground friction then slows you down sharply. Use it as a backup for a late Jump Grapple. It combines with TS and Slide Grapple.
- **Version:** S21-present (fundamental; no date given).
- **Evidence:** **A**. The disconnect-on-passing rule is untested in R5 → G-3.

### 3.24 Slingshot
- **Sources:** W-GrF (full text); V-MokSS (C, 2019 tutorial, chapters); V-MokGr 08:14 (C); TF2 origin V-Norse (16 Dec 2016) and V-Froth (5 Feb 2017).
- **Inputs (W-GrF, quoted as steps):**
  1. Choose a point. For maximum range pick one about 45° above you, from as far away as the range indicator allows.
  2. Press Tactical; let it connect.
  3. Turn your view 80° left (mirror for right).
  4. Strafe 45° left: **Forward + Left**.
  5. As the pull carries you, turn the view right, so that you look forward as you pass the grapple point.
  6. Switch the strafe to the other side (Forward + Right) roughly halfway through the pull.
  7. The grapple disconnects by itself as you pass the anchor.
- **Tips:**
  - On controller it is one smooth half-circle; on MnK keep left a little longer, then swap both together.
  - Learn air strafing first.
  - 45° is steeper than people think, but max range matters more than the exact angle.
  - Jump only if the anchor is more than 45° up; below that, a jump shortens the Slingshot (the wiki says it slackens the rope).
  - Forward/back strafes are also usable.
  - Peak about 1200 hu/s (Velocities page: 1300, peak).
- **V-MokSS chapter titles** (Step 5 and Step 6, on tilting and braking the view line) describe the camera method. The content is not read.
- **Mechanism reading [inf]:**
  - SWING found that W accelerates along the flat view with a clamp on **v·ŵ** (483), not on |v|, and that v_h reached 560–609 with the view off the rope.
  - With the view 80° off and a diagonal wish, the clamped component is the one along the wish direction. The rope pull (+495 u/s² along the rope) keeps adding speed across that direction.
  - That is the air-strafe mechanism, so |v| can grow well past 483 without any pendulum term.
  - The wiki's 1200 at 850 u range and 45° is then a range-and-geometry question for R5. It is not evidence that RF is wrong.
  - **Untested parts:** the A/D response during a pull (SWING tested only W), the strafe swap, and a high (45°) anchor at maximum range.
- **Version:** TF2 (Dec 2016), present in Apex since launch; S21-present. The current peak figures are not S21-verified.
- **Evidence:** **A** (inputs and order explicit; timing only roughly halfway). The magnitude is **unverified** (SWING never ran this input; it is not a contradiction) → spec G-1.

### 3.25 Grapple hop
- **Sources:** W-GrF; V-MokGr 04:02 (C).
- **Inputs:** look down; Tactical; Jump as the hook connects to the ground, i.e. a very short moment after the tactical. The height should be clearly more than a normal jump; if not, the timing was off. If you aim further forward, look up afterwards to disconnect.
- **Version:** first days after launch (Feb 2019); the earliest clip found by the wiki is 17 Nov 2019. S21-present.
- **Mechanism reading [inf]:** the attach hop sets vz = 200 (measured). A jump on or right after that command adds the 289.8 jump, if Apex adds rather than overrides. Which applies decides the height → spec G-2b.
- **Evidence:** **A** (order; the delay is only described as very short). Not measured.

### 3.26 Momentum carry (air) and Momentum carry exit (zipline)
- **Sources:** W-GrF (Momentum carry); W-PZ (Momentum carry exit; first public post by Mokeysniper on 19 Nov 2022, linked on X).
- **Inputs:**
  - *Momentum carry:* have air momentum (Slingshot, pad, cannon); press Tactical at any geometry mid-air. Often you are fast enough for it to disconnect by itself; sometimes you must "look away from the grapplepoint again so its disconnects". Use: turn downward momentum into horizontal, prevent fall stun, gain distance.
  - *Exit:* ride a zipline, look straight down, press Tactical. It keeps full velocity, where a jump-off would cut you to 445 (the wiki's figure). It also works on ziprails and, less reliably, sideways.
- **Mechanism reading [inf]:** the measured 200 u/s attach hop and the RF tangential brake would remove downward speed, and the grapple is gone before the pull ramps. The "look away" detach supports a view-angle rule.
- **Version:** carry since launch; exit public Nov 2022. Both S21-present.
- **Evidence:** **A** (inputs). Not measured. The wiki's "445" is already **contradicted** by R5's 400 exit cap (LIB9 §3.13); what matters here is the claim that the carry keeps more than the jump-off cap → spec G-4.

### 3.27 Slide Grapple (backwards slide grapple, rubber band)
- **Sources:** W-GrF (full text); V-MokGr 06:00 "Backwards Slide Grapple" (C; the wiki's earliest dated mention is that video, 31 Jul 2021); V-Gruic (C, 4 Apr 2022).
- **Inputs (W-GrF):**
  1. Line up a point; most commonly a slightly lower one that you can swing under (a ceiling, a lamp post).
  2. Walk **Backwards**.
  3. Jump.
  4. Hold Crouch.
  5. Press Tactical.
  6. Let it connect while still holding Crouch.
  7. Start holding Forward as you cross under the grapple point.

  Key condition: the grapple must connect **while already in the slide**; tactical too soon after the jump connects in the air and loses the effect. Stand closer than for a Slingshot. Grappling out of a faster slide breaks the grapple.
- **Claim:** for a short time the slide wins over the grapple pull (a rubber-band effect), giving a lower arc. The wiki has no clip where a Slide Grapple out-ranges a normal Slingshot.
- **Combinations:** Momentumshift into a backwards Slide Grapple; slidehops after.
- **Version:** S21-present (≤ Jul 2021).
- **Mechanism reading [inf]:** the faster-slide break fits a length/stretch detach (the rope exceeding a length while moving away) or the `m_grappleSwingDetachLowSpeed`-type logic. Unknown.
- **Evidence:** **A** (order explicit; no timing values). Not measured → spec G-5.

### 3.28 Super Grapple (connect while retracting) and Super Jump Grapple
- **Sources:** W-GrA (full text); V-MokGr 04:41 (C); V-Pesky (C, 28 Feb 2023).
- **Inputs (W-GrA):**
  1. Aim at the target to check the range.
  2. Aim next to it or above it.
  3. Tactical.
  4. Use movement (falling, sideways or a jump) so that the hook connects **while it is being reeled back in**.

  Easier when not at maximum range. An easy setup: aim above an object as you fall next to it. The result: the pull's acceleration curve shifts, giving more speed early in the pull.
- **Super Jump Grapple:** aim slightly above the point; Tactical; do not move your aim; Jump so that the retracting hook connects.
- **Native basis [src]:** `m_grappleRetracting` / `m_grappleForcedRetracting` exist in GrappleData. So a retract-phase connect is a native state, not a script trick.
- **Version:** first days after launch; S21-present.
- **Evidence:** **A** (method stated, no timing). Not measured. In R5 it needs a hook fired past an edge (a miss), then a body move that brings the returning hook line into geometry → spec G-6. The exact change to the acceleration curve is unknown.

### 3.29 Rodeo Grapple (orbit) and pillar wrap
- **Sources:** W-GrA (full text; it recommends watching Cau7ioN, who uses Rodeos constantly); V-Dirk (C, controller); V-BOOL (C, 28 Aug 2021); Cau7ioN videos V-Cau1–4 (C; no chapters, so they can't be timestamped).
- **Inputs (W-GrA):**
  1. Aim at an object (thinner is better); Tactical.
  2. Hold **Sideways** throughout.
  3. **Keep looking at the grapple point** throughout.
  4. Hold **Backwards** briefly as you approach the furthest point (where the rope is most stretched); release.
  5. Repeat each lap.

  Keep the Backwards tap as short as you can, or it pulls you into a tighter circle. The timing depends on anchor height, distance and object thickness, and the wiki says it is learned by feel.
- **Uses:** reverse a Slingshot mid-air; dodge and return.
- **Pillar wrap:** no wiki entry by that name. The SDK `m_grapplePoints[4]` (rope wrapping up to 4 points) is the native feature that would let a rope bend around a pillar [src]. **No text I read describes "pillar wrap" inputs** → C / unidentified.
- **Mechanism reading [inf]:**
  - With the view on the anchor, Sideways is tangential to the rope. RF brakes tangential speed at about 420 u/s².
  - A side-key accelerate of about 575 u/s² (if A/D behave like the measured W) would out-pull the brake. The rope ramp keeps pulling inward; Backwards at the far point offsets it.
  - Whether the orbit survives depends on (a) the untested A/D response during the pull and (b) the detach rule. Keeping the view on the anchor again suggests a view-angle detach, and the rope wraps when passing a thin object.
- **Version:** first days after launch; S21-present.
- **Evidence:** **A** (inputs explicit; timing by feel). D2 noted that it conflicts with RF in magnitude. That is **not a contradiction yet**: RF was fitted without side keys and without a wrap → spec G-7.

### 3.30 Grapple Bounce, Grapple Super Bounce, Grapple Double-Bounce
- **Sources:** W-GrA (full text); V-Kovah (C, double-bounce guide, 2/3 Jul 2023); Super Bounce: Lowgantree on r/Apexrollouts, 6 Aug 2022 (link only).
- **Inputs, Grapple Bounce:**
  1. Tactical at a wall; move toward it.
  2. Disconnect at the right height.
  3. Hold Forward, facing the wall, to connect.
  4. Release Forward.
  5. Jump.

  The climb space resets to where the grapple disconnected, so the climb green zone is measured from there. Manual disconnect with Crouch or Tactical helps you learn the timing.
- **Super Bounce:** wallbounce **immediately** after the disconnect, holding Forward + Sideways.
- **Inputs, Double-Bounce (W-GrA):**
  1. Wallbounce.
  2. At the apex, face the wall and press Tactical.
  3. Disconnect once it connects.
  4. Climb.
  5. Jump.

  The hook connects only beyond 20 hu (look at the wall at a slight angle). Between 20 and 27 hu it auto-disconnects, with the right angle (40°–43°) after a wall-skip (Forward held). Crouch to disconnect always works but blocks the wall grab if held too long; Tactical sometimes has a small delay.
- **Version:** Bounce since launch (mechanism understood later); Super Bounce Aug 2022; Double-Bounce Jul 2023 (Kovah), with the auto-disconnect worked out by Mokeysniper for the wiki. All S21-present.
- **Evidence:** **A** (order and distances explicit). Not measured. Our R5 has the climb green zone (M3/M6) and the bounce, but not the grapple climb-space reset → spec G-8.

### 3.31 Infinite Grapple climb and Grapple scrape
- **Infinite Grapple climb** (W-GrA):
  1. Start a climb; look straight at the wall.
  2. Spam Grapple (it does not actually connect).
  3. Release Forward before maximum climb height.
  4. Feather Forward to stay in place.
  5. Hold Sideways to climb sideways.

  It resets the climb timer, not the maximum height. Discovered **May 2024 by El Gato** (Treeree Discord post; the wiki says May 2024). That is inside or just before S21 (S21 started 7 May 2024) → **S21-borderline**: present in the S21 build if it is a code behaviour, but community knowledge of it starts at the S21 boundary. **Evidence A**, not measured.
- **Grapple scrape** (W-GrA):
  1. Take a jump pad (crouch allowed).
  2. Grapple a wall.
  3. Hold Sideways to hug the wall while looking at the grapple spot.
  4. Release all directions once stuck, still looking at the spot.
  5. Press Backwards to leave.

  It uses the pad "wallbug". Clip on 7 Mar 2023 (SeerByy); the method was worked out in **late Dec 2024** (El Gato) → the method text is post-S21; the behaviour is probably older. **Evidence A for inputs, version uncertain.** Low value.

### 3.32 Grapple + zipline: auto-mount, Grapple Hyper jump, Zip dash
- **Auto-mount:** W-ZipB says Pathfinder is the only legend whose ability auto-connects him to a zipline (when he grapples it). **Measured** in GZ §2: the handoff is automatic, use not needed, mount on the command after `gr` ends.
- **Grapple Hyper jump** (W-RemL): stand under a horizontal zip, look at it, Tactical, then two Jump inputs together with Interact. Shown by Mokeysniper on 20 Nov 2021 (V-MokSecret, wiki t=158); the wiki author could not reproduce it in the current build. **The removal date is unknown**, so S21 status is unknown → keep it out of Reference (C).
- **Zip dash / stacked zip dash** (W-RemL, V-MokZD 21 Jul 2022): combining multiple ziplines' speed into one detach; **removed, date not given.** S21 status unknown (C).
- **Zipline tap-strafe, Grapple tap-strafing, Angled-zipline slide boost:** V-MokGr chapters 03:22, 07:28 and 01:50 only (C).

### 3.33 Other grapple notes
- **Grapple enemies / slide pull:** in a fast slide downhill you pull a grappled enemy along (W-GrF). Not relevant to HSD (no enemies).
- **Drone grapple** (Crypto drone; Oct 2019; Generic page). Not relevant.
- **Landing Gear** (Horizon-style air control and soft landing for Pathfinder): **S29 (23 Jun 2026), post-S21.**

### 3.34 Zipline Gun (Pathfinder ultimate): S21 rules
**Script / weapon file [src, SRC-Zg]**

| Item | Value | Note |
|---|---|---|
| Fire requirement | owner `IsOnGround()` **or** `IsWallRunning()` **or** `IsWallHanging()`; the ground entity must be valid, not `entity_blocker`, and `IsAllowedToAttachZiplines` | you cannot fire from mid-air (the 19 Mar 2019 fix for deployment failing when jumping is about the start station) |
| Begin station | a pole on the ground, a wall anchor when wallrunning/hanging; parented to the ground entity, destroyed if the parent moves | |
| Projectile | `projectile_launch_speed` 2600, `projectile_gravity_scale` 0, fuse 10 s | straight line |
| Length | `zipline_distance_min` 700, `zipline_distance_max` 8000 | 17.8–203 m (wiki.gg: about 200 m; +60 % on 14 Feb 2023) |
| Snapping | `zipline_grenade_snap_distance` 250, `zipline_grenade_snap_angle` 10 | |
| Validity | native `ZiplineGrenadeHasValidSpot()` (dry-fire if invalid) and `Zipline_FindZiplineStationSpotsForProjectile` (end station: ground / wall / ledge animation variants) | the rule inside is native; not in script |
| Rope | `CreateGunZipline`: rest points begin/end; `ZiplineAutoDetachDistance` 100; `ZiplineBreakable` 1; **`ZiplineVertical` = `ZiplinePreserveVelocity` = (\|dir.z\| > 0.7)** | 0.7 ⇒ steeper than about 44.4°: the wiki's 45° Ziplines |
| Limits | `ZIPLINE_MAX_IN_WORLD` 10 (per owner, oldest removed); refund if destroyed within `ZIPLINE_REFUND_TIME` 3 s, or if the grenade never deploys | the current wiki.gg infobox says 4, which is post-S21 or unverified |
| Cooldown | clip 180, regen 1/s ⇒ **180 s**; `cooldown_reduction_1…8` mods (passive scans, 170 → 120 s in steps of 10) | wiki.gg: 90 → 120 s (Oct 2019); 3 → 2 min on 23 Jun 2026, so 3 min was the pre-2026 value |
| Energized rope (Zipline Zen) | `sh_pilot_passive_zipline_shield.gnut`, `PAS_ULT_UPGRADE_ONE`; damage mitigation (WG-Path: Zipline Zen 25 → 50 % on 26 Mar 2024) | S21: an upgrade, damage only, no movement effect |

**Wiki facts (W-ZipB, W-PZ, W-Vel)**
- Pathfinder ziplines ride at **1000 hu/s** (regular 600, vertical 480, evac 840, ziprails 1260).
- You cannot carry more speed into a zipline than its maximum.
- 45° ziplines: riding to the end gives **800 instead of the regular 600**, and you can jump off in any direction. You can tell one because the zip does not pull your view on mount, or by checking `cl_showpos` angles.
- Super jumps near the pole work in all directions on 45° zips.
- The wiki suggests practising the zipline carry on a Pathfinder zipline placed parallel to a wall.

**Version**
- 14 Feb 2023 (S16): range +60 %, speed +66 % (WG-Path; V-MokS16 chapter 02:52 "Pathfinder").
- Zipline Zen ×2 on 26 Mar 2024 (before S21).
- After S21: 7 Jan 2025 Zen 25 %; 6 May 2025 Zen built in at 50 %; 23 Jun 2026 launch speed up and 2 min cooldown; Feeling Zippy (+1 charge) is post-S21.

**Community techniques on placed ropes:** every LIB9 §3.13–3.16 rope technique works on gun ropes (they are ordinary `zipline` entities with the same Find/ride code, plus the speed). Gun-specific items:
- **45° zip exit** (A; the slope rule is now explained by script).
- **Momentum carry exit** (§3.26).
- **Zipline carry practice** (W-Carry).
- **Shallow Pad** (Set3kh, 8 Sep 2023): a pad at the bottom of a vertical zip; Interact and very quickly Jump or Crouch keeps the pad double jump (W-Pad2) (A).
- **Ceiling surf stored through a zipline** (Suomikala, 22 Apr 2021) (B).
- **Portal placed while riding a zipline** (W-Portal; unreplicated) (C).

**Evidence:** rules [src]; ride speed 1000 and the 800 exit are wiki (current) → specs Z-1…Z-4. Our R5 has never fired the gun (M10-PLAN audit).

### 3.35 Octane Stim: S21 rules
- **Script [src, SRC-Stim]:**
  - Duration `STIM_DURATION` 6.0 (playlist `octane_stim_duration`).
  - Health cost 20; Thick Skin −5 per pick (`upgrade_octane_stim_health_cost` / `_again`); health floors at 1.
  - Clears move_slow / turn_slow unless healing (`octane_stim_clear_slows`).
  - `StatusEffect speed_boost` 0.15 for duration + 0.5 with a 0.5 fade; `anti_slow`; the `stim_sprint` settings mod for 6.0 s.
  - **Re-use:** `OnWeaponAttemptOffhandSwitch` returns false while `stim_visual_effect` is active (the full 6.0 s).
  - Weapon file: `charge_time` 6.0, `charge_cooldown_time` **0.7**, `upgrade_core_tac_duration_increase` charge 8.0.
- **R5 measured (OCT):**
  - Onset 0.16 s after the tap; ×1.298038 (0.149 = 38/255); 6.0 s full plus a 0.5 s cosine fade.
  - Sprint mod 282/120.
  - The lurch clamp follows 0.7 × the current sprint cap (294.67).
  - **Carry-over trials (r1517, r1519): a tap during an active stim gave no new stim.** That agrees with the script's re-use block.
- **Wiki (W-Stim, W-Gen):**
  - Current text: 45.9 % sprint / 34.5 % walk; 20 damage per stim (1 hp floor); stim does not clear fall stun; "delay between consecutive Stim activations of 0.7sec".
  - History: buffed **6 Jan 2026** from 40 % to 52 % and the "Stim delay" from **1.8 s to 0.7 s**, plus sprinting while healing.
  - The W-Gen table still shows "Stim 40.7 %" for slide boost and superglide; that row is the old value.
- **S21 reading:**
  - Speed: R5's sprint 420.95/299 = +40.8 % matches the pre-2026 40 % and the W-Gen table's Stim 40.7 % → **measured**.
  - Duration 6 s and cost 20 (−5/−10 with upgrades): **S21** (EA-S21 for Thick Skin).
  - The weapon file's 0.7 s cooldown is the **2026** value (pre-2026: 1.8 s). The `upgrade_core_tac_duration_increase` mod and Stim Surge / Daredevil are **2026 (post-S21)**.
  - **Open conflict:** the wiki's activation delay (1.8 s pre-2026) implies re-stimming *during* an active stim was possible after the delay. R5 (script and OCT) blocks re-use until the visual effect ends (6 s). Which one was live S21 behaviour is unresolved → spec O-2.
- **Combinations:** every msc-scaled quantity (OCT §2.4); fastest slidehop-heal (W-Stim); stimming into a pad has no effect on the pad arc (W-Pad), consistent with the velocity-replacing launch (OCT §3.1).
- **Evidence:** **measured** (speed, timing); **A** (input: press Tactical); re-use rule **[src] + measured, wiki-conflicting**.

### 3.36 Octane Jump Pad: S21 rules
- **Script [src, SRC-Pad, SRC-PadSDK]:**
  - Launch: push 1150, V 2.0, ducked ×0.5; radius 32, trigger height +32/−16.
  - Push ×1.2 if `PAS_ULT_UPGRADE_ONE` (version unknown, see §1.5).
  - `PAS_ULT_UPGRADE_THREE` → UPGRADED skin → the double jump gets `enable_doublejump_aircontrol`. This is **Airborne Agility**; the skin is looked up from the nearest pad within 100 u at launch.
  - Mad Hops = weapon mod `upgrade_ult_one`, clip 180 (2 × 90).
  - Ult cooldown 90 s (clip 90, regen 1).
  - Activation: the pad plays its deploy animation and activates when it is done (`WaittillAnimDone`; `JUMP_PAD_ACTIVATION_TIME` 0.5 is declared). This is the pre-2026 landing → active delay. W-RemL: the pad used to need a moment between landing and activating; that delay was removed on 6 Jan 2026.
  - Debounce 1.0 s.
  - Slow-mo flight until ground (the SDK sets `m_slowMoEnabled` on launch and clears it on the landing command).
  - A double jump is granted while airborne and removed on ground or zipline.
- **R5 measured (OCT, RD1, M8):**
  - v = 1150·normalize(ĥ + V·ẑ): standing |h| 514.3 / vz 1028.6; crouched 813.2 / 813.2.
  - The approach speed is discarded; flight runs on dt·0.8; hard-landing slowdown.
  - The pad launch opens no lurch window; the pad double jump does (M8 / RD1).
- **Stand vs crouch (W-Pad):**
  - A high arc without Crouch, and a flatter but longer arc with Crouch.
  - Heights: crouched 442.8, standing 707.9; straight up 884–920 (it creeps up to 920 on repeated up/down, then resets to 884).
  - Crouched flat-ground distance about 42 m; with a double jump about 70 m; with a slide after, 90–100 m.
  - Pad contact does not count as ground contact.
  - **Check:** v² / (2·750) gives 440.8 (crouch), 705.4 (stand) and 881.7 (straight up) → the wiki heights agree with the OCT formula to within 0.5 % → **measured-consistent**.
  - History: separate crouch arcs since **S8 (2 Feb 2021)**; the double jump since 23 Jun 2020; before S8 the arc differed by jumping on the pad.
- **Launch direction ĥ (W-PadDir, W-Pad):**
  - Melee onto the pad without Forward → straight up. Holding Forward → normal.
  - Backwards or Sideways after the melee → fly backwards or sideways.
  - Very high approach speed can launch you straight up. The wiki's going-straight-up item also lists climbing into a pad and throwing it at your feet.

  [inf]: ĥ = the horizontal **wish** direction at contact. With no input it is zero, giving pure vertical 1150 (881.7 up, which matches "884"). The very-fast case may come from the launch normalisation or the trigger geometry. OCT could not separate ĥ, because input, view and velocity were all +X → spec O-3.
- **Double jump (W-Pad):**
  - Press Jump (or the Movement-ability bind) once airborne; the timing barely matters after the apex.
  - Hold Forward to steer slightly; turn around + Forward to kill the momentum.
  - **Direction change** (look where you want to go, hold Forward, jump; momentum drops sharply above 90°) = the former **Airborne Agility** upgrade → **S21 Level 3 upgrade, not base** (EA-S21; base only from 6 Jan 2026).
  - Tiny delay before the double jump is available (used by Shallow Pad).
  - The double jump is stored through a Wraith portal and a quick Rampart-turret mount.
- **Upgrades in S21 (EA-S21):** L2 Mad Hops (extra charge) / Thick Skin; L3 Airborne Agility / Thick Skin. Triple Jump (+100 hu/s) and Squad Rush: **6 Jan 2026, post-S21**.
- **Evidence:** launch **measured**; heights **measured-consistent**; ĥ rule **B** (wiki implies it; no explicit statement); upgrades **official + [src]**.

### 3.37 Ceiling surf (focus item for M10-C3)
- **Sources:**
  - W-Pad (full text).
  - V-MokOct, Mokeysniper, 12 Jan 2021, chapter **01:52 Ceiling Surfing** (the wiki links t=112 = 01:52).
  - V-MokSecret (20 Nov 2021) links the Suomikala zipline clip (r/Apexrollouts, 22 Apr 2021).
  - V-Stras (11 Jul 2021) and V-Baner (8 May 2022): short clips (C).
- **Definition (W-Pad):** take the jump pad under a low ceiling and you slide along the ceiling, keeping the upward momentum "till it runs out or the ceiling ends".
- **Inputs (W-Pad):**
  1. Be under a low ceiling.
  2. Take the jump pad.
  3. Hold **Forward** until the surf has started.
- **Conditions and tips (W-Pad):**
  - It needs a **smooth, continuous ceiling**.
  - It works better with a **Crouch** on the pad.
  - It is possible without Forward, but Forward makes it much more consistent.
  - Once surfing you can release Forward and **air strafe on the ceiling**.
  - The duration appears to depend on how far the ceiling is above the pad.
  - If surf potential remains when the roof ends, you are thrown upward.
  - The surf potential is **stored through a zipline interaction** (the Fire Range tower zip, aligned with the pole).
- **Failure causes (implied by the text):** a rough or interrupted ceiling; no Forward (less consistent); the ceiling too high (little or no potential left); hitting the ceiling edge or geometry.
- **Uses:** travel under low roofs; the upward throw at the roof edge onto overhangs; TS back onto the same roof.
- **Mechanism (my reading; to be tested) [inf]:**
  - The pad launch replaces velocity with vz0 = 1028.6 (standing) or 813.2 (crouched) and enables slow-mo (dt·0.8) until ground.
  - The wiki's three observations all follow from one rule: **the ceiling contact clips the position, but the stored vertical velocity is not zeroed. It keeps decreasing under gravity while the player is pinned.**
    - Duration grows as the ceiling gets lower: vz at contact = √(vz0² − 2·g·h), and the pinned time ≈ vz_contact / g in sim time (÷ 0.8 in real time).
    - Leftover vz throws you up when the roof ends.
    - The stored vz survives a zipline touch.
  - In Source-style movement a ceiling hit normally clips vz to 0, so this rule would be an Apex-specific behaviour (ceiling-clip skipped or deferred). R5 can show it directly: in MOVE-TRACE, vz > 0 on commands where z is constant under the ceiling.
  - Horizontal: if the player counts as airborne while pinned, air strafe (500 u/s², wish cap 60·msc) applies. That matches the wiki's air strafing on the ceiling. There should be no ground friction.
  - Why crouch helps: a 45° launch gives more horizontal speed (813 vs 514) and lower vz, so the player reaches the ceiling with more forward travel per unit of surf time [inf].
  - Why Forward helps: unknown. One possibility is that Forward with view and approach toward the pad sets ĥ (see §3.36) so that the launch has a horizontal component into the ceiling region [inf].
- **Version:** discovered before 12 Jan 2021 (S7); the zipline storage was found 22 Apr 2021. No removal is recorded. **S21-present.**
- **Evidence:** **A** for inputs (three steps plus conditions, no timing); the mechanism is **unverified** → spec O-6 (decisive) and O-7 (height grid).

### 3.38 Other Octane techniques (pre-S21 unless marked)

| Technique | Inputs (as stated) | Source and date | Version | Evidence |
|---|---|---|---|---|
| **Tap strafe off pad** | Sprint toward the pad; "Perform a 180° Tap strafe as if you would do it on normal flat ground"; start early and move it later until it happens at contact | W-PadDir; Mokeysniper video 19 Jul 2021 (t=15) | S21-present | **B** (the TS input itself is LIB9 §3.3; the timing relative to the pad is vague). See §1.8 and spec O-5 |
| **Double "tap strafe"** | TS off the pad + TS off the double jump | W-PadDir | S21 | B |
| **Melee jump pad** | Stand in front of the pad, Melee, **no Forward**; for back/side add Backwards/Sideways after the melee; possible out of a sprint and with Crouch for the low arc | W-PadDir; melee: comments of V-MokOct19 (11 Dec 2019); direction method: r/apexuniversity, 11 Dec 2020 | S21 | **A** → spec O-3 |
| **Flick strafe** (controller) | Left stick fully sideways; turn the right stick the same way as you are about to jump; Jump and flick the left stick to the front and back to the side | W-PadDir; Cryo, 19–20 Apr 2021 (V-Shm) | S21 | A (controller-only; low priority for MnK HSD) |
| **Direction change with the double jump** | Look the new way, hold Forward, Jump | W-Pad | **S21 = the Airborne Agility L3 upgrade**; base only from Jan 2026 | A |
| **Jump Pad wallrunning** | Pad in the wall–floor corner; sprint at about 20° to the wall; hit the pad close to the wall; slide into it; hold Sideways into the wall; keep looking into the wall; walls at least chest high | W-Pad2; Mokeysniper 16 Aug 2021 (V-MokPadWR); also chapter 03:24 of V-MokOct (12 Jan 2021) | S21 (uses the "wallbug") | **A** → spec O-8 (low priority) |
| **Shallow Pad** | Pad at the bottom of a vertical zip; hit the pad; Interact then very quickly Jump or Crouch; Jump again mid-air (double jump kept) | W-Pad2; Set3kh, 8 Sep 2023 | S21 | A |
| **Mantle double jump** | Place the pad where you mantle-jump; mantle jump | W-Pad2; Set3kh, 8 Sep 2023 | S21 | B (the wiki gives no tips) |
| **2nd pad combos** | Throw the second pad slightly up after the double/triple jump, or far ahead just before landing, then slide into it | W-Pad | S21 **only with Mad Hops (L2 upgrade)** | A |
| **Slide-through tap strafe** | Sprint, throw the pad ahead, slide through it, TS 180° back onto it | W-RemL; Mokeysniper 19 Jul 2021 | **S21-present** (it relied on the activation delay, removed 6 Jan 2026) | A |
| **Jump Pad dash** (red pad) | Jump and Backwards on the same frame on a red jump pad | W-RemL (stub) | removed, date unknown | C |
| **Grapple scrape**, **Ceiling surf → TS** | see §3.31, §3.37 | | | |
| **Triple jump, Squad Rush, Stim Surge** | — | W-Pad, W-Stim | **post-S21 (Jan 2026)** | do not use |

### 3.39 Wraith Into the Void (tactical): S21 rules
- **WG-Wr history (summary):**
  - 23 Jun 2020: activation 0.4 → 1.25 s, +30 % void speed, duration 3 → 4 s, cooldown 25 s.
  - May 2021: small wall bumps no longer cancel it.
  - 26 Mar 2024: the tactical cooldown upgrade moved to Level 3.
  - 7 May 2024 (S21): highlighting in the void.
  - **25 Mar 2025 (post-S21):** cooldown 20 s, activation 0.8 s, exit any time, Fast Phase −30 %.
  - **31 Mar 2026:** 15 s base; Void Jumper (6 s plus a double jump in the void) → post-S21.
- **S21 values:** activation 1.25 s; duration 4 s; +30 % (37–38 % in W-Phase / W-Gen, measured as the sprint cap); cooldown 25 s (20 s with the L3 upgrade).
- **Script [src, SRC-Void]:**
  - Deploy slow `wraith_phase_walk_slow_amount` 0.2 over the deploy time.
  - `speed_boost` 0.3 for `charge_time` with fade = 0.3 × charge time; forced auto-sprint; `PhaseShift(PHASETYPE_BALANCE)`.
  - Heal upgrade 25 hp over the duration (`PAS_TAC_UPGRADE_TWO`); Fast Phase (`PAS_FASTER_TAC_WINDUP`).
  - The weapon file has `charge_time` 4.0 and cooldown 150/10 = 15 s. **15 s is the 2026 base**, so the file mixes versions; trust the measurement.
- **R5 measured (P3):** deploy msc 0.80 for 1.17 s; boost ×1.388 for 2.77 s; 0.79 s fade; sprint **414.98** = 260 × 1.5961.
- **Agreement:** the W-Gen phase row (414) equals R5 414.98 → **measured**.
- **Community (W-Phase):** the game forces sprint in the void and it stays on after; speed boosts work on the walk base, so phase gives "the fastest Slide, Superglide and the biggest climb jolt increase" (W-Gen table: phase slide 638, SG 695, climb +17).
- **Evidence:** **measured** (speed and timing); techniques: **A** (a slide or SG during the phase uses the existing inputs).

### 3.40 Wraith Dimensional Rift (ultimate): S21 rules and portal techniques
- **Script [src, SRC-Rift]:**
  - Placement: walk from the start point; the second portal is placed at your position.
  - `wraith_portal_max_distance` 6000 (152 m); the min portal separation is 128 u.
  - Placement heights: standing 45, crouched 20 (crouch portals have a smaller trigger: radius 16, height 32/16).
  - Lifetime `PHASE_TUNNEL_LIFETIME` 45 s.
  - While placing: auto-sprint; weapons locked; `speed_boost` severity **0.2**, raised by **+0.1 each time the straight-line distance from the start exceeds another 20 % of 6000 u** (≈ 30 m steps).
  - Travel: the recorded path is cleaned to valid exit nodes and replayed by a mover at `wraith_portal_max_travel_speed` **1024 u/s**, clamped to **0.3–2.0 s** (Wraith: max time scaled to 3.5 s for paths of 3000–6000 u), stepped every 0.1 s. Crouched nodes force crouch.
  - **On each step `player.SetVelocity(node.velocity)`**, so the exit velocity is the velocity you had when you walked that node.
  - Reuse debounce 0.5 s; projectiles are teleported too.
- **WG-Wr (summary):**
  - 14 Feb 2023: max 76 → 152 m; lifetime 60 → 45 s; speed increases on longer portals.
  - 25 Mar 2025 (post-S21): cooldown 3 → 2.5 min, ramps faster.
  - The S21 cooldown was **3 min** (2 min with the L2 upgrade, moved to Rare L2 on 26 Mar 2024).
  - S21 change: void highlighting only (EA-S21).
- **Speed ramp (W-Portal):**
  - Current: 22 % at 0 m → 26 % at 16 m → … → 74 % at 57 m.
  - **Before 25 Mar 2025 (= S21):** "22% at 0m –> 39% at 60m –> 57% at 90m –> 74% at 120m".
  - Script thresholds at 30.5/61/91/122/152 m match the 60/90/120 m steps. The 30 m step and the severity→% mapping (0.2 → 22 %?) are **not reconciled** (by the stim formula, 0.2 would be +40 %) → spec W-2.
  - Speed is computed from the **direct** (3D) distance to the start; energy is consumed by **horizontal** distance. So starting on a balloon and dropping gives more than 90 m of direct distance for almost no energy (W-Portal).
- **Techniques:**
  - **Portal speed manipulation** (W-Portal; Mokeysniper's S16 investigation, 18 Feb 2023, V-MokS16 00:00): start high, drop, cross the distance thresholds. **S21-present** (pre-2025 thresholds). Evidence A.
  - **Portal glide** (thevilnside, 11 Jul 2021):
    1. Stand in front of the SG object; Ultimate.
    2. Climb and Superglide.
    3. Attack right after the SG to place the portal.

    Placing within 3 m refunds the ult but keeps the first speed boost. Placed instead of refunded = too late. With the S21 script the refund threshold is a portal energy rule [src not located]. S21-present. **A.**
  - **Double jump stored through a portal** (W-Pad, W-Portal). B.
  - **Gruic's portal trick** (Jun 2023) and **Faide's portal tech** (Jul 2025 = post-S21): titles only (C).
- **Momentum reading:**
  - P3 assumed the exit velocity is "fixed" (preset 300 u/s along the view plus a 0.3 s lock, M5 design).
  - The script says the exit velocity is the **recorded velocity at the exit node**: whatever you were doing when you walked past that point during placement (usually the boosted sprint, about 364–515 u/s). So a portal "keeps" placement-time momentum, not entry momentum [src].
  - Spec W-3 checks this.
- **Evidence:** rules **[src]**; ramp **wiki (dated history)**; travel momentum **[src]**, not measured.

### 3.41 E2 candidates: Mad Maggie, Newcastle, others

**Mad Maggie, Wrecking Ball speed pads (S12 kit, S21-present)**
- **Script [src, SRC-Mag]:**
  - Ball duration 10 s; wake pieces last 60 s.
  - Speed triggers: radius **88**, height 16.
  - Inside: endless `speed_boost` **0.15**; on leaving, 0.15 for **2 s** with a 0.25 s fade (the duration reads the `wrecking_ball_wake_duration_override` playlist var, a script quirk).
  - No buff FX while stimmed or phased; jump-pad window 0.2 s (no ball bounce).
  - **No per-pad re-activation delay** in this script.
- **Wiki (W-Mag):** current pads boost for 3.5 s, give Fortified, have a 6 s re-activation (**S26.1, 16 Sep 2025**), sprint-only (**23 Jun 2026**); the boost does not stack with other speed boosts.
- **Community:** "fairly popular to combine the Pads with Lurch strafing" before the 6 s rule, i.e. micro-boosts in a small area (S21-era use). Ball explosion knockback combines with a jump, grapple hop or pad (do the movement before the hit) (W-Mag).
- **HSD fit:** a placeable zone that applies the existing `StimAbility` multiplier. Cheap (S); an unusual "zone" primitive; with lurch strafing it has a real community use. **Evidence: [src] + A** (inputs trivial). D2 "n/a" should change to **candidate (S)**.

**Newcastle, Castle Wall leap (S13 kit)**
- **Script [src, SRC-NC]:**
  - Leap ≤ 40 m (80 m to an ally); max leap height 25 m (50 m to an ally).
  - Ground dash ≤ 600 u (height limit 250; 800–1500 u/s).
  - Air launch 1000 u/s with a 0.8 ease-out; hover 0.55 s (gravity ×0.45, velocity ×0.5).
  - Slam 2000 (near) – 2500 (far), max 3500; jump speeds 1800–2500.
  - Interrupt keeps **35 %** of travel velocity if above 300 u/s; jump timeout 2.75 s.
  - `PAS_ULT_UPGRADE_ONE` = ult distance upgrade (version unknown).
  - S21 changes (EA-S21): energized wall 1 min, Mobile Shield throw about 2.5× faster. Neither is a movement change.
- **Community:** Castle boost (W-NC): **other** players Jump as the slam lands to get a big push. It combines with a super jump; you can air strafe or TS out of it. W-Vel: Newcastle ult peak 2453. The page's history is truncated, so the date is unknown. Mobile Shield: bobz guide (12 May 2022) is about steering the shield, not self-movement.
- **HSD fit:** a targeted kinematic leap (reuses the Echo path driver). No self-movement community tech beyond the leap itself. **Evidence [src]; techniques B/C.** Medium value.

**Others with unique movement (short)**

| Legend / item | S21 status | Note |
|---|---|---|
| Lifeline glide (drone) | **post-S21** (rework S23, 5 Nov 2024) | do not use |
| Horizon Gravity Boots / NEWT Scoot | **post-S21** (S27, 4 Nov 2025) | do not use |
| Crypto drone invisibility | post-S21 (S22 upgrade) | not movement |
| Rampart Amped Cover wallbounce / wallrun / stun-cancel | S21-present (No-Ma crouched bounces Aug 2023; the uncrouched-bounce investigation is Set3kh 7 Jun 2024) | placeable collider only (D2 C12) |
| Fuse Motherlode push | S21-present (removed S28) | knockback from an enemy ult; not self-movement |
| Seer hover, Axle jump gate, Valk moonboots removal | post-S21 | ignore |
| Maggie passive (shotgun holstered speed) | **date not verified** | a speed-preset row only |

## 4. Version boundaries found this round

| Change | Date | S21 relation |
|---|---|---|
| Grapple cooldown by distance 10–35 s; then max 30 s + 5 s travel cap | 6 Oct / 4 Nov 2020 | in S21 (matches the script) |
| Grapple flat 30 s; then variable again | 7 Jan / 6 May 2025 | after S21 |
| Grapple 2 charges, flat 20 s; Landing Gear | 23 Jun 2026 | after S21 |
| Zipline Gun +60 % range, +66 % speed (1000 u/s) | 14 Feb 2023 | in S21 |
| Zipline Zen 25 → 50 % | 26 Mar 2024 | in S21 (damage only) |
| Zipline Gun 3 → 2 min, launch speed up | 23 Jun 2026 | after S21 |
| Octane pad crouch/stand arcs | S8, 2 Feb 2021 | in S21 |
| Octane pad double jump | 23 Jun 2020 | in S21 |
| Legend upgrades introduced (Mad Hops L3, Airborne Agility L3, Thick Skin −25 %, Wreckless) | S20, 13 Feb 2024 | superseded in S21 |
| **Octane S21 upgrades: L2 Mad Hops / Thick Skin (−5); L3 Airborne Agility / Thick Skin (−5)** | **S21, 7 May 2024 (EA, 6 May)** | **S21** |
| Pad activation delay removed; 2 charges and the direction change made base; Triple Jump; Squad Rush; Stim 52 % and 0.7 s delay; Stim Surge | 6 Jan 2026 | after S21 |
| Ceiling surf discovered / zipline storage | ≤ 12 Jan 2021 / 22 Apr 2021 | in S21 |
| Wraith Void: 1.25 s activation, 4 s, +30 % | 23 Jun 2020 | in S21 |
| Wraith Void faster (0.8 s, 20 s, exit any time) | 25 Mar 2025 | after S21 |
| Wraith Rift 152 m, 45 s, speed by distance | 14 Feb 2023 | in S21 |
| Wraith Rift ramp compressed (57 m) | 25 Mar 2025 | after S21 |
| Void Jumper (double jump in the void) | 31 Mar 2026 | after S21 |
| Maggie pads: 6 s re-activation / sprint-only | 16 Sep 2025 / 23 Jun 2026 | after S21 (pads themselves S12) |
| Infinite Grapple climb discovered | May 2024 | S21 boundary |
| Grapple scrape method | Dec 2024 | after S21 (the behaviour is probably older) |
| Grapple Hyper jump, Zip dash | removed, dates unknown | unknown; keep out |

## 5. Mapping to our R5 models (consistency only, no new claims)

| Claim | Our model | Status |
|---|---|---|
| Slingshot ≈ 1200 | RF + W (clamp v·ŵ ≤ 483 only) | **compatible in mechanism, untested in magnitude** (G-1) |
| Rodeo orbit | RF tangential brake 420; A/D during the pull unmeasured | **untested** (G-7) |
| Detach: passed the anchor / view turned away / Crouch | unidentified after 79 trials; Tactical release measured | **new candidates** (G-3) |
| Jump does not release | measured | **agrees** (the wiki never claims a jump release) |
| Jump Grapple = coyote jump | attach hop 200 measured; coyote 0.2 s (wiki); M4 jump at +0.6 s was outside the window | **untested** (G-2) |
| Pad heights 442.8 / 707.9 / 884 | OCT formula 440.8 / 705.4 / 881.7 | **agrees** |
| Stim +40 % sprint | OCT 420.95/299 = +40.8 % | **agrees** (pre-2026 wiki) |
| Stim re-use | R5: blocked for 6 s (script and OCT); wiki pre-2026: 1.8 s delay | **conflict** (O-2) |
| Phase 414 | P3 414.98 | **agrees** |
| Portal exit fixed 300 + lock (M5 preset) | script: exit = recorded node velocity | **preset is a design value; the script differs** (W-3) |
| Pad launch → lurch | RD1: none | the wiki TS off pad needs a pre-pad jump (O-5); **no conflict** with the D3 decision |

## 6. Reproduction specs (evidence A or measured only)

Conventions as in LIB9 §6: 120 fps, 1 cmd = 1/120 s; "edge" = key-down on that command. **R** = R5 trial; **U** = Unity real-input demo after R confirms. Trials run on the R5 dedi with MOVE-TRACE and `[HSD-STATE]`. "Verify" names what settles it.

| # | Technique (source) | Exact input script | Expected outcome (source) | Verify with |
|---|---|---|---|---|
| G-1 | Slingshot (W-GrF, A) | Pathfinder; anchor 45° up at 800 u (and 600 u); stand still. Tactical at t0. From attach + 0.2 s (pull start): yaw view to +80° (left) over 0.15 s, hold **W+A**. At 50 % of the predicted pull time (RF model), yaw back to −10° over 0.3 s and switch to **W+D**. Variants: no turn (control); W only; jump at attach + 2 cmds | peak \|v\| well above the no-input pull (wiki ≈ 1200 at max range); auto-disconnect near the anchor pass | max \|v\|, v·ŵ (expect clamp 483), heading; RF-plus-W open-loop prediction vs observed |
| G-1b | A/D response during a pull (needed by G-1 and G-7) | Anchor 45° up at 600 u; view fixed on the anchor; from pull start hold **A** only (then **D** only; then **S** only) for the whole pull | measure accel along the flat view's right axis; is there a clamp on v·ŵ for side wishes like the 483 for W? | per-cmd Δv decomposed as in SWING §3.2 |
| G-2 | Jump Grapple (W-GrF, A) | Ground anchor 700 u ahead, pitch +20° down; Tactical; Jump edge at attach + k, k = 1, 6, 12, 18, 24, 30, 48 cmds | jump applied (+289.8 vz) up to ≈ 24 cmds after leaving the ground (coyote 0.2 s); not after | vz step on the jump cmd; M4-LG's jump at +0.6 s is the k > 24 control |
| G-2b | Grapple hop (W-GrF, A) | Pitch +89° (straight down); Tactical; Jump at attach + 0, 1, 2, 4 cmds | apex height clearly above a normal jump (56 u) | does the 200 hop add to or get replaced by the 289.8 jump; apex z |
| G-3 | Detach rule candidates (W-GrF/W-GrA, A as statements) | Anchor on a free-standing thin pole (no wall behind), 500 u: (a) no input, run past the anchor; (b) yaw away from the anchor at 180°/s from pull start, record the angle at release; (c) Crouch edge at pull + 0.3 s; (d) Tactical edge (control, GZ) | (a) release on passing the anchor; (b) release at some view–rope angle (the games.gg text says 90°: low-trust); (c) release on the Crouch command | release cmd vs anchor-relative position, view–rope angle, Crouch edge |
| G-4 | Momentum carry exit (W-PZ, A) | Ride a sloped map zip to full speed (≥ 560); pitch +89°; Tactical; compare with a Jump-off at the same point | the carry keeps more horizontal speed than the jump-off cap 400 (A3) | v_h after detach vs 400 |
| G-5 | Slide Grapple (W-GrF, A) | Anchor 300 u ahead-low (pole top at z + 100); walk **S** (backwards) at 199.5; Jump; hold Crouch from airborne; Tactical edge after the landing slide begins (+2 cmds) vs before landing (control); W edge when crossing under the anchor | slide continues (the slide briefly wins over the pull), then a low arc under the anchor; control (air connect) gives the normal pull | trajectory height vs control; did the slide state persist during the pull |
| G-6 | Super Grapple (W-GrA, A) | Stand 300 u from a ledge; aim 30 u above the ledge top (miss); Tactical; at 0.2 s jump (Super Jump Grapple) or strafe so that the retracting line hits the ledge | an attach during the retract (`m_grappleRetracting`) and a faster early pull than a normal attach | ramp over the first 0.3 s vs the RF A = 541 |
| G-7 | Rodeo (W-GrA, A) | Thin pole (r ≈ 8 u) 300 u away, anchor at eye height + 100; Tactical; hold **D** throughout; view locked on the anchor (yaw tracking); S pulse 6 cmds when the rope length is at its maximum for the lap; repeat for 3 laps | ≥ 1 full orbit without release | angular position vs time; rope point count if visible (`m_grapplePointCount`) |
| G-8 | Grapple Double-Bounce (W-GrA, A) | Wallbounce (LIB9 R-8 basic), W held (wall-skip); at the bounce apex face the wall at 40–43° and press Tactical at 22 u from the wall (20–27 u band); climb; Jump | the grapple auto-disconnects; the climb space resets; a second bounce | climb-space baseline z vs the disconnect z; bounce height |
| Z-1 | Zipline Gun fire rules (SRC-Zg) | Pathfinder with ult: fire at targets 600 / 800 / 4000 / 7900 / 8100 u; fire while airborne (control); fire while wall-hanging | valid between 700 and 8000 only; dry-fire when airborne | entity created? `ZiplineGrenadeHasValidSpot` result |
| Z-2 | Gun rope ride speed (W-ZipB) | Ride a gun rope of 3000 u (slope 10°) from mid-rope | constant 1000 (wiki); map rope control 600 | steady \|v\| on the rope |
| Z-3 | 45° gun rope (W-PZ, SRC-Zg) | Gun ropes at 40° and 50° slope; ride to the end without disconnecting; then jump off mid-rope facing 90° off the rope | 50°: exit about 800 and free jump direction (`ZiplinePreserveVelocity`); 40°: exit capped, jump along the rope | end exit \|v\|; jump-off heading |
| Z-4 | Gun rope = map rope for techniques | On a gun rope repeat LIB9 R-11 (zip jump), R-12 (carry), R-13 (super jump), R-16 (mid-rope mount) | same results as on map ropes, apart from the speed | regression vs A3 |
| O-1 | Stim baseline regression (OCT) | Tap Tactical; sprint 8 s | ×1.298, 6.0 s + 0.5 s fade, sprint 420.95 | already measured; regression only |
| O-2 | Stim re-use (W-Stim vs SRC-Stim) | Stim; tap Tactical again at +1.0, +2.0, +3.0, +5.9, +6.1 s | R5/script: no new stim before 6.0 s; the pre-2026 wiki implies re-stim after 1.8 s | health drop and msc refresh per tap |
| O-3 | Pad launch direction (W-PadDir, A) | Stand 40 u in front of a pad: (a) Melee, no keys; (b) Melee, then S edge at +4 cmds; (c) Melee, then D edge; (d) walk onto the pad holding W with the view yawed 90° from the approach; (e) approach at 600 u/s (pad-chain entry), no input on contact | (a) pure vertical 1150; (b) backwards; (c) sideways; (d) tells view vs wish vs velocity; (e) straight up per the wiki | the launch-command velocity vector vs input / view / velocity |
| O-4 | Pad stand / crouch arcs (W-Pad) | Regression of OCT pad_walk and pad_crouch; plus straight up (O-3a) | heights 705 / 441 / 882 (wiki 707.9 / 442.8 / 884) | apex z − pad z |
| O-5 | TS off pad (W-PadDir, B) | Sprint at the pad; jump at 36 / 24 / 12 cmds before contact (and none); after contact scroll W edges every 2 cmds × 12 with D held and yaw right 720°/s | if the pre-pad jump's lurch window survives the launch: heading change ≤ 0.5 s after the jump; none when there was no jump (RD1) | heading change after the launch; \|Δv\| per edge ≤ 0.7 × the sprint cap |
| O-6 | **Ceiling surf mechanism** (W-Pad, A) | Pad on flat floor under a flat ceiling at h = 250 u above the pad (and a 2000 u long ceiling); walk onto the pad holding W (stand), and crouched (hold Crouch); keep W until 0.3 s after ceiling contact | the wiki says you surf along the ceiling; **decisive reading: vz stays > 0 while z is pinned**, decaying at about 750 × 0.8 per real second; leaving the ceiling edge with vz > 0 throws you up | per-cmd z, vz, \|v_h\|, onGround flag; surf duration vs √(vz0² − 2gh)/g |
| O-7 | Ceiling surf height grid | As O-6, ceiling h = 150 / 250 / 400 / 600 u, stand vs crouch, with vs without W | duration falls as h rises (wiki); crouch better; W more consistent | duration, horizontal distance under the ceiling |
| O-8 | Pad wallrun (W-Pad2, A) | Pad in the wall corner; sprint at 20° to the wall; slide into the pad within 20 u of the wall; hold the side key into the wall, view into the wall | horizontal-only travel along the wall at pad speed | z flat while attached; v_h |
| W-1 | Phase regression (P3) | Into the Void from sprint | deploy 0.8 for 1.17 s; 414.98 for 2.77 s; 0.79 s fade | already measured |
| W-2 | Portal speed ramp (SRC-Rift, W-Portal) | Wraith ult; sprint straight 6000 u on flat ground, recording msc vs distance; then a variant starting on a 2000 u high ledge and dropping | msc steps at about 1200 u spacing (script); the % per step vs the wiki's 22/39/57/74 at 0/60/90/120 m; the 3D-distance rule on the drop | msc time series vs distance |
| W-3 | Portal exit velocity (SRC-Rift) | Place a portal while (a) sprinting, (b) sliding the last 200 u before placement, (c) crouch-walking; enter the other end from rest | exit velocity = the recorded placement velocity at the exit node (≈ 364–515 sprint, slide speed, 92 crouch), not a fixed 300 | velocity on the first free command after the replay |

Unity real-input demos should follow G-1, G-2, G-3, G-5, G-7, O-3, O-5, O-6/7 and Z-2/Z-3 once R confirms them. As in M9, nothing in the Reference model changes just to make a video sequence work (M10-PLAN A2: no hard-coded actions or speed bonuses for techniques).

## 7. To-watch list (for the user or a vision-capable reviewer; timestamps are the authors' own chapter marks)

| Priority | Video | Timestamp(s) | Why |
|---|---|---|---|
| 1 | V-MokOct https://youtu.be/uka85Jx_-yY | **01:52 Ceiling Surfing**; 03:24 Wallrunning; 06:02 Instant Direction Change | ceiling height, approach, stance and Forward timing for O-6/O-7 |
| 2 | V-MokSS https://youtu.be/hB0Wa2fCVAk | 02:37 grapple inputs; 03:37 grappling; **04:44 tilting the view line; 05:25 braking the view line**; 07:42 tips | camera and key timing for the Slingshot (G-1) |
| 3 | V-MokGr https://youtu.be/R7YOuYMohNY | **04:41 Super Grapple; 06:00 Backwards Slide Grapple**; 04:02 Grapple Hop; 07:28 Grapple Tap-Strafing; 08:14 Slingshots; 01:50 Angled Ziplines | G-2b, G-5, G-6 inputs; the grapple → TS combo |
| 4 | Cau7ioN V-Cau1 https://youtu.be/mlj9SBY7qq8 (20 Aug 2023) | no chapters (683 s) | Rodeo and advanced grapple as played by the player the wiki recommends for Rodeo (G-7) |
| 5 | V-Kovah https://youtu.be/DiB9vBvjgWE | no chapters (538 s) | Grapple Double-Bounce distances and angles (G-8) |
| 6 | V-MokPadDir https://youtu.be/ZxDwH37uT24 | from 0:15 (wiki link) | TS off pad and slide-through TS timing relative to pad contact (O-5) |
| 7 | V-MokS16 https://youtu.be/wIrGCO7VNkg | 00:00 Wraith (portal speed); 02:52 Pathfinder (zipline gun changes) | W-2 ramp; gun rope speed (Z-2) |
| 8 | V-Dirk https://youtu.be/x70w21VYtew; V-BOOL https://youtu.be/8CpQBWnzuo4 | whole (about 30 s each) | Rodeo laps: anchor height and radius |
| 9 | V-Gruic https://youtu.be/zfZ6wI1KEOo | whole (58 s) | Slide Grapple timing (G-5) |
| 10 | V-Baner https://youtu.be/3kYoyYOGjX0; V-Stras https://youtu.be/vm1brUdu_Uo | whole | ceiling-surf clips: ceiling height estimate |
| 11 | V-MokPadWR https://youtu.be/BEVo2RTMkq8 | whole (53 s) | pad wallrun (O-8) |
| 12 | V-MokZD https://youtu.be/cG13set9FwA | 01:16; 02:41; 04:05 | zip-dash family (removed, date unknown): decide whether any of it was live in S21 |

## 8. Open items for the leader
1. **The grapple detach rule:** test the wiki's three rules (passed the anchor, view turned away, Crouch) on a free-standing pole before any Unity grapple change (G-3). If a view-angle rule holds, SWING's turn_w result (still pulled at contact) needs re-reading: was its view–rope angle under the threshold?
2. **A/D during the pull (G-1b)** is the one missing measurement that decides whether RF plus wish-accelerate produces the Slingshot and Rodeo. Do it before modelling a swing state.
3. **The pad push ×1.2 (`PAS_ULT_UPGRADE_ONE`)** has no dated source. Check in R5 whether giving Mad Hops (or that passive) changes the launch speed; until then it is not S21.
4. **Stim re-use:** R5 and the script block re-use for 6 s; the pre-2026 wiki implies a 1.8 s delay. Decide which to keep (keep R5 unless O-2 shows otherwise).
5. **Portal exit velocity:** the M5 preset (300 u/s + 0.3 s lock) is a design value; the S21 script sets the recorded placement velocity. Fix this in the Wraith design before implementation (W-3).
6. **D2 corrections:** Maggie speed pads are S12 kit and S21-present (only the 6 s re-activation and sprint-only rules are later). Octane "double pad" in S21 = Mad Hops L2 upgrade, not base. Airborne Agility is an S21 L3 upgrade, not base.
