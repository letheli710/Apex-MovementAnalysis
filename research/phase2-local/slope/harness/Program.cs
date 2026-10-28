using System;
using System.Collections.Generic;
using System.IO;
using HSD.R5Replay;

// R6 slope harness: FeelReplay.GameBody with the trial's slope lane (trial.json world.slope_segments) in the MovementWorld.
// FeelBatch's world has only a floor, one wall box and rails, so the ramps are built here with MovementWorld.AddRamp and the
// game body is stepped exactly as FeelReplay.Run does. Reads the HSD-Unity sources unchanged.
//   SlopeHarness <trials_root> <out_root>   -> <out_root>/<trial_id>/reference.csv
static class Program
{
    static MovementWorld World(Trial trial)
    {
        var w = (Dictionary<string, object>)trial.manifest["world"];
        var world = new MovementWorld(MiniJson.GetNumber(w, "floor_z") ?? trial.initial.pos.z);
        foreach (object o in (List<object>)w["slope_segments"])
        {
            var s = (Dictionary<string, object>)o;
            double xa = (double)s["xa"], xb = (double)s["xb"], za = (double)s["za"], zb = (double)s["zb"];
            double y0 = (double)s["y0"], y1 = (double)s["y1"], rise = (double)s["rise_deg"];
            double bottom = Math.Min(za, zb) - 600;
            if (Math.Abs(rise) < 1e-9) world.Add(new Vec3d(xa, y0, bottom), new Vec3d(xb, y1, za));
            else if (rise > 0) world.AddRamp(xa, y0, xb, y1, bottom, za, zb, RampRise.PlusX);
            else world.AddRamp(xa, y0, xb, y1, bottom, zb, za, RampRise.MinusX);
        }
        return world;
    }

    static List<SimStep> Run(Trial trial, SkillBody b)
    {
        var steps = new List<SimStep>(trial.samples.Count);
        foreach (TrialSample s in trial.samples)
        {
            SkillInput i = FeelReplay.Input(s);
            int n = Math.Max(1, s.nCmds);
            var st = new SimStep { step = s.step, cmd = s.cmd, nCmds = s.nCmds, t = s.t, dt = s.dt };
            for (int k = 0; k < n; k++)
            {
                b.Step(i, s.dt / n);
                MotorFlags f = b.motor.Flags;
                st.tookOff |= f.tookOff; st.landed |= f.landed; st.slideStarted |= f.slideStarted; st.slideEnded |= f.slideEnded;
            }
            MotorFlags fl = b.motor.Flags;
            st.pos = b.motor.Position; st.vel = b.motor.Velocity;
            st.grounded = fl.grounded; st.sliding = fl.sliding; st.ducked = fl.ducked; st.sprinting = fl.sprinting; st.maxSpeed = fl.maxSpeed;
            st.state = "none";
            steps.Add(st);
        }
        return steps;
    }

    static int Main(string[] args)
    {
        int n = 0, failed = 0;
        foreach (string dir in Directory.GetDirectories(args[0]))
        {
            if (!File.Exists(Path.Combine(dir, "trial.json"))) continue;
            try
            {
                Trial trial = TrialLoader.Load(dir);
                string od = Path.Combine(args[1], trial.trialId);
                Directory.CreateDirectory(od);
                SkillBody b = MovementConfigs.Reference().CreateBody(SkillLoadouts.PathfinderOctane(), World(trial));
                b.Reset(trial.initial.pos, trial.initial.vel, trial.initial.grounded);
                FeelReplay.WriteCsv(Run(trial, b), Path.Combine(od, "reference.csv"));
                n++;
            }
            catch (Exception e)
            {
                failed++;
                Console.WriteLine($"{Path.GetFileName(dir)}: {e.GetType().Name}: {e.Message}");
            }
        }
        Console.WriteLine($"[slope] {n} trials, {failed} failed");
        return failed == 0 ? 0 : 1;
    }
}
