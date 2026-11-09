"""Phase analysis of TF2 titan locomotion cycles: how each body channel lines up with the
foot contacts, how far from a plain sine it is, and where the body pauses.

Input: ../pose/out/joint_frames_<chassis>.csv (decoded per-frame joint metrics, made by
../pose/joints.py) and out/seqgraph_<chassis>.csv (IK contact phases, this folder).
Output: out/walkphase.csv (one row per chassis x clip x channel) and out/walkevents.csv.
Numbers only; no animation data is copied.
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = os.path.join(HERE, "..", "pose", "out")
OUT = os.path.join(HERE, "out")
CLIPS = {
    "walk": "a_WalkForward", "run": "a_RunForward", "sprint": "a_combat_sprint",
    "walk_back": "a_combat_WalkBackward", "crouch_walk": "a_Crouch_WalkForward",
    "walk_left45": "a_WalkForward_L", "doomed_walk": "@at_doomed_walk_F", "idle": "a_MP_CQB_idle",
}
SEQ_OF = {"a_WalkForward": "Walk_forward_MP", "a_RunForward": "Run_forward_MP", "a_combat_sprint": "Sprint_mp_forward",
          "a_combat_WalkBackward": "Walk_backward_MP", "a_Crouch_WalkForward": "Walk_Crouch_forward_MP",
          "a_WalkForward_L": "Walk_forward_MP"}
CHANNELS = ["hip_z", "hip_y", "pelvis_roll", "pelvis_yaw", "pelvis_pitch", "chest_roll", "chest_yaw", "chest_pitch",
            "waist_twist", "waist_side", "head_z", "cam_z", "l_ankle_z", "r_ankle_z", "l_sh_fwd", "r_sh_fwd", "l_elbow", "r_elbow"]


def harmonics(y):
    """Amplitude (half peak-to-peak of that component) and phase (cycle of its max) of harmonic 1 and 2."""
    n = len(y)
    m = sum(y) / n
    out = []
    for h in (1, 2):
        c = sum((y[k] - m) * math.cos(2 * math.pi * h * k / n) for k in range(n)) * 2 / n
        s = sum((y[k] - m) * math.sin(2 * math.pi * h * k / n) for k in range(n)) * 2 / n
        amp = math.hypot(c, s)
        ph = (math.atan2(s, c) / (2 * math.pi * h)) % (1.0 / h)
        out.append((amp, ph))
    var = sum((v - m) ** 2 for v in y) / n
    explained = (out[0][0] ** 2 + out[1][0] ** 2) / 2
    resid = 1 - explained / var if var > 1e-9 else 0.0
    return out, max(0.0, resid)


def contacts(seqrows, seq):
    for r in seqrows:
        if r["seq"] == seq and r["part"] == "mp_core":
            out = {}
            for part in r["ikrules(type chain start/peak/tail/end contact)"].split(" ; "):
                f = part.split()
                if len(f) >= 4 and f[0] == "ground":
                    chain = "R" if f[1] == "c0" else "L"
                    st, pk, tl, en = (float(x) for x in f[2].split("/"))
                    ct = float(f[3][2:])
                    out.setdefault(chain, []).append((st, pk, tl, en, ct))
            ev = [x.split(":") for x in r["events(cycle:name)"].split(" ; ") if "FOOTSTEP" in x]
            return out, [(float(c), n) for c, n in ev], float(r["dur"])
    return {}, [], 0.0


def main():
    rows, evrows = [], []
    for ch in ("light", "medium", "heavy"):
        frames = {}
        with open(os.path.join(POSE, "joint_frames_%s.csv" % ch), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                frames.setdefault(r["anim"], []).append(r)
        seqrows = list(csv.DictReader(open(os.path.join(OUT, "seqgraph_%s.csv" % ch), encoding="utf-8")))
        for clip, anim in CLIPS.items():
            fr = frames.get(anim)
            if not fr:
                continue
            fr.sort(key=lambda r: int(r["frame"]))
            n = len(fr) - 1 if len(fr) > 2 else len(fr)  # last frame of a loop repeats the first
            fps = float(fr[0]["fps"])
            dur = n / fps
            ik, ev, _ = contacts(seqrows, SEQ_OF.get(anim, ""))
            cR = [c[4] for c in ik.get("R", []) if c[4] > 0 or c[1] > 0] or [None]
            cL = [c[4] for c in ik.get("L", []) if c[4] > 0 or c[1] > 0] or [None]
            evrows.append([ch, clip, anim, round(dur, 3), cR[0], cL[0], " ".join("%s@%g" % (nm[-1], c) for c, nm in ev)])
            for chn in CHANNELS:
                y = [float(r[chn]) for r in fr[:n]]
                p2p = max(y) - min(y)
                kmax = max(range(n), key=lambda k: y[k])
                kmin = min(range(n), key=lambda k: y[k])
                ((a1, p1), (a2, p2)), resid = harmonics(y)
                d = [(y[(k + 1) % n] - y[k]) * fps for k in range(n)]
                dmax = max(abs(v) for v in d) or 1
                still = sum(1 for v in d if abs(v) < 0.15 * dmax) / n
                rows.append([ch, clip, chn, round(dur, 3), round(sum(y) / n, 2), round(p2p, 2), round(kmax / n, 3), round(kmin / n, 3),
                             round(a1, 2), round(p1, 3), round(a2, 2), round(p2, 3), round(resid, 3), round(still, 3), round(dmax, 1)])
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "walkphase.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["chassis", "clip", "channel", "cycle_s", "mean", "p2p", "phase_max", "phase_min",
                                   "h1_amp", "h1_phase_max", "h2_amp", "h2_phase_max", "non_sine_frac", "still_frac", "max_rate_per_s"]] + rows)
    with open(os.path.join(OUT, "walkevents.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["chassis", "clip", "anim", "cycle_s", "ik_contact_R", "ik_contact_L", "footstep_events"]] + evrows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
