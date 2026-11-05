// Gun probe (Frida, read-only: hooks only log and call read-only getters, nothing is changed). Addresses are Ghidra (base 0x140000000) of r5apex_dx12.exe.
// frames.csv, one line per first-person CalcView (0x1407f2bb0). Punch and spring as in RECOIL-VIEW, zoom and view model as in ADS-CURVES.
//   clip / stock = weapon +0x1590 / +0x1594, ws = weapon state +0x15a4, next = next ready time +0x1568, w = low 24 bits of the active weapon pointer.
//   vx vy vz = player +0x170, oz = origin z (vtable +0x40). vm* = view model origin in camera axes, then its angles, cycle +0xf4, sequence +0xe44.
// shots.csv, one line per kick (0x140711ce0). vars.jsonl: every weapon var (table at 0x146e8fe40, stride 0x40: name +0, type +0x18, id +0x1a, offset +0x1c; value at weapon +0x19d0 + offset), written when a weapon first shows and when DUMP_EVERY frames pass after it changes.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || isNaN(x)) ? '' : (Math.round(x * 10000) / 10000);
const DIR = 'OUT_DIR_HERE';
const frames = new File(DIR + '/frames.csv', 'w');
const shots = new File(DIR + '/shots.csv', 'w');
const vars = new File(DIR + '/vars.jsonl', 'w');
frames.write('t,ct,ft,zf,fov,fP,fY,fR,puP,puY,puR,s2P,s2Y,s2R,v2P,v2Y,hot,val,idx,clip,stock,ws,next,w,vx,vy,vz,oz,kP,dP,vmF,vmR,vmU,vmaP,vmaY,vmaR,cyc,seq\n');
shots.write('t,ct,w,val,idx,row,c0,c1,c2,c3,zf,hard,soft,s2P0,s2Y0,v2P0,v2Y0,s2P1,s2Y1,v2P1,v2Y1,s2R1,vx,vy,vz\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const kickVal = new NativeFunction(at('0x140712c80'), 'float', ['pointer']);
const heat = new NativeFunction(at('0x140713060'), 'float', ['pointer']);
const ENT = at('0x1424139b8'), SER = at('0x1424139c0'), GV = at('0x1419832d8').readPointer(), PAT = at('0x142819e70');
const TAB = at('0x146e8fe40');
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const fromHandle = (h) => {
  if (h === 0xffffffff) return null;
  const i = h & 0xffff;
  if (SER.add(i * 32).readU32() !== (h >>> 16)) return null;
  const w = ENT.add(i * 32).readPointer();
  return w.isNull() ? null : w;
};
const weaponOf = (p) => fromHandle(p.add(0x1930).readU32());
// the var table, once
const VT = [];
for (let i = 0; i < 1600; i++) {
  const e = TAB.add(i * 0x40);
  try {
    const np = e.readPointer();
    if (np.isNull()) continue;
    const n = np.readCString();
    if (!n || !/^[a-zA-Z_][\w]*$/.test(n)) continue;
    VT.push([n, e.add(0x18).readU8(), e.add(0x1a).readU16(), e.add(0x1c).readU16()]);
  } catch (e2) { }
}
const dump = (w, why) => {
  const o = {};
  const b = w.add(0x19d0);
  for (const [n, ty, id, off] of VT) {
    try {
      if (ty === 5) o[n] = f(b.add(off).readFloat());
      else if (ty === 4 || ty === 9 || ty === 10) o[n] = b.add(off).readS32();
      else if (ty === 1) o[n] = b.add(off).readU8();
      else if (ty === 8) o[n] = r3(b.add(off)).map(f);
      else if (ty === 6 || ty === 7) { const q = b.add(off).readPointer(); o[n] = q.isNull() ? '' : q.readCString(); }
    } catch (e) { }
  }
  vars.write(JSON.stringify({ t: (Date.now() - t0) / 1000, why, w: w.toString(), v: o }) + '\n');
  vars.flush();
};
let n = 0, fr = null, spr = [NaN, NaN], curW = null, sinceW = 0, vmr = [NaN, NaN, NaN, NaN, NaN, NaN, NaN, NaN];
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.ang = args[2]; this.fov = args[3]; fr = {}; },
  onLeave() {
    if (fr === null) return;
    const p = this.p, a = r3(this.ang), pu = fr.punch || [NaN, NaN, NaN];
    const s2 = r3(p.add(0x2448)), v2 = r3(p.add(0x2454)), vv = r3(p.add(0x170));
    let zf = zoomFrac(p), val = NaN, hot = NaN, idx = NaN, clip = NaN, stock = NaN, ws = NaN, nx = NaN, wid = 0;
    const w = weaponOf(p);
    if (w !== null) {
      val = kickVal(w); hot = heat(w); idx = w.add(0x1700).readS32(); clip = w.add(0x1590).readS32(); stock = w.add(0x1594).readS32();
      ws = w.add(0x15a4).readS32(); nx = w.add(0x1568).readFloat(); wid = w.toUInt32() & 0xffffff;
      const hd = p.add(0x1930).readU32();
      if (curW !== hd) { curW = hd; sinceW = 0; }
      if (++sinceW === 25) dump(w, 'new');
    }
    let oz = NaN;
    try { oz = new NativeFunction(p.readPointer().add(0x40).readPointer(), 'pointer', ['pointer'])(p).add(8).readFloat(); } catch (e) { }
    const row = [(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), GV.add(0x30).readFloat(), zf, this.fov.readFloat(), a[0], a[1], a[2], pu[0], pu[1], pu[2],
      s2[0], s2[1], s2[2], v2[0], v2[1], hot, val, idx, clip, stock, ws, nx, wid, vv[0], vv[1], vv[2], oz, spr[0], spr[1]].concat(vmr);
    frames.write(row.map(f).join(',') + '\n');
    fr = null;
    if (++n % 100 === 0) { frames.flush(); shots.flush(); }
  }
});
Interceptor.attach(at('0x140af1ed0'), { onEnter(args) { this.o = args[1]; }, onLeave() { if (fr !== null) fr.punch = r3(this.o); } });
Interceptor.attach(at('0x140712920'), {
  onEnter(args) { this.o = args[1]; },
  onLeave(ret) { if (ret.toInt32() & 1) { const o = this.o; spr = [o.readFloat(), o.add(12).readFloat()]; } else spr = [NaN, NaN]; }
});
Interceptor.attach(at('0x14085c3e0'), {
  onEnter(args) { this.vm = args[0]; this.m = args[2]; },
  onLeave() {
    const m = this.m, vm = this.vm;
    const fw = r3(m), rt = r3(m.add(12)), up = r3(m.add(24)), cp = r3(m.add(36)), ca = r3(m.add(48));
    const o = r3(vm.add(0x188)), an = r3(vm.add(0x194));
    const d = [o[0] - cp[0], o[1] - cp[1], o[2] - cp[2]];
    vmr = [dot(d, fw), dot(d, rt), dot(d, up), an[0] - ca[0], an[1] - ca[1], an[2] - ca[2], vm.add(0xf4).readFloat(), vm.add(0xe44).readS16()];
  }
});
Interceptor.attach(at('0x140711ce0'), {
  onEnter(args) {
    const w = args[0]; this.w = w;
    const h = w.add(0x1560).readU32(), own = fromHandle(h);
    if (own === null) { this.own = null; return; }
    this.own = new NativeFunction(own.readPointer().add(0x588).readPointer(), 'pointer', ['pointer'])(own);
    const p = this.own;
    if (p.isNull()) { this.own = null; return; }
    this.v0 = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat()];
    const val = kickVal(w), per = w.add(0x2190).readFloat(), pidx = w.add(0x2124).readS32(), idx = w.add(0x1700).readS32();
    let row = -1, c = [NaN, NaN, NaN, NaN];
    if (pidx >= 0) {
      const pat = PAT.add(pidx * 0x42c), cnt = pat.add(0x20).readS32();
      row = Math.min(per > 0 ? Math.floor(val / per) : idx, cnt - 1);
      const r = pat.add(row * 0x10 + 0x2c);
      c = [r.readFloat(), r.add(4).readFloat(), r.add(8).readFloat(), r.add(12).readFloat()];
    }
    this.line = [(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), w.toUInt32() & 0xffffff, val, idx, row].concat(c, [zoomFrac(p), w.add(0x2138).readFloat(), w.add(0x2134).readFloat()]);
  },
  onLeave() {
    if (this.own === null) return;
    const p = this.own, a = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat(), p.add(0x2450).readFloat()], vv = r3(p.add(0x170));
    shots.write(this.line.concat(this.v0, a, vv).map(f).join(',') + '\n');
  }
});
send({ ready: true, wall: Date.now(), vars: VT.length, sample: VT.slice(0, 4) });
