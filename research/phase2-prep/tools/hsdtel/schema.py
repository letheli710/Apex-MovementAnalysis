"""Column contract for the unified telemetry table (schema id "hsdtel1").

Provenance classes (every column has exactly one):
  meta  written by the parser about where a row came from
  obs   read from the game: a field the SDK/engine printed, or a value a script
        read from an engine API without arithmetic (positions, velocities,
        flags, Time(), FrameTime(), input states, log-sink wall clock)
  ing   computed inside the game by the HSD.MoveDiag mod (e.g. airtime);
        prefixed "ing_"
  drv   computed offline by hsdtel; prefixed "drv_"

Units: Source units (u, 1 u = 1 inch) and seconds; angles in degrees.
"""
from collections import OrderedDict

# name -> (provenance, unit, description)
COLUMNS = OrderedDict([
    ("file", ("meta", "", "source log file (basename)")),
    ("line_no", ("meta", "", "1-based line number in that file")),
    ("source", ("meta", "", "MT = SDK [MOVE-TRACE]; HSD = HSD.MoveDiag mod; CV = SDK [CLASSVAR] bridge_classvar_get output; LOG = engine level-load line")),
    ("side", ("obs", "", "cl = S21 client prediction, sv = S3 dedi; from the log prefix Native(C)/Script(S)/... or --side (LOG rows: from the folder)")),
    ("session", ("meta", "", "log session: the GUID folder of the file (platform/logs/<side>/<GUID>/), else the name of its folder; one game process")),
    ("kind", ("obs", "", "cmd (MT) | classvar (CV) | map (LOG) | frame | evt | takeoff | land | mark | run | setting | dump | dumpfile | init | error")),
    ("wall", ("obs", "s", "log-sink wall clock from the [YYYY-MM-DD HH:MM:SS.mmm] file prefix, as seconds since 1970 reading the logged local time as if UTC; ms resolution; time the line was written, not simulation time; empty on console copies")),
    ("run", ("obs", "", "HSD: value of hsd_md_run when the line was printed")),
    ("seq", ("obs", "", "HSD: per-VM line counter (gaps = lost lines)")),
    ("t", ("obs", "s", "HSD: script Time() (game clock)")),
    ("ft", ("obs", "s", "HSD: script FrameTime()")),
    ("cmd", ("obs", "", "MT: usercmd command_number")),
    ("ent", ("obs", "", "MT ent= / HSD ent= entity index")),
    ("bot", ("obs", "", "HSD server: 1 = fake client")),
    ("replay", ("obs", "", "MT client: 1 = re-predicted command (rp=1)")),
    ("ox", ("obs", "u", "origin x (MT: before the move)")),
    ("oy", ("obs", "u", "origin y")),
    ("oz", ("obs", "u", "origin z")),
    ("vx", ("obs", "u/s", "velocity x (MT: before the move)")),
    ("vy", ("obs", "u/s", "velocity y")),
    ("vz", ("obs", "u/s", "velocity z")),
    ("pox", ("obs", "u", "MT: origin x after the move")),
    ("poy", ("obs", "u", "MT: origin y after the move")),
    ("poz", ("obs", "u", "MT: origin z after the move")),
    ("pvx", ("obs", "u/s", "MT: velocity x after the move")),
    ("pvy", ("obs", "u/s", "MT: velocity y after the move")),
    ("pvz", ("obs", "u/s", "MT: velocity z after the move")),
    ("pitch", ("obs", "deg", "HSD client: EyeAngles().x")),
    ("yaw", ("obs", "deg", "HSD client: EyeAngles().y")),
    ("ground", ("obs", "", "1/0; MT ge= (ground entity before the move); HSD IsOnGround(); -1 = API unavailable")),
    ("slide", ("obs", "", "1/0; MT slide= (before the move); HSD IsSliding(); -1 = unavailable")),
    ("sprint", ("obs", "", "1/0; MT spr=; HSD IsSprinting(); -1 = unavailable")),
    ("crouch", ("obs", "", "HSD IsCrouched(); -1 = unavailable")),
    ("duck", ("obs", "", "MT duck= m_duckState (0 stand, 2 ducked)")),
    ("buttons", ("obs", "", "MT b= m_nButtons (held) as integer; bits per in_buttons.h")),
    ("fwd", ("obs", "", "MT fwd= forwardmove")),
    ("sidemove", ("obs", "", "MT sd= sidemove")),
    ("maxspeed", ("obs", "u/s", "MT ms= CMoveData maxspeed")),
    ("movescale", ("obs", "", "MT msc= m_cachedMoveScale")),
    ("in_jump", ("obs", "", "HSD client IsInputCommandHeld(IN_JUMP); -1 = unavailable")),
    ("in_duck", ("obs", "", "HSD client IsInputCommandHeld(IN_DUCK)")),
    ("in_fwd", ("obs", "", "HSD client IsInputCommandHeld(IN_FORWARD)")),
    ("ax_fwd", ("obs", "", "HSD client GetInputAxisForward(); -9 = unavailable")),
    ("ax_right", ("obs", "", "HSD client GetInputAxisRight(); -9 = unavailable")),
    ("evt", ("obs", "", "HSD server movement event name")),
    ("label", ("obs", "", "HSD mark label")),
    ("key", ("obs", "", "HSD setting key")),
    ("vtype", ("obs", "", "HSD setting getter that succeeded: float|int|string|ERR")),
    ("value", ("obs", "", "HSD setting value as printed; LOG map: the map name")),
    ("msg", ("obs", "", "HSD error text")),
    ("where", ("obs", "", "HSD error: which mod function contained the error")),
    ("prev", ("obs", "", "HSD run: previous run label")),
    ("ok", ("obs", "", "HSD dump: keys read successfully")),
    ("total", ("obs", "", "HSD dump: keys attempted")),
    ("dumpfile_ok", ("obs", "", "HSD dumpfile: DevTextBufferDumpToFile return value")),
    ("mod", ("obs", "", "HSD init: mod version")),
    ("ing_airtime", ("ing", "s", "mod: Time() between sampled takeoff and landing")),
    ("ing_groundtime", ("ing", "s", "mod: Time() on the ground before a takeoff")),
    ("ing_takeoff", ("ing", "u/s", "mod: horizontal speed at the takeoff sample")),
    ("ing_peak", ("ing", "u/s", "mod: max horizontal speed sampled in the air")),
    ("ing_land", ("ing", "u/s", "mod: horizontal speed at the landing sample")),
    ("ing_gain", ("ing", "u/s", "mod: land - takeoff")),
    ("ing_hop", ("ing", "", "mod: consecutive takeoffs with < 0.1 s ground time")),
    ("drv_run", ("drv", "", "trial id: HSD run if present, else MT burst index")),
    ("drv_burst", ("drv", "", "MT: index of a contiguous command range (gap > --burst-gap cmds starts a new one)")),
    ("drv_batch", ("drv", "", "MT: reset batch within the stream; +1 when cmd goes backwards, or jumps > --burst-gap across a level load / VM start / dedi RESPAWN / position jump (TELEMETRY-SCHEMA.md 5)")),
    ("drv_join", ("drv", "", "MT: ok = paired with the other side's line for the same usercmd on (session, ent, drv_batch, cmd); none; ambiguous (more than one candidate)")),
    ("drv_spd2d", ("drv", "u/s", "hypot(vx, vy)")),
    ("drv_spd2d_post", ("drv", "u/s", "MT: hypot(pvx, pvy)")),
    ("drv_dspd2d", ("drv", "u/s", "MT: post - pre horizontal speed within one command")),
    ("drv_dheading", ("drv", "deg", "MT: change of horizontal velocity direction within one command")),
    ("drv_dt", ("drv", "s", "HSD: t - previous t of the same side/kind; MT: drv_dt_est")),
    ("drv_dt_est", ("drv", "s", "MT: |po_xy - o_xy| / |pv_xy| when |pv_xy| > 20 u/s (assumes origin += post velocity * frametime and no collision; positions are printed with 3 decimals, so the relative error is about 0.0005 u / displacement)")),
    ("drv_accel2d", ("drv", "u/s^2", "HSD: (spd2d - prev spd2d) / drv_dt; MT: drv_dspd2d / drv_dt_est")),
    ("drv_pressed", ("drv", "", "MT: buttons pressed this command vs the previous line of the stream")),
    ("drv_wish_yaw", ("drv", "deg", "HSD client: yaw + atan2(-ax_right, ax_fwd); empty without input")),
    ("drv_flags", ("drv", "", "quality flags: nonfinite|teleport|api_missing")),
])

PROVENANCE = {name: spec[0] for name, spec in COLUMNS.items()}
NUMERIC = {
    "line_no", "wall", "run", "seq", "t", "ft", "cmd", "ent", "bot", "replay", "ox", "oy", "oz", "vx", "vy", "vz",
    "pox", "poy", "poz", "pvx", "pvy", "pvz", "pitch", "yaw", "ground", "slide", "sprint", "crouch", "duck", "buttons",
    "fwd", "sidemove", "maxspeed", "movescale", "in_jump", "in_duck", "in_fwd", "ax_fwd", "ax_right",
    "ing_airtime", "ing_groundtime", "ing_takeoff", "ing_peak", "ing_land", "ing_gain", "ing_hop",
    "drv_burst", "drv_batch", "drv_spd2d", "drv_spd2d_post", "drv_dspd2d", "drv_dheading", "drv_dt", "drv_dt_est",
    "drv_accel2d", "drv_pressed", "drv_wish_yaw",
}

# Required observed keys per HSD (side, kind) for ver=2 lines.
HSD_REQUIRED = {
    "frame": ("t", "o", "vel", "ground"),
    "evt": ("evt", "t", "o", "vel"),
    "takeoff": ("t", "o", "vel", "groundtime"),
    "land": ("t", "o", "vel", "airtime", "takeoff", "peak", "land"),
    "mark": ("t", "label"),
    "run": ("prev",),
    "setting": ("key", "vtype", "value"),
    "dump": ("ok", "total"),
    "dumpfile": ("file",),
    "init": (),
    "error": ("where", "msg"),
}

# in_buttons.h:17-43
BUTTON_BITS = OrderedDict([
    ("ATTACK", 1 << 0), ("JUMP", 1 << 1), ("DUCK", 1 << 2), ("FORWARD", 1 << 3), ("BACK", 1 << 4),
    ("USE", 1 << 5), ("MOVELEFT", 1 << 9), ("MOVERIGHT", 1 << 10), ("ATTACK2", 1 << 11),
    # +speed (sprint) is bit 15 in this build: observed in every sprinting usercmd of M2 (2160/2160 with the
    # bit set, 0 with 1 << 17), although s21-r5sdk public/game/shared/in_buttons.h:34 names 1 << 17 IN_SPEED
    # (that header is Source/TF2-derived; it calls bit 15 IN_ALT2).
    ("SPEED", 1 << 15), ("DODGE", 1 << 28),
])
IN_JUMP = BUTTON_BITS["JUMP"]
IN_DUCK = BUTTON_BITS["DUCK"]
IN_SPEED = BUTTON_BITS["SPEED"]
LURCH_MASK = 0x618  # tapstrafe.cpp:26


def button_names(mask):
    return "|".join(n for n, b in BUTTON_BITS.items() if mask & b)


def as_json():
    return {
        "schema": "hsdtel1",
        "columns": [
            {"name": n, "provenance": p, "unit": u, "description": d}
            for n, (p, u, d) in COLUMNS.items()
        ],
        "hsd_required_keys": {k: list(v) for k, v in HSD_REQUIRED.items()},
    }


def as_markdown():
    lines = ["| column | provenance | unit | description |", "|---|---|---|---|"]
    for n, (p, u, d) in COLUMNS.items():
        lines.append(f"| `{n}` | {p} | {u} | {d.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


BEGIN_MARK = "<!-- BEGIN GENERATED COLUMNS -->\n"
END_MARK = "<!-- END GENERATED COLUMNS -->"


def update_doc(path):
    """Rewrite the generated column table between the markers in a Markdown file."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    start = text.index(BEGIN_MARK) + len(BEGIN_MARK)
    end = text.index(END_MARK)
    new = text[:start] + as_markdown() + text[end:]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    return new != text
