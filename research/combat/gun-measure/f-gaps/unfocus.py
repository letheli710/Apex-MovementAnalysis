#!/usr/bin/env python3
"""If the R5 client window holds the foreground, hand the foreground to the next visible non-game top window
(AttachThreadInput + SetForegroundWindow; no input is sent). The game keeps rendering behind it.  py -3 -I unfocus.py"""
import ctypes, subprocess
from ctypes import wintypes as W
u32 = ctypes.WinDLL("user32"); k32 = ctypes.WinDLL("kernel32")
out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
pids = {int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"r5apex')}
pid = lambda h: (lambda p: (u32.GetWindowThreadProcessId(h, ctypes.byref(p)), p.value)[1])(W.DWORD())
fg = u32.GetForegroundWindow()
print("fg is r5:", pid(fg) in pids)
if pid(fg) in pids:
    cand = []
    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, _):
        b = ctypes.create_unicode_buffer(200); u32.GetWindowTextW(h, b, 200)
        if u32.IsWindowVisible(h) and not u32.IsIconic(h) and pid(h) not in pids and b.value and b.value not in ("StatusBarWnd", "RzMonitorForegroundWindow") and not b.value.startswith("R5F"):
            cand.append((h, b.value))
        return True
    u32.EnumWindows(cb, 0)
    if cand:
        h, t = cand[0]
        tf = u32.GetWindowThreadProcessId(fg, None); tm = k32.GetCurrentThreadId()
        u32.AttachThreadInput(tm, tf, True); ok = u32.SetForegroundWindow(h); u32.AttachThreadInput(tm, tf, False)
        print("handed to", repr(t[:40]), ok, "now fg is r5:", pid(u32.GetForegroundWindow()) in pids)
