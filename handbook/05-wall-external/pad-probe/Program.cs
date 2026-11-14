// Probe: why the standing pad apex (LS-24) is 841 u, not ~880 u. Same setup as hb-tables level_scale_harness Pads().
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using HSD.Game;
using HSD.R5Replay;

static class Program
{
    static int Main(string[] args)
    {
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
        {
            string n = new AssemblyName(e.Name).Name + ".dll";
            foreach (string d in new[] { @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed\UnityEngine", @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed" })
            { string p = Path.Combine(d, n); if (File.Exists(p)) return Assembly.LoadFrom(p); }
            return null;
        };
        Units.SetMode(UnitMode.ResearchU);
        string lname = args.Length > 0 ? args[0] : "Wraith S21"; bool sprint = args.Length > 1 && args[1] == "sprint"; foreach (var l0 in SkillLoadouts.All()) Console.Error.WriteLine("LOADOUT " + l0.name);
        var m = new PracticeMap();
        m.pads.Add(new Vec3d(0, 0, 0));
        var r = new TimeTrialRoute { name = "t", spawn = new Vec3d(-90000, 0, 0) };
        r.checkpoints.Add(new Checkpoint { name = "s", position = new Vec3d(-90000, 0, 0) });
        r.checkpoints.Add(new Checkpoint { name = "e", position = new Vec3d(-90000, 5000, 0) });
        m.routes.Add(r);
        SkillLoadout lo = SkillLoadouts.All().FirstOrDefault(l => l.name == lname) ?? SkillLoadouts.All().First();
        var s = new PracticeSession(m, new[] { MovementConfigs.Reference() }, new[] { lo });
        s.ResetToPose(new Vec3d(sprint ? -900 : 0, 0, 0), 0, "p");
        double prevVz = 0;
        for (int k = 0; k < 1200; k++)
        {
            var i = new SkillInput { yawDeg = 0, sprint = sprint }.WithKeys(SkillInput.Keys(sprint, false, false, false));
            s.Step(i);
            var mo = s.Body.motor;
            string ev = s.Body.lastEvents == null ? "" : string.Join(",", s.Body.lastEvents);
            if (mo.landed) ev += ",LAND";
            bool print = k < 6 || ev.Length > 0 || Math.Sign(mo.vel.z) != Math.Sign(prevVz) || k % 60 == 0;
            if (print) Console.WriteLine($"{k}\tt={k / 120.0:0.000}\tpos=({mo.pos.x:0.###},{mo.pos.y:0.###},{mo.pos.z:0.###})\tvel=({mo.vel.x:0.###},{mo.vel.y:0.###},{mo.vel.z:0.###})\tg={mo.grounded}\t{ev}");
            prevVz = mo.vel.z;
        }
        return 0;
    }
}
