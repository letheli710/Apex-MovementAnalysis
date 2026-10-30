"""Detect whether an R5 (Apex) measurement is running, so TF2 runs never disturb it.

R5 runs (Apex-MovementAnalysis*/research/phase2-local/tools) launch r5apex_dx12.exe and
r5apex_ds.exe through hsd_launch.ps1, talk AgentLink on TCP 37019/37020, need UDP 37015
free, and fail their fps check (+-3 %) under extra load. Any of these signals counts:
  1. an R5 game process: r5apex.exe, r5apex_dx12.exe, r5apex_ds.exe
  2. an R5 runner process: command line mentions hsd_session.py, hsd_trial.py,
     hsd_launch.ps1, hsd_cvar_help.py or agentlink.py
  3. a listener on TCP 37019 or 37020 (AgentLink)
  4. the shared lock file GAME-LOCK.txt held by R5 (first word "r5")

Shared lock (agreed with the R5 sessions, user request 2026-10-28): one game side at a time.
GAME-LOCK.txt in the workspace root holds one line "<r5|tf2> <session> <iso time>". The side
that runs writes it, deletes it when done; the other side waits. Locks older than
LOCK_STALE_H hours are treated as stale (a crashed session).

Usage: python -I r5_guard.py   -> prints the reasons, exit 1 if R5 is active, 0 if idle.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

LOCK = Path(r"C:\Workspace\Playground\ReApex-DataAnalysis\GAME-LOCK.txt")
LOCK_STALE_H = 6

R5_IMAGES = ("r5apex.exe", "r5apex_dx12.exe", "r5apex_ds.exe")
R5_SCRIPTS = ("hsd_session.py", "hsd_trial.py", "hsd_launch.ps1", "hsd_cvar_help.py", "agentlink.py")
R5_PORTS = (37019, 37020)

_PS = ("Get-CimInstance Win32_Process | Select-Object ProcessId,Name,CommandLine | "
       "ConvertTo-Json -Compress")


def _processes():
    out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", _PS],
                         capture_output=True, text=True, timeout=60).stdout
    data = json.loads(out or "[]")
    return data if isinstance(data, list) else [data]


def _listening_ports():
    out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True, timeout=30).stdout
    ports = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "TCP" and parts[3] == "LISTENING":
            try:
                ports.add(int(parts[1].rsplit(":", 1)[1]))
            except ValueError:
                pass
    return ports


def lock_owner():
    """'r5', 'tf2' or None (no lock, or a stale one)."""
    try:
        text = LOCK.read_text(encoding="utf-8").strip()
        age_h = (time.time() - LOCK.stat().st_mtime) / 3600
    except OSError:
        return None
    if not text or age_h > LOCK_STALE_H:
        return None
    return text.split()[0].lower()


def _clear_stale_lock():
    """Move a stale lock aside. The rename is atomic, so of two takers that both saw it stale
    only one moves it; if what it moved turns out fresh (someone took the lock in between),
    it is put back (a Windows rename never overwrites, so that is exclusive too)."""
    aside = LOCK.with_name(f"GAME-LOCK.stale-{os.getpid()}.txt")
    try:
        if (time.time() - LOCK.stat().st_mtime) / 3600 <= LOCK_STALE_H:
            return
        os.rename(LOCK, aside)
    except OSError:
        return
    try:
        if (time.time() - aside.stat().st_mtime) / 3600 <= LOCK_STALE_H:
            os.rename(aside, LOCK)
        else:
            aside.unlink()
    except OSError:
        pass


def take_lock(session):
    """Take GAME-LOCK.txt atomically; True if this process now holds it.
    2026-10-29 11:34 (W1): two runners waiting on the lock both saw it free and both wrote it.
    Now the file is created exclusive (O_CREAT|O_EXCL), so only one creator wins; a held lock
    (r5 or tf2) makes this return False and the caller waits again. pid=<n> marks which TF2
    runner wrote it: several TF2 sessions share this runner and the session name (2026-10-29:
    one runner deleted another one's lock while its game ran)."""
    if LOCK.exists() and lock_owner() is None:
        _clear_stale_lock()
    line = f"tf2 {session} {datetime.now().isoformat(timespec='seconds')} pid={os.getpid()}\n"
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(line)
    # re-check: the file on disk must be ours (guards against a writer that ignores O_EXCL,
    # e.g. an R5 session writing the lock by hand)
    return own_lock()


def own_lock():
    try:
        return f"pid={os.getpid()}" in LOCK.read_text(encoding="utf-8").split()
    except OSError:
        return False


def release_lock():
    if own_lock():
        LOCK.unlink(missing_ok=True)


def r5_activity():
    """Reasons R5 looks active (empty list = idle)."""
    reasons = []
    if lock_owner() == "r5":
        reasons.append("GAME-LOCK.txt held by r5")
    for p in _processes():
        name = (p.get("Name") or "").lower()
        cmd = (p.get("CommandLine") or "").lower()
        if name in R5_IMAGES:
            reasons.append(f"process {name} (pid {p.get('ProcessId')})")
        elif any(s in cmd for s in R5_SCRIPTS) and "r5_guard.py" not in cmd:
            hit = next(s for s in R5_SCRIPTS if s in cmd)
            reasons.append(f"runner {hit} in {name} (pid {p.get('ProcessId')})")
    for port in sorted(_listening_ports() & set(R5_PORTS)):
        reasons.append(f"AgentLink port {port} listening")
    return reasons


if __name__ == "__main__":
    r = r5_activity()
    print("R5 active: " + "; ".join(r) if r else "R5 idle")
    sys.exit(1 if r else 0)
