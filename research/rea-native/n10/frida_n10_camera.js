// N10 camera probe (Frida, read-only: hooks only log, nothing is changed).
// Per rendered frame of the view setup (0x140838830): the camera angles out of CalcView (0x1407ee480), the angle change made by
// the cockpit spring (0x1407ef190, CAM-19) and by the screen shake (0x1407ee050), the angle change sway (0x1405fc020, CAM-18)
// makes on the view-model angles, the spring's own angle state (player +0x34fc..+0x3504), the zipline roll output
// (0x1407fb580, CAM-13) with the branch it took (instruction hooks: 0x1407fb8b1 only in branch B, 0x1407fbf80 only in branch A),
// and counts of footstep jolts (0x1407f0330) and landing / script jolts (0x1407f1350).
// Rows go to OUT_PATH (set when the script is loaded; one CSV line per frame): [t, calcP, calcY, calcR, springDP, springDY, springDR, shakeDP, shakeDR, swayDP, swayDR,
//   sprP, sprY, sprR, zipRoll, zipBranch, steps, jolts]. Addresses are Ghidra (image base 0x140000000) of r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => Math.round(x * 10000) / 10000;
const OUT_PATH = 'OUT_PATH_HERE';
const out = new File(OUT_PATH, 'w');
out.write('t,calcP,calcY,calcR,springDP,springDY,springDR,shakeDP,shakeDR,swayDP,swayDR,sprP,sprY,sprR,zipRoll,zipBranch,steps,jolts\n');
let nrows = 0;
let fr = null, steps = 0, jolts = 0, zipRoll = NaN, zipBranch = '', branchNow = '';

function frame() {
  return { calc: [NaN, NaN, NaN], spring: [0, 0, 0], shake: [0, 0, 0], sway: [0, 0, 0], spr: [NaN, NaN, NaN] };
}

Interceptor.attach(at('0x140838830'), {
  onEnter() { fr = frame(); },
  onLeave() {
    if (fr === null) return;
    out.write([((Date.now() - t0) / 1000).toFixed(4), f(fr.calc[0]), f(fr.calc[1]), f(fr.calc[2]),
               f(fr.spring[0]), f(fr.spring[1]), f(fr.spring[2]), f(fr.shake[0]), f(fr.shake[2]), f(fr.sway[0]), f(fr.sway[2]),
               f(fr.spr[0]), f(fr.spr[1]), f(fr.spr[2]), f(zipRoll), zipBranch, steps, jolts].join(',') + '\n');
    fr = null; zipRoll = NaN; zipBranch = '';
    if (++nrows % 1200 === 0) { out.flush(); send({ rows: nrows }); }
  }
});
Interceptor.attach(at('0x1407ee480'), {
  onEnter(args) { this.ang = args[2]; },
  onLeave() { if (fr !== null) fr.calc = r3(this.ang); }
});
function deltaHook(addr, key, angArg, player) {
  Interceptor.attach(at(addr), {
    onEnter(args) { this.ang = args[angArg]; this.a0 = r3(this.ang); this.p = args[0]; },
    onLeave() {
      if (fr === null) return;
      const a1 = r3(this.ang);
      fr[key] = [a1[0] - this.a0[0], a1[1] - this.a0[1], a1[2] - this.a0[2]];
      if (player) fr.spr = r3(this.p.add(0x34fc));
    }
  });
}
deltaHook('0x1407ef190', 'spring', 2, true);
deltaHook('0x1407ee050', 'shake', 2, false);
deltaHook('0x1405fc020', 'sway', 2, false);
Interceptor.attach(at('0x1407fb580'), {
  onEnter(args) { this.out = args[3]; branchNow = ''; },
  onLeave() { zipRoll = this.out.readFloat(); zipBranch = branchNow; }
});
Interceptor.attach(at('0x1407fb8b1'), { onEnter() { branchNow = 'B'; } });
Interceptor.attach(at('0x1407fbf80'), { onEnter() { branchNow = 'A'; } });
Interceptor.attach(at('0x1407f0330'), { onEnter() { steps++; } });
Interceptor.attach(at('0x1407f1350'), { onEnter() { jolts++; } });
send({ ready: true, wall: Date.now() });
