// hb-slam (practice A) harness, 2026-11-14. Runs the HSD game body (PracticeSession + SkillBody + R5MotorV2, Reference config) with the
// GroundSlamAbility switched on, on hand-built geometry, and prints the slam level-scale numbers. All [u], 120 Hz commands.
// Build: see slam.csproj. Run: dotnet <out>/slam.dll [all|check] [out.tsv]
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using HSD.Game;
using HSD.R5Replay;

static class Program
{
    static readonly List<string> rows = new List<string>();
    const double Dt = PracticeSession.CommandDt;
    const double H = 72;
    static double Hz(Vec3d v) => Math.Sqrt(v.x * v.x + v.y * v.y);
    static int fails;
    static void Check(bool ok, string what) { Console.WriteLine((ok ? "ok   " : "FAIL ") + what); if (!ok) fails++; }

    static int Main(string[] args)
    {
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
        {
            string n = new AssemblyName(e.Name).Name + ".dll";
            foreach (string d in new[] { @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed\UnityEngine", @"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Data\Managed" })
            { string p = Path.Combine(d, n); if (File.Exists(p)) return Assembly.LoadFrom(p); }
            return null;
        };
        string what = args.Length > 0 ? args[0] : "all";
        rows.Add("id\tcase\tslam\theight_u\tstart_vh_u_s\tland_vz_u_s\tland_vh_before_u_s\tland_vh_after_u_s\tfall_time_s\tfall_dist_u\tslide_time_s\tslide_dist_u\ttotal_dist_u\tnote");
        if (what == "all" || what == "drop") Drops();
        if (what == "all" || what == "jump") Jumps();
        if (what == "all" || what == "check") Checks();
        if (args.Length > 1) File.WriteAllLines(args[1], rows);
        Console.WriteLine(fails == 0 ? "ALL OK" : $"{fails} FAIL");
        return fails == 0 ? 0 : 1;
    }

    static PracticeSession Make(Action<PracticeMap> build, bool slam)
    {
        var m = new PracticeMap();
        build?.Invoke(m);
        var r = new TimeTrialRoute { name = "t", spawn = new Vec3d(-90000, 0, 0) };
        r.checkpoints.Add(new Checkpoint { name = "s", position = new Vec3d(-90000, 0, 0) });
        r.checkpoints.Add(new Checkpoint { name = "e", position = new Vec3d(-90000, 5000, 0) });
        m.routes.Add(r);
        SkillLoadout lo = SkillLoadouts.All().First(l => l.name == "Wraith S21");   // movement-neutral passive (as the level-scale table)
        var s = new PracticeSession(m, new[] { MovementConfigs.Reference() }, new[] { lo });
        if (slam) s.SetSlam(true);
        return s;
    }
    static void Block(PracticeMap m, double x0, double y0, double z0, double x1, double y1, double z1)
        => m.blocks.Add(new MapBlock(new Vec3d(x0, y0, z0), new Vec3d(x1, y1, z1), BlockKind.Ledge));
    static SkillInput In(bool w = false, bool jump = false, bool duck = false, bool sprint = false, double pitch = 0)
        => new SkillInput { yawDeg = 0, pitchDeg = pitch, jump = jump, duck = duck, sprint = sprint }.WithKeys(SkillInput.Keys(w, false, false, false));
    static List<string> Ev(PracticeSession s) => s.Body.lastEvents ?? new List<string>();

    sealed class Run
    {
        public bool slammed, refused; public string refusal = "";
        public double landVz = double.NaN, landBefore = double.NaN, landAfter = double.NaN, fallT, fallD, slideT, slideD, startVh, height;
        public string note = "";
    }

    /// <summary>From the slam press (or the drop) to the slide end: crouch held and W held after the press.</summary>
    static Run Follow(PracticeSession s, bool pressSlam, double pitch = 60)
    {
        var r = new Run();
        var mo = s.Body.motor;
        r.startVh = Hz(mo.vel); r.height = mo.pos.z - mo.floorZ;
        var slam = s.Ability<GroundSlamAbility>();
        Vec3d p0 = mo.pos; double vzPrev = mo.vel.z; bool landed = false; Vec3d pl = p0; double tl = 0;
        int k;
        for (k = 0; k < 2000; k++)
        {
            double vzStart = mo.vel.z, vhStart = Hz(mo.vel);
            s.Step(In(w: true, duck: pressSlam || landed, pitch: pitch));
            var ev = Ev(s);
            if (ev.Contains("SLAM_START")) r.slammed = true;
            var rf = ev.FirstOrDefault(e => e.StartsWith("SLAM_REFUSED_")); if (rf != null) { r.refused = true; r.refusal = rf.Substring(13); }
            if (!landed && mo.landed)
            {
                landed = true; r.landVz = -vzStart; r.landAfter = Hz(mo.vel);
                r.landBefore = slam != null && slam.landings > 0 ? slam.lastLandS : r.landAfter;
                if (ev.Contains("LAND_SLOW")) r.note += $"hard landing cut to {Hz(mo.vel):0.0}; ";
                pl = mo.pos; tl = (k + 1) * Dt; r.fallT = tl; r.fallD = pl.x - p0.x;
                if (!mo.sliding) { r.note += "no slide; "; break; }
                continue;
            }
            if (landed && !mo.sliding) { r.slideT = (k + 1) * Dt - tl; r.slideD = mo.pos.x - pl.x; break; }
            if (!landed) vzPrev = mo.vel.z;
        }
        return r;
    }

    static void Row(string id, string name, bool slam, Run r)
        => rows.Add(string.Join("\t", id, name, slam ? (r.slammed ? "yes" : "refused " + r.refusal) : "off", F(r.height), F(r.startVh), F(r.landVz), F(r.landBefore), F(r.landAfter), F(r.fallT, 3), F(r.fallD), F(r.slideT, 3), F(r.slideD), F(r.fallD + r.slideD), r.note.Trim()));
    static string F(double v, int d = 1) => double.IsNaN(v) ? "—" : v.ToString("F" + d, System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>The body in the air at height h above flat ground with horizontal speed vh, crouch pressed on the first command.</summary>
    static Run Hover(double h, double vh, bool slam)
    {
        var s = Make(null, slam);
        s.ResetToPose(new Vec3d(0, 0, 0), 0, "slam");
        s.Body.Reset(new Vec3d(0, 0, h), new Vec3d(vh, 0, 0), false);
        return Follow(s, true);
    }

    static void Drops()
    {
        foreach (double n in new[] { 1.0, 2, 4, 8 })
            foreach (double vh in new[] { 0.0, 299 })
            {
                double h = n * H;
                string tag = $"{n:0}H.{(vh == 0 ? "still" : "sprint")}";
                Row($"SL-drop.{tag}", $"{n:0} 个身高（{h:0} u）空中{(vh == 0 ? "静止" : "带冲刺速度 299")}按蹲 + 低头 60°", true, Hover(h, vh, true));
                Row($"SL-drop.{tag}.off", $"同上，开关关（普通落下、按住蹲落地续滑）", false, Hover(h, vh, false));
            }
    }

    // ------------------------------------------------------------------ from jump apexes

    /// <summary>Run up on a platform (top <paramref name="top"/>, edge at x = 0; flat ground beyond), take off at the edge with the given jump,
    /// press crouch + look down at the apex. top = 0: flat ground everywhere.</summary>
    static Run FromApex(string kind, double top, bool slam)
    {
        var s = Make(m => { if (top > 0) Block(m, -6000, -600, 0, 0, 600, top); }, slam);
        s.ResetToPose(new Vec3d(-3000, 0, top), 0, "apex");
        var mo = s.Body.motor;
        bool sprint = kind != "stand";
        if (kind != "stand") for (int k = 0; k < 400 && mo.pos.x < -400; k++) s.Step(In(w: true, sprint: true));
        if (kind == "slide")
        {
            while (mo.pos.x < -16 - 25 * 410 * Dt) s.Step(In(w: true, sprint: true));
            for (int k = 0; k < 25; k++) s.Step(In(w: true, sprint: true, duck: true));      // 0.208 s: the best slide jump (LS-06/07)
        }
        else if (kind == "sprint") while (mo.pos.x < -16) s.Step(In(w: true, sprint: true));
        else
        {
            s.ResetToPose(new Vec3d(top > 0 ? -20 : -3000, 0, top), 0, "apex");
            mo = s.Body.motor;
            for (int k = 0; k < 120; k++) s.Step(In());
        }
        s.Step(In(w: sprint, sprint: sprint, jump: true));
        // to the apex (first command whose post vz <= 0), W held
        for (int k = 0; k < 400 && mo.vel.z > 0; k++) s.Step(In(w: sprint, sprint: sprint));
        return Follow(s, true);
    }

    static void Jumps()
    {
        foreach (var (kind, cn) in new[] { ("stand", "原地跳"), ("sprint", "冲刺跳"), ("slide", "滑铲跳（0.208 s）") })
        {
            Row($"SL-apex.flat.{kind}", $"平地{cn}，最高点按蹲 + 低头 60°", true, FromApex(kind, 0, true));
            foreach (double n in kind == "stand" ? new[] { 1.0 } : new[] { 1.0, 2 })
            {
                if (kind == "stand") { Row($"SL-apex.{n:0}H.{kind}", $"{n:0} 个身高的台子上原地跳（落回台上，等于平地），最高点按蹲 + 低头 60°", true, FromApex(kind, n * H, true)); continue; }
                Row($"SL-apex.{n:0}H.{kind}", $"{n:0} 个身高的台子边上{cn}，最高点按蹲 + 低头 60°", true, FromApex(kind, n * H, true));
                Row($"SL-apex.{n:0}H.{kind}.off", $"同上，开关关（按住蹲落地续滑）", false, FromApex(kind, n * H, false));
            }
        }
    }

    // ------------------------------------------------------------------ quick rule checks (the EditMode tests are the real ones)

    static void Checks()
    {
        var r = Hover(72, 0, true);
        Check(r.slammed, "1 H still: slams");
        double v1 = Math.Sqrt(1200 * 1200 + 2 * 750 * 72);
        Check(Math.Abs(r.landAfter - (r.landBefore + 0.35 * r.landVz)) < 0.02, $"1 H still (W held: air accel adds {r.landBefore:0.0}): s' = s + 0.35 v ({r.landAfter:0.00} vs {r.landBefore + 0.35 * r.landVz:0.00}; continuous v {v1:0.0})");
        r = Hover(144, 299, true);
        Check(Math.Abs(r.landAfter - 520) < 1e-6, $"2 H sprint: 520 ({r.landAfter:0.000})");
        r = Hover(71, 0, true);
        Check(!r.slammed && r.refusal == "HEIGHT", "71 u: refused HEIGHT");
        var s = Make(null, true); s.ResetToPose(new Vec3d(0, 0, 0), 0, "p"); s.Body.Reset(new Vec3d(0, 0, 200), Vec3d.Zero, false);
        r = Follow(s, true, 20);
        Check(!r.slammed && r.refusal == "PITCH", "pitch 20: refused PITCH");
        r = FromApex("slide", 0, true);
        Check(!r.slammed && r.refusal == "HEIGHT", "flat slide jump apex: refused HEIGHT");
    }
}
