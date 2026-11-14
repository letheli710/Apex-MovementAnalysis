using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using HSD.Game;
using HSD.R5Replay;

// hb-judge (2026-11-14): the answer key of the handbook rebuild test, from the Unity reference implementation.
// Game body MovementConfigs.Reference() (msc forced to 1), native camera (NativeCameraFeedback), u mode, 120 Hz commands, the
// HSD-Unity sources compiled read-only. Scenario definitions: ../PROBLEMS.md.   JudgeHarness <out_dir>
static class Program
{
    const double Dt = PracticeSession.CommandDt;           // 1/120 s
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    sealed class Sim
    {
        public PracticeSession s;
        public NativeCameraFeedback cam;
        public R5MotorV2 M => s.Body.motor;
        public StringBuilder csv = new StringBuilder("tick,t_s,pos_x_u,pos_z_u,speed_h_u_s,vel_z_u_s,state,events,cam_pitch_punch_deg,eye_height_u\n");
        public int tick;
        public bool slideStarted, slideEnded, landed, jumped;
        public bool camCols;

        public void Step(SkillInput i)
        {
            cam.commandNumberOverride = tick;              // the landing / jump kick random is drawn with the command number = tick
            s.Step(i);
            MotorFlags f = M.Flags;
            slideStarted = f.slideStarted; slideEnded = f.slideEnded; landed = f.landed; jumped = M.jumped;
            var ev = new List<string>();
            if (slideStarted) ev.Add("slide_start");
            if (slideEnded) ev.Add("slide_end");
            if (jumped) ev.Add("jump");
            if (landed) ev.Add("land");
            string state = !f.grounded ? "air" : f.sliding ? "slide" : i.duck ? "crouch" : "ground";
            double punch = cam.punchPitch.angle + cam.punch2Pitch.angle;
            NativeCameraFeedback.State c = cam.Current;
            csv.Append(string.Join(",", new[]
            {
                tick.ToString(Inv), (tick * Dt).ToString("0.######", Inv), M.pos.x.ToString("0.####", Inv), M.pos.z.ToString("0.####", Inv),
                M.vel.HorizontalLength.ToString("0.####", Inv), M.vel.z.ToString("0.####", Inv), state, string.Join(";", ev),
                punch.ToString("0.######", Inv), c.eye.ToString("0.####", Inv),
            })).Append('\n');
            tick++;
        }
    }

    static Sim NewSim(Func<PracticeMap, IMovementWorld> world, Vec3d start)
    {
        MovementConfig config = MovementConfigs.Reference();
        config.motor.moveScale = 1.0;                       // the problem: msc = 1
        var sim = new Sim();
        sim.s = new PracticeSession(null, new[] { config }, null, world);
        sim.cam = new NativeCameraFeedback(CameraFeedbackSettings.Default(), null);
        sim.cam.Attach(sim.s);
        sim.s.ResetToPose(start, 0, "rebuild-test");
        sim.cam.Reset();
        return sim;
    }

    static MovementWorld Flat(PracticeMap m) => new MovementWorld(0);

    /// <summary>A 20° ramp falling along +x from x = 0 (z = 0) to x = 20000, one static solid (no prop: no ground-entity seams).</summary>
    static MovementWorld Slope20(PracticeMap m)
    {
        var w = new MovementWorld(-20000);
        double t = Math.Tan(20 * Math.PI / 180), len = 20000;
        w.AddRamp(-200, -2000, len, 2000, -20000, -len * t, 200 * t, RampRise.MinusX);
        return w;
    }

    static SkillInput In(bool fwd, bool sprint, bool duck, bool jump = false)
        => new SkillInput { forward = fwd ? 1 : 0, side = 0, yawDeg = 0, sprint = sprint, duck = duck, jump = jump };

    /// <summary>S1 / S2 / S3 / S4 / S5. Ticks 0–239 W + sprint; from tick 240 duck held (W + sprint stay held).</summary>
    static string Slide(string id, Func<PracticeMap, IMovementWorld> world, Vec3d start)
    {
        Sim sim = NewSim(world, start);
        const int pressTick = 240;
        int endTick = -1, stopAt = int.MaxValue, secondPress = -1, phase = 0;
        bool duck = false;
        for (int guard = 0; guard < 120 * 30 && sim.tick < stopAt; guard++)
        {
            int k = sim.tick;
            bool jump = false;
            if (k < pressTick) duck = false;
            else if (id == "S2") duck = k < pressTick + 60;                   // released 0.5 s after the slide start
            else if (id == "S5" && phase >= 1)
            {
                // released on the command after the first slide end; pressed again on the first command whose pre speed >= 200
                if (phase == 1) { duck = false; phase = 2; }
                else if (phase == 2 && sim.M.vel.HorizontalLength >= 200) { duck = true; phase = 3; secondPress = k; }
            }
            else duck = true;
            if (id == "S3" && k == pressTick + 25) jump = true;                // 0.208 s after the press → tick 240 + 25
            sim.Step(In(true, true, duck, jump));
            if (sim.slideEnded && !sim.jumped && k >= pressTick)
            {
                if (id == "S5" && phase == 0) phase = 1;
                else if (id != "S5" || phase == 3) { endTick = k; stopAt = k + 1 + 120; }
            }
            if (id == "S4" && k >= pressTick + 480) break;                     // 20°: the slide does not end (v_eq ≈ 395); 4 s of crouch
        }
        File.WriteAllText(Path.Combine(outDir, id + ".csv"), sim.csv.ToString());
        return $"{id}: rows {sim.tick}, end tick {endTick}" + (secondPress >= 0 ? $", second press tick {secondPress}" : "");
    }

    /// <summary>L1: still from height h, no keys; L2: standing jump on tick 30. Record until 180 commands after the landing.</summary>
    static string Landing(string id, double h, bool jump)
    {
        Sim sim = NewSim(Flat, new Vec3d(0, 0, h));
        int stopAt = int.MaxValue, landTick = -1;
        double peak = 0; int peakTick = -1;
        for (int guard = 0; guard < 120 * 10 && sim.tick < stopAt; guard++)
        {
            int k = sim.tick;
            sim.Step(In(false, false, false, jump && k == 30));
            if (sim.landed && landTick < 0) { landTick = k; stopAt = k + 1 + 180; }
            double p = sim.cam.punchPitch.angle + sim.cam.punch2Pitch.angle;
            if (landTick >= 0 && Math.Abs(p) > Math.Abs(peak)) { peak = p; peakTick = k; }
        }
        File.WriteAllText(Path.Combine(outDir, id + ".csv"), sim.csv.ToString());
        return $"{id}: rows {sim.tick}, land tick {landTick}, punch peak after landing {peak:0.0000} deg at tick {peakTick}";
    }

    static string outDir;

    static void Main(string[] args)
    {
        outDir = args.Length > 0 ? args[0] : "out";
        Directory.CreateDirectory(outDir);
        var log = new List<string>
        {
            Slide("S1", Flat, Vec3d.Zero),
            Slide("S2", Flat, Vec3d.Zero),
            Slide("S3", Flat, Vec3d.Zero),
            Slide("S4", Slope20, new Vec3d(0, 0, 2)),
            Slide("S5", Flat, Vec3d.Zero),
        };
        foreach (int h in new[] { 50, 100, 200, 400 }) log.Add(Landing("L1_" + h, h, false));
        log.Add(Landing("L2", 0, true));
        foreach (string l in log) Console.WriteLine(l);
    }
}
