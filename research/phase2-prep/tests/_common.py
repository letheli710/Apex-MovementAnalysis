import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PREP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PREP))
TOOLS = os.path.join(PREP, "tools")
FIXTURES = os.path.join(PREP, "fixtures", "synthetic")
LOGS = os.path.join(FIXTURES, "platform", "logs")
FAULTY = os.path.join(FIXTURES, "faulty")
MOD = os.path.join(REPO, "research", "phase1", "mod", "hsd_movediag")
PHASE1_TOOLS = os.path.join(REPO, "research", "phase1", "tools")
# Base script tree for the per-VM check; tests that need it skip when absent.
_SRC_ROOT = os.environ.get("HSD_SRC_ROOT") or next(
    (os.path.normpath(p) for p in ("/home/user/research-src", os.path.join(REPO, os.pardir, "research-src"))
     if os.path.isdir(p)), "/home/user/research-src")
BASE_SCRIPTS = os.environ.get("HSD_BASE_SCRIPTS", os.path.join(_SRC_ROOT, "s21-platform", "scripts", "vscripts"))

if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
