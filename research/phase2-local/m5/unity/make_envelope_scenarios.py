"""Write scenarios_envelope.json: ../../m4/unity/scenarios.json without the recorded grapple release steps (stdlib only).

    python make_envelope_scenarios.py

With it the replay ends each grapple pull by the model's own detach envelope (origin within 34.1 u of the hooked surface,
SWING §4/§6) instead of the recorded detach command, so the release timing becomes a model output. Nothing else changes.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "m4", "unity", "scenarios.json")


def main():
    with open(SRC, encoding="utf-8") as fh:
        sc = json.load(fh)
    removed = []
    for tid, t in sc.get("trials", {}).items():
        if "grapple_release_step" in t:
            removed.append((tid, t.pop("grapple_release_step")))
            t["source"] = "release step removed by m5/unity/make_envelope_scenarios.py (model detach envelope instead)"
    sc["description"] = sc["description"] + " M5 variant: grapple_release_step removed (detach envelope)."
    with open(os.path.join(HERE, "scenarios_envelope.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sc, fh, indent=1)
        fh.write("\n")
    for tid, s in removed:
        print(f"{tid}: recorded release step {s} removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
