"""Attachment path of a titan sequence, from the local unpacked model (research tool; numbers only).

clip_path(seq_label, attachment, chassis="medium", base_label=None)
  -> list of (t, f, r, u) relative to the model origin (+f forward, +r right, +u up), one per frame.
  For a delta (gesture) sequence the delta is applied at full weight on top of frame 0 of base_label
  (default: the plain stand idle), so the path shape and timing are right; the exact amplitude is not
  (the real layer weights spine 0.47-0.64).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pose"))
from anim53 import Anim, Mdl, Seq, attachments, qmul, qrot, world  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "..", "local", "titan-models", "models")
BASES = {"light": "titans/light/titan_light", "medium": "titans/medium/titan_medium", "heavy": "titans/heavy/titan_heavy"}
PARTS = ["mp_core", "mp_reactions", "mp_scripted", "mp_synced", "mp_embark", "mp_melee", "sp_core"]
_cache = {}


def find(chassis, label):
    for part in PARTS:
        p = os.path.join(ROOT, BASES[chassis] + "_" + part + ".mdl")
        if not os.path.exists(p):
            continue
        m = _cache.get(p) or Mdl(p)
        _cache[p] = m
        for k in range(m.numlocalseq):
            s = Seq(m, k)
            if s.label == label:
                return m, s
    raise KeyError(label)


CHAR = {"light": "titans/light/titan_light_northstar", "medium": "titans/medium/titan_medium_vanguard", "heavy": "titans/heavy/titan_heavy_ogre"}


def _att(m, W, name, chassis="medium"):
    cp = os.path.join(ROOT, CHAR[chassis] + ".mdl")
    cm = _cache.get(cp) or Mdl(cp)
    _cache[cp] = cm
    idx = {b["name"]: b["idx"] for b in m.bones}
    for a in attachments(cm):
        if a["name"] == name:
            bp, bq = W[idx[cm.bones[a["bone"]]["name"]]]
            r = qrot(bq, a["pos"])
            return (bp[0] + r[0], bp[1] + r[1], bp[2] + r[2])
    raise KeyError(name)


def clip_path(label, att, chassis="medium", base_label="a_MP_CQB_idle", delta_order="base_first"):
    m, s = find(chassis, label)
    an = s.anims()
    a = Anim(m, an[len(an) // 2])
    base = None
    if a.delta:
        bm, bs = find(chassis, base_label)
        if bm is not m:
            raise ValueError("base sequence lives in another model file")
        base = Anim(bm, bs.anims()[len(bs.anims()) // 2]).local(0)
    out = []
    for fr in range(a.frames):
        loc = a.local(fr)
        if base is not None:
            mix = []
            for b in range(m.numbones):
                bb = base[b]
                dd = loc[b]
                if bb is None:
                    mix.append(None if dd is None else dd)
                    continue
                if dd is None:
                    mix.append(bb)
                    continue
                pos = (bb[0][0] + dd[0][0], bb[0][1] + dd[0][1], bb[0][2] + dd[0][2])
                q = qmul(bb[1], dd[1]) if delta_order == "base_first" else qmul(dd[1], bb[1])
                mix.append((pos, q))
            loc = mix
        W = world(m, loc)
        x, y, z = _att(m, W, att, chassis)
        out.append((fr / a.fps, x, -y, z))
    return out


if __name__ == "__main__":
    lab = sys.argv[1] if len(sys.argv) > 1 else "mp_stand_gesture_xo16_vanguard"
    for t, f, r, u in clip_path(lab, "HAND_L")[::5]:
        print("%.3f %.1f %.1f %.1f" % (t, f, r, u))
