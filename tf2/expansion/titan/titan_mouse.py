"""T0 mouse driver: identical scripted mouse input for the pilot / titan turn-rate test.

The game has no script API for look input, so the runner (runner.py --mouse) starts this
thread next to the game. It tails the live Northstar log; when the client plan prints
  HSDDIAG CMD <t> hsd_mouse <name> <dx> <dy> <count> <interval_ms>
it sends <count> relative mouse moves of (dx, dy) counts, one every <interval_ms>, with
SendInput (the same path a real mouse's raw input takes). Before each burst it checks that the
Titanfall 2 window is in the foreground; if not it tries once to bring it forward and otherwise
skips the burst (so it never moves the cursor of whatever window the user is working in).
Every burst is recorded (wall time, focus, events sent) and written to mouse.json by the runner.

The measurement never depends on this thread's timing: the turn rate comes from the per-frame
HSDDIAG C / CAM lines; this only has to deliver the same counts to the pilot and to the titan.
"""
import ctypes
import ctypes.wintypes as wt
import threading
import time
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)
winmm = ctypes.WinDLL("winmm")

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wt.DWORD), ("wParamL", wt.WORD), ("wParamH", wt.WORD)]


class _U(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("u", _U)]


def send_move(dx, dy):
    inp = INPUT(type=INPUT_MOUSE, u=_U(mi=MOUSEINPUT(dx=dx, dy=dy, mouseData=0, dwFlags=MOUSEEVENTF_MOVE,
                                                     time=0, dwExtraInfo=0)))
    return user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def foreground_pid():
    hwnd = user32.GetForegroundWindow()
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def game_window(pids):
    found = []

    def cb(hwnd, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return found[0] if found else None


class MouseDriver(threading.Thread):
    def __init__(self, logs_dir, t0, game_pids):
        super().__init__(daemon=True)
        self.logs_dir = Path(logs_dir)
        self.t0 = t0
        self.game_pids = game_pids  # callable -> list of pids
        self.stop_flag = threading.Event()
        self.records = []
        self.seen_lines = 0

    def stop(self):
        self.stop_flag.set()

    def _log(self):
        logs = [p for p in self.logs_dir.glob("nslog*.txt") if p.stat().st_mtime >= self.t0 - 5]
        return max(logs, key=lambda p: p.stat().st_mtime) if logs else None

    def run(self):
        winmm.timeBeginPeriod(1)
        try:
            self._run()
        finally:
            winmm.timeEndPeriod(1)

    def _run(self):
        log = None
        while log is None and not self.stop_flag.is_set():
            log = self._log()
            time.sleep(0.5)
        if log is None:
            return
        with open(log, "r", encoding="utf-8", errors="replace") as f:
            buf = ""
            while not self.stop_flag.is_set():
                chunk = f.read()
                if not chunk:
                    time.sleep(0.02)
                    continue
                buf += chunk
                *lines, buf = buf.split("\n")
                for line in lines:
                    if "HSDDIAG CMD" in line and " hsd_mouse " in line:
                        self.seen_lines += 1
                        self._burst(line[line.index(" hsd_mouse ") + len(" hsd_mouse "):].split(), time.time())

    def _focus(self, pids):
        if foreground_pid() in pids:
            return "ok"
        hwnd = game_window(pids)
        if hwnd:
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.15)
            if foreground_pid() in pids:
                return "raised"
        return "nofocus"

    def _burst(self, args, seen):
        rec = {"args": args, "seen_wall": seen}
        try:
            name, dx, dy, count, interval_ms = args[0], int(args[1]), int(args[2]), int(args[3]), float(args[4])
        except (IndexError, ValueError):
            rec["error"] = "bad args"
            self.records.append(rec)
            return
        pids = set(self.game_pids())  # tasklist is slow: once per burst
        rec["focus"] = self._focus(pids)
        if rec["focus"] == "nofocus":
            self.records.append(rec)
            return
        sent = 0
        start = time.perf_counter()
        rec["start_wall"] = time.time()
        for i in range(count):
            target = start + i * interval_ms / 1000.0
            while time.perf_counter() < target:
                if target - time.perf_counter() > 0.002:
                    time.sleep(0.001)
            # stop at once if the user switched windows mid-burst
            if i % 16 == 0 and foreground_pid() not in pids:
                rec["focus_lost_at"] = i
                break
            sent += send_move(dx, dy)
        rec["sent"] = sent
        rec["duration_s"] = time.perf_counter() - start
        rec["name"] = name
        self.records.append(rec)
