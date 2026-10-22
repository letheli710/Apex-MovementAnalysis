# M9 track D: traceable technique library (M9-A2), zipline evidence (A1), reproduction specs (A3)

Desk research only: no game, no Unity. Date 2026-10-22. This file extends `../../m8/d_techniques/TECHNIQUES.md` (M8-D). It does not repeat M8-D's mechanism mapping. It replaces M8-D's snippet-level sources with sources I read in full text, and it adds authors, dates, video timestamps and evidence levels.

## 0. Method, honesty rules and evidence levels

**What I could read**
- **Apex Movement Wiki (apexmovement.tech).** The site is a SvelteKit app, and WebFetch sees only the navigation. Its pages are bundled as **markdown source** inside the site's JS chunks, so I downloaded the chunks (`/_app/immutable/chunks/*.js`) and extracted 101 page sources. That is the full text, including the "Technique/Inputs", "Helpful Tips" and "History" sections. The pages are the **current (Oct 2026) wiki**: the velocity article says "Numbers up to date with S27". Each page's History section dates the technique. I cite pages by their wiki URL (the path the wiki itself links to).
- **YouTube.** I read video **titles, channel names, publish dates and descriptions**, including the chapter timestamps that authors wrote. **Transcripts could not be read.** The caption endpoints return empty bodies without a player token, and third-party transcript sites block scripted access. **I watched no video.** Every claim about what a video shows is the author's own chapter title or description, quoted as such. Nothing in this file comes from frame analysis or an on-screen overlay.
- **Other web text:** ProGuides (full HTML read this time, not a snippet), apexlegends.wiki.gg (raw wikitext, including a **June 2024 revision**, which is S21-era), PCGamesN, and search summaries for the 2021 tap-strafe announcement.
- **Local source (read-only):** `C:\Workspace\Playground\ReApex-DataAnalysis\research-src\s21-platform\scripts\vscripts\...` (S21 game scripts) and `...\research-src\s21-r5sdk\src\...` (the R5 SDK bridge). No game binaries were scanned.
- **Blocked:** Reddit (403), Medium (Cloudflare), esports.net, youtubetotranscript, and the Discord servers. Those sources appear as links only.

**Evidence levels** (per technique, and per claim where they differ)
- **A**: a source I read in text states the inputs and their order/timing explicitly.
- **B**: described in text, but the inputs are incomplete or ambiguous.
- **C**: a name, a video title or a chapter timestamp only.
- **measured**: matches an HSD R5 measurement (file + number cited).
- **contradicted**: conflicts with an HSD R5 measurement.
- **[src]**: S21 script / SDK constant read locally.

**Version rule.** The wiki is a living document. I mark a technique as **S21-present** only when the source dates it before S21 (S21 = 7 May – 6 Aug 2024) and nothing removes it before then. Wiki numbers ("up to date with S27") are **not** S21 values unless an HSD measurement or the S21 script agrees.

Local measurement files cited (all under `research/phase2-local/`): `m6/a1_lurch/A1-LURCH.md` (A1), `m3/M3-REPORT.md` (M3), `m6/a2_climb/A2-CLIMB.md` (A2), `m6/a3_zip/A3-ZIPLINE.md` (A3), `m8/r_lurch/LURCH.md` (RL), `m8/r_sg/SG.md` (RSG), `m8/r2_revenant/REVENANT-CLIMB.md` (RRev), `m8/r2_vantage/VANTAGE-JETDRIVE.md` (RVan), `m8/unity/M8B-UNITY.md` (M8B).

## 1. Top findings

1. **The wiki numbers that we can check agree with our R5 numbers.** This raises confidence that the wiki input descriptions transfer to our build:

   | Wiki value | HSD R5 value |
   |---|---|
   | Slide boost 150·msc, capped at 400·msc | SG exit min(v + 172.5, 460) (RSG) |
   | Superglide ≈540 (3D) | √(460² + 286²) = 542 |
   | Zip jump ≈490 | √(400² + 289.8²) = 494 (A3) |
   | Super jump ≈690 | √(400² + 564²) = 691 (A3 §9.2) |
   | Zip crouch ≈400 | 400 (A3) |
   | `mountZiplineTime 0.5`, `ziplineAcceleration 400`, `ziplineJumpOffSpeed 400` | 0.5 s mount state, then 400 u/s², and the 400 exit cap (A3 §2–3) |
   | Climb peak 225 | 226 (RRev) |
   | Walk 199.53 | 199.5 |

   Pounce: the wiki/EladNLG values (35° arc correction, −15° ideal, 75° max down, 20°/200 u ground check, 0.9 s + 1.3 s holds, 0.75 s climb lock) equal the S21 script constants [src].
2. **Lurch rules: three agree, one conflicts, two untested.**
   - Agree: "holding a key before the jump never lurches", "held Left + pressed Right = null lurch" and "held Right + pressed Forward = diagonal" are all **measured** (RL b1, b2).
   - Conflict: the 400 ms window (full 200 ms, then linear decay) **contradicts** the measured 0.5 s fade end (A1 §7, M3).
   - Untested: two of the wiki's combination rules (Left + Forward held, Right pressed → forward; Forward + Back held, Right pressed → right). Both are cheap R5 trials (§4).
3. **LS/RAS has no input definition in readable text.**
   - The wiki says its advanced lurch-strafe section is being revamped and points to Zeddo (2022) and Xzylas (2024) videos, which I could not watch.
   - The only explicit text is ProGuides 2023 ("Ras strafe: A + jump, then W, D … S") and the wiki's **OG Ras strafe** = "mastered Momentumshift": turn straight backwards into a jump slide without turning the camera, "only out of a walk".
   - **No source gives an initial speed, key spacing or angle.** The M8 156° result (sprint jump 299, W→W+D→D→S+D→S, 0.05 s spacing) is one point and not a ceiling. The sources point to a **walk-speed (≈200) entry** for the full reversal and say higher speeds need "more advanced lurch strafes" (§3.6, §4).
4. **Zipline mid-rope mounting is normal community behaviour, both in S21-era text and today.** Nothing I read says a mount is restricted to the rope ends:
   - **S21-era text** (wiki.gg, June 2024): horizontal ziplines ride "in either direction, regardless of incline", and you "reconnect … after a brief delay".
   - **Current wiki:** you ride "from your interact point"; there is an interact range plus a look requirement of 35° on the ground, extended to 90° in the air by **Mid Air Interact** (Aug 2022, before S21); the travel direction follows your look (vertical ropes prefer up); and there are 3 re-grabs, reset on ground/mantle, +1 per 3 s.
   - Our R5 Find rule (130 u sphere around origin+72, cone 27–40.7°; A3 §1) fits the 35° ground cone.
   - **Our R5 build refused an air mount on the dedi** (A3 §9.4). That **contradicts** S21 community behaviour and should be treated as a probable bridge defect until R-track re-tests at close range.
5. **Version boundaries found:**

   | Change | Date | S21 relation |
   |---|---|---|
   | Zipline re-grab cooldown introduced | 23 June 2020 patch | before S21 |
   | Revenant rework: pounce and pounce tap strafe | S18, 8 Aug 2023 | present in S21 |
   | Pounce tap-strafe angle limit (lurch cap likely lowered) | ~17 Sep 2024 | after S21 |
   | Vantage Echo no longer needs LOS | S22, 6 Aug 2024 | after S21; the S21 script checks LOS + a 60° on-screen cone [src] |
   | Tap-strafe buffer added, then reverted | Jan 2025 | after S21 |
   | Official Mantle Boost | S27, 4 Nov 2025 | after S21; our R5 FSM boost is a backport, not S21 |
   | Echo dash / Echo TS / Echolevator | 2024–2025 sources | post-S21 |
   | Tap-strafe removal announced | 31 Aug 2021 | delayed, never shipped as removal before S21 |

## 2. Source register (sources actually read; date = publish date)

| Id | Source | Author | Date | What I read |
|---|---|---|---|---|
| W-Lurch | https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20Fundamentals%3ELurch%20Fundamentals%20Techpage (page source "Basic Lurch Tech": Lurch, Lurch stack) | wiki; co-written with Mephisto | live page | full text |
| W-BLT | https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3EBasic%20Lurch%20Tech%3EBasic%20Lurch%20Tech%20article (Momentumshift, OG Ras, Tap strafe) | wiki | live | full text |
| W-LS | https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20strafe%3ELurch%20Strafing%20article | wiki | live | full text (a guide index only) |
| W-Air | https://apexmovement.tech/wiki/tech/General%20Tech%3EFundamentals%3EAir%3EFundamental%20Air%20Tech%20article (Air strafe, Lurchless, Coyote) | wiki | live | full text |
| W-Ground | https://apexmovement.tech/wiki/tech/General%20Tech%3EFundamentals%3EGround%3EFundamental%20Ground%20Movement%20article (Jump, Jump fatigue, Bunnyhop) | wiki; fatigue rewritten Sep 2025 with Ilses | live | full text |
| W-WB | https://apexmovement.tech/wiki/tech/General%20Tech%3EWall%20Tech%3EWallbounce%3EWallbounce%20article | wiki | live | full text |
| W-SG | https://apexmovement.tech/wiki/tech/General%20Tech%3EMantle%20Tech%3ESuperglide%3ESuperglide%20article | wiki | live | full text |
| W-MB | https://apexmovement.tech/wiki/tech/General%20Tech%3EMantle%20Tech%3EMantle%20boost%3EMantle%20boost%20entry | wiki | live | history |
| W-Zip | https://apexmovement.tech/wiki/tech/General%20Tech%3EZip%20Tech%3EZipline%20Basics%3EZipline%20basics%20article (Basics, Mid Air Interact, Zip jump, Zip crouch) | wiki; Mid Air entry drafted by Raptor | live | full text |
| W-SJ | https://apexmovement.tech/wiki/tech/General%20Tech%3EZip%20Tech%3ESuperjump%20Variations%3ESuperjump%20variations%20article (Super jump, Mantle jump, Gorilla jump) | wiki; Theeb, Fat9L, thevilnside | live | full text |
| W-Dis | https://apexmovement.tech/wiki/tech/General%20Tech%3EZip%20Tech%3EDismounts%20%26%20Juking%3EDismounts%20%26%20Juking%20article (Mantle crouch, Mantle ladder, Float jump, Air dance, Ghost jump) | wiki | live | full text |
| W-Carry | https://apexmovement.tech/wiki/tech/General%20Tech%3EZip%20Tech%3EZipline%20Carries%3EZipline%20Carries%20Tech%20page (Carry, Bounce-carry, Hyper jump) | wiki; G0f, Raptor | live | full text |
| W-Weird | https://apexmovement.tech/wiki/tech/Map%20Tech%3ESpecific%20weird%20Ziplines%3ESpecific%20weird%20Ziplines%20article | wiki | live | full text |
| W-Myst | https://apexmovement.tech/wiki/tech/Mysteries%20%26%20Removed%20Tech%3EMysteries%3EGeneral%20Mysteries%3EMysteries%20article (Zipline Zones, 45° zips, momentum-carry exit) | wiki / Mokeysniper | live | full text |
| W-Rem | Removed General Tech page (Infinite Interact Spam, Ultra jump) | wiki | live | full text |
| W-Pounce | https://apexmovement.tech/wiki/tech/Legend%20Tech%3ERevenant%3EShadow%20Pounce%3EPounce%20Tech | Mokeysniper (first person) | live | full text |
| W-RevP | Revenant Passive page (basics, re-attach, Corner Wallrun) | Mokeysniper with EladNLG | live | full text |
| W-Echo | https://apexmovement.tech/wiki/tech/Legend%20Tech%3EVantage%3EEcho%3Eecho%20article | wiki | live | full text |
| W-Vel | "Velocities collected in one place" article | Mokeysniper | 8 Jun 2025, numbers S27 | full text |
| W-Tim | "Timings collected in one place" article | Mokeysniper | 16 Jun 2024 (S21) | full text |
| PG | https://www.proguides.com/guides/apex-legends/learn-these-epic-movement-mechanics-in-apex-legends/ | ProGuides | 11 May 2023 (mod. 3 Jul 2023) | full HTML |
| WG-MF | apexlegends.wiki.gg "Map Feature", revision of **17 Jun 2024**, section Ziplines | wiki.gg editors | S21-era | raw wikitext |
| WG-Zip | https://apexlegends.wiki.gg/wiki/Zipline | Jockshocker | created 20 Aug 2024 | raw wikitext |
| WG-P20 | https://apexlegends.wiki.gg/wiki/June_23,_2020_Patch | wiki.gg | patch 23 Jun 2020 | raw wikitext |
| PCG | https://www.pcgamesn.com/apex-legends/tap-strafe-nerf | PCGamesN | updated 8 Jan 2025 | full text |
| SRC-Pounce | `research-src/s21-platform/scripts/vscripts/weapons/mp_ability_revenant_shadow_pounce_free.nut` lines 48–65 | S21 script | — | constants |
| SRC-Echo | `.../weapons/mp_ability_companion_launch.nut` (`CanLaunchToCompanion`, lines 648–712; constants 73–91); `.../weapons/sh_vantage_companion.nut` lines 78–134 | S21 script | — | code |
| SRC-Zip | `research-src/s21-r5sdk/src/game/server/zipline_disconnect.cpp`, `zipline_cooldown.cpp`, `zipline_exit_parity.cpp` (`Zipline_Find` signature, line 128); `src/engine/server/zipline_validation.cpp` lines 2134–2136 | R5 SDK bridge | — | code + comments |

**Video sources (description and chapters read; not watched)**

| Id | Video | Channel | Date | Chapters relevant (author's own) |
|---|---|---|---|---|
| V-Zed1 | https://youtu.be/-0cK8B07MFs "HOW TO: Lurch Strafe (Beginner/Intermediate)" | Zeddo | 11 Jul 2022 | none in description (6:06 long) |
| V-Zed2 | https://youtu.be/e2gXI5-wMus "HOW TO: ADVANCED LURCH STRAFE PART 1" | Zeddo | 25 Oct 2022 | none (13:21) |
| V-Xzy | https://youtu.be/JonGQ6F_p6E "NEO STRAFE WITHOUT CONFIGS: A COMPLETE LURCH GUIDE" | Xzylas | 14 Feb 2024 | 03:12 changing lurch directions; 04:16 mini neo, fwd/back lurches; 05:23 neo strafe; 07:18 snake / backwards snake; 08:56 magic strafe; 09:18 silly strafe; follow-along half/full speed 10:20–12:10 |
| V-Xzy2 | https://youtu.be/zlSkzpik4Js "The ULTIMATE Full Movement Guide" | Xzylas | 16 Apr 2023 | 00:55 tap strafing; 1:43 wall bounces; 3:30 fatigue bounces; 7:29 supergliding; 8:19 directional SG; 9:54 bhopping; 10:49 lurches; 12:16 Ras strafes / bhop lurches; 15:06 zipline / super jump; 15:34 mantle jumps; 16:19 mantle cancels / zip dancing; 17:24 ghost jumping |
| V-RU | https://youtu.be/lp8DvQ9qW7I "ЛУЧШИЙ ГАЙД ПО LURCH STRAFE" (the wiki says it has the most complete keyboard-overlay slow-motion showcase) | "Lurch" | 24 Jun 2024 | 01:41 table; 02:35 Pito; 03:17 RAS; 04:17 RAS variations; 05:17 snake; 05:45 double tap; 06:58 backward snake; 07:51 neostrafe; 09:22 magic; slow-motion repeats 10:51 Pito slow, 11:26 RAS slow, 11:52 RAS var. slow, 12:14 snake slow, 12:38 double tap slow, 13:17 neo slow |
| V-Swe | https://youtu.be/PpNa7Y3JsZY "Lurch strafes - how to become UNHITTABLE IN 1v1s" | Sweloh | 4 May 2023 | the description says it covers "more advanced RAS strafes"; no chapters |
| V-H1y | https://youtu.be/PL-xWPoR9tM (Korean subtitles) | H1yaA | 6 Oct 2023 | 02:03 lurch vs tap strafe; 03:28 method and theory; 04:57 consecutive + practice |
| V-Jon | https://youtu.be/FUKp93wVwzw "How to bunnyhop 'neo' strafe (no configs)" | Jonza | 5 Jun 2023 | none |
| V-Pito | https://youtu.be/jF28uOF7Gsc "Pito's insane octane strafe tutorial" | Gruic | 2 May 2022 | none |
| V-Yuki | https://youtu.be/-fAHHNLCytQ "How to Yuki Strafe" | eskyja | 19 Jun 2022 | none; credits the creator's original video |
| V-MokTS | https://youtu.be/pP5CBIpirHA "TAP-STRAFING" | Mokeysniper | 26 Aug 2020 | 02:06 tutorial section |
| V-Zweek | https://youtu.be/AjPSwwnKm1o "The mechanic that shaped Titanfall speedruns" | zweek | 26 Apr 2022 | 2:01 what is strafe lurch; 8:01 tapstrafe era; 12:15 input emulation |
| V-MokSG | https://youtu.be/_cP1YO5Idts "This is why you still Can't Superglide" | Mokeysniper | 31 Oct 2023 | 01:06 basic mechanics; 02:48 FPS dependent?; 04:39 jump-crouch timing; 07:00 mantle timing; 13:09 hardware |
| V-MokNoMa | https://youtu.be/v9y0wcyugkY "NO-MA BOUNCE" | Mokeysniper | 31 May 2024 | levels 0–4, 00:37–06:10 |
| V-MokMJ | https://youtu.be/-cMBnwNCC24 "MANTLE-JUMP" (title says outdated, see pinned comment) | Mokeysniper | 28 Jun 2022 | none |
| V-MokHyp | https://youtu.be/Rj7oJh1ZWMw "Zipline HYPER Jumping" | Mokeysniper | 15 Jul 2021 | none |
| V-MokZone | https://youtu.be/1USJXOMVRsQ "Zipline Zones and how they 'break' some vertical Ziplines" | Mokeysniper | 4 Dec 2024 | theory in the description (§5) |
| V-Ghost | https://youtu.be/MsIAQiuLt2I "Ghost Jump" | thevilnside | 1 Dec 2022 | none |
| V-Set3 | https://youtu.be/VRmCM5PqcV0 "Zipline ghost interact" | Set3kh | 29 Aug 2022 | none |
| V-Allu | https://youtu.be/8xxiX2ZNgSI "Zip Strafing" | Alluringly | 16 Aug 2024 | 1:11 interaction zone; 2:00 interaction limit; 2:30 basic combos; 11:03 zipline walljump |
| V-Tree | https://youtu.be/o7z7TG83JPI "New Zipline Movement Tech - Part 1" (mantle crouch) | Treeree | 30 Aug 2022 | none |
| V-Butt | https://youtu.be/Gm68Kyf3juc "ELITEJUMP" | Buttonsie | 4 Sep 2021 | none |
| V-MokRevTS | https://youtu.be/8VyVYt4HdQY "How to REVENANT TAP-STRAFE" | Mok3ysnip3r | 9 Aug 2023 | 45 s clip |
| V-MokRev | https://youtu.be/Tz3OcCXjNCU "The NEW MOVEMENT MECHANICS of Revenant Reborn" | Mokeysniper | 27 Aug 2023 | 02:05 tactical basics; 03:30 distance; 05:29 speed; 06:52 over obstacles; 09:05 down terrain; 15:10 tap-strafe; 18:41 passive fundamentals; 21:38 re-attach |
| V-Verzz | https://youtu.be/qqcq9fUqr2g "Super Glide Tutorial" | Verzz | 30 Mar 2021 | none |

## 3. Technique library

Format per entry: **Sources**, **Inputs (only as stated by the source)**, **Limits / failures / chains**, **Version**, **Evidence**.

### 3.1 Lurch (single) and lurch direction rules
- **Sources:** W-Lurch (full text); V-Zweek (C, TF2 history).
- **Inputs (W-Lurch):**
  - Have momentum, press Jump, then press a direction "up to 400ms after the Jump".
  - Releasing a key does not lurch. A key held before the jump does not lurch.
  - Strength is full for 200 ms, then decays linearly to 0 at 400 ms.
  - The direction is "the combined direction of all active directional inputs". Examples: held Left + pressed Right = null lurch; held Right + pressed Forward = ↗; held Left + Forward, pressed Right = ↑; held Forward + Back, pressed Right = →.
  - The lurch window continues through a zipline mount or a mantle.
  - A speed cap of "between 1150hu/s and 1300hu/s" (the Velocities article: cap ≈1200, a "threshold" ≈850; S27 numbers).
- **Version:** inherited from TF2 and present since launch. The ~17 Sep 2024 pounce/TS change (Eraised; Chaosmonkey measured it) suggests the cap was lowered then, which is **after S21**.
- **Evidence:** **A** (inputs). **Measured:** held key before the jump = no lurch (A1 turn_hold_w); null lurch on opposing keys (RL b2: no lurch); held A + pressed W = 45° diagonal (RL b1). **Contradicted:** the window. R5 fades to 0 at **0.5 s** (full to 0.2 s; A1 §7, M3 ±1 ms), not 0.4 s. **Untested:** the two three-key examples (↑ and →) and the cap (SDK 1100 [src], A1 §8).

### 3.2 Lurch stack
- **Sources:** W-Lurch.
- **Inputs:** Jump, then press the same direction repeatedly. Holding the main key blocks a second bind (for example a scroll forward) from registering. Changing the set of active keys "ends" a stack (a naming rule).
- **Evidence:** **A**; **measured** (A1 §3: three clamped presses in one jump, no budget). The "stack ends" rule is naming only; in R5 every edge is an independent lurch (A1).

### 3.3 Tap strafe (TS)
- **Sources:** W-BLT (full text); V-MokTS (C, tutorial at 02:06); PG (text); PCG (version).
- **Inputs (W-BLT):**
  - Sprint, Slide, let go of Forward, hold a sideways key, Jump.
  - Then stacked Forward inputs, manually or (recommended) with Forward bound to the mouse wheel, while turning the view the same way as the side key.
  - "DO NOT hold Forward" while scrolling.
  - Sync the scroll rate with the turn rate; "It's not a super fast flick".
  - Variants: no slide jump is needed (only momentum + a jump); side keys are optional; back + left/right while scrolling "nullify" the forward lurches → pure side lurch, called "fundamental Lurch strafing".
- **Limits:** keyboard only (lurch is digital). The scroll bind is a config choice. Failure: holding W, or scrolling/turning too fast.
- **Chains:** out of wall bounce, jump-pad double jump, super jump, mantle jump, pounce, Echo (later section).
- **Version:**
  - Removal announced 31 Aug 2021, then delayed for "unexpected side effects" (search results; M8-D Dexerto); not removed before S21, and our R5 TS works.
  - Jan 2025 mid-season "buffer to tap strafes" was reverted after it changed movement "more than we intended" (PCG). Post-S21.
- **Evidence:** **A**; **measured:** 360°/s −81.0° (A1 §4); 720°/s −161.2°; 1440°/s heading ≈30° behind the view (RL c).

### 3.4 Momentumshift
- **Sources:** W-BLT; the wiki credits Mendo, within a week of launch.
- **Inputs (W-BLT):** Sprint, Slide, let go of Forward, Jump. Then press Left, Backwards, Right (or Right, Backwards, Left) while turning the view 90° toward the first key. Result: momentum redirected "90 degree backwards". Practice tip: tap the directions "in a circular motion".
- **Version:** since launch; S21-present.
- **Evidence:** **A** (order and camera stated; no key spacing stated). **Measured as a mechanism** with the camera fixed (A1 "shift": R, B, L 0.067 s apart, 297 → 78 u/s, clamp on each press). **Never recorded as the wiki sequence** (with the 90° turn) → spec R-4.

### 3.5 OG Ras strafe / "mastered Momentumshift" (the reversal)
- **Sources:** W-BLT (full text); PG (text); local REPORT G021 calls it "early RAS".
- **Inputs:**
  - W-BLT: with good lurch timing you can "turn straight backwards and land in a Jump slide, without having to turn your camera. This is also known as a OG Ras strafe. This only works out of a walk. At higher speeds you need more advanced Lurch strafes."
  - The key order is inherited from Momentumshift (side, back, other side) but **not restated** for the camera-fixed form.
- **Evidence:** **B** (order implied, not stated; no spacing). **Consistent with our model:** M8B Unity walk jump D→D+S→S at 0.05 s = 162° keeping 98% [model]; the same chain from 299 keeps 72%. **Not R5-measured at walk speed** → spec R-5.

### 3.6 Lurch strafe (LS) chains: Ras, Yuki, Pito, Neo, snake, magic, silly, "spins"
- **Sources:** W-LS (an index only; it says "We are working on fully revamping how advanced Lurch strafes are presented"); PG (text); videos V-Zed1, V-Zed2, V-Xzy, V-RU, V-Swe, V-H1y, V-Jon, V-Pito, V-Yuki (C).
- **Inputs from text:**
  - **Ras strafe (PG, 2023):** "press A and jump, hit W and then D as you tap strafe as well as S at the same exact time". The order of W/D/S is ambiguous: is S simultaneous with D, or with all? → **B**.
  - **Yuki strafe (PG):** W + A, jump, then S + A "as you tap strafe" → **B** (no timing).
  - **Neo strafe:** both video titles say "without configs" (V-Jon, V-Xzy), and a search result shows paid macro tools advertising neo strafe. That implies the original was a config/macro trick. No inputs in text → **C**.
  - **Pito, snake, backwards snake, magic, silly, double tap:** chapter names only (V-Xzy, V-RU) → **C**.
  - **"Front/back spins":** no source I read uses this name; the closest are the Pito/magic chapters → **C** / unidentified.
- **Version:** Yuki (Jun 2022), Pito (May 2022), Zeddo LS (Jul/Oct 2022), PG Ras (2023), Xzylas (Feb 2024), RU (Jun 2024). All are S21-era or earlier as names; the inputs are not documented in text.
- **Evidence:** **B/C.** In our model they are all lurch chains with changing wish directions (M8-D §3.4). The M8B demos `m8b_snake` (+49° / −45°, 299 kept) and the key-only spin D, S, A, W every 0.05 s (450–515°, speed down to 25–40%) are **[model]**, not reproductions of any named author sequence.
- **The best "to watch" source for inputs is V-RU:** the wiki says it has "the most completely showcase of clips with Keyboard overlays in slow motion", and its slow-motion chapters are listed above.

### 3.7 Lurchless air strafe
- **Sources:** W-Lurch, W-Air.
- **Inputs:** hold Left **and** Right before the jump, press Jump, release the undesired key, then air strafe immediately. Alternative: wait 0.4 s after the jump. Side input during a slide barely changes the slide jump.
- **Evidence:** **A.** Partly **measured**: a held key gives no lurch (A1); opposing keys give no lurch (RL b2). The release-one-key step is untested → spec R-2.

### 3.8 Air strafe / skiing
- **Sources:** W-Air.
- **Inputs:** side key + view turn at "the correct speed" (slower when faster). Values: Air acceleration 500, Air speed 60.
- **Evidence:** **A** (qualitative); **measured:** 500 u/s² and wish cap 60·msc = 69 (M2, A3 §3).

### 3.9 Coyote time
- **Sources:** W-Air, W-Tim.
- **Inputs:** leave a standable surface, then Jump within **0.2 s**. Zipline mounts and abilities do not interrupt coyote time; starting a climb does. Super jumps and Float jumps rely on it.
- **Evidence:** **A.** **Partly measured:** super-jump window 3–8 commands applied, ≥ 63 not (A3 §9.2). The 0.2 s edge (24 commands at 120 fps) is unmeasured → spec R-13. Note RL d: a walk-off opens no **lurch** window; that is a different timer.

### 3.10 Bunny hop / jump fatigue
- **Sources:** W-Ground, W-Tim.
- **Inputs (W-Ground):** hit the ground and press Jump "as quickly as possible", repeatedly. Fatigue values:
  - Fatigue: the jump within 0.15–0.75 s after landing is lowered (16.3 u for 0.15 s, linear to 56 u at 0.75 s); `antiMultiJumpTimeMin 0.15`, `Max 0.75`, `HeightFrac 0.3`.
  - Fatigue is turned on by ground / coyote / climb / pad jumps, and **not** by zipline or mantle jumps.
  - Speed: leaving the ground within 1 s of landing (`skip_time`) costs "up to 100hu/s * speedMultiplier" when above sprint speed.
- **Evidence:** **A.** **Measured:** fatigue frac 0.3, 0.15 / 0.75 s (M2, M8B). **Unresolved:** M3 found `skip_speed_reduce` unobserved and says min(v, 299) and max(v − 100, 299) "cannot be told apart below 399 u/s" (M3 line 107). → spec R-10 (hop at 450/600).

### 3.11 Wall bounce family
- **Sources:** W-WB (full text); V-Xzy2 1:43 / 3:30 / 6:23 (C).
- **Inputs, Basic (W-WB):**
  - Sprint, Crouch → slide, Jump.
  - Look fairly perpendicular (you can turn up to 45° away).
  - Let go of Forward before the wall.
  - Hit the wall at the jump apex or slightly after, then Jump after contact. Only a jump inside the climb "Green zone" bounces; the lower in the zone, the higher the bounce.
  - The exit direction depends on the approach angle and side inputs, not on the view.
- **Inputs, other variants:**
  - **Jump-fatigue bounce** (thevilnside, 31 Mar 2021): stand at the wall, Jump, after landing hold Forward, Jump at the wall (climb), release Forward, Jump.
  - **No-Ma bounce** (MobileMinigun / Jay, 4 Aug 2023; Mokey tutorial 31 May 2024): fatigue jump, then hold Forward + Sideways, turn ≥ 5° (≈10° recommended) toward the side key, Jump to climb, Jump to bounce.
  - **U-bounce** (Jay, 4 Dec 2022) and **bounce chains** are described too.
- **Velocities (W-Vel, S27):** wall bounce 350–484, mini 278, crouch kick 320, wall push 258.
- **Version:** the basic bounce dates from Feb 2019. All variants above are dated before S21.
- **Evidence:** **A** (basic, fatigue, No-Ma); **measured:** the bounce restarts the lurch window (A1 §6). The exit speeds vs the wiki 350–484 are not yet compared → spec R-8.

### 3.12 Superglide and variants
- **Sources:** W-SG (full text); V-MokSG (C, chapters); V-Verzz (C).
- **Inputs (W-SG):**
  - Sprint, mantle; "In the last 0.15 second of a mantle": Jump, then Crouch 1 frame later.
  - Hardware / FPS sensitivity is discussed.
  - The mantle pull takes 0.3 s and completes even if Forward is released.
- **Variants:**
  - **Sideways SG:** release Forward during the pull and switch to a side key before the SG inputs.
  - **Backwards SG:** release Forward in the pull, look up > 25° (so S does not cancel the mantle), hold Back, then SG. Without the look-up, Back must be pressed exactly 1 frame before the SG inputs.
  - **Glide-bounce:** SG into a wall, wait "a tiny moment", Jump (30–50 u objects work).
  - **Glide-boost:** SG into a climb end boost (90–100 u objects).
  - **Insta-glide:** SG after an insta-mantle (2024).
- **Version:**
  - SG was discovered by Verzz on 30 Mar 2021 and is S21-present.
  - Backwards SG with speed boost: thevilnside, 8 Jan 2022.
  - The look-up method was shown on 27 Apr 2024, just before S21.
  - Insta-glide: Apr 2024.
  - **Mantle Boost (official) arrived in S27 (4 Nov 2025)**: post-S21. Our R5 FSM boost (388.7 / 367.4) is a backport and is not S21-official behaviour.
- **Evidence:**
  - **A** (basic, sideways, backwards).
  - **Measured:** native SG 460 at H90–H232; the jump + crouch order (RSG).
  - **Contradicted in detail:** the wiki's "last 0.15 s". R5 succeeds at ≤ 0.085 s left, is mixed at 0.086–0.12 s, and cuts above 0.12 s (RSG table).
  - **Agrees:** the wiki "Slideboost cooldown 2 sec" (W-Tim) with R5's "no SG after a slide-jump approach" (RSG 0/15; boost not re-armed).
  - **Untested:** sideways SG with only a side key (RSG open 4) and backwards SG → specs R-7a/b.

### 3.13 Zipline: zip jump, zip crouch, carry
- **Sources:** W-Zip, W-Carry.
- **Inputs:**
  - **Zip jump:** Interact, Jump (any delay). Does not activate jump fatigue.
  - **Zip crouch:** Interact, Crouch.
  - **Zipline carry:** Interact a **horizontal** zip, then Jump or Crouch "on the next frame". The zip does not get to adjust your direction, so prior speed is carried; the 400 exit cap still applies, with jump speed added after the cap. The timing equals the SG timing, so the Superglide trainer is recommended.
- **Version:** zip jump/crouch since launch. The carry was first noticed via a Set3kh clip and understood around **June 2025**, but the mechanism probably existed earlier (it was thought to be part of Mid Air Interact, Aug 2022).
- **Evidence:**
  - **A.** **Measured:** v_out = ĥ_rope·min(v, 400) + ẑ·289.83, 125 exits, residual 0 (A3 §3, §9.1); jump-off one command after the mount gave (0, 0, 289.8) **from rest** (A3 z5b M=1).
  - **Untested:** the carry with a perpendicular running entry → spec R-12.
  - **Contradicted:** the wiki line "Manual disconnect maximum: 445hu/s" (also "slowing you down to 445" in W-Myst). R5 caps the horizontal at **400**. The wiki's own `ziplineJumpOffSpeed 400` and the carry page agree with 400.

### 3.14 Zipline super jump, elite jump, mantle jump, gorilla jump, hyper jump
- **Sources:** W-SJ, W-Carry, V-Butt (C), V-MokMJ (C), V-MokHyp (C).
- **Inputs:**
  - **Super jump:** be on the ground or in coyote time; MnK: Interact, then scroll-wheel Jump (two jump edges); controller: Interact-Jump, Jump.
    - Looking up gives a bigger jump.
    - Delaying both jumps rides the zip first.
    - Delaying only the second jump gives a lower result.
    - On vertical zips you jump the way you look; on horizontal zips it goes roughly straight up when still, along the zip when moving.
    - **Slide super jump:** hold-crouch, then Interact during the crouch-down animation.
  - **Elite jump** (Buttonsie, 4 Sep 2021): Interact, turn, then the two jumps within coyote time.
  - **Mantle jump** (thevilnside, 16 Jun 2022):
    1. Interact, and hold Forward + Interact.
    2. Jump into a mantle, keeping Forward until the mantle animation nearly ends.
    3. Switch Forward → Backward to cancel.
    4. Look straight up or down.
    5. Interact, Jump, Jump.

    Failure causes from thevilnside's Q&A:
    - cancel too low → hit the ledge;
    - jump before the interact → no super jump;
    - not enough flick down → missed interact;
    - Forward released before the ledge → no mantle.
  - **Gorilla jump** (Dulzura, 3 Dec 2022): the same, with no Forward and Back or Crouch to cancel, looking down.
  - **Hyper jump** (TravisXD, 1 Jul 2021; Mokey, 15 Jul 2021): super jump, then a zipline carry when the prompt reappears mid-air.
- **Version:** all before S21. **Ultra jump** was removed with the Zip-dash patch (date not given).
- **Evidence:** super jump **A + measured** (A3 §9.2: second press 3–8 commands after leaving the ground, +289.83 impulse, 5/5 per condition; 0/40 at ≥ 63). Mantle/gorilla/hyper: **A** (inputs) but **not measured**; they need mid-air interact and mantle cancel, both open in R5.

### 3.15 Mid Air Interact (formerly "Ghost Interact"), Ghost jump
- **Sources:** W-Zip, W-Dis, V-Set3 (C), V-Ghost (C).
- **Inputs (W-Zip):**
  - Be in the air. Facing between 35° and 90° horizontally from the zip, press Interact. Beyond 90°, look straight up or down, then Interact.
  - Works on zips of all angles.
  - The grounded prompt appears up to 35° horizontal; in the air up to 90°.
  - Does not work looking down while jump-fatigued; works looking up.
  - ADS blocks the grounded interact (only the mid-air prompt shows).
  - A small "promptless interact" radius exists.
  - Use cases: grabbing a zip while falling, **re-grabbing a zipline you jumped off**, interacting with one you passed.
- **Ghost jump:** a Mid Air Interact, then Jump.
- **Version:** discovered by Set3kh (wiki: 22 Aug 2022; video dated 29 Aug 2022); thevilnside's video 1 Dec 2022. **S21-present.**
- **Evidence:** **A.** **Contradicted by our R5 build:** the air grab at 120 u was predicted by the client but **refused by the dedi**, three times per trial (A3 §9.4); an earlier air test was out of range (A3 §5). Treat this as a probable R5 bridge/server divergence, not S21 behaviour, until a close-range (≤ 40 u) re-test → spec R-14.

### 3.16 Zipline juking and re-mounting: air dance, mantle crouch, mantle ladder, float jump, zipline strafing
- **Sources:** W-Dis, W-Zip, V-Tree (C), V-Allu (C).
- **Inputs:**
  - **Air dance** (thevilnside, 28 Feb 2022, **vertical zips at full speed**):
    1. Hold Back + Interact.
    2. Jump to disconnect.
    3. Switch Back → Sideways.
    4. Turn 180°; halfway through the turn, switch Sideways → Forward.
  - **Mantle crouch** (RMSB, before Aug 2022; Treeree tutorial 30 Aug 2022):
    1. Ride, holding Interact; Jump toward a mantle edge.
    2. Hold Crouch right after, to cancel the mantle.
    3. Look down while dropping and release Crouch.
    4. Crouch again = zip crouch. Without looking down you ride **up**.
  - **Mantle ladder:** the same, looking up, then Jump again.
  - **Float jump** (thevilnside, 29 Nov 2021): behind a zip, Interact, Crouch, Jump (in coyote time).
  - **Zipline strafing:** zip crouch, turn, re-interact **before leaving the interact range**, touching ground in between (resets the re-grab limit).
- **Version:** all before S21; Alluringly's video (16 Aug 2024) is just after S21.
- **Evidence:** **A** (inputs); none measured. They prove that community play routinely **re-mounts mid-rope** (zip strafing, air dance, mantle crouch) and that each re-interact picks its direction from the look.

### 3.17 Revenant Shadow Pounce, pounce tap strafe
- **Sources:** W-Pounce (Mokeysniper, first person); V-MokRev (C, chapters); V-MokRevTS (C); SRC-Pounce [src].
- **Inputs (W-Pounce):**
  - Tap Tactical = small pounce after a 0.9 s delay. Hold and release Tactical = bigger pounce; distance grows up to **2.2 s** of hold.
  - The pounce is aimed 35° above the view ("angle correction").
    - Up to 15° up gives the same distance.
    - Beyond 15° up loses velocity.
    - Looking ≥ 20° down fixes the launch at 15° up (fastest).
    - If no ground is within 200 u along the view, you can pounce downward, 1150 at full charge.
  - Velocity table: pounce ≈1300 (W-Vel, S27).
- **Pounce tap strafe** (Mokey, found 8 Aug 2023, guide 9 Aug 2023):
  1. Hold Tactical.
  2. Jump.
  3. Release Tactical and do the TS inputs.

  "It does not work if you jump after releasing". Since the lurch cap change: below −6° pitch only with holds < 2 s.
- **Climb lock:** 0.75 s after the pounce (≈ 20 m at full charge).
- **Version:** the rework is S18 (8 Aug 2023), so it is S21-present. The **TS angle limit appeared ~17 Sep 2024, post-S21.** In S21, a pounce TS at any angle is expected to work (the wiki's history implies no cap issue before Sep 2024).
- **Evidence:**
  - **A** (pounce; pounce TS order stated, no spacing).
  - **[src]** constants equal: MAX_IDEAL_UP_ANGLE −15, MAX_DOWN_ANGLE 75, GROUND_CHECK 20° / 15° / 200, MAX_EYE_ANGLE_INCREASE 35, VELOCITY_MULTIPLIER 700 / 1150, MAX_HOLD 1.3 (0.9 + 1.3 = 2.2), WALL_CLIMB_DISABLE 0.75.
  - **Measured:** v = (700 + 450c)·dir(pitch − 35°) (M4); the 0.75 s climb lock (RRev).
  - **Open:** pounce TS vs the R5 lurch cutoff (SDK 1100 < 1150) → spec R-18.

### 3.18 Revenant passive (long climb), re-attach floor, corner wallrun
- **Sources:** W-RevP (Mokey with EladNLG); V-MokRev 18:41 / 21:38 (C).
- **Inputs:**
  - The climb needs a Forward input to start (a side key alone = normal-legend wallrun).
  - When climbing sideways, do not look toward the side key: look straight or opposite.
  - **Re-attach floor:** set where the climb started; re-attach at the same floor works up to 9 times; leaving at a vertical edge resets it.
  - Revenant always gets a **mini-bounce**, never a full wall bounce.
  - **Corner wallrun** (The Dapper Cat, Jul 2021):
    1. Slide jump into the wall at ~45°.
    2. Hold the side key in the travel direction and look slightly opposite.
    3. Jump near the corner and scroll Forward while turning 90°.
    4. Keep the side key.
- **Version:** the passive dates from S4 and was "upgraded for more height and sideways control" in S18 (Aug 2023); S21-present.
- **Evidence:** **A** (qualitative inputs). **Measured:** long climb (800 u mantles, vz = 0.0921·(Z0 − z)) and the 0.75 s lock (RRev). The end rule, sideways climb, re-attach ×9 and mini-bounce-only are unmeasured (B-track items).

### 3.19 Vantage Echo relocation (jet drive)
- **Sources:** W-Echo; SRC-Echo [src].
- **Inputs:** tap Tactical = position Echo; hold Tactical = launch to Echo; crouch drops out early; Jump on arrival = double jump. A mid-air send places Echo 40 m away; Echo hovers ≥ 5 m (script: `ECHO_ORDER_MIN_HEIGHT` 6 m); Echo follows at > 55 m.
- **S21 rule [src]:** `CanLaunchToCompanion` requires Echo **on screen within 60°** (`DOT_60DEGREE`) and an **unblocked trace** (eye → Echo, plus two offset retries). Both are playlist-gated (`vantage_los_check_onscreen` / `vantage_los_check_blocked`, default true). Other constants: double-jump velocity <13 m, 0, 10 m> = <512, 0, 394>; back-jump fraction 0.5; path speed 20 m = 787; decel distance 5 m; range 40 / 55 m (buffed 50 / 65 m).
- **Post-S21 techniques (do not mix into S21 Reference):**
  - The **LOS removal** ("slithering") in S22 (6 Aug 2024).
  - **Echo dash:**
    1. With Echo out, press Utility to recall him and hold Tactical at the same time.
    2. Walk backwards so that the recall and the launch coincide.
    3. Jump.

    Source: wiki; buckettyf clips dated Feb 2024, but the wiki ties it to the S22 rework.
  - **Echo TS** (Treeree, Jul 2025): hold Tactical; Jump right at the launch; Crouch; scroll Forward.
  - **Echolevator** (PiffQ, 27 Apr 2025).
- **Evidence:** basics **A + measured** (RVan: launch 943 = 787 × 1.2, path speed 787, double jump vz 394 / h ≈ 500 replacing the velocity, crouch ×0.8, tracks moving targets). The Echo range in RVan (Echo settled 1969 u ≈ 50 m with kit) matches the **buffed** range constant, not the 40 m base [inf]. Echo TS / dash / echolevator: **A** as inputs but **post-S21**.

### 3.20 Other zipline facts relevant to movement (W-Zip)
- Climb space moves with the zipline. Riding > 0.5 s resets the climb attach point, so you can climb or wall bounce out of a zipline near a wall.
- Ziplines do not interrupt the lurch window, coyote time or jump fatigue.
- Hitting geometry while riding throws you off; a partial pill hit keeps much of the speed.
- A pathfinder **grapple from a zip while looking straight down keeps full velocity** ("momentum carry exit", Mokey post 19 Nov 2022).
- Our R5 grapple→zip work is in `../../m6/a3_zip/GRAPPLE-ZIP.md`.

## 4. LS/RAS reversal vs the M8 156° measurement

**What R5 measured (RL a)**
- Entry: sprint jump at 299, camera fixed.
- Sequence: W → W+D → D → S+D → S (and the mirror), one edge every g.
- Result: 156.4° at g = 0.05 s, 125.9° at 0.083 s, 104.6° at 0.1 s. Speed ×0.98–1.00. The first W does nothing.

**What the sources say**

| Source | Entry state | Sequence | Camera | Claimed result |
|---|---|---|---|---|
| W-BLT Momentumshift | sprint → slide → **release W** → jump (slide jump: wiki slide-jump threshold 350, W-Vel) | L, B, R (or R, B, L), "circular" | turned 90° toward the first key | 90° backwards redirect |
| W-BLT OG Ras | "**only works out of a walk**" | not restated (Momentumshift family) | **not turned** | "turn straight backwards", landing in a jump slide |
| W-BLT, the same page | "At higher speeds" | "more advanced Lurch strafes" | — | — |
| W-BLT tap strafe combos | slide jump | scroll W while holding side + back → pure side lurch | turning | — |
| PG Ras (2023) | not stated | A + jump, then W, D (tap strafe), S | tap-strafe turning implied | — |
| PG Yuki (2023) | not stated | W+A, jump, S+A taps | — | — |
| V-Xzy / V-RU / V-Zed | unknown (videos not watched) | — | — | — |

**Implications (no new claims, only consistency)**
- The sources' 180° reversal is a **walk-speed** claim. At 199.5 u/s, the 209.3 clamp allows larger per-press turns than at 299, so fewer presses reach 180°. M8B's model gives 162° keeping 98% for D → D+S → S at 0.05 s.
- At sprint/slide speed the sources rely on (a) **camera turning** (Momentumshift, TS) or (b) longer chains. Neither was in the R5 156° chain, which was camera-fixed and sprint-entry.
- So **156° is the R5 result for one sprint, camera-fixed, 5-edge chain at 50 ms spacing**. It is not a general limit. Specs R-4, R-5 and R-6 cover the source conditions.
- Note: Momentumshift's own claim (90°) is less than 156°; the 180° claim is only for walk speed.

## 5. Zipline evidence for M9-A1

### 5.1 S21-era statements (dated ≤ Aug 2024)

| Topic | Statement (short) | Source, date |
|---|---|---|
| Mid-rope use / direction | Horizontal ziplines can be ridden "in either direction, regardless of incline". After dropping off with Jump, players can "reconnect to ziplines after a brief delay" | WG-MF, revision of 17 Jun 2024 |
| Re-grab restriction history | 23 Jun 2020 patch: "A cooldown will be applied to re-grabbing ziplines without touching the ground"; it grows with each disconnect/re-grab and resets on touching ground | WG-P20 |
| Re-grab cooldown ladder (S21 client) | `zipline_cooldown_time_0..4` = 0.1 / 0.2 / 1.0 / 3.0 / 5.0 s, plus `_decay` / `_decay_rate`. The R5 dedi ships it OFF ("the live client does not refuse in step") | SRC-Zip `zipline_cooldown.cpp` header and ConVars [src] |
| Re-grab count (R5) | 3 Use grants, then refused; landing or mantle resets; +1 after 3 s off the rope | SRC-Zip `zipline_disconnect.cpp` (comment says "latest" count) [src]; A3 §6 measured consume left = 2, reset left = 3 |
| Mid Air Interact | Ghost interact discovered Aug 2022; air interact uses a wider prompt cone; re-grab after a jump-off is a use case | W-Zip (history dated), V-Set3 (29 Aug 2022), V-Ghost (1 Dec 2022) |
| Juking by re-mounting | Air dance (Feb 2022), mantle crouch (2022), float jump (Nov 2021): all re-interact mid-rope in the air | W-Dis |
| Mount search geometry (R5) | Collector sphere 120 u around origin + 72; `Zipline_Find(player, position, eyeDirection, …, outReverse)`: the travel direction (reverse flag) is decided at Find from the eye direction | SRC-Zip `zipline_validation.cpp` 2134–2136, `zipline_exit_parity.cpp` 128 [src]; A3 §1 fit: 130 u, cone 27–40.7° |
| Zip-rail reverse rule (S21 client) | A ziprail mount reverses when the eye is along the path and the far end is within `ziprailMountReverseDistance` (200) | SRC-Zip `ZiplineRail_ShouldReverse` [src] (ziprails only) |
| Timings | Coyote 0.2 s; lurch 0.4 s / full 0.2 s | W-Tim (16 Jun 2024) |

### 5.2 Current-wiki statements (post-S21 text; behaviour may predate it)

| Topic | Statement | Source |
|---|---|---|
| Ride start point | You ride "from your interact point"; interacting "within that Range will pull you towards the Zipline before riding it" | W-Zip |
| Interact range and look | You must look at the zip. The grounded prompt appears up to **35°** horizontally; in the air up to **90°**; beyond that, look straight up/down. A bug: at the exact edge of the range you get pulled toward the zip but not mounted ("move a bit closer") | W-Zip |
| Direction | "Generally speaking you take a Zipline into the direction you look. Up, Down, Left or Right." Near zip poles the zip forces you away from the pole. Vertical zips "prefer to send players upwards whenever possible" | W-Zip; WG-Zip (20 Aug 2024) |
| Vertical end zones | Theory: a "force off" zone (ends a downward ride early) and a "force up" zone (forces upward on mount even when looking down); they are misaligned on all tested vertical zips | V-MokZone (4 Dec 2024), W-Myst |
| Re-grab limit | Get off and re-interact 3 times; ground contact or a full mantle resets; after 3 s "not on a Zipline" you get one more | W-Zip. Its history line says "June 23rd, 2023 … Lost Treasures Event" but links the **June 23, 2020** patch; the patch page confirms 2020, so the wiki's "2023" is a typo |
| Interact cooldown | `useZiplineCooldown 0.4`. "Lack of an interact cooldown between different Ziplines" (two zips allow an earlier carry) | W-Zip values; W-Carry (Rapid hyper jump) |
| Removed | "Infinite Interact Spam": you used to be able to attach and detach as often and as quickly as you wanted | W-Rem (removed; date not given, probably the 2020 patch [inf]) |
| Jump-off direction | Zips steeper than 45° let you disconnect in any direction; below 45° you are forced along the zip. Broken Moon S20 zips are an exception: the look direction is used, and mid-air interacts do not work on them | W-Zip, W-Weird, W-Myst |
| Values | `mountZiplineTime 0.5`, `ziplineSpeed 600`, `ziplineAcceleration 400`, `ziplineJumpOnAcceleration 1000`, `ziplineJumpOffSpeed 400`, `ziplineJumpOffDampScale 1`; vertical zips 480 | W-Zip |
| Exit speed | "Manual disconnect maximum: 445hu/s" (**contradicted**: R5 400) | W-Zip |

### 5.3 What this means for A1 (no cause assumed)
- **The sources unanimously allow a mid-rope mount** (any point within the interact range) and a mid-air re-grab (Mid Air Interact, S21-present).
- The R5 numbers to compare are in A3 §1: a rope point within 130 u of origin+72, view cone ≤ 27–40.7°, no auto-attach on touch, +22 snap, then the blend.
- An R-track mid-rope test should cover:
  - standing under / beside the rope at mid-length, at several rope heights relative to origin+72;
  - facing along vs across the rope;
  - vertical-rope mid-height mounts looking up vs down (the "force up" theory and "prefers up");
  - jump-off then re-grab at 2–10 commands (watch the client ladder 0.1 / 0.2 / 1.0 s vs the dedi);
  - air grab at ≤ 40 u.
- **Divergence risk:** in A3 §9.4 the dedi refused an air mount that the client accepted. Our R5 build may diverge from S21 for air mounts; the wiki's "edge of range" bug looks similar but is a grounded case.
- Direction on a mid-rope mount: the sources say look direction (horizontal both ways; vertical prefers up / force-up zone). In R5 this is decided inside `Zipline_Find` from the eye direction (outReverse) [src]. Our A3 runs never mounted mid-rope facing backwards → untested.

## 6. Reproduction spec (evidence A or measured only)

Conventions: 120 fps, one usercmd = 1/120 s; "edge" = key-down on that command. **R** = R5 trial (track R); **U** = Unity real-input demo. "Verify" names the R5 measurement that settles it.

| # | Technique (source) | Exact input script | Expected outcome (source) | Verify with |
|---|---|---|---|---|
| R-1 | Lurch combos (W-Lurch) | a) Hold A+W from before the jump, sprint jump (299), D edge at t = 0.10 s. b) Hold W+S, jump, D edge at 0.10 s. | a) lurch toward the view-forward direction (↑); b) pure right lurch (→) | RL b-series extension: heading change, \|Δv\| ≤ 209.3 |
| R-2 | Lurchless air strafe (W-Lurch, W-Air) | Hold A+D from before the jump; jump; release D at +2 cmds; keep A; mouse turn left 90°/s for 0.5 s | no lurch on any command (\|Δv\| = AirAccelerate only, ≤ 4.17 u/s per cmd); heading follows slowly | per-cmd Δv vs A1 model |
| R-3 | Tap strafe (W-BLT) | Sprint, slide 0.3 s, release W, hold D, jump; W edges every 2 cmds × 15; view yaw right at 360 / 720 °/s | −81° / −161°, speed kept | **already measured** (A1 §4, RL c); regression only |
| R-4 | Momentumshift (W-BLT) | Sprint, slide, release W, slide jump; A, S, D edges at +6, +12, +18 cmds (and +4/+8/+12); view yaw +90° (toward A) evenly over the press period | heading ≈ 90° "backwards" relative to the view; record the speed fraction | new; compare with A1 "shift" (camera fixed) |
| R-5 | OG Ras (W-BLT, B: order implied) | **Walk** (199.5) jump, camera fixed; two orders: (i) A, S, D edges and (ii) D, D+S, S edges, spacing 4 / 6 / 10 cmds; then crouch held for a jump slide on landing | "straight backwards", landing in a jump slide | new; compare with RL a (156° at sprint) and the M8B model 162° / 98% |
| R-6 | Reverse chain at other entries (M8 follow-up) | RL a's chain W→W+D→D→S+D→S at entries walk 199.5 / sprint 299 / slide jump ≈350, spacing 4 / 6 cmds; also the same chain with a 90° view turn | heading vs entry speed; whether 180° is reached below 299 | RL a; M8B §3 |
| R-7a | Sideways SG (W-SG) | Sprint into H120; during the mantle pull release W, hold D; at time-left 0.04 s press jump, crouch +1 cmd | exit 460 along D (view-relative) | RSG open 4 |
| R-7b | Backward SG (W-SG) | As 7a, but pitch up > 25° during the pull and hold S instead of D (variant: no look-up, S edge 1 cmd before the jump) | exit 460 straight backwards; the variant without look-up cancels the mantle unless S is exactly 1 cmd early | new |
| R-8 | Wall bounce speeds (W-WB, W-Vel) | Basic: sprint, slide, slide jump perpendicular, release W 0.2 s before contact, jump at contact + 2 / 6 / 12 cmds; fatigue bounce (W-WB inputs) | exit speed in 350–484 (S27 wiki); a lower attach gives a higher bounce | A1 §6 data + exit speed |
| R-9 | Jump-fatigue wall bounce (W-WB) | At the wall: jump; on landing hold W; jump at +0.2 s (fatigue); on climb contact release W; jump at +4 cmds | bounce from a lower attach | new |
| R-10 | Bunny hop above 399 (W-Ground) | Pad / slide-boosted entries at 450 and 600 (horizontal); land; jump on the first grounded cmd; repeat 3 hops | wiki: loses "up to 100hu/s * speedMultiplier" per hop vs R5 min(v, 299) (M3 cannot separate them below 399) | M3 line 107 open item |
| R-11 | Zip jump / crouch (W-Zip) | Interact, jump (or crouch) at M = 1…200 cmds | (min(v, 400)·rope, 289.8) / (min(v, 400), 0) | **measured** (A3) |
| R-12 | Zipline carry (W-Carry) | Sprint perpendicular to a horizontal rope (299 along +y, rope along x); interact; jump on the next cmd (control: jump at +3 cmds) | carry: horizontal ≈ prior velocity (capped 400), not rope-aligned; failed: rope-aligned | new; A3 z5b only from rest |
| R-13 | Super jump edge (W-SJ, W-Air coyote 0.2 s) | Ground mount; jump-off at M = 1; second jump edge at K = 12, 18, 22, 24, 26, 30 cmds | applied up to ≈ 24 cmds (0.2 s), not beyond | A3 §9.2 window gap 9–62 |
| R-14 | Mid Air Interact (W-Zip) | Running jump toward a horizontal rope; interact at 20 / 40 / 80 u from the rope, facing 0° / 45° / 80° horizontally off the rope; plus > 90° with pitch ±89° | the mount is accepted on the dedi within range; prompt cone 90° in the air | A3 §9.4 (dedi refusal), log `Zipline_Find` on both sides |
| R-15 | Re-grab limit (W-Zip, SRC-Zip) | Mount, jump off, re-grab mid-air (as R-14) × 4 without ground; then wait 3 s airborne (tall drop) and re-grab | 4th refused; one regained after 3 s; ground resets | A3 §6 + `[ZIP-DISC]` |
| R-16 | Mid-rope mount (W-Zip, WG-MF) | Stand under the rope at mid-length: rope height above origin = 120 / 160 / 200 / 240 u; view along the rope (both directions) and across (90°); press use | mount wherever a rope point is within the range/cone; direction = look direction | A3 §1 rule (130 u, 27–40.7°) |
| R-17 | Vertical-rope mid mount (W-Zip, WG-Zip, V-MokZone) | Mid-height of a vertical rope, pitch +45° (down) vs −45° (up); jump off and re-grab looking the other way | look down → ride down unless in a "force up" zone; vertical prefers up | A3 Z3 (only one geometry) |
| R-18 | Pounce tap strafe (W-Pounce) | Revenant: hold tactical 1.0 s and 2.5 s; jump edge while holding; release tactical 2 cmds later; D held; W edges every 2 cmds × 10, yaw right 360 °/s; pitch 0° and −10° | S21: TS works (lurch applies at ≈1150); post-Sep-2024 limits do not apply | M4 pounce + A1 lurch; tests the lurch cutoff (SDK 1100) |
| R-19 | Pounce angle grid (W-Pounce, SRC) | Full charge at pitch −30, −15, 0, +10, +25 (down), +45 | ideal −15…0; ≥ 20° down → launch fixed at 15° up; > 15° up loses speed | M4 formula |
| R-20 | Echo LOS rule (SRC-Echo, S21) | Echo placed, then (a) view 70° away from Echo and (b) a wall between; hold tactical | (a) no launch (60° on-screen gate); (b) no launch (LOS), unless playlist vars are off | RVan (not covered) |

Unity real-input demos already cover R-3 (`m8b_ts_720`), the R-5 model (`m8b_ras_reverse`), the snake model (`m8b_snake`) and R-11/R-13 (M6-A zip demos). New U demos should follow R-1, R-2, R-4, R-7a/b, R-12, R-14–R-17 once R confirms the outcome. Per the plan, nothing in the Reference model changes to make a video sequence succeed.

## 7. "To watch" list (the user or a vision-capable reviewer; timestamps are the authors' chapter marks)

| Priority | Video | Timestamp(s) | Why |
|---|---|---|---|
| 1 | V-RU https://youtu.be/lp8DvQ9qW7I | 01:41 table; 11:26 RAS slow; 11:52 RAS variations slow; 12:14 snake slow; 12:38 double tap slow; 13:17 neo slow; 10:51 Pito slow | keyboard overlay in slow motion (per the wiki) → exact LS/RAS key orders and spacing |
| 2 | V-Xzy https://youtu.be/JonGQ6F_p6E | 03:12; 04:16; 05:23; 07:18; 08:56; 09:18; follow-along 10:20–12:10 (half/full speed) | the same family; half-speed follow-along gives timing |
| 3 | V-Zed1 https://youtu.be/-0cK8B07MFs and V-Zed2 https://youtu.be/e2gXI5-wMus | no chapters | the wiki's recommended basic and advanced LS guides |
| 4 | V-Swe https://youtu.be/PpNa7Y3JsZY | no chapters | "advanced RAS strafes": entry speed / sequence for R-5/R-6 |
| 5 | V-Xzy2 https://youtu.be/zlSkzpik4Js | 12:16 Ras strafes / bhop lurches; 8:19 directional SG; 16:19 zip dancing | RAS from bhop entry; SG variants |
| 6 | V-Allu https://youtu.be/8xxiX2ZNgSI | 1:11 interaction zone; 2:00 interaction limit | interact range and re-grab limit in practice (Aug 2024, ≈ S21) |
| 7 | V-MokZone https://youtu.be/1USJXOMVRsQ | whole (77 s) | vertical force-up / force-off zones |
| 8 | V-MokSG https://youtu.be/_cP1YO5Idts | 04:39; 07:00; 13:09 | SG timing window claims vs RSG |
| 9 | V-MokRev https://youtu.be/Tz3OcCXjNCU | 15:10 tap-strafe; 18:41 passive; 21:38 re-attach | pounce TS input timing; sideways climb |
| 10 | V-Pito / V-Yuki / V-Jon / V-H1y | — | named-strafe definitions |

## 8. Open items for the leader
1. **LS/RAS remains undefined in text.** Watching V-RU at the slow-motion chapters is the cheapest way to get author sequences; until then, R-5/R-6 use the wiki's walk-entry claim and our own chains.
2. **The R5 air-mount refusal** (A3 §9.4) conflicts with S21-present Mid Air Interact; it could also explain the user's "can't re-grab mid-rope" report. R-14/R-16 settle it before any Unity fix.
3. **Wiki 445 vs R5 400** zipline exit: R5 is measured; treat the wiki 445 as stale or combined-speed.
4. **Lurch window 0.4 s (wiki) vs 0.5 s (R5):** keep the R5 value.
5. **Bunny-hop penalty above 399** (R-10) and the **pounce-TS lurch cap** (R-18) are the two cheap tests that check wiki claims against SDK constants.
