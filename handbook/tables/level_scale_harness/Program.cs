// hb-tables level-scale harness (2026-11-14). Runs the HSD game body (PracticeSession + SkillBody + R5MotorV2) on hand-built
// test geometry and prints the level-scale numbers. All in [u] (ResearchU mode). Output: TSV-ish lines "KEY\tvalue\tnote".
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using HSD.Game;
using HSD.R5Replay;

static class Program
{
    static readonly List<string> outLines = new List<string>();
    static void Out(string key, double v, string note = "") { string l = $"{key}\t{v:0.###}\t{note}"; outLines.Add(l); Console.WriteLine(l); }

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
        string what = args.Length > 0 ? args[0] : "all";
        if (what == "names") { foreach (var l in SkillLoadouts.All()) Console.WriteLine(l.name); return 0; }
        if (what == "all" || what == "jump") Jumps();
        if (what == "all" || what == "mantle") Mantles();
        if (what == "mtrace") { var (ok, ev) = TryMantle(double.Parse(args[1]), args[2], int.Parse(args[3]), true); Console.WriteLine(ok + " " + ev); return 0; }
        if (what == "all" || what == "step") Steps();
        if (what == "all" || what == "slope") Slopes();
        if (what == "all" || what == "slide") Slides();
        if (what == "all" || what == "wall") WallRuns();
        if (what == "all" || what == "djump") DoubleJumps();
        if (what == "all" || what == "pad") Pads();
        if (args.Length > 1) File.WriteAllLines(args[1], outLines);
        return 0;
    }

    // ------------------------------------------------------------------ setup

    public const string Loadout = "Wraith S21";   // movement-neutral passive; every loadout has the same motor values
    static PracticeSession Make(Action<PracticeMap> build, MovementConfig cfg = null)
    {
        var m = new PracticeMap();
        build?.Invoke(m);
        var r = new TimeTrialRoute { name = "t", spawn = new Vec3d(-90000, 0, 0) };
        r.checkpoints.Add(new Checkpoint { name = "s", position = new Vec3d(-90000, 0, 0) });
        r.checkpoints.Add(new Checkpoint { name = "e", position = new Vec3d(-90000, 5000, 0) });
        m.routes.Add(r);
        SkillLoadout lo = SkillLoadouts.All().FirstOrDefault(l => l.name == Loadout) ?? SkillLoadouts.All().First();
        return new PracticeSession(m, new[] { cfg ?? MovementConfigs.Reference() }, new[] { lo });
    }
    static void Block(PracticeMap m, double x0, double y0, double z0, double x1, double y1, double z1)
        => m.blocks.Add(new MapBlock(new Vec3d(x0, y0, z0), new Vec3d(x1, y1, z1), BlockKind.Wall));

    static SkillInput In(bool w = false, bool jump = false, bool duck = false, bool sprint = false, double yaw = 0)
        => new SkillInput { yawDeg = yaw, jump = jump, duck = duck, sprint = sprint }.WithKeys(SkillInput.Keys(w, false, false, false));

    sealed class Rec { public Vec3d pos, vel; public bool grounded, sliding; public List<string> ev; }
    static Rec Step(PracticeSession s, SkillInput i)
    {
        s.Step(i);
        var mo = s.Body.motor;
        var rr = new Rec { pos = mo.pos, vel = mo.vel, grounded = mo.grounded, sliding = mo.sliding, ev = s.Body.lastEvents == null ? new List<string>() : s.Body.lastEvents.ToList() };
        if (mo.slideStarted) rr.ev.Add("SLIDE_START"); if (mo.slideEnded) rr.ev.Add("SLIDE_END"); if (mo.jumped) rr.ev.Add("JUMP"); if (mo.landed) rr.ev.Add("LAND");
        return rr;
    }
    static bool Has(Rec r, string p) => r.ev.Any(e => e.StartsWith(p, StringComparison.Ordinal));
    const double Dt = PracticeSession.CommandDt;
    static double H(Vec3d v) => Math.Sqrt(v.x * v.x + v.y * v.y);

    // ------------------------------------------------------------------ jumps

    static void Jumps()
    {
        // standing jump
        {
            var s = Make(null); s.ResetToPose(new Vec3d(0, 0, 0), 0, "j");
            for (int k = 0; k < 120; k++) Step(s, In());
            double maxZ = 0, t0 = double.NaN, t1 = double.NaN; int k2 = 0;
            for (; k2 < 400; k2++)
            {
                var r = Step(s, In(jump: k2 == 0));
                if (k2 == 0) t0 = k2 * Dt;
                maxZ = Math.Max(maxZ, r.pos.z);
                if (k2 > 2 && r.grounded) { t1 = k2 * Dt; break; }
            }
            Out("jump.stand.height", maxZ, "standing jump apex, feet [u]");
            Out("jump.stand.airtime", t1 - t0, "takeoff to landing [s]");
        }
        // running jumps: walk (no sprint), sprint, crouch-walk; hold W in the air
        foreach (var (name, sprint, duck) in new[] { ("walk", false, false), ("sprint", true, false), ("crouchwalk", false, true) })
        {
            var s = Make(null); s.ResetToPose(new Vec3d(0, 0, 0), 0, "j");
            for (int k = 0; k < 360; k++) Step(s, In(w: true, sprint: sprint, duck: duck));
            double v0 = H(s.Body.motor.vel);
            Vec3d p0 = s.Body.motor.pos; double maxZ = 0; int land = -1; Vec3d p1 = p0;
            for (int k = 0; k < 600; k++)
            {
                var r = Step(s, In(w: true, sprint: sprint, duck: duck, jump: k == 0));
                maxZ = Math.Max(maxZ, r.pos.z);
                if (k > 2 && r.grounded) { land = k; p1 = r.pos; break; }
            }
            Out($"jump.{name}.speed", v0, "horizontal speed at takeoff [u/s]");
            Out($"jump.{name}.distance", p1.x - p0.x, "takeoff to landing on flat ground, W held [u]");
            Out($"jump.{name}.height", maxZ, "apex [u]");
            Out($"jump.{name}.airtime", land * Dt, "[s]");
        }
        // slide jump: sprint, press crouch (slide), jump after k commands; sweep k
        {
            double best = 0; int bestK = -1; double bestV = 0, bestH = 0, bestT = 0;
            var rows = new List<string>();
            for (int kj = 1; kj <= 150; kj++)
            {
                var s = Make(null); s.ResetToPose(new Vec3d(0, 0, 0), 0, "j");
                for (int k = 0; k < 360; k++) Step(s, In(w: true, sprint: true));
                for (int k = 0; k < kj; k++) Step(s, In(w: true, sprint: true, duck: true));
                if (!s.Body.motor.sliding) continue;
                Vec3d p0 = s.Body.motor.pos; double maxZ = 0; Vec3d p1 = p0; int land = -1; double vt = 0;
                for (int k = 0; k < 600; k++)
                {
                    var r = Step(s, In(w: true, sprint: true, jump: k == 0));
                    if (k == 0) vt = H(r.vel);
                    maxZ = Math.Max(maxZ, r.pos.z);
                    if (k > 2 && r.grounded) { land = k; p1 = r.pos; break; }
                }
                double d = p1.x - p0.x;
                rows.Add($"{kj}\t{kj * Dt:0.000}\t{vt:0.0}\t{d:0.0}");
                if (d > best) { best = d; bestK = kj; bestV = vt; bestH = maxZ; bestT = land * Dt; }
            }
            File.WriteAllLines(Path.Combine(AppContext.BaseDirectory, "slidejump_sweep.tsv"), rows);
            Out("jump.slide.best.delay", bestK * Dt, "crouch press -> jump press delay giving the longest slide jump [s]");
            Out("jump.slide.best.speed", bestV, "horizontal speed after the jump command [u/s]");
            Out("jump.slide.best.distance", best, "[u]");
            Out("jump.slide.best.height", bestH, "[u]");
            Out("jump.slide.best.airtime", bestT, "[s]");
            // early (refund) and late
            foreach (string row in rows.Where(r => r.StartsWith("6\t") || r.StartsWith("30\t") || r.StartsWith("60\t") || r.StartsWith("120\t")))
                Console.WriteLine("  slidejump " + row);
        }
    }

    // ------------------------------------------------------------------ mantle

    // wall face at x = 100 (block 100..400), height h; variants
    static (bool ok, string ev) TryMantle(double h, string variant, int jumpCmd, bool trace = false)
    {
        var s = Make(m => Block(m, 100, -500, 0, 30000, 500, h));
        bool sprint = variant.Contains("sprint"), duckAll = variant.Contains("duckall"), duckAir = variant.Contains("duckair");
        double x0 = sprint ? 100 - 16 - 700 : 100 - 16 - 0.5;
        s.ResetToPose(new Vec3d(x0, 0, 0), 0, "m");
        for (int k = 0; k < 60; k++) Step(s, In(duck: duckAll));
        var evs = new HashSet<string>();
        for (int k = 0; k < 900; k++)
        {
            bool air = k > jumpCmd;
            var r = Step(s, In(w: true, sprint: sprint, jump: k == jumpCmd, duck: duckAll || (duckAir && air)));
            if (trace && (k % 12 == 0 || r.ev.Count > 0)) Console.WriteLine($"{k} {r.pos} g{r.grounded} {string.Join(",", r.ev)}");
            foreach (var e in r.ev) { string t = e.Split(' ')[0]; if (t.StartsWith("MANTLE") || t.StartsWith("CLIMB") || t.StartsWith("WALL")) evs.Add(t); }
        }
        var p = s.Body.motor.pos;
        bool ok = p.x > 100 + 1 && Math.Abs(p.z - h) < 1.0 && s.Body.motor.grounded;
        return (ok, string.Join(",", evs.OrderBy(x => x)));
    }

    static void Mantles()
    {
        foreach (string variant in new[] { "stand", "stand_duckair", "stand_duckall", "sprint", "sprint_duckair" })
        {
            double maxOk = 0; string evAt = "";
            int[] jumpCmds = variant.StartsWith("sprint") ? Enumerable.Range(0, 30).Select(i => 200 + i * 4).ToArray() : new[] { 1 };
            for (double h = 10; h <= 400; h += 1)
            {
                bool any = false; string ev = "";
                foreach (int jc in jumpCmds) { var (ok, e) = TryMantle(h, variant, jc); if (ok) { any = true; ev = e; break; } }
                if (any) { maxOk = h; evAt = ev; }
            }
            Out($"mantle.{variant}.maxHeight", maxOk, "highest wall top (1 u grid) the body ends standing on; events at that height: " + evAt);
        }
        // the highest wall reached WITHOUT the wall climb (pure jump + mantle): climb events absent
        foreach (string variant in new[] { "stand", "stand_duckair" })
        {
            double maxNoClimb = 0;
            for (double h = 10; h <= 400; h += 1) { var (ok, e) = TryMantle(h, variant, 1); if (ok && !e.Contains("CLIMB")) maxNoClimb = h; }
            Out($"mantle.{variant}.maxHeightNoClimbEvent", maxNoClimb, "same, only runs without a CLIMB_* event");
        }
    }

    // ------------------------------------------------------------------ step

    static void Steps()
    {
        double maxOk = 0;
        for (double h = 0.5; h <= 40; h += 0.25)
        {
            var s = Make(m => Block(m, 100, -500, 0, 3000, 500, h));
            s.ResetToPose(new Vec3d(0, 0, 0), 0, "s");
            bool jumped = false;
            for (int k = 0; k < 240; k++) { var r = Step(s, In(w: true)); if (Has(r, "JUMP") || Has(r, "MANTLE")) jumped = true; }
            var p = s.Body.motor.pos;
            if (!jumped && p.x > 150 && Math.Abs(p.z - h) < 0.01) maxOk = h;
        }
        Out("step.walk.maxHeight", maxOk, "highest step walked up without jump / mantle (0.25 u grid) [u]");
    }

    // ------------------------------------------------------------------ slopes

    static void Slopes()
    {
        double maxWalk = 0;
        for (double a = 30; a <= 60; a += 0.25)
        {
            double run = 400, top = run * Math.Tan(a * Math.PI / 180);
            var s = Make(m => m.ramps.Add(new MapRamp(100, -500, 100 + run, 500, 0, top, RampRise.PlusX)));
            s.ResetToPose(new Vec3d(0, 0, 0), 0, "sl");
            double maxX = 0;
            for (int k = 0; k < 600; k++) { var r = Step(s, In(w: true, sprint: true)); maxX = Math.Max(maxX, r.pos.x); }
            if (maxX > 100 + run - 40) maxWalk = a;
        }
        Out("slope.sprint.maxAngle", maxWalk, "steepest ramp sprinted up to its top (0.25 deg grid) [deg]");
    }

    // ------------------------------------------------------------------ slides

    static (double dist, double time, double endSpeed, bool stopped, double peak) SlideRun(double angleDeg, bool downhill, double L = 6000)
    {
        double tan = Math.Tan(Math.Abs(angleDeg) * Math.PI / 180), hgt = L * tan;
        PracticeSession s;
        Vec3d start;
        if (angleDeg == 0) { s = Make(null); start = new Vec3d(0, 0, 0); }
        else if (downhill)
        {
            // platform at the top (x < 0, z = hgt), ramp from x = 0 (z = hgt) down to x = L (z = 0)
            s = Make(m => { Block(m, -2000, -500, 0, 0, 500, hgt); m.ramps.Add(new MapRamp(0, -500, L, 500, 0, hgt, RampRise.MinusX)); });
            start = new Vec3d(-1200, 0, hgt);
        }
        else
        {
            s = Make(m => m.ramps.Add(new MapRamp(0, -500, L, 500, 0, hgt, RampRise.PlusX)));
            start = new Vec3d(-1200, 0, 0);
        }
        s.ResetToPose(start, 0, "sd");
        // sprint up to the slide point (x = -2 for slopes, after 3 s on flat)
        int k = 0;
        for (; k < 2000; k++) { var r = Step(s, In(w: true, sprint: true)); if (angleDeg == 0 ? k >= 360 : r.pos.x >= -2) break; }
        Vec3d p0 = s.Body.motor.pos; double t = 0, peak = 0; bool started = false, stopped = false; Vec3d p1 = p0;
        for (int j = 0; j < 12000; j++)
        {
            var r = Step(s, In(w: true, sprint: true, duck: true));
            if (Has(r, "SLIDE_START") && !started) { started = true; p0 = r.pos; t = 0; }
            if (started) { t += Dt; peak = Math.Max(peak, r.vel.Length); p1 = r.pos; }
            if (started && (Has(r, "SLIDE_END") || (!r.sliding && r.grounded))) { stopped = true; break; }
            if (downhill && r.pos.x > L - 50) break;
            if (!downhill && angleDeg != 0 && r.pos.x > L - 50) break;
        }
        var d = p1 - p0;
        return (d.Length, t, s.Body.motor.vel.Length, stopped, peak);
    }

    static void Slides()
    {
        var f = SlideRun(0, false);
        Out("slide.flat.distance", f.dist, "SLIDE_START -> SLIDE_END from 299 u/s sprint, crouch held, W held [u]");
        Out("slide.flat.time", f.time, "[s]");
        Out("slide.flat.peak", f.peak, "peak speed (after the boost) [u/s]");
        foreach (double a in new[] { 5.0, 10, 15, 20, 30, 40 })
            foreach (bool down in new[] { true, false })
            {
                var r = SlideRun(a, down);
                string tag = down ? "down" : "up";
                Out($"slide.{tag}{a}.distance", r.dist, r.stopped ? "stopped (3D path length) [u]" : $"NOT stopped within the 6000 u ramp; speed {r.endSpeed:0} u/s, peak {r.peak:0}");
                Out($"slide.{tag}{a}.time", r.time, "[s]");
            }
    }

    // ------------------------------------------------------------------ wall run (HSD / TF2 rules)

    static MovementConfig FunWith(Action<MovementConfig> edit) { var c = MovementConfigs.Fun(); edit(c); return c; }

    static void WallRuns()
    {
        var sets = new (string name, Func<WallRunParams> p)[] { ("m7design", () => WallRunParams.Fun()), ("tf2B_r5values", () => WallRunParams.Tf2B()), ("tf2A_tf2values", () => WallRunParams.Tf2A()) };
        foreach (var (name, mk) in sets)
        {
            double bestD = 0, bestT = 0, bestDz = 0, bestYaw = 0;
            foreach (double yaw in new[] { 10.0, 15, 20, 25, 30, 40 })
                foreach (double gap in new[] { 20.0, 40, 60, 80 })
                {
                    var cfg = FunWith(c => { c.hsd.wallRun = mk(); });
                    // wall face at y = 50 (block 50..100) along x; run at yaw toward it, jump when the hull is gap u from the face
                    var s = Make(m => Block(m, -2000, 50, 0, 8000, 100, 3000), cfg);
                    s.ResetToPose(new Vec3d(-1500, -400, 0), yaw, "w");
                    for (int k = 0; k < 2000; k++) { var r0 = Step(s, In(w: true, sprint: true, yaw: yaw)); if (r0.pos.y + 16 >= 50 - gap) break; }
                    Vec3d p0 = default; double t = 0; bool on = false; double z0 = 0, zmax = 0; Vec3d p1 = default;
                    for (int k = 0; k < 1200; k++)
                    {
                        var r = Step(s, In(w: true, sprint: true, jump: k == 0, yaw: yaw));
                        if (!on && Has(r, "WALLRUN_START")) { on = true; p0 = r.pos; z0 = r.pos.z; zmax = z0; }
                        if (on) { t += Dt; p1 = r.pos; zmax = Math.Max(zmax, r.pos.z); if (Has(r, "WALLRUN_END") || r.grounded) break; }
                    }
                    double d = on ? H(p1 - p0) : 0;
                    if (d > bestD) { bestD = d; bestT = t; bestDz = zmax - z0; bestYaw = yaw; }
                }
            Out($"wallrun.{name}.distance", bestD, $"WALLRUN_START -> end, sprint-jump into the wall, W held, best of 24 approaches (yaw {bestYaw} deg) [u]");
            Out($"wallrun.{name}.time", bestT, "[s]");
            Out($"wallrun.{name}.rise", bestDz, "highest point above the start of the run [u]");
        }
    }

    // ------------------------------------------------------------------ double jump

    static void DoubleJumps()
    {
        foreach (var (name, mk) in new (string, Func<DoubleJumpParams>)[] { ("hsd", () => DoubleJumpParams.Fun()), ("tf2", () => DoubleJumpParams.Tf2()) })
        {
            double best = 0, bestT = 0;
            for (int k2 = 6; k2 <= 90; k2 += 2)
            {
                var cfg = FunWith(c => { c.hsd.doubleJump = mk(); c.hsd.wallRun.enabled = false; });
                var s = Make(null, cfg); s.ResetToPose(new Vec3d(0, 0, 0), 0, "d");
                for (int k = 0; k < 120; k++) Step(s, In());
                double maxZ = 0;
                for (int k = 0; k < 600; k++) { var r = Step(s, In(jump: k == 0 || k == k2)); maxZ = Math.Max(maxZ, r.pos.z); if (k > k2 + 2 && r.grounded) break; }
                if (maxZ > best) { best = maxZ; bestT = k2 * Dt; }
            }
            Out($"djump.{name}.standHeight", best, $"standing jump + air jump, best second press at {bestT:0.000} s [u]");
        }
    }

    // ------------------------------------------------------------------ jump pad (map pad fixture)

    static void Pads()
    {
        foreach (var (name, sprint) in new[] { ("still", false), ("sprint", true) })
        {
            var s = Make(m => m.pads.Add(new Vec3d(0, 0, 0)));
            s.ResetToPose(new Vec3d(sprint ? -900 : 0, 0, 0), 0, "p");
            Vec3d p0 = default; bool on = false; double maxZ = 0; Vec3d p1 = default; double t = 0;
            for (int k = 0; k < 2400; k++)
            {
                var r = Step(s, In(w: sprint, sprint: sprint));
                if (!on && !r.grounded && r.vel.z > 500) { on = true; p0 = r.pos; }
                if (on) { t += Dt; maxZ = Math.Max(maxZ, r.pos.z); p1 = r.pos; if (r.grounded) break; }
            }
            Out($"pad.{name}.height", maxZ, "apex above the pad [u]");
            Out($"pad.{name}.distance", on ? H(p1 - p0) : double.NaN, "launch to landing, horizontal [u]");
            Out($"pad.{name}.airtime", t, "[s]");
        }
    }
}
