"""AgentLink ping: both VMs answer? (server/client info + a trivial eval)."""
import sys; sys.path.insert(0,'../../phase2-local/tools')
from agentlink import AgentLink, DEFAULT_GAME
for side in ('server','client'):
    try:
        with AgentLink(side, DEFAULT_GAME, timeout=20) as s:
            print(side, s.info()); print(s.eval('AgentLink_Reply( "pong " + Time() )', check=False))
    except Exception as e: print(side, 'ERR', repr(e))
