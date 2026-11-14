// hb-slam dash harness (practice A2), 2026-11-14. Runs the HSD game body (PracticeSession + SkillBody + R5MotorV2, Reference config) with the
// DashAbility switched on (design values; the cooldown does not matter: one dash per run), on hand-built geometry. All [u], 120 Hz commands.
// Build: see dash.csproj. Run: dotnet <out>/dash.dll [all|check] [out.tsv]
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
    static double Hz(Vec3d v) => Math.Sqrt(v.x * v.x + v.y * v.y);
    static int fails;
    static void Check(bool ok, string what) { Console.WriteLine((ok ? "ok   " : "FAIL ") + what); if (!ok) fails++; }
    static void Row(string id, string what, string cond, string dim, double u, string note = "")
        => rows.Add(string.Join("\t", id, what, cond, dim, double.IsNaN(u) ? "—" : u.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture), note));

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
        rows.Add("id\t项\t条件\t量纲\t[u]\t备注");
        if (what == "all" || what == "basic") Basic();
        if (what == "all" || what == "gap") Gaps();
        if (what == "all" || what == "ledge") Ledges();
        if (args.Length > 1) File.WriteAllLines(args[1], rows);
        Console.WriteLine(fails == 0 ? "ALL OK" : $"{fails} FAIL");
        return fails == 0 ? 0 : 1;
    }

    static PracticeSession Make(Action<PracticeMap> build)
    {
        var m = new PracticeMap();
        build?.Invoke(m);
        var r = new TimeTrialRoute { name = "t", spawn = new Vec3d(-90000, 0, 0) };
        r.checkpoints.Add(new Checkpoint { name = "s", position = new Vec3d(-90000, 0, 0) });
        r.checkpoints.Add(new Checkpoint { name = "e", position = new Vec3d(-90000, 5000, 0) });
        m.routes.Add(r);
        var s = new PracticeSession(m, new[] { MovementConfigs.Reference() }, new[] { SkillLoadouts.All().First(l => l.name == "Wraith S21") });
        s.SetDash(true);
        return s;
    }
    static void Block(PracticeMap m, double x0, double y0, double z0, double x1, double y1, double z1)
        => m.blocks.Add(new MapBlock(new Vec3d(x0, y0, z0), new Vec3d(x1, y1, z1), BlockKind.Ledge));
    static SkillInput In(bool w = false, bool jump = false, bool duck = false, bool sprint = false, bool dash = false)
        => new SkillInput { yawDeg = 0, jump = jump, duck = duck, sprint = sprint, dash = dash }.WithKeys(SkillInput.Keys(w, false, false, false));
    static List<string> Ev(PracticeSession s) => s.Body.lastEvents ?? new List<string>();

    /// <summary>Steps until the dash ends; returns (distance of the dash, commands, exit speed, z change).</summary>
    static (double dist, int cmds, double exit, double dz) DashOnce(PracticeSession s, Func<SkillInput> hold)
    {
        var d = s.Ability<DashAbility>();
        int before = d.ends, k = 0;
        double z0 = s.Body.motor.pos.z;
        SkillInput i = hold(); i.dash = true; s.Step(i);
        if (d.starts == 0) return (double.NaN, 0, double.NaN, double.NaN);
        k = 1;
        while (d.ends == before && k < 200) { s.Step(hold()); k++; }
        return (Hz(d.endPos - d.startPos), k, Hz(s.Body.motor.vel), d.endPos.z - z0);
    }

    static void Basic()
    {
        // standing, flat
        var s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d");
        for (int k = 0; k < 30; k++) s.Step(In());
        var r = DashOnce(s, () => In());
        Row("DA-01", "冲刺距离：站着、平地", "原地，没按方向键（朝视角前）", "Length", r.dist, $"{r.cmds} 条命令 = {r.cmds * Dt:0.000} s；出口 {r.exit:0.0} u/s");
        Row("DA-02", "冲刺时长", "同上", "Time", r.cmds * Dt);
        Row("DA-03", "冲刺出口速度：站着", "同上", "Speed", r.exit, "max(420, 冲刺前 0)");
        Check(Math.Abs(r.dist - 403.33) < 1.5, $"flat standing distance {r.dist:0.00} ~ 403.3");
        Check(r.cmds == 40 && Math.Abs(r.exit - 420) < 1e-6, $"40 commands ({r.cmds}), exit 420 ({r.exit:0.00})");
        // until the speed is back to the sprint cap / stopped
        double xEnd = s.Body.motor.pos.x; int n = 0;
        while (Hz(s.Body.motor.vel) > 1 && n < 600) { s.Step(In()); n++; }
        Row("DA-04", "冲刺 + 松手滑停：总距离", "原地冲刺、之后什么都不按", "Length", s.Body.motor.pos.x, $"冲刺结束后再滑 {s.Body.motor.pos.x - xEnd:0.0} u、{n * Dt:0.00} s 停下（地面减速 1250）");
        // from a sprint
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d");
        for (int k = 0; k < 360; k++) s.Step(In(w: true, sprint: true));
        double v0 = Hz(s.Body.motor.vel);
        r = DashOnce(s, () => In(w: true, sprint: true));
        Row("DA-05", "冲刺距离：冲刺跑中", $"冲刺 {v0:0} u/s，按住 W", "Length", r.dist, $"出口 {r.exit:0.0} u/s（max(420, {v0:0})）");
        int nn = 0; while (Hz(s.Body.motor.vel) > 299.5 && nn < 600) { s.Step(In(w: true, sprint: true)); nn++; }
        Row("DA-06", "冲刺后回到冲刺速度 299 的时间", "同上，按住 W + 冲刺", "Time", nn * Dt, "地面减速 1250 u/s²");
        // from a slide (460)
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d");
        for (int k = 0; k < 360; k++) s.Step(In(w: true, sprint: true));
        s.Step(In(w: true, duck: true));
        double vs = Hz(s.Body.motor.vel);
        r = DashOnce(s, () => In(w: true));
        Row("DA-07", "冲刺打断滑铲：出口速度", $"冲刺起滑后第 2 条命令冲刺（滑铲 {vs:0.0} u/s）", "Speed", r.exit, "保留更快的滑铲速度（P3），滑铲结束");
        Check(!s.Body.motor.sliding && Math.Abs(r.exit - vs) < 1e-6, $"slide ended, exit keeps {vs:0.0} ({r.exit:0.0})");
        // in the air (still, high)
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d"); s.Body.Reset(new Vec3d(0, 0, 400), Vec3d.Zero, false);
        r = DashOnce(s, () => In());
        Row("DA-08", "冲刺距离：空中（静止开始）", "离地 400 u，速度 0", "Length", r.dist, $"高度变化 {r.dz:0.###} u（一条起始命令的重力也没有）");
        Check(Math.Abs(r.dz) < 1e-9, $"no height lost in the air ({r.dz})");
        // after a standing jump: dash at the apex
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d"); for (int k = 0; k < 30; k++) s.Step(In());
        s.Step(In(jump: true)); while (s.Body.motor.vel.z > 0) s.Step(In());
        double apex = s.Body.motor.pos.z;
        r = DashOnce(s, () => In());
        int fall = 0; while (!s.Body.motor.grounded && fall < 400) { s.Step(In()); fall++; }
        Row("DA-09", "原地跳 + 最高点冲刺：落地水平距离", $"最高点 {apex:0.0} u 冲刺", "Length", s.Body.motor.pos.x, $"冲刺 {r.dist:0.0} u 后再飞 {fall * Dt:0.00} s");
        // sprint jump + dash at the apex
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d"); for (int k = 0; k < 360; k++) s.Step(In(w: true, sprint: true));
        double x0 = s.Body.motor.pos.x;
        s.Step(In(w: true, sprint: true, jump: true)); while (s.Body.motor.vel.z > 0) s.Step(In(w: true));
        r = DashOnce(s, () => In(w: true));
        fall = 0; while (!s.Body.motor.grounded && fall < 400) { s.Step(In(w: true)); fall++; }
        Row("DA-10", "冲刺跳 + 最高点冲刺：落地水平距离", "冲刺 299 u/s 起跳，最高点冲刺，按住 W", "Length", s.Body.motor.pos.x - x0, $"普通冲刺跳 226.9 u（LS-04）；出口 {r.exit:0.0}");
        // sprint jump + dash right after takeoff
        s = Make(null); s.ResetToPose(Vec3d.Zero, 0, "d"); for (int k = 0; k < 360; k++) s.Step(In(w: true, sprint: true));
        x0 = s.Body.motor.pos.x;
        s.Step(In(w: true, sprint: true, jump: true)); s.Step(In(w: true));
        r = DashOnce(s, () => In(w: true));
        fall = 0; while (!s.Body.motor.grounded && fall < 400) { s.Step(In(w: true)); fall++; }
        Row("DA-11", "冲刺跳 + 起跳后马上冲刺：落地水平距离", "起跳后第 2 条命令冲刺", "Length", s.Body.motor.pos.x - x0, "冲刺在上升中开始：竖直速度清零、高度只到起跳后 2 条命令的高度");
    }

    /// <summary>Two decks (top 144), gap g: sprint on the first, jump at the edge, dash at the apex, W held. Land on the far deck?</summary>
    static bool Gap(double g, bool dash)
    {
        var s = Make(m => { Block(m, -3000, -400, 0, 0, 400, 144); Block(m, g, -400, 0, g + 3000, 400, 144); });
        s.ResetToPose(new Vec3d(-1500, 0, 144), 0, "gap");
        var mo = s.Body.motor;
        while (mo.pos.x < -16 - 2.5 && mo.grounded) s.Step(In(w: true, sprint: true));
        s.Step(In(w: true, sprint: true, jump: true));
        while (mo.vel.z > 0) s.Step(In(w: true));
        if (dash) s.Step(In(w: true, dash: true));
        for (int k = 0; k < 400 && !mo.grounded; k++) s.Step(In(w: true));
        return mo.grounded && mo.pos.z > 143 && mo.pos.x > g;
    }

    static void Gaps()
    {
        double best = 0, bestNo = 0;
        for (double g = 100; g <= 1200; g += 5) { if (Gap(g, true)) best = g; if (Gap(g, false)) bestNo = g; }
        Row("DA-12", "能跳 + 冲刺过去的最宽的坑", "两边台子同高（144 u），冲刺 299 到台边起跳，最高点冲刺，按住 W", "Length", best, $"5 u 网格；不冲刺最宽 {bestNo:0} u");
        Row("DA-13", "不冲刺能跳过去的最宽的坑（同上，对照）", "同上，不按冲刺键", "Length", bestNo, "");
        Check(best >= 400, $"a 400 u gap can be crossed (max {best})");
    }

    /// <summary>A wall face at x = 0 (top h). Sprint from 700 u back, jump at distance d from the face, dash at the apex (or just after takeoff), W held.</summary>
    static (bool ok, bool climbed) Ledge(double h, double d, bool apex)
    {
        var s = Make(m => Block(m, 0, -500, 0, 3000, 500, h));
        s.ResetToPose(new Vec3d(-900, 0, 0), 0, "ledge");
        var mo = s.Body.motor;
        bool climbed = false;
        while (mo.pos.x < -16 - d) s.Step(In(w: true, sprint: true));
        s.Step(In(w: true, sprint: true, jump: true));
        if (apex) while (mo.vel.z > 0) s.Step(In(w: true)); else s.Step(In(w: true));
        s.Step(In(w: true, dash: true));
        for (int k = 0; k < 600; k++)
        {
            s.Step(In(w: true));
            if (Ev(s).Any(e => e.StartsWith("CLIMB_START"))) climbed = true;
            if (mo.grounded && k > 5 && (mo.pos.z >= h - 1 || mo.pos.z < 1)) break;
        }
        return (mo.grounded && Math.Abs(mo.pos.z - h) < 1 && mo.pos.x > 0, climbed);
    }

    static void Ledges()
    {
        double bestMantle = 0, bestAny = 0, bestD = 0;
        foreach (double d in new[] { 150.0, 250, 350, 450 })
            foreach (bool apex in new[] { true, false })
                for (double h = 40; h <= 320; h += 2)
                {
                    var (ok, climbed) = Ledge(h, d, apex);
                    if (!ok) continue;
                    if (h > bestAny) { bestAny = h; bestD = d; }
                    if (!climbed && h > bestMantle) bestMantle = h;
                }
        Row("DA-14", "跳 + 冲刺 + 翻越（不攀爬）能上的最高台子", "冲刺接近，离墙 150 / 250 / 350 / 450 u 起跳，最高点或起跳后马上冲刺，按住 W", "Length", bestMantle, "2 u 网格；只靠跳 + 翻越是 84 u（LS-10）");
        Row("DA-15", "跳 + 冲刺 + 攀爬 / 翻越能上的最高台子", "同上，允许攀爬", "Length", bestAny, $"最好的起跳距离 {bestD:0} u；贴墙原地跳 + 攀爬是 222 u（LS-08），冲刺跳 275 u（LS-09）");
    }
}
