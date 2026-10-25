"""B1 traversal class of a runs.csv row (shared by aggregate_b1.py and anim_time_b1.py)."""


def cls(r):
    s, h, T = r["schedule"], int(r["height"]), float(r["duration"])
    app = s.split("_")[1]
    if app == "cr":
        if h >= 120:
            return "crouch_h120_long" if T > 0.72 else "crouch_h120"
        return "crouch_h%d" % h
    if app == "wd":
        return "stand_h120_yaw45"
    return {80: "stand_h80", 100: "stand_h100"}.get(h, "stand_h120plus")
