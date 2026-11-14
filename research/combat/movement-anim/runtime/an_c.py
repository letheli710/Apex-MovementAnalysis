#!/usr/bin/env python3
"""C1-C5 analysis. Read-only on the raw run dir (frida/, runs/, marks.tsv).
  py -3 -I an_c.py <raw runtime dir> <out dir>
Writes SEQTABLE.tsv, TIMELINE.tsv, C1-RELOAD.tsv, C2-GUNS.tsv, C3-SPRINT.tsv, C4-CROUCHWALK.tsv, C5-CROUCH.tsv, FADES.tsv, OVERLAY.tsv and prints a summary.
Clocks: frida w = wall ms (same clock as the marks), frida ct10 = client Time() (checked: key line Time 225.329 vs ct10 225.336)."""
import gzip, csv, json, os, sys, math, bisect, re, statistics as st, collections

def opn(p):
    """plain file, or its .gz (the raw repo keeps the big CSVs gzipped)"""
    return open(p, encoding="utf-8") if os.path.exists(p) else gzip.open(p + ".gz", "rt", encoding="utf-8")
D, O = sys.argv[1:3]
os.makedirs(O, exist_ok=True)
SKIP = ("test",)

# ---- sequence tables
SEQ = {}   # gun dir -> {idx: (short, act, fi, fo, flags)}
# The CStudioHdr address (frames "mdl") is reused when the gun changes, so tables are keyed by the weapon folder in the labels,
# and each run gets its gun from the sequence names in its client log.
with open(os.path.join(O, "SEQTABLE.tsv"), "w", encoding="utf-8") as f:
    f.write("gun\tidx\tname\tactivity\tfade_in\tfade_out\tflags\n")
    for l in open(os.path.join(D, "frida", "seqtable.jsonl"), encoding="utf-8"):
        o = json.loads(l)
        names = [s[1] for s in o["seqs"] if len(s) > 2 and s[1] not in ("?", "")]
        g = "?"
        for n in names:
            m = re.search(r"weapons/([^/]+)/", n)
            if m: g = m.group(1); break
        if g in SEQ: continue
        SEQ[g] = {}
        for s in o["seqs"]:
            if len(s) < 6: continue
            short = s[1].split("/")[-1].replace(".rseq", "")
            SEQ[g][s[0]] = (short, s[2], s[3], s[4], s[5])
            f.write(f"{g}\t{s[0]}\t{short}\t{s[2]}\t{s[3]}\t{s[4]}\t{s[5]}\n")
CUR = [None]
nm = lambda _mdl, i: SEQ.get(CUR[0], {}).get(i, (str(i),))[0]

# ---- marks
MK = collections.defaultdict(list)
for l in open(os.path.join(D, "marks.tsv"), encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    if len(p) >= 3: MK[p[0]].append((float(p[1]) * 1000, p[2]))
TAGS = [t for t in MK if not t.startswith("t_")]

# ---- frames
F = []
PPN = None
with opn(os.path.join(D, "frida", "frames.csv")) as fh:
    rd = csv.reader(fh)
    head = next(rd)
    PPN = [h for h in head if h.startswith("pp_")]
    for r in rd:
        if len(r) < len(head): continue
        x = dict(zip(head, r))
        try:
            y = {k: float(x[k]) if x[k] not in ("", "NaN") else float("nan") for k in head if k not in ("ovA", "ovS")}
        except ValueError:
            continue
        y["ovA"] = x["ovA"]; y["ovS"] = x["ovS"]
        F.append(y)
W = [x["w"] for x in F]
def cut(a, b): return F[bisect.bisect_left(W, a):bisect.bisect_right(W, b)]
TR = list(csv.DictReader(opn(os.path.join(D, "frida", "trans.csv"))))
OVR = []
p_ov = os.path.join(D, "frida", "ovraw.csv")
if os.path.exists(p_ov) or os.path.exists(p_ov + ".gz"):
    for l in opn(p_ov):
        p = l.rstrip("\n").split(",")
        try: OVR.append([float(p[0])] + [float(v) if v else float("nan") for v in p[1:]])
        except ValueError: pass
OW = [r[0] for r in OVR]

# ---- client logs
def clog(tag):
    rows = []
    p = os.path.join(D, "runs", tag + ".txt")
    if not os.path.exists(p): return rows
    for l in open(p, encoding="utf-8", errors="replace"):
        if "[RT] a t=" not in l: continue
        d = dict(re.findall(r"(\w+)=([^ ]+)", l[l.index("[RT] a "):]))
        rows.append(d)
    return rows

RUNGUN = {}
def setgun(tag):
    if tag not in RUNGUN:
        g = "?"
        p = os.path.join(D, "runs", tag + ".txt")
        if os.path.exists(p):
            for l in open(p, encoding="utf-8", errors="replace"):
                m = re.search(r"sq=animseq[^ ]*/weapons/([^/]+)/", l)
                if m: g = m.group(1); break
        RUNGUN[tag] = g
    CUR[0] = RUNGUN[tag]
    return RUNGUN[tag]
GUN = collections.defaultdict(lambda: CUR[0])

def win(tag):
    setgun(tag)
    m = MK[tag]
    a = [t for t, x in m if x == "logstart"][0]
    b = [t for t, x in m if x == "end"][-1]
    return a, b + 600

def key(tag, k, n=0):
    v = [t for t, x in MK[tag] if x == k]
    return v[n] if len(v) > n else None

def seqruns(fr):
    o = []
    for f in fr:
        s = int(f["seq"]) if f["seq"] == f["seq"] else -1
        if not o or o[-1][0] != s: o.append([s, f["w"], f["w"], f["cyc"], f["cyc"], f["mdl"]])
        o[-1][2] = f["w"]; o[-1][4] = f["cyc"]
    return o

def ovruns(fr):
    o = []
    for f in fr:
        k = (f["ovA"], f["ovS"])
        if not o or o[-1][0] != k: o.append([k, f["w"], f["w"], f["mdl"]])
        o[-1][2] = f["w"]
    return o

def ovtext(k, mdl):
    a, s = k[0].split(), k[1].split()
    return " ".join(f"L{i}:{'on' if a[i] == '1' else 'off'}:{nm(mdl, int(s[i]))}" for i in range(len(a)) if a[i] == "1" or s[i] != "0")

def amp(fr, k):
    v = sorted(x[k] for x in fr if x[k] == x[k])
    if len(v) < 20: return float("nan")
    return (v[int(.95 * len(v))] - v[int(.05 * len(v))]) / 2

def period(fr, k):
    fr = [x for x in fr if x[k] == x[k]]
    if len(fr) < 60: return float("nan")
    t = [x["ct10"] for x in fr]; v = [x[k] for x in fr]; m = sum(v) / len(v)
    n = int((t[-1] - t[0]) * 200); g = []; j = 0
    for i in range(n):
        xx = t[0] + i / 200
        while j < len(t) - 2 and t[j + 1] < xx: j += 1
        g.append(v[j] - m)
    c0 = sum(a * a for a in g) or 1
    best = (0, float("nan"))
    for lag in range(30, min(n // 2, 400)):
        c = sum(g[i] * g[i + lag] for i in range(n - lag)) / c0 * n / (n - lag)
        if c > best[0]: best = (c, lag / 200)
    return best[1]

def spd(f): return math.hypot(f["vx"], f["vy"])

def ovcyc(a, b):
    """overlay raw floats in [a, b]: returns list of rows"""
    return OVR[bisect.bisect_left(OW, a):bisect.bisect_right(OW, b)]

# ---- TIMELINE.tsv: keys, main sequences, overlays, transitions, client states
TL = open(os.path.join(O, "TIMELINE.tsv"), "w", encoding="utf-8")
TL.write("tag\tt\tkind\tdetail\n")
for tag in TAGS:
    a, b = win(tag)
    fr = cut(a, b)
    if not fr: continue
    ev = []
    for t, x in MK[tag]:
        if x not in ("logstart", "end"): ev.append((t, "key", x))
    for s in seqruns(fr):
        ev.append((s[1], "main", f"{nm(s[5], s[0])} ({s[0]}) {(s[2] - s[1]) / 1000:.3f}s cyc {s[3]:.2f}->{s[4]:.2f}"))
    for o in ovruns(fr):
        ev.append((o[1], "overlay", ovtext(o[0], o[3]) or "none"))
    mdl = fr[-1]["mdl"]
    # the overlay's own transitioner reports the same old->new every frame without making a layer (n 0->0): keep the first of each repeat
    last = None
    for r in TR:
        w = float(r["w"])
        if a <= w <= b:
            k = (r["old"], r["new"], r["n0"], r["n1"])
            if k == last: continue
            last = k
            ev.append((w, "trans", f"{nm(mdl, int(r['old']))} -> {nm(mdl, int(r['new']))} fade {r['fade']} layers {r['n0']}->{r['n1']}"))
    cl = clog(tag)
    prev = None
    ct0 = fr[0]["ct10"]
    for d in cl:
        st_ = " ".join(f"{k}={d.get(k)}" for k in ("gr", "duck", "spr", "sl", "zp", "ga", "rel"))
        if st_ != prev:
            ev.append((a + (float(d["t"]) - ct0) * 1000, "state", st_ + f" spd={d.get('spd')}"))
            prev = st_
    ev.sort()
    for t, k, x in ev: TL.write(f"{tag}\t{(t - a) / 1000:.3f}\t{k}\t{x}\n")
TL.close()

# ---- FADES.tsv: measured fade vs table
with open(os.path.join(O, "FADES.tsv"), "w", encoding="utf-8") as f:
    f.write("gun\told\tnew\tfade_measured\tmin_table\tcount\n")
    cnt = collections.Counter()
    spans = sorted((win(t)[0], win(t)[1], t) for t in TAGS)
    for r in TR:
        w = float(r["w"])
        tg = [t for a_, b_, t in spans if a_ <= w <= b_]
        if not tg: continue
        g = setgun(tg[0]); mdl = 0
        o, n = int(r["old"]), int(r["new"])
        if o == n or r["n1"] == r["n0"]: continue  # only calls that made a fade layer
        t = SEQ.get(g, {})
        mt = min(t[o][3], t[n][2]) if o in t and n in t else float("nan")
        cnt[(g, nm(mdl, o), nm(mdl, n), r["fade"], f"{mt:g}")] += 1
    for k, v in sorted(cnt.items()): f.write("\t".join(k) + f"\t{v}\n")

def say(*x): print(*x); OUT.write(" ".join(str(y) for y in x) + "\n")
OUT = open(os.path.join(O, "OUT-c.txt"), "w", encoding="utf-8")

# ---- C1
say("== C1 reload x movement (R-301)")
with open(os.path.join(O, "C1-RELOAD.tsv"), "w", encoding="utf-8") as f:
    f.write("tag\treload_key_s\treload_seq_start_s\treload_seq_len_s\treload_cyc_end\tended_by\tclip_after\tstates_during\toverlays_during\n")
    for tag in sorted(t for t in TAGS if t.startswith("c1_")):
        a, b = win(tag)
        kr = key(tag, "+reload")
        fr = cut(a, b)
        if not fr or kr is None: continue
        sr = seqruns(fr)
        rl = [s for s in sr if nm(s[5], s[0]).startswith("reload")]
        cl = clog(tag); ct0 = fr[0]["ct10"]
        stt = collections.Counter()
        if rl:
            s0, s1 = rl[0][1], rl[-1][2]
            for d in cl:
                w = a + (float(d["t"]) - ct0) * 1000
                if s0 <= w <= s1:
                    stt["slide" if d["sl"] == "1" else "zip" if d["zp"] == "1" else "grapple" if d["ga"] == "1" else "spr" if d["spr"] == "1" else "duck" if d["duck"] == "1" else "air" if d["gr"] == "0" else "ground"] += 1
            nxt = [s for s in sr if s[1] > rl[-1][2]]
            ov = collections.Counter(ovtext(o[0], o[3]) for o in ovruns(cut(s0, s1)))
            clip = [x["clip"] for x in cut(s1, s1 + 800)]
            f.write(f"{tag}\t{(kr - a) / 1000:.3f}\t{(rl[0][1] - kr) / 1000:.3f}\t{(rl[-1][2] - rl[0][1]) / 1000:.3f}\t{rl[-1][4]:.3f}\t{nm(nxt[0][5], nxt[0][0]) if nxt else '-'}\t{clip[-1] if clip else ''}\t{dict(stt)}\t{' | '.join(ov)}\n")
            say(tag, "reload", nm(rl[0][5], rl[0][0]), "len %.2f cyc_end %.2f ->" % ((rl[-1][2] - rl[0][1]) / 1000, rl[-1][4]), nm(nxt[0][5], nxt[0][0]) if nxt else "-", dict(stt))
        else:
            seen = [nm(s[5], s[0]) for s in sr]
            f.write(f"{tag}\t{(kr - a) / 1000:.3f}\t-\t-\t-\tno reload sequence: {' '.join(seen)}\t\t\t\n")
            say(tag, "NO reload seq;", seen)

# ---- C3 / C4: per speed bins
def bins(tag, kfrom, seqok, lo=0.4):
    a, b = win(tag)
    k0 = key(tag, kfrom); k1 = key(tag, "-forward")
    if k0 is None or k1 is None: return []
    fr = [x for x in cut(k0 + lo * 1000, k1) if seqok(x)]
    return fr

with open(os.path.join(O, "C3-SPRINT.tsv"), "w", encoding="utf-8") as f:
    f.write("tag\tspeed_lo\tspeed_hi\tn\tsprintfrac\tcycle_rate_per_s\tloop_s\tamp_vmaP\tamp_vmaY\tamp_vmaR\tamp_vmR\tamp_vmU\n")
    say("== C3 sprint loop vs speed")
    for tag in sorted(t for t in TAGS if (t.startswith("c3_") and "sprint" in t) or (t.startswith(("c2_", "c2b_")) and t.split("_")[2] == "sprint")):
        a, b = win(tag)
        setgun(tag)
        k0 = key(tag, "+speed"); k1 = key(tag, "-speed")
        if k0 is None: continue
        fr = cut(k0, k1)
        mdl = fr[-1]["mdl"] if fr else 0
        sp = [x for x in fr if nm(x["mdl"], int(x["seq"])).startswith("sprint") if x["seq"] == x["seq"]]
        # rate from consecutive frames in the loop
        rows = collections.defaultdict(list)
        for i in range(1, len(sp)):
            p, q = sp[i - 1], sp[i]
            dt = q["ct10"] - p["ct10"]
            if dt <= 0 or dt > 0.05: continue
            dc = q["cyc"] - p["cyc"]
            if dc < -0.5: dc += 1
            v = spd(q)
            bn = int(v // 50) * 50 if v > 30 else 0
            rows[bn].append((dc / dt, q))
        for bn in sorted(rows):
            rs = rows[bn]
            if len(rs) < 30: continue
            fq = [q for _, q in rs]
            rate = st.median(r for r, _ in rs)
            f.write(f"{tag}\t{bn}\t{bn + 50}\t{len(rs)}\t{st.mean(q['pp_sprintfrac'] for q in fq):.2f}\t{rate:.3f}\t{1 / rate:.3f}\t" + "\t".join(f"{amp(fq, k):.3f}" for k in ("vmaP", "vmaY", "vmaR", "vmR", "vmU")) + "\n")
            say(tag, f"speed {bn}-{bn + 50} n={len(rs)} rate {rate:.3f}/s loop {1 / rate:.3f}s sprintfrac {st.mean(q['pp_sprintfrac'] for q in fq):.2f} ampY {amp(fq, 'vmaY'):.2f} ampR {amp(fq, 'vmaR'):.2f}")

def steady(tag, k_on, k_off, lo, seqname=None):
    k0 = key(tag, k_on); k1 = key(tag, k_off)
    if k0 is None or k1 is None: return []
    fr = cut(k0 + lo * 1000, k1)
    if seqname: fr = [x for x in fr if x["seq"] == x["seq"] and nm(x["mdl"], int(x["seq"])) == seqname]
    return fr

with open(os.path.join(O, "C4-CROUCHWALK.tsv"), "w", encoding="utf-8") as f:
    f.write("tag\tgun\tstate\tspeed\tcrouchFraction\tvelocity_pp\tperiod_vmaY\tperiod_vmaP\tamp_vmaP\tamp_vmaY\tamp_vmaR\tamp_vmR\tamp_vmU\tmain\toverlays\n")
    say("== C3/C4 walk and crouch-walk bob vs speed")
    for tag in sorted(t for t in TAGS if (t.startswith("c4_") or (t.startswith("c3_") and "_walk_" in t) or (t.startswith(("c2_", "c2b_")) and t.split("_")[2] in ("walk", "crouchwalk", "adswalk")))):
        setgun(tag)
        fr = steady(tag, "+forward", "-forward", 1.2)
        if len(fr) < 60: continue
        mdl = fr[-1]["mdl"]
        mains = collections.Counter(nm(x["mdl"], int(x["seq"])) for x in fr if x["seq"] == x["seq"])
        ovs = collections.Counter(ovtext((x["ovA"], x["ovS"]), x["mdl"]) for x in fr)
        v = st.mean(spd(x) for x in fr)
        row = [tag, CUR[0], tag.split("_")[2], f"{v:.1f}", f"{st.mean(x['pp_crouchFraction'] for x in fr):.2f}" if fr[0]['pp_crouchFraction'] == fr[0]['pp_crouchFraction'] else "-",
               f"{st.mean(x['pp_velocity'] for x in fr):.2f}" if fr[0]['pp_velocity'] == fr[0]['pp_velocity'] else "-", f"{period(fr, 'vmaY'):.3f}", f"{period(fr, 'vmaP'):.3f}"] + [f"{amp(fr, k):.3f}" for k in ("vmaP", "vmaY", "vmaR", "vmR", "vmU")] + [str(dict(mains.most_common(2))), str(dict(ovs.most_common(2)))]
        f.write("\t".join(row) + "\n")
        say(*row[:13])

# ---- C2 per gun summary
say("== C2 guns")
with open(os.path.join(O, "C2-GUNS.tsv"), "w", encoding="utf-8") as f:
    f.write("tag\tgun\tmain sequences (name len_s)\toverlays seen\tpose params on the model\n")
    PR = {}
    for l in open(os.path.join(D, "frida", "ranges.jsonl"), encoding="utf-8"):
        o = json.loads(l); PR[int(o["mdl"], 16) & 0xffffff] = o["idx"]
    for tag in sorted(t for t in TAGS if t.startswith(("c2_", "c2b_", "c5_", "f_", "c4_"))):
        a, b = win(tag)
        k = [t for t, x in MK[tag] if x not in ("logstart", "end")]
        fr = cut(k[0] - 300 if k else a, b)
        if not fr: continue
        mdl = fr[-1]["mdl"]
        sr = seqruns(fr)
        ms = " ".join(f"{nm(s[5], s[0])}:{(s[2] - s[1]) / 1000:.2f}" for s in sr)
        ov = []
        for o in ovruns(fr):
            t_ = ovtext(o[0], o[3])
            if not ov or ov[-1] != t_: ov.append(t_)
        # ranges.jsonl is keyed by the (reused) model address, so read which pose parameters exist from the frames instead
        pp = ",".join(n[3:] for n in PPN if any(x[n] == x[n] for x in fr))
        f.write(f"{tag}\t{CUR[0]}\t{ms}\t{' / '.join(ov)}\t{pp}\n")
        say(tag, CUR[0], ms[:300], "|", " / ".join(ov)[:300])
OUT.close()
