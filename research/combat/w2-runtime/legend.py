"""Set the local player's legend and give its kit (same calls as hsd_trial.py --legend/--kit)."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "phase2-local", "tools"))
from agentlink import AgentLink, DEFAULT_GAME
import hsd_trial
with AgentLink("server", DEFAULT_GAME) as s:
    print(s.eval('Agent_SetLegend( "me", "%s" )' % sys.argv[1], check=False).get("reply"))
    time.sleep(2.0)
    print(s.eval(hsd_trial.KIT_SERVER, check=False).get("reply"))
