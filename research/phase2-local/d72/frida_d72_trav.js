// D-74 B traversal probe (Frida, read-only: hooks only log, nothing is changed). S21 client r5apex_dx12.exe.
// One CSV line per call of
//   TraversalMove 0x140a45380 (ev T): traversal state +0x2b34 / fraction +0x2b7c on entry and on return, type +0x2b38,
//     duck state +0x2a70, anim cycle +0x2234, +0x2b60 (PickAnim param_10), +0x2ba8 / +0x2bb4, start time +0x2b80,
//     movedata origin z (+0x120) and buttons (+0x24), gpGlobals curtime / frametime, prediction bytes 0x142373788 / 0x142373798;
//   PlayerMove 0x140a54e80 (ev P, on return, once the player pointer is known): duck state, traversal state, fraction;
//   both: view offset z +0xf0 (the eye height TraversalMove reads; added after the h120 session).
//   ev S on every traversal start (arg2 = 1): the base-state inputs of TraversalMove — point P = 0x140b05910(player), direction
//     D = 0x140b05ca0(player) (both getters into a stack buffer), view offset +0xe8..+0xf0, origin = movedata +0x118..+0x120, hull
//     movedata +0xd0, constant 0x1417f8880; h = eye z - P.z (vs -10 / 10 / 30), dot = (eye - P) . D (vs -(hull) - constant).
// Time column = wall clock ms (Date.now) so the rows join with the runner's trial times. Settings / ConVar floats that
// TraversalMove reads are sent once at the first call. Addresses are Ghidra (image base 0x140000000).
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const OUT_PATH = 'OUT_PATH_HERE';
const out = new File(OUT_PATH, 'w');
const G = at('0x1419832d8').readPointer();              // gpGlobals: +0x10 curtime, +0x30 frametime
const PRED_A = at('0x142373788'), PRED_B = at('0x142373798');
const f = (x) => (x === undefined || x === null || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
out.write(['ev', 'wall', 'cur', 'ft', 'pa', 'pb', 'arg2', 's0', 'fr0', 's1', 'fr1', 'type', 'duck', 'cyc', 'p2b60', 'p2ba8', 'p2bb4',
  'p2b80', 'z', 'btn', 'eye'].join(',') + '\n');
let P = null, nrows = 0, sentSettings = false;
const getP = new NativeFunction(at('0x140b05910'), 'pointer', ['pointer', 'pointer']);
const getD = new NativeFunction(at('0x140b05ca0'), 'pointer', ['pointer', 'pointer']);
const BUF1 = Memory.alloc(64), BUF2 = Memory.alloc(64);
const C8880 = at('0x1417f8880').readFloat();
function startRow(p, md) {
  try {
    const pp = getP(p, BUF1), dd = getD(p, BUF2);
    const P3 = [pp.readFloat(), pp.add(4).readFloat(), pp.add(8).readFloat()], D3 = [dd.readFloat(), dd.add(4).readFloat(), dd.add(8).readFloat()];
    const o = [md.add(0x118).readFloat(), md.add(0x11c).readFloat(), md.add(0x120).readFloat()];
    const v = [p.add(0xe8).readFloat(), p.add(0xec).readFloat(), p.add(0xf0).readFloat()];
    const e = [v[0] + o[0] - P3[0], v[1] + o[1] - P3[1], v[2] + o[2] - P3[2]];
    const hull = md.add(0xd0).readFloat();
    send({ ev: 'S', cur: G.add(0x10).readFloat(), P: P3, D: D3, o: o, v: v, h: e[2], dot: e[0] * D3[0] + e[1] * D3[1] + e[2] * D3[2],
      rhs: -hull - C8880, hull: hull, c: C8880, duck: p.add(0x2a70).readS32() });
    out.write(['S', Date.now(), G.add(0x10).readFloat(), '', '', '', '', P3.join(' '), D3.join(' '), o.join(' '), v.join(' '),
      '', '', '', '', '', '', '', e[2], e[0] * D3[0] + e[1] * D3[1] + e[2] * D3[2], -hull - C8880].map((x) => typeof x === 'number' ? f(x) : x).join(',') + '\n');
  } catch (err) { send({ ev: 'S_err', err: String(err) }); }
}

function settings(p) {
  const r = { ev: 'settings' };
  try {
    const s = p.add(0x2598).readPointer();
    for (const g of ['0x141af5038', '0x141ac5e38', '0x1419b0138', '0x1419ae818', '0x1419aedf8', '0x141ac5e3c']) {
      try { const off = at(g).readU32(); r['set_' + g] = [off, s.add(off).readFloat()]; } catch (e) { r['set_' + g] = 'err'; }
    }
  } catch (e) { r.err = String(e); }
  for (const g of ['0x1427fb7c0', '0x1427fc880', '0x1427cc9e0', '0x1427e59d0', '0x1427f9a20', '0x1427ccf40', '0x1427fa510',
    '0x1427cd080', '0x1427fd1e0', '0x1427caa80', '0x1427cb8e0', '0x1427fb860', '0x1427c7680']) {
    try {
      const cv = at(g).readPointer();
      let name = '';
      for (const o of [0x8, 0x10, 0x18]) { try { const s = cv.add(o).readPointer().readCString(64); if (s && /^[a-z_0-9]+$/i.test(s)) { name = s; break; } } catch (e) { } }
      r['cv_' + g] = [name, cv.add(0x60).readFloat()];
    } catch (e) { r['cv_' + g] = 'err'; }
  }
  send(r);
}

function row(ev, p, extra) {
  const cols = [ev, Date.now(), G.add(0x10).readFloat(), G.add(0x30).readFloat(), PRED_A.readU8(), PRED_B.readU8()].concat(extra);
  out.write(cols.map((x) => typeof x === 'number' ? f(x) : x).join(',') + '\n');
  if (++nrows % 5000 === 0) { out.flush(); send({ rows: nrows }); }
}

Interceptor.attach(at('0x140a45380'), {
  onEnter(args) {
    this.p = args[0].add(8).readPointer();
    this.md = args[0].add(0x10).readPointer();
    this.a2 = args[1].toInt32() & 0xff;
    this.s0 = this.p.add(0x2b34).readS32();
    this.fr0 = this.p.add(0x2b7c).readFloat();
    if (this.a2 === 1) startRow(this.p, this.md);
    if (!sentSettings) { sentSettings = true; P = this.p; settings(this.p); setTimeout(() => settings(P), 5000); }
    P = this.p;
  },
  onLeave() {
    const p = this.p, md = this.md;
    row('T', p, [this.a2, this.s0, this.fr0, p.add(0x2b34).readS32(), p.add(0x2b7c).readFloat(), p.add(0x2b38).readS32(),
      p.add(0x2a70).readS32(), p.add(0x2234).readFloat(), p.add(0x2b60).readFloat(), p.add(0x2ba8).readFloat(),
      p.add(0x2bb4).readFloat(), p.add(0x2b80).readFloat(), md.add(0x120).readFloat(), md.add(0x24).readU32(), p.add(0xf0).readFloat()]);
  }
});
Interceptor.attach(at('0x140a54e80'), {
  onLeave() {
    if (P === null) return;
    row('P', P, ['', '', '', P.add(0x2b34).readS32(), P.add(0x2b7c).readFloat(), P.add(0x2b38).readS32(), P.add(0x2a70).readS32(),
      '', '', '', '', '', '', '', P.add(0xf0).readFloat()]);
  }
});
send({ ready: true, wall: Date.now() });
