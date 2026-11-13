"""Loader for tf2-kits-measure runs (HSD.KitMeasure + HSD.TF2Diag). Usage: from km_tools import Run

Client clock: CMD, PC, PJNEW / PJ / PJEND, SA. Server clock: TAG, TS, TF, PSNEW / PS, PF, TD, KM, KIT, KDMG, KFIN.
Run.offset = median(server TAG - client CMD of the same hsd_tag); server t - offset = client t.
"""
import math
import os
import statistics
from collections import defaultdict


def fl(xs):
    return [float(x) for x in xs]


class Run:
    def __init__(self, run_dir):
        self.dir = run_dir
        self.cmds, self.tags_sv = [], []
        self.PC = []                      # t titan x y z vx vy vz pitch yaw ex ey ez
        self.pj_new = {}                  # h -> (t, class, weapon, x, y, z)
        self.pj = defaultdict(list)       # h -> [(t, x, y, z)]
        self.pj_end = {}
        self.SA = []                      # (t, slot, weapon, [(h, frac, active)])
        self.TS, self.TF = [], []
        self.ps_new = {}                  # h -> (t, class, weapon, owner, src, mods)
        self.ps = defaultdict(list)       # h -> [(t, x, y, z, vx, vy, vz)]
        self.pf = defaultdict(list)
        self.TD, self.KM, self.KDMG, self.KFIN, self.KIT, self.other = [], [], [], [], [], []
        for line in open(os.path.join(run_dir, "diag.tsv"), encoding="utf-8", errors="replace"):
            p = line.replace("class C_", "C_").split()
            if len(p) < 3 or p[0] != "HSDDIAG":
                continue
            k = p[1]
            try:
                if k == "CMD":
                    self.cmds.append((float(p[2]), " ".join(p[3:])))
                elif k == "TAG":
                    self.tags_sv.append((float(p[3]), p[2]))
                elif k == "PC":
                    self.PC.append([float(p[2]), int(p[3])] + fl(p[4:15]))
                elif k == "PJNEW":
                    self.pj_new[int(p[3])] = (float(p[2]), p[4], p[5]) + tuple(fl(p[6:9]))
                elif k == "PJ":
                    self.pj[int(p[3])].append(tuple(fl([p[2]] + p[4:7])))
                elif k == "PJEND":
                    self.pj_end[int(p[3])] = float(p[2])
                elif k == "SA":
                    n = int(p[5])
                    ts = [(p[6 + 3 * i], float(p[7 + 3 * i]), int(p[8 + 3 * i])) for i in range(n)]
                    self.SA.append((float(p[2]), int(p[3]), p[4], ts))
                elif k == "TS":
                    self.TS.append([float(p[2]), int(p[3])] + fl(p[4:12]) + [int(p[12]), int(p[13])] + ([float(p[14])] if len(p) > 14 else []))
                elif k == "TF":
                    self.TF.append([float(p[2]), int(p[3])] + fl(p[4:10]) + [int(p[10]), int(p[11]), float(p[12]), float(p[13])])
                elif k == "PSNEW":
                    self.ps_new[int(p[3])] = (float(p[2]), p[4], p[5], p[6], int(p[7]) if p[7].lstrip("-").isdigit() else -1, p[8])
                elif k == "PS":
                    self.ps[int(p[3])].append(tuple(fl([p[2]] + p[4:10])))
                elif k == "PF":
                    self.pf[int(p[3])].append(tuple(fl([p[2]] + p[4:10])))
                elif k == "TD":
                    self.TD.append([float(p[2]), p[3], float(p[4]), int(p[5]), p[6], int(p[7]), int(p[8])] + fl(p[9:12]))
                elif k == "KDMG":
                    self.KDMG.append(p[2:])
                elif k == "KFIN":
                    self.KFIN.append(p[2:])
                elif k == "KIT":
                    self.KIT.append(p[2:])
                elif k == "KM":
                    self.KM.append(p[2:])
                else:
                    self.other.append(p[1:])
            except (ValueError, IndexError):
                self.other.append(p[1:])
        for h, pts in self.pj.items():           # PJNEW lines were lost in the 11-13 01:56 run (string concat in printt)
            if h not in self.pj_new and pts:
                self.pj_new[h] = (pts[0][0], "?", "?") + tuple(pts[0][1:])
        for h, pts in self.ps.items():
            if h not in self.ps_new and pts:
                self.ps_new[h] = (pts[0][0], "?", "?", "?", -1, "-")
        ct = [(t, c.split()[1]) for t, c in self.cmds if c.startswith("hsd_tag ")]
        sv = dict((n, t) for t, n in self.tags_sv)
        d = [sv[n] - t for t, n in ct if n in sv]
        self.offset = statistics.median(d) if d else 0.0
        self.tags = [(t, ct[i + 1][0] if i + 1 < len(ct) else t + 30.0, n) for i, (t, n) in enumerate(ct)]

    def tag(self, name):
        for a, b, n in self.tags:
            if n == name:
                return a, b
        return None

    def pc_at(self, t):
        best = None
        for r in self.PC:
            if r[0] <= t:
                best = r
            else:
                break
        return best

    def client_proj_in(self, a, b):
        return sorted([h for h, v in self.pj_new.items() if a <= v[0] < b], key=lambda h: self.pj_new[h][0])

    def server_proj_in(self, a, b):
        """a, b in client time"""
        return sorted([h for h, v in self.ps_new.items() if a <= v[0] - self.offset < b], key=lambda h: self.ps_new[h][0])


def basis(pitch, yaw):
    """Source angles (pitch down positive) -> forward, right, up"""
    p, y = math.radians(pitch), math.radians(yaw)
    f = (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), -math.sin(p))
    r = (math.sin(y), -math.cos(y), 0.0)
    u = (f[1] * r[2] - f[2] * r[1], f[2] * r[0] - f[0] * r[2], f[0] * r[1] - f[1] * r[0])
    # make up point up
    if u[2] < 0:
        u = tuple(-c for c in u)
    return f, r, u


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))
