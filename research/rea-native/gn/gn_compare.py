"""GN: the grapple before / after table (R5 against Unity Reference variants).

Usage: gn_compare.py --m4 <label>=<FeelBatch out> [...] --cam <camera trials dir> <label>=<CameraFeelBatch out> [...]
  --m4   the four M4 wall pulls (A-1): detach command (the step of the GRAPPLE_RELEASE_* event; R5 = scenarios.json grapple_release_step,
         the first command without pull) and apex (max origin z - start z)
  --cam  the camera trials (feel/camera_to_trial.py, F7 / N6): per trial the release time after the Q press (Unity: body.csv events;
         R5: the first client frame with [M10-GRC] att false is not in the trial, so the R5 column comes from N13 / N6: see GN doc),
         the apex after the press, the roll peak (Unity reference.csv; R5 camera_client.csv if present (F-1), else camera.csv) and for the
         N6 ceiling trials the pull -> release time
stdlib only. Part of rea-native GN (GN-GRAPPLE-NATIVE.md).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
M4 = os.path.join(REPO, "research", "phase2-local", "m4", "trials")
SCEN = os.path.join(REPO, "research", "phase2-local", "m4", "unity", "scenarios.json")
OFFHAND1 = 1 << 21
M4_TRIALS = ["m4_grapple_hold_r1701", "m4_grapple_hold_r1702", "m4_grapple_near_r2101", "m4_grapple_near_r2102"]


def rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def release(rs, key="step"):
    for r in rs:
        ev = r.get("events") or ""
        for e in ev.split("|"):
            if e.startswith("GRAPPLE_RELEASE_"):
                return r[key], e[len("GRAPPLE_RELEASE_"):]
    return None, None


def first(rs, name, key):
    for r in rs:
        if name in (r.get("events") or "").split("|"):
            return float(r[key])
    return None


def apex(rs, z0, t0=None, key="t"):
    zs = [float(r["pos_z"]) for r in rs if t0 is None or float(r[key]) >= t0]
    return max(zs) - z0


def m4(variants):
    sc = json.load(open(SCEN, encoding="utf-8"))
    print("| trial | R5 detach | " + " | ".join("%s detach" % l for l, _ in variants) + " | R5 apex | "
          + " | ".join("%s apex" % l for l, _ in variants) + " |")
    print("|---" * (3 + 2 * len(variants)) + "|")
    for t in M4_TRIALS:
        r5 = rows(os.path.join(M4, t, "samples.csv"))
        z0 = float(r5[0]["pos_z"])
        rel = sc["trials"]["M4_" + t]["grapple_release_step"]
        cells, apexes = [], []
        for _, d in variants:
            u = rows(os.path.join(d, "M4_" + t, "reference.csv"))
            s, why = release(u)
            cells.append("%s %s" % (s, why))
            apexes.append("%.1f" % apex(u, z0))
        print("| %s | %s | %s | %.1f | %s |" % (t, rel, " | ".join(cells), apex(r5, z0), " | ".join(apexes)))


def press_time(trial_dir):
    for r in rows(os.path.join(trial_dir, "samples.csv")):
        if int(r["buttons"]) & OFFHAND1:
            return float(r["t"])
    return None


def roll_peak(rs, press, tkey="t"):
    best = 0.0
    for r in rs:
        t = float(r[tkey])
        if press <= t <= press + 1.6 and abs(float(r["roll"])) > abs(best):
            best = float(r["roll"])
    return best


def cam(root, variants):
    print("| trial | R5 roll peak | R5 apex | " + " | ".join("%s release (s after Q) / apex / roll peak / pull->release" % l for l, _ in variants) + " |")
    print("|---" * (3 + len(variants)) + "|")
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or "n12_rodeo_y90" in name:
            continue
        press = press_time(d)
        if press is None:
            continue
        r5 = rows(os.path.join(d, "samples.csv"))
        z0 = float(r5[0]["pos_z"])
        cc = os.path.join(d, "camera_client.csv")
        if os.path.exists(cc):
            r5roll = "%.2f (client-only; measured %.2f)" % (roll_peak(rows(cc), 0.0, "t_press"), roll_peak(rows(os.path.join(d, "camera.csv")), press))
        else:
            r5roll = "%.2f" % roll_peak(rows(os.path.join(d, "camera.csv")), press)
        cells = []
        for _, od in variants:
            b = rows(os.path.join(od, name, "body.csv"))
            t, why = release(b, "t")
            pull = first(b, "GRAPPLE_PULL", "t")
            pr = "%.3f" % (float(t) - pull) if t is not None and pull is not None else "-"
            rel = "%.3f %s" % (float(t) - press, why) if t is not None else "none"
            cells.append("%s / %.1f / %.2f / %s" % (rel, apex(b, z0, press), roll_peak(rows(os.path.join(od, name, "reference.csv")), press), pr))
        print("| %s | %s | %.1f | %s |" % (name, r5roll, apex(r5, z0, press), " | ".join(cells)))


def main():
    a = sys.argv[1:]
    if "--m4" in a:
        i = a.index("--m4") + 1
        v = []
        while i < len(a) and not a[i].startswith("--"):
            l, d = a[i].split("=", 1); v.append((l, d)); i += 1
        m4(v)
        print()
    if "--cam" in a:
        i = a.index("--cam") + 1
        root = a[i]; i += 1
        v = []
        while i < len(a) and not a[i].startswith("--"):
            l, d = a[i].split("=", 1); v.append((l, d)); i += 1
        cam(root, v)


if __name__ == "__main__":
    main()
