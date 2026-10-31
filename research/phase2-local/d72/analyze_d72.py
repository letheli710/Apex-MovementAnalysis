"""D-72 crouched mantle sweep: one row per trial from hsd_session D72_* sessions (schedules d72_<cr|st>_d<D>_e<E>, hsd_trial.py).

Per trial (client Time(), 120 fps):
  lead        crouch lead = first mantling frame ([B1-MB] mant=true) minus the duck press (the [HSD-SCHED] down duck edge), s
  lead_f      the same in client frames (FrameCount)
  duck_t      the duck press to the client crouch flag ([HSD-MD] crouch=1: the duck is complete, the eye snaps to 32), s
  snap        that moment from the mantle start (s; < 0 = ducked before the mantle); duck_done = crouch=1 at the mantle start
  mantle      True when a mantle block of >= 0.1 s exists (shorter mant=true blips are dropped first); dur = its length (frames x dt), kind = short / long / stand (see classify())
  zmax        highest origin z of the trial; climbed = zmax reached the wall top (geometry_wall_z + floor)
  st          the [B1-MB] traversal states seen during the mantle (MantleBoost_GetState)
  camera      pitch = cang - eang ([HSD-MD], Source: + = down) relative to the frame before the mantle; peak / peak time from
              the mantle start; c1..c3 = the first three mantle frames' change (sign: does the camera first go down or up)
  S27         peak delta, window open (anim, s left), window frames: the B1 gate (analyze_b1.analyse_run)

Usage: analyze_d72.py <out_dir> <session_dir> [<session_dir> ...]   ->  runs.csv, cam.csv (per mantle frame), prints a table.
Raw logs stay local; the output tables are derived data.
"""
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "b1"))
import analyze_b1 as B  # noqa: E402

MD = re.compile(r"\[HSD-MD\] ver=2 side=cl kind=frame run=(\d+) seq=\d+ t=([\d.]+) .*?o=([-\d.]+),([-\d.]+),([-\d.]+) .*?"
                r"crouch=(\d) .*?in_duck=(\d) .*?cang=([-\d.]+),([-\d.]+),([-\d.]+) epos=\S+ eang=([-\d.]+),([-\d.]+),([-\d.]+)")
FLOOR = 294.92


def classify(dur, cr):
    if not cr:
        return "stand"
    return "short" if dur < 0.73 else "long"


def md_frames(sdir):
    out = {}
    for f in glob.glob(os.path.join(sdir, "platform", "logs", "client", "*", "script*.log")):
        for ln in open(f, encoding="utf-8", errors="replace"):
            m = MD.search(ln)
            if m:
                g = m.groups()
                out.setdefault(int(g[0]), []).append(dict(t=float(g[1]), z=float(g[4]), crouch=g[5] == "1", duck=g[6] == "1",
                                                          pitch=float(g[7]) - float(g[10])))
    for v in out.values():
        v.sort(key=lambda r: r["t"])
    return out


def drop_blips(sess, min_frames=12):
    """Clear mant on mantling blocks shorter than min_frames (0.1 s): one- to three-frame flags before the real mantle (h130 / h140)."""
    for frames in sess["frames"].values():
        ks = sorted(frames)
        i = 0
        while i < len(ks):
            if not frames[ks[i]]["mant"]:
                i += 1
                continue
            j = i
            while j < len(ks) and frames[ks[j]]["mant"]:
                j += 1
            if j - i < min_frames:
                for k in ks[i:j]:
                    frames[k]["mant"] = False
            i = j


def edge_t(lines, key, kind="down"):
    for ln in lines:
        if f"edge={kind} key={key} " in ln:
            return float(re.search(r" t=([\d.]+)", ln).group(1)), int(re.search(r" fc=(\d+)", ln).group(1))
    return None, None


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    runs, cams = [], []
    for sdir in sys.argv[2:]:
        man = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
        wall = man.get("geometry_wall_z")
        sess = B.load_session(sdir)
        drop_blips(sess)
        md = md_frames(sdir)
        for tr in man["trials"]:
            if tr.get("warmup"):
                continue
            run, name = tr["run"], tr["schedule"]
            m = re.fullmatch(r"d72_(cr|st)_d(\d+)_e(\d+)", name)
            cr = m.group(1) == "cr"
            fr = [sess["frames"].get(run, {})[k] for k in sorted(sess["frames"].get(run, {}))]
            mdr = md.get(run, [])
            td, fcd = edge_t(tr["sched_lines"], "duck") if cr else (None, None)
            tj, fcj = edge_t(tr["sched_lines"], "jump")
            res, rows = B.analyse_run(sess, run) if fr else (None, [])
            zmax = max((r["z"] for r in mdr), default=None)
            row = dict(session=os.path.basename(sdir), run=run, schedule=name, height=sess["height"], cr=int(cr),
                       d=int(m.group(2)), e=int(m.group(3)), fps=tr.get("measured_fps"), ok=tr.get("ok"),
                       zmax=round(zmax, 2) if zmax is not None else None,
                       climbed=int(zmax is not None and sess["height"] is not None and zmax >= FLOOR + sess["height"] - 10.0), mantle=int(res is not None))
            duck_on = next((r["t"] for r in mdr if td is not None and r["t"] >= td - 1e-6 and r["crouch"]), None)
            row["duck_t"] = round(duck_on - td, 4) if duck_on is not None and td is not None else None
            if res:
                blk = [f for f in fr if f["mant"]]
                i0 = fr.index(blk[0])
                t0 = blk[0]["t"]
                row.update(t_jump_mantle=round(t0 - tj, 4), lead=round(t0 - td, 4) if td is not None else None,
                           lead_f=fr[i0]["fc"] - fcd if fcd is not None else None, dur=res["duration"], frames=res["frames"],
                           kind=classify(res["duration"], cr), st="/".join(sorted({str(f["st"]) for f in blk[:len(rows)]})))
                row.update(z0=round(blk[0]["z"], 2), vz0=round(fr[i0 - 1]["vz"], 1) if i0 > 0 else None,
                           ztop=round(blk[-1]["z"], 2), rise=round(blk[-1]["z"] - blk[0]["z"], 2),
                           anim0=blk[0]["anim"], ss=blk[-1]["ss"])
                at = next((r for r in mdr if r["t"] >= t0 - 1e-6), None)
                row["duck_done"] = int(at["crouch"]) if at else None
                row["snap"] = round(duck_on - t0, 4) if duck_on is not None else None     # duck complete, from the mantle start
                # camera: pitch from the frame before the mantle, over the mantle and 0.3 s after
                pre = [r for r in mdr if r["t"] < t0 - 1e-6]
                p0 = pre[-1]["pitch"] if pre else 0.0
                span = [r for r in mdr if t0 - 1e-6 <= r["t"] <= t0 + res["duration"] + 0.3]
                if span:
                    pk = max(span, key=lambda r: r["pitch"] - p0)
                    row.update(cam_peak=round(pk["pitch"] - p0, 3), cam_peak_t=round(pk["t"] - t0, 4))
                    c = [round(r["pitch"] - p0, 3) for r in span[:3]]
                    row.update(c1=c[0] if c else None, c2=c[1] if len(c) > 1 else None, c3=c[2] if len(c) > 2 else None)
                    row["cam_first"] = ("down" if c[0] > 0.02 else "up" if c[0] < -0.02 else
                                        ("down" if len(c) > 1 and c[1] > 0.02 else "up" if len(c) > 1 and c[1] < -0.02 else "flat"))
                    for r in span:
                        cams.append(dict(run=run, height=sess["height"], kind=row["kind"], lead=row["lead"], t=round(r["t"] - t0, 4),
                                         pitch=round(r["pitch"] - p0, 4), crouch=int(r["crouch"])))
                row.update(peak_delta=res["peak_delta"], peak_anim=res["peak_anim"], win_open_anim=res["win_open_anim"],
                           win_open_rem=res["win_open_rem"], win_frames=res["win_frames"])
            runs.append(row)
    keys = []
    for r in runs:
        keys += [k for k in r if k not in keys]
    for name, rows, ks in (("runs.csv", runs, keys), ("cam.csv", cams, list(cams[0]) if cams else [])):
        if rows:
            with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=ks)
                w.writeheader()
                w.writerows(rows)
    for r in runs:
        print(" ".join(f"{k}={r.get(k)}" for k in ("height", "schedule", "fps", "lead", "lead_f", "duck_t", "snap", "duck_done", "t_jump_mantle",
                                                   "dur", "kind", "z0", "vz0", "rise", "zmax", "climbed", "cam_peak", "cam_peak_t", "cam_first",
                                                   "c1", "c2", "c3", "peak_delta", "win_open_rem")))


if __name__ == "__main__":
    main()
