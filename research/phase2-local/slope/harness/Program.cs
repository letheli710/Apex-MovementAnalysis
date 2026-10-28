using System;
using System.Collections.Generic;
using System.IO;
using HSD.R5Replay;

// R6 slope harness: FeelReplay.GameBody with the trial's slope lane (trial.json world.slope_segments) in the MovementWorld.
// FeelBatch's world has only a floor, one wall box and rails, so the ramps are built here with MovementWorld.AddRamp and the
// game body is stepped exactly as FeelReplay.Run does. Reads the HSD-Unity sources unchanged.
//   SlopeHarness <trials_root> <out_root> [--segments] [--pre-r6u] [--off U1,U2,U3,U4]   -> <out_root>/<trial_id>/reference.csv
// R6U: the lane is built tile by tile as in R5 (tools/slope_geo.py tiles(): 1023 u tiles, each its own prop, so every seam is a ground-entity
// change); --segments builds one solid per planar segment (the #67 world). --pre-r6u switches every R6U rule off (the #67 Reference body);
// --off switches single rules off (U1 slopeUphillKeepStep, U2 hullBottomRadius, U3 slideRebeginOnGroundChange, U4 slideSlopeAnyGrade).
static class Program
{
    const double Tile = 1023;

    static MovementWorld World(Trial trial, bool tiles)
    {
        var w = (Dictionary<string, object>)trial.manifest["world"];
        var world = new MovementWorld(MiniJson.GetNumber(w, "floor_z") ?? trial.initial.pos.z);
        foreach (object o in (List<object>)w["slope_segments"])
        {
            var s = (Dictionary<string, object>)o;
            double xa = (double)s["xa"], xb = (double)s["xb"], za = (double)s["za"], zb = (double)s["zb"];
            double y0 = (double)s["y0"], y1 = (double)s["y1"], rise = (double)s["rise_deg"];
            if (!tiles)
            {
                Add(world, xa, xb, za, zb, y0, y1, rise);
                continue;
            }
            // slope_geo.tiles(): tile starts along the surface by the segment's alignment, rows of tiles across Y
            double len = (double)s["len"], t = rise * Math.PI / 180;
            string align = (string)s["align"];
            int n = (int)Math.Ceiling(len / Tile - 1e-9), ny = Math.Max(1, (int)Math.Round((y1 - y0) / Tile));
            for (int i = 0; i < n; i++)
            {
                double s0 = align == "both" ? Math.Min(i * Tile, len - Tile) : align == "a" ? i * Tile : len - Tile - i * Tile;
                double x0 = xa + s0 * Math.Cos(t), x1 = xa + (s0 + Tile) * Math.Cos(t);
                double z0 = za + s0 * Math.Sin(t), z1 = za + (s0 + Tile) * Math.Sin(t);
                double yc = (y0 + y1) / 2;
                for (int j = 0; j < ny; j++)
                {
                    double yy = yc + (j - (ny - 1) / 2.0) * Tile;
                    Add(world, x0, x1, z0, z1, yy - Tile / 2, yy + Tile / 2, rise).prop = true;
                }
            }
        }
        return world;
    }

    static ConvexSolid Add(MovementWorld world, double xa, double xb, double za, double zb, double y0, double y1, double rise)
    {
        double bottom = Math.Min(za, zb) - 600;
        if (Math.Abs(rise) < 1e-9) return world.AddSolid(ConvexSolid.FromBox(new Box(new Vec3d(xa, y0, bottom), new Vec3d(xb, y1, za))));
        if (rise > 0) return world.AddRamp(xa, y0, xb, y1, bottom, za, zb, RampRise.PlusX);
        return world.AddRamp(xa, y0, xb, y1, bottom, zb, za, RampRise.MinusX);
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
        bool tiles = Array.IndexOf(args, "--segments") < 0, pre = Array.IndexOf(args, "--pre-r6u") >= 0;
        int io = Array.IndexOf(args, "--off");
        string off = io >= 0 && io + 1 < args.Length ? args[io + 1] : "";
        MovementConfig cfg = MovementConfigs.Reference();
        if (pre || off.Contains("U1")) cfg.motor.slopeUphillKeepStep = false;
        if (pre || off.Contains("U2")) cfg.motor.hullBottomRadius = 0;
        if (pre || off.Contains("U3")) cfg.motor.slideRebeginOnGroundChange = SlideRebegin.Off;
        if (pre || off.Contains("U4")) cfg.motor.slideSlopeAnyGrade = false;
        if (pre) cfg.motor.slideSlopeNeedsDuck = true;
        int n = 0, failed = 0;
        foreach (string dir in Directory.GetDirectories(args[0]))
        {
            if (!File.Exists(Path.Combine(dir, "trial.json"))) continue;
            try
            {
                Trial trial = TrialLoader.Load(dir);
                string od = Path.Combine(args[1], trial.trialId);
                Directory.CreateDirectory(od);
                SkillBody b = cfg.CreateBody(SkillLoadouts.PathfinderOctane(), World(trial, tiles));
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
