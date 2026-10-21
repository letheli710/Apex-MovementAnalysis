#!/usr/bin/env python3
"""Minimal client for the R5Flowstate SDK AgentLink loopback socket.

The SDK opens it when the game runs with -devsdk (s21-r5sdk/src/engine/agent_link.cpp:1-19):
dedi on 127.0.0.1:37019 (token platform/agentlink.token), client on 37020
(platform/agentlink_client.token). One request per line, one reply line each:

  AUTH <token>                         -> OK | ERR ...
  EVAL <id> <server|client|ui> <code>  -> RESULT <id> ok|err {json}
  EVAL64 <id> <ctx> <base64>           (multi-line code)
  CMD  <id> <console line>             -> RESULT <id> ok {json}
  LOG  <id> <sinceSeq> [max]           -> RESULT <id> ok {json}

A script answers an EVAL with AgentLink_Reply( string ); the reply text lands in
the JSON next to the captured console lines. Standard library only.

  py -3 agentlink.py --side server eval "printt( GetPlayerArray().len() )"
"""
import argparse
import base64
import itertools
import json
import os
import socket
import sys

PORTS = {"server": 37019, "client": 37020}
TOKENS = {"server": "agentlink.token", "client": "agentlink_client.token"}
DEFAULT_GAME = os.path.join(os.path.expanduser("~"), "Games", "R5Flowstate")


class AgentLinkError(RuntimeError):
    pass


class AgentLink:
    def __init__(self, side, game=DEFAULT_GAME, port=None, timeout=30.0):
        self.side = side
        self.ids = itertools.count(1)
        with open(os.path.join(game, "platform", TOKENS[side]), encoding="ascii") as fh:
            token = fh.read().strip()
        self.sock = socket.create_connection(("127.0.0.1", port or PORTS[side]), timeout=timeout)
        self.buf = b""
        hello = self._line()
        if not hello.startswith("AGENTLINK"):
            raise AgentLinkError(f"unexpected hello {hello!r}")
        self._send(f"AUTH {token}")
        r = self._line()
        if r != "OK":
            raise AgentLinkError(f"auth failed: {r}")

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _send(self, line):
        self.sock.sendall(line.encode("utf-8") + b"\n")

    def _line(self):
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise AgentLinkError("connection closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line.decode("utf-8", "replace").rstrip("\r")

    def _request(self, op, *args):
        rid = str(next(self.ids))
        self._send(" ".join([op, rid] + [a for a in args if a != ""]))
        while True:
            line = self._line()
            if line.startswith("RESULT "):
                _, got, status, payload = (line.split(" ", 3) + [""])[:4]
                if got != rid:
                    continue  # a late reply to an earlier, timed-out request
                data = json.loads(payload) if payload else {}
                data["ok"] = status == "ok"
                return data
            if line.startswith("ERR"):
                raise AgentLinkError(line)

    def eval(self, code, ctx=None, check=True):
        """Run Squirrel code in the given VM; returns the parsed reply JSON."""
        ctx = ctx or self.side
        if "\n" in code:
            r = self._request("EVAL64", ctx, base64.b64encode(code.encode("utf-8")).decode("ascii"))
        else:
            r = self._request("EVAL", ctx, code)
        if check and not r["ok"]:
            raise AgentLinkError(f"EVAL failed: {json.dumps(r)[:800]}")
        return r

    def cmd(self, line):
        return self._request("CMD", line)

    def log(self, since=0, limit=500):
        return self._request("LOG", str(since), str(limit))

    def info(self):
        return self._request("INFO")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--side", choices=sorted(PORTS), default="server")
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("op", choices=["eval", "cmd", "info", "log"])
    ap.add_argument("text", nargs="?", default="")
    a = ap.parse_args(argv)
    with AgentLink(a.side, a.game) as link:
        if a.op == "eval":
            r = link.eval(a.text, check=False)
        elif a.op == "cmd":
            r = link.cmd(a.text)
        elif a.op == "info":
            r = link.info()
        else:
            r = link.log(int(a.text or 0))
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
