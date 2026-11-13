#!/usr/bin/env python3
"""E-MOUSE runs: real mouse (SendInput relative moves) and real keys with r5apex_dx12 in the foreground.

  py -3 -I emouse_run.py <marks.tsv> <tag> <weapon> "<schedule>" [mods=a,b] [secs=20] [reset=1]
schedule: ';'-separated
  wait <s> | down <cmd> | up <cmd> | tap <cmd> | hold <cmd> <s>     client ClientCommand("+cmd"/"-cmd") as in recoil_run.py
  mouse <dx/s> <dy/s> <s>    real relative mouse counts per second for <s> seconds (125 Hz ticks), blocks
  mstart <dx/s> <dy/s>       same, in the background until mstop
  mstop
  key <name>                 real key press (scan code) b / x / e / v / r / g / h / ...
  wheel <+1|-1>              real mouse wheel notch
  rclick                     real right mouse button click
  mods                       server prints the active weapon's mods and fire state
Every step and every mouse tick is written to marks with time.time() (same clock as Date.now() in frida_emouse.js).
"""
import ctypes, os, sys, threading, time
from ctypes import wintypes as W

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

u32 = ctypes.WinDLL("user32", use_last_error=True)
ctypes.WinDLL("winmm").timeBeginPeriod(1)
ULONG_PTR = ctypes.c_size_t


class MI(ctypes.Structure):
    _fields_ = [("dx", W.LONG), ("dy", W.LONG), ("mouseData", W.DWORD), ("dwFlags", W.DWORD), ("time", W.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KI(ctypes.Structure):
    _fields_ = [("wVk", W.WORD), ("wScan", W.WORD), ("dwFlags", W.DWORD), ("time", W.DWORD), ("dwExtraInfo", ULONG_PTR)]


class HI(ctypes.Structure):
    _fields_ = [("uMsg", W.DWORD), ("wParamL", W.WORD), ("wParamH", W.WORD)]


class _U(ctypes.Union):
    _fields_ = [("mi", MI), ("ki", KI), ("hi", HI)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", W.DWORD), ("u", _U)]


def send(*inps):
    arr = (INPUT * len(inps))(*inps)
    return u32.SendInput(len(inps), arr, ctypes.sizeof(INPUT))


def mmove(dx, dy):
    i = INPUT(type=0); i.mi = MI(dx, dy, 0, 0x0001, 0, 0); send(i)


def mflag(flag, data=0):
    i = INPUT(type=0); i.mi = MI(0, 0, data & 0xffffffff, flag, 0, 0); send(i)


SCAN = {"b": 0x30, "x": 0x2D, "e": 0x12, "v": 0x2F, "r": 0x13, "g": 0x22, "h": 0x23, "n": 0x31, "1": 0x02, "2": 0x03, "3": 0x04, "esc": 0x01}


def keypress(name, hold=0.06):
    sc = SCAN[name]
    d = INPUT(type=1); d.ki = KI(0, sc, 0x0008, 0, 0)
    up = INPUT(type=1); up.ki = KI(0, sc, 0x0008 | 0x0002, 0, 0)
    send(d); time.sleep(hold); send(up)


def find_hwnd(exe="r5apex_dx12.exe"):
    import subprocess
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    pids = {int(l.split('","')[1]) for l in out.splitlines() if l.startswith('"')}
    found = []
    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, _):
        pid = W.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value in pids and u32.IsWindowVisible(h):
            found.append(h)
        return True
    u32.EnumWindows(cb, 0)
    return found[0] if found else None


def focus(hwnd):
    if u32.GetForegroundWindow() == hwnd:
        return True
    # Alt tap lets SetForegroundWindow work from a background process.
    a = INPUT(type=1); a.ki = KI(0x12, 0, 0, 0, 0)
    b = INPUT(type=1); b.ki = KI(0x12, 0, 0x0002, 0, 0)
    send(a, b)
    u32.ShowWindow(hwnd, 9)
    u32.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    return u32.GetForegroundWindow() == hwnd


class Mover:
    def __init__(self, rows):
        self.rows, self.th, self.stop = rows, None, threading.Event()

    def _run(self, rx, ry, dur):
        tick, t0, sx, sy, k = 0.008, time.perf_counter(), 0, 0, 0
        while not self.stop.is_set():
            el = time.perf_counter() - t0
            if dur is not None and el >= dur:
                break
            k += 1
            tx, ty = round(rx * min(el, dur or el)), round(ry * min(el, dur or el))
            dx, dy = tx - sx, ty - sy
            if dx or dy:
                mmove(dx, dy); sx += dx; sy += dy
                self.rows.append((time.time(), "m", f"{dx},{dy},{sx},{sy}"))
            nxt = t0 + k * tick
            d = nxt - time.perf_counter()
            if d > 0:
                time.sleep(d)  # timeBeginPeriod(1): ~1 ms; no busy loop, so the AgentLink thread keeps the GIL timing of key steps
        self.rows.append((time.time(), "mend", f"{sx},{sy}"))

    def start(self, rx, ry, dur=None):
        self.stop.clear()
        self.th = threading.Thread(target=self._run, args=(rx, ry, dur), daemon=True); self.th.start()

    def halt(self):
        self.stop.set()
        if self.th: self.th.join()


MODS_NUT = r'''entity p = GetPlayerArray()[0]
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
string o = ""
try { o += w.GetWeaponClassName() + " mods="; foreach ( m in w.GetMods() ) o += m + ","; o += " zf=" + p.GetZoomFrac() } catch ( e ) { o += " err=" + string( e ) }
printt( "[RT] mods " + o )
AgentLink_Reply( o )'''


def main():
    marks, tag, weap, sched = sys.argv[1:5]
    kv = dict(a.split("=", 1) for a in sys.argv[5:])
    code = open(os.path.join(HERE, "..", "..", "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    fill = dict(weap=weap, mods=kv.get("mods", "none"), stock="500", target="none", dist="150", yaw="0", snap="0", lift="0",
                heat="0.0", track="0", secs=kv.get("secs", "20"))
    for k, v in fill.items():
        code = code.replace("{{" + k + "}}", v)
    hwnd = find_hwnd()
    rows = []
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        if kv.get("reset", "1") == "1":
            s.eval('GetPlayerArray()[0].SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )', check=False)
        r = s.eval(code, check=False)
        print(tag, r.get("reply"))
        ok = focus(hwnd)
        print(tag, "focus", ok)
        if not ok:
            print(tag, "NO FOCUS, abort"); return 2
        pl.sleep(float(kv.get("settle", "1.5")))
        mv = Mover(rows)
        rows.append((time.time(), "start", ""))
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, _, arg = st.partition(" ")
            def key(sign, k):
                c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)
                rows.append((time.time(), sign + k, ""))
            if u32.GetForegroundWindow() != hwnd:
                rows.append((time.time(), "LOST_FOCUS", "")); focus(hwnd)
            if op == "wait": pl.sleep(float(arg))
            elif op == "down": key("+", arg)
            elif op == "up": key("-", arg)
            elif op == "tap": key("+", arg); pl.sleep(0.05); key("-", arg)
            elif op == "hold":
                k, d = arg.split(); key("+", k); pl.sleep(float(d)); key("-", k)
            elif op == "mouse":
                rx, ry, d = map(float, arg.split()); rows.append((time.time(), "mstart", arg)); mv.start(rx, ry, d); mv.th.join()
            elif op == "mstart":
                rx, ry = map(float, arg.split()); rows.append((time.time(), "mstart", arg)); mv.start(rx, ry)
            elif op == "mstop": mv.halt()
            elif op == "key": keypress(arg); rows.append((time.time(), "key " + arg, ""))
            elif op == "wheel": mflag(0x0800, 120 * int(arg)); rows.append((time.time(), "wheel " + arg, ""))
            elif op == "rclick": mflag(0x0008); time.sleep(0.05); mflag(0x0010); rows.append((time.time(), "rclick", ""))
            elif op == "mods":
                rr = s.eval(MODS_NUT, check=False); rows.append((time.time(), "mods", str(rr.get("reply"))))
        mv.halt()
        rows.append((time.time(), "end", ""))
        pl.sleep(0.3)
    with open(marks, "a", encoding="utf-8") as f:
        for t, m, x in rows:
            f.write(f"{tag}\t{t:.4f}\t{m}\t{x}\n")
    runs = os.path.join(HERE, "runs"); os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, f"{tag}.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {sched} {kv} {time.strftime('%Y%m%d_%H%M%S')}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    print(tag, "done", [x for _, m, x in rows if m == "mods"], [m for _, m, _ in rows if m == "LOST_FOCUS"])


if __name__ == "__main__":
    sys.exit(main() or 0)
