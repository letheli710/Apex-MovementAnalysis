// Probe: Octane sprint pad -> landing -> 3 ground cmds -> jump -> hop landing. Does Unity end the slowdown on the soft hop landing (PAD-REJUMP §2)?
using System; using System.IO; using System.Linq; using System.Reflection; using HSD.Game; using HSD.R5Replay;
static class Program {
  static int Main(string[] args) {
    AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string n = new AssemblyName(e.Name).Name + ".dll";
      foreach (string d in new[] { @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed\UnityEngine", @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed" })
      { string p = Path.Combine(d, n); if (File.Exists(p)) return Assembly.LoadFrom(p); } return null; };
    Units.SetMode(UnitMode.ResearchU);
    var m = new PracticeMap(); m.pads.Add(new Vec3d(0, 0, 0));
    var r = new TimeTrialRoute { name = "t", spawn = new Vec3d(-90000, 0, 0) };
    r.checkpoints.Add(new Checkpoint { name = "s", position = new Vec3d(-90000, 0, 0) }); r.checkpoints.Add(new Checkpoint { name = "e", position = new Vec3d(-90000, 5000, 0) }); m.routes.Add(r);
    SkillLoadout lo = SkillLoadouts.All().First(l => l.name == "Octane S21");
    var s = new PracticeSession(m, new[] { MovementConfigs.Reference() }, new[] { lo });
    s.ResetToPose(new Vec3d(-900, 0, 0), 0, "p");
    bool launched = false; int landK = -1, hopLandK = -1; bool hopped = false;
    for (int k = 0; k < 1400; k++) {
      bool keys = !launched;
      bool jump = landK >= 0 && k == landK + 4;
      var i = new SkillInput { yawDeg = 0, sprint = keys, jump = jump }.WithKeys(SkillInput.Keys(keys, false, false, false));
      double preVz = s.Body.motor.vel.z; double preVh = Math.Sqrt(s.Body.motor.vel.x * s.Body.motor.vel.x + s.Body.motor.vel.y * s.Body.motor.vel.y);
      s.Step(i); var mo = s.Body.motor;
      string ev = s.Body.lastEvents == null ? "" : string.Join(",", s.Body.lastEvents); if (mo.landed) ev += ",LAND"; if (mo.jumped) ev += ",JUMP";
      if (ev.Contains("PAD_LAUNCH")) launched = true;
      if (launched && landK < 0 && mo.landed) landK = k;
      if (jump) hopped = true;
      if (hopped && hopLandK < 0 && mo.landed && k > landK + 5) hopLandK = k;
      double vh = Math.Sqrt(mo.vel.x * mo.vel.x + mo.vel.y * mo.vel.y);
      bool print = ev.Length > 0 || (landK >= 0 && k <= landK + 6) || (hopLandK >= 0 && k <= hopLandK + 3);
      if (print) Console.WriteLine($"{k}\tt={k/120.0:0.000}\tvh {preVh:0.###} -> {vh:0.###}\tpreVz={preVz:0.###} vz={mo.vel.z:0.###} f0={s.Body.set.Get<LandingSlowdown>().f0:0.####} tLand={s.Body.set.Get<LandingSlowdown>().tLand:0.###}\tg={mo.grounded}\t{ev}");
      if (hopLandK >= 0 && k > hopLandK + 3) break;
    }
    return 0; } }
