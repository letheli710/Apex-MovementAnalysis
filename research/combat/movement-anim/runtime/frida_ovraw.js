// Overlay-layer raw dump (Frida, read-only). Added mid-batch (from c1_rl_slide_2 on) to find the overlay layers' cycle / weight fields:
// one line per 0x14085c3e0 call on the view model: w = Date.now, then 0x1570..0x1760 of the view model as 124 floats (0x1694.. bytes and 0x1730.. shorts come out as garbage floats; read those from frames.csv).
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const DIR = 'OUT_DIR_HERE';
const out = new File(DIR + '/ovraw.csv', 'w');
let n = 0, last = 0;
Interceptor.attach(at('0x14085c3e0'), {
  onEnter(args) {
    const now = Date.now();
    if (now === last) return;
    last = now;
    const vm = args[0], a = [];
    for (let k = 0; k < 124; k++) { const x = vm.add(0x1570 + 4 * k).readFloat(); a.push(isFinite(x) && Math.abs(x) < 1e6 ? Math.round(x * 1e5) / 1e5 : ''); }
    out.write(now + ',' + a.join(',') + '\n');
    if (++n % 60 === 0) out.flush();
  }
});
send({ ready: 'ovraw' });
