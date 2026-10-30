"""Concurrent dummy takers for the TF2 runner lock (no game). Uses a scratch lock path.
python lock_race_test.py <runtime dir> <scratch dir>"""
import json
import multiprocessing as mp
import os
import sys
import time
import types
from pathlib import Path


def worker(runtime, scratch, start_at, mode, q):
    sys.path.insert(0, runtime)
    import r5_guard
    r5_guard.LOCK = Path(scratch) / "GAME-LOCK.txt"
    while time.time() < start_at:
        pass
    if mode == "raw":
        ok = r5_guard.take_lock("test")
        q.put({"pid": os.getpid(), "ok": ok})
        return
    import runner
    runner.r5_activity = lambda: []
    runner.game_pids = lambda: []
    _sleep = time.sleep
    runner.time.sleep = lambda s: _sleep(min(s, 0.3))
    runner.acquire(types.SimpleNamespace(attach=False, r5_wait=2))
    t_in = time.time()
    on_disk = r5_guard.LOCK.read_text(encoding="utf-8")
    _sleep(0.4)
    r5_guard.release_lock()
    q.put({"pid": os.getpid(), "in": t_in, "out": time.time(), "own": f"pid={os.getpid()}" in on_disk})


def run(runtime, scratch, n, mode, pre=None):
    lock = Path(scratch) / "GAME-LOCK.txt"
    lock.unlink(missing_ok=True)
    if pre:
        lock.write_text(pre, encoding="utf-8")
        old = time.time() - 7 * 3600
        os.utime(lock, (old, old))
    q = mp.Queue()
    start_at = time.time() + 3
    ps = [mp.Process(target=worker, args=(runtime, scratch, start_at, mode, q)) for _ in range(n)]
    for p in ps:
        p.start()
    res = [q.get(timeout=120) for _ in ps]
    for p in ps:
        p.join()
    return res


if __name__ == "__main__":
    runtime, scratch = sys.argv[1], sys.argv[2]
    out = {}
    for trial in range(5):
        r = run(runtime, scratch, 8, "raw")
        out[f"raw_{trial}"] = sum(x["ok"] for x in r)
        (Path(scratch) / "GAME-LOCK.txt").unlink(missing_ok=True)
    r = run(runtime, scratch, 8, "raw", pre="tf2 crashed 2026-10-29T00:00:00 pid=1\n")
    out["stale_winners"] = sum(x["ok"] for x in r)
    out["stale_aside_left"] = [p.name for p in Path(scratch).glob("GAME-LOCK.stale-*")]
    (Path(scratch) / "GAME-LOCK.txt").unlink(missing_ok=True)
    r = sorted(run(runtime, scratch, 6, "acquire"), key=lambda x: x["in"])
    overlaps = sum(1 for a, b in zip(r, r[1:]) if b["in"] < a["out"])
    out["acquire_n"] = len(r)
    out["acquire_overlaps"] = overlaps
    out["acquire_all_own"] = all(x["own"] for x in r)
    out["lock_left"] = (Path(scratch) / "GAME-LOCK.txt").exists()
    print(json.dumps(out, indent=1))
