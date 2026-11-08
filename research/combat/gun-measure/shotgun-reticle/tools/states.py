#!/usr/bin/env python3
"""Crosshair in sprint, reload and part-way into ADS (the RUI's isSprinting, isReloading, adsFrac args).  py -3 -I states.py <out dir> [gun]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr  # noqa: E402


def main():
    out = sys.argv[1]; gun = sys.argv[2] if len(sys.argv) > 2 else "eva8"
    r = sr.R5(out)
    try:
        r.give(sr.GUNS[gun], 0)
        r.key("+", "forward"); r.key("+", "speed"); r.pl.sleep(1.2); r.state("sprint"); r.shot(f"{gun}_sprint")
        r.key("-", "speed"); r.key("-", "forward"); r.pl.sleep(1.2)
        r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.4)
        r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack"); r.pl.sleep(1.2)
        r.key("+", "reload"); r.pl.sleep(0.1); r.key("-", "reload"); r.pl.sleep(0.4); r.state("reload"); r.shot(f"{gun}_reload")
        r.pl.sleep(4)
        for i, dt in enumerate((0.03, 0.08, 0.13)):
            r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.4)
            r.key("+", "zoom"); r.pl.sleep(dt); r.state(f"ads{dt}"); r.shot(f"{gun}_adsin_{i}"); r.state(f"ads{dt} after")
            r.key("-", "zoom"); r.pl.sleep(1.0)
    finally:
        r.close()
        print("\n".join(l[:160] for l in r.log if "st t=" in l))


if __name__ == "__main__":
    main()
