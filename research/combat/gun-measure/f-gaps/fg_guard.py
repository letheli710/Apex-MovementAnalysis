#!/usr/bin/env python3
"""Keep the user's window in front while the R5 client starts (no input is sent).
  py -3 -I fg_guard.py <secs>
Remembers the foreground window at start; whenever an r5apex window takes the foreground, hands it back
(SetForegroundWindow with AttachThreadInput) and minimizes nothing. Prints what it did."""
import ctypes, sys, time, subprocess
from ctypes import wintypes as W
u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32")


def pids():
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    return {int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"r5apex')}


def pid_of(h):
    p = W.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(p)); return p.value


def give_back(prev):
    fg = u32.GetForegroundWindow()
    t_fg = u32.GetWindowThreadProcessId(fg, None)
    t_me = k32.GetCurrentThreadId()
    u32.AttachThreadInput(t_me, t_fg, True)
    ok = u32.SetForegroundWindow(prev)
    u32.AttachThreadInput(t_me, t_fg, False)
    return ok


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 180
    prev = u32.GetForegroundWindow()
    end = time.time() + secs
    n = 0
    while time.time() < end:
        fg = u32.GetForegroundWindow()
        if fg and fg != prev:
            if pid_of(fg) in pids():
                ok = give_back(prev); n += 1
                print(time.strftime("%H:%M:%S"), "r5 took foreground, gave back", ok, flush=True)
            else:
                prev = fg  # the user switched windows themselves
        time.sleep(0.25)
    print("guard done, handed back", n, flush=True)


if __name__ == "__main__":
    main()
