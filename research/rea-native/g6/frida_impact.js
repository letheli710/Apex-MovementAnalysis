// G-6 impact vertical boost probe (Frida, read-only: hooks only log, nothing is changed).
// Logs, around every grapple detach of the S21 client (r5apex_dx12.exe):
//   - the pull step 0x14066fb60: vz on entry and on return (the proximity branch adds grapple_impactVerticalBoost there),
//     its return value (1 = detach on this command) and the hook's parent handle (+0x148 of the 4th argument);
//   - the grapple update 0x140670ff0 on return (after GrappleAnimSelectSequence, which writes the velocity back);
//   - PlayerMove 0x140a54e80 on entry and on return for the next 24 calls after a detach: the velocity of the whole move
//     (prediction re-runs show as repeated calls; the time stamp separates them).
// Velocity = the movedata globals 0x1423736c4..cc (Ghidra addresses, image base 0x140000000).
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const BASE = mod.base;
const GH = ptr('0x140000000');
const at = (a) => BASE.add(ptr(a).sub(GH));
const t0 = Date.now();
const now = () => (Date.now() - t0) / 1000;
const VEL = at('0x1423736c4');
const v3 = () => [VEL.readFloat(), VEL.add(4).readFloat(), VEL.add(8).readFloat()];

let after = 0;       // PlayerMove calls still to log after a detach
let seq = 0;         // detach counter
Interceptor.attach(at('0x14066fb60'), {
  onEnter(args) {
    this.vin = v3();
    try { this.p148 = args[3].add(0x148).readU32() >>> 0; } catch (e) { this.p148 = -1; }
    try { this.pulling = args[0].add(0x49).readU8(); } catch (e) { this.pulling = -1; }
  },
  onLeave(ret) {
    if ((ret.toInt32() & 0xff) !== 0) {
      seq++;
      send({ ev: 'detach', seq: seq, t: now(), p148: '0x' + this.p148.toString(16), pulling: this.pulling, vin: this.vin, vout: v3() });
      after = 24;
    }
  }
});
Interceptor.attach(at('0x140670ff0'), {
  onLeave() { if (after === 24) send({ ev: 'update_ret', seq: seq, t: now(), v: v3() }); }
});
Interceptor.attach(at('0x140a54e80'), {
  onEnter() { this.vin = v3(); },
  onLeave() {
    if (after > 0) { send({ ev: 'move', seq: seq, n: 24 - after, t: now(), vin: this.vin, vout: v3() }); after--; }
  }
});
send({ ev: 'ready', base: BASE.toString() });
