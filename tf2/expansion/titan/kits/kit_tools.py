"""Loaders for the kit runs (hsd_diag_kit.gnut / hsd_diag_kit_cl.gnut). Usage: from kit_tools import Run

Clocks: CMD and C / KC lines carry the client time; TAG, KIT, KDMG, TT, NDMG the server time.
Run.offset = median(server TAG time - client CMD time of the same hsd_tag) maps one onto the other.
"""
import os
import statistics


class Run:
    def __init__(self, run_dir):
        self.dir = run_dir
        self.cmds = []          # (client t, command)
        self.tags_sv = []       # (server t, name)
        self.C = []             # client movement: t ox oy oz vx vy vz pitch yaw ground
        self.KC = []            # client kit: t phase act clip chg reloading zoom o0 o1 o2 energy
        self.KIT = []           # server kit (10 Hz), split fields
        self.KDMG = []          # (t, victim, dmg, hp, shield, src, dtype, inflictor, x, y, z)
        self.TT = []            # t titan dodge sprint hp shield
        self.NDMG = []          # t id dmg hpbefore attacker src x y z
        self.other = []
        for line in open(os.path.join(run_dir, "diag.tsv"), encoding="utf-8", errors="replace"):
            p = line.split()
            if len(p) < 3 or p[0] != "HSDDIAG":
                continue
            k = p[1]
            try:
                if k == "CMD":
                    self.cmds.append((float(p[2]), " ".join(p[3:])))
                elif k == "TAG":
                    self.tags_sv.append((float(p[3]), p[2]))
                elif k == "C":
                    self.C.append([float(x) for x in p[2:12]])
                elif k == "KC":
                    self.KC.append([float(p[2]), int(p[3]), p[4], int(p[5]), float(p[6]), int(p[7]), float(p[8]), p[9], p[10], p[11], int(p[12])])
                elif k == "KIT":
                    self.KIT.append(p[2:])
                elif k == "KDMG":
                    self.KDMG.append([float(p[2]), p[3], float(p[4]), int(p[5]), int(p[6]), int(p[7]), int(p[8]), p[9]] + [float(x) for x in p[10:13]])
                elif k == "TT":
                    self.TT.append([float(x) for x in p[2:8]])
                elif k == "NDMG":
                    self.NDMG.append([float(p[2]), int(p[3]), float(p[4]), float(p[5]), p[6], int(p[7])] + [float(x) for x in p[8:11]])
                else:
                    self.other.append(p[1:])
            except (ValueError, IndexError):
                self.other.append(p[1:])
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

    def cmd_after(self, t0, prefix, t1=None):
        """client time of the first command starting with prefix at or after t0"""
        for t, c in self.cmds:
            if t >= t0 - 1e-6 and c.startswith(prefix) and (t1 is None or t < t1):
                return t
        return None

    def sv(self, t_client):
        return t_client + self.offset

    def rows(self, table, a, b, server=False):
        if server:
            a, b = self.sv(a), self.sv(b)
        return [r for r in table if a <= float(r[0]) < b]
