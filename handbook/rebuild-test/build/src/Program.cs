// 重建检验（hb-rebuild）：只照 handbook/*.md 和 handbook/tables/ 写的最小实现。
// 单位：u、s、°（README 写法规范第 4 条：整个文件都在 u 体系下）。
// 覆盖：地面（三段加速 + 原生摩擦）、冲刺、滑铲（起滑 / 衰减 / 结束 / 松蹲 / 落地续滑 / 滑铲跳）、
//       起跳、半步重力、空中加速（含 extraAirAccel）、落地（含硬着陆降速）、斜坡上的地面移动和滑铲坡面项、
//       下蹲碰撞体计时、眼高（下蹲比例 + 冲刺下沉）、落地 / 起跳 punch 弹簧。
// 没做：lurch、翻越、碰撞（题目都在无障碍的平地 / 无限斜面上）、上坡、台阶、FOV、横滚。
// 每一处靠猜的地方在代码里标 "GAP-xx"，和 ../GAPS.md 的编号对应。

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;

static class P
{
    // ---- 第 02 章 §2.1：固定 120 Hz
    public const double Dt = 1.0 / 120.0;

    // ---- 第 03 章 §3.1–§3.5（参数总表）
    public static double Msc = 1.0;            // GAP-01：题目写 msc = 1；手册"空手"是 1.15
    public const double Speed = 173.5, SprintSpeed = 260, CrouchSpeed = 80;
    public const double LowSpeed = 120, LowAccel = 2500, Accel = 450;
    public const double SprintAccel = 102;     // GAP-02：03 §3.2 用 102；tables/params G-07 说 R5 多数传奇 100
    public const double Decel = 1250, SprintDecel = 1250, CrouchDecel = 1500, StopSnap = 1;
    // ---- §3.6 空中
    public const double AirSpeed = 60, AirAccel = 500, ExtraAirAccel = 2;
    // ---- §3.7 / §3.8 重力和起跳
    public const double G = 750;               // sv_gravity × gravityScale(1)
    public const double JumpHeight = 56, SlideJumpHeight = 50;
    public const double AmjFrac = 0.3, AmjT0 = 0.15, AmjRamp = 0.60;
    public const double SkipTime = 1.0, SkipReduce = 100;
    // ---- 第 02 章
    public const double GroundProbe = 2;
    public const double HullCrouchTime = 0.2, AirUnduckDrop = 16.5, AirUnduckMin = 0.08;
    public const double HullBottomR = 16, FlatNormalZ = 0.999, StandableNz = 0.7;
    // ---- 第 04 章 §4.7 常数表
    public const double SlideReq = 200, SlideBoost = 150, SlideBoostCap = 400, SlideRearm = 2.0;
    public const double SlideDecel = 100, SlideStopDecel = 400, SlideDecay = 0.7;
    public const double SlideStopSpeed = 125, SlideMaxStopSpeed = 350, SlideSteer = 50;
    public const double RefundWindow = 0.4, DuckTransition = 0.2, SlideMaxJump = 350, SlideFloorLow = 0.85;
    public const double SlideSlopeGravityScale = 1;
    // ---- 第 03 章 §3.9 硬着陆降速（Unity 拟合，手册暂以它为准）
    public const double LandA = 1.996467, LandB = -1.6714e-6, LandT = 1.0, LandExp = 2;
    // ---- 第 07 章 §1.1 / §2.1 / §2.3 / §3.1
    public const double SpringK = 65, SpringC = 9, SecondGroup = 0.2, KickGain = 20;
    public const double JumpPitchBase = 2, JumpPitchRand = 1, JumpYawRand = 1, JumpRollBase = 0.9, JumpRollRand = 0.5;
    public const double KickPitchBase = 2, KickPitchRand = 0.75, KickFallMinFt = 10, KickFallMaxFt = 70, KickMaxScale = 12;
    public const double StandEye = 70, CrouchEye = 32, SprintOffset = -6, DuckTime = 0.4, SlideDuckTime = 0.2;
    public const double SprintRiseDelay = 0.16, SprintRiseRate = 1.25, SprintFallDelay = 0.11, SprintFallRate = 6.67;
}

// 地面：一个无限大的平面。theta = 0 平地；theta > 0 时沿 +x 往下（下坡方向 = +x）。
sealed class World
{
    public readonly double Theta;
    public readonly double Nx, Nz;            // 法线 (sinθ, 0, cosθ)，水平分量指向下坡
    public World(double thetaDeg) { Theta = thetaDeg * Math.PI / 180; Nx = Math.Sin(Theta); Nz = Math.Cos(Theta); }
    public bool IsSlope => Nz < P.FlatNormalZ;
    // 02 §2.8 第 6 条：坡上原点在坡面上方 R·(1/n_z − 1)（圆底）；平地 0。
    public double Support(double x) => -Math.Tan(Theta) * x + (IsSlope ? P.HullBottomR * (1 / Nz - 1) : 0);
}

struct Input
{
    public double Fwd;            // 前后轴，0 或 1
    public bool Sprint, Duck, Jump;
    public bool ForceDuckPress, ForceSprintPress;   // S5：两条命令之间的"短按"（02 §2.1 第 5 条的锁存），GAP-16
}

sealed class Axis
{
    public double X, V;
    // 07 §1.1 实现模板：欠阻尼精确解
    public void Step(double k, double c, double dt)
    {
        double a = c / 2, wd = Math.Sqrt(k - a * a), e = Math.Exp(-a * dt);
        double cs = Math.Cos(wd * dt), sn = Math.Sin(wd * dt);
        double x2 = e * (X * cs + (V + a * X) / wd * sn);
        double v2 = e * (V * cs - (a * V + k * X) / wd * sn);
        X = x2; V = v2;
        // GAP-21：R5 有 x²+v² < 0.001 归零，Unity 没做；这里照 Unity 参考实现不做
    }
}

static class R5Random
{
    // 07 §1.4：MD5(命令号 4 字节小端) 第 6–9 字节 → & 0x7fffffff → Jenkins OAAT(base 8 字节 + 盐 4 字节) → Park–Miller
    // GAP-19：字节下标按 0 起算、小端；OAAT 初值 0；种子不再取模就乘 48271。
    public static bool Zero;     // 第三个参数 r0：所有 r = 0（命令号对不上 R5 时用来对公式中值）
    public static float R(int command, uint salt)
    {
        if (Zero) return 0f;
        byte[] md5 = MD5.HashData(BitConverter.GetBytes(command));
        uint b = (uint)(md5[6] | md5[7] << 8 | md5[8] << 16 | md5[9] << 24) & 0x7fffffff;
        var bytes = new List<byte>();
        bytes.AddRange(BitConverter.GetBytes(b)); bytes.AddRange(new byte[4]); bytes.AddRange(BitConverter.GetBytes(salt));
        uint h = 0;
        foreach (byte x in bytes) { h += x; h += h << 10; h ^= h >> 6; }
        h *= 9; h ^= h >> 11; h *= 0x8001;
        ulong next = (48271UL * h) % 2147483647UL;
        float r = -0.5f + Math.Min((float)next / 2147483648f, 0.99999988f);
        return r;
    }
}

sealed class Body
{
    public readonly World W;
    public double X, Z, Vx, Vz;              // 只走 x 方向（题目都是直线），y 恒为 0
    public bool Grounded = true, Sliding, Boosted;
    public double LastBoost, BoostTime = double.NegativeInfinity, SlideStartTime = double.NegativeInfinity;
    public double DuckTransitionStart = double.NegativeInfinity, LastLandTime = double.NegativeInfinity;
    public double LastTakeoff = double.NegativeInfinity;
    public bool PrevDuck, PrevSprint, PrevJump;
    public bool HullCrouched; public double DuckHeldSince = double.NaN;
    public bool LsActive; public double LsF0 = 1, LsTLand;
    // 这条命令的事实（给镜头读）
    public bool Jumped, Landed, SprintingFlag, DuckedUsed; public double VzEndPrev; public double VzEnd;
    public List<string> Events = new List<string>();

    public Body(World w) { W = w; }
    double Hs => Math.Abs(Vx);

    public void Step(Input inp, int tick)
    {
        double dt = P.Dt, now = tick / 120.0;     // GAP-17：时钟写成 tick/120，不累加
        Events.Clear(); Jumped = false; Landed = false;
        VzEndPrev = VzEnd;
        bool duckPressed = (inp.Duck && !PrevDuck) || inp.ForceDuckPress;
        bool jumpPressed = inp.Jump && !PrevJump;

        // ---- 世界·移动前（02 §2.6）
        double floorZ = W.Support(X);
        double drop = Z - floorZ;
        if (Grounded && drop > P.GroundProbe)
        {
            Grounded = false; LastTakeoff = now;
            if (Sliding) { Sliding = false; Events.Add("slide_end"); }
        }

        // ---- 硬着陆降速：乘在移动倍率上（03 §3.9 实现模板）
        double msc = P.Msc;
        if (LsActive)
        {
            double t = now - LsTLand;
            if (t < P.LandT) msc *= LsF0 + (1 - LsF0) * Math.Pow(t / P.LandT, P.LandExp);
            else LsActive = false;
        }

        bool ducked = PrevDuck;                                    // 03 §3.1 第 5 条
        bool sprinting = Grounded && inp.Sprint && PrevSprint && inp.Fwd > 0 && !ducked && !inp.Duck && !Sliding;
        double s = Hs; double dir = Vx >= 0 ? 1 : -1; if (s == 0) dir = 1;   // 题目里始终朝 +x

        UpdateDuckHull(inp, now, floorZ);

        // ---- 按蹲起滑（04 §4.1，移动之前）
        if (Grounded && !Sliding && duckPressed && s >= P.SlideReq && W.Nz > P.StandableNz)
        {
            Boosted = now - SlideStartTime >= P.SlideRearm;
            if (Boosted)
            {
                double peak = Math.Min(s + P.SlideBoost * msc, P.SlideBoostCap * msc);
                LastBoost = peak - s; BoostTime = now; s = peak; Vx = dir * s;
            }
            Sliding = true; SlideStartTime = now; DuckTransitionStart = now + dt;
            sprinting = false;
            Events.Add("slide_start");
        }

        if (Grounded && jumpPressed) JumpCommand(inp, now, dt, msc, ducked, floorZ);
        else if (Grounded) GroundCommand(inp, now, dt, msc, ref ducked, sprinting, floorZ);
        else AirCommand(inp, now, dt, msc, ducked, floorZ);

        SprintingFlag = sprinting; DuckedUsed = ducked;
        VzEnd = Vz;
        PrevDuck = inp.Duck; PrevSprint = inp.Sprint; PrevJump = inp.Jump;
    }

    // 02 §2.4 / 04 §4.8 实现模板
    void UpdateDuckHull(Input inp, double now, double floorZ)
    {
        if (inp.Duck)
        {
            if (double.IsNaN(DuckHeldSince)) DuckHeldSince = now;
            if (Grounded && now - DuckHeldSince >= P.HullCrouchTime) HullCrouched = true;
            return;
        }
        DuckHeldSince = double.NaN;
        if (!HullCrouched) return;
        if (Grounded) { HullCrouched = false; return; }        // 头顶没东西
        if (now - LastTakeoff < P.AirUnduckMin) return;
        Z = Math.Max(floorZ, Z - P.AirUnduckDrop);
        HullCrouched = false;
    }

    static double MultiJumpFrac(double t)
    {
        if (double.IsPositiveInfinity(t)) return 1;
        double f = P.AmjFrac + (1 - P.AmjFrac) * (t - P.AmjT0) / P.AmjRamp;
        return Math.Clamp(f, P.AmjFrac, 1);
    }

    // 03 §3.6：空中加速。题目里意图方向 = +x，只有 x 分量。
    void AirAccelerate(Input inp, double msc, bool ducked, double dt)
    {
        double m = Math.Min(Math.Abs(inp.Fwd), 1);          // GAP-11：空中不走输入曲线（全按时没区别）
        if (m <= 0) return;
        double wishspeed = m * (ducked ? P.CrouchSpeed : P.Speed) * msc;
        double wishcap = Math.Min(wishspeed, P.AirSpeed * msc);
        if (wishcap <= 0) return;
        double w = Math.Sign(inp.Fwd);
        double add = wishcap - Vx * w;
        if (add > 0) Vx += w * Math.Min(P.AirAccel * dt, add);
        else if (P.ExtraAirAccel > 0)
        {
            double before = Math.Sqrt(Vx * Vx + Vz * Vz);
            Vx += w * P.ExtraAirAccel * dt;
            double lim = Math.Max(before, wishcap);
            double now3 = Math.Sqrt(Vx * Vx + Vz * Vz);
            if (now3 > lim) { Vx *= lim / now3; Vz *= lim / now3; }
        }
    }

    void JumpCommand(Input inp, double now, double dt, double msc, bool ducked, double floorZ)
    {
        double tLand = now - LastLandTime;
        double frac = MultiJumpFrac(tLand);
        double s = Hs, dir = Vx >= 0 ? 1 : -1;
        double H;
        if (Sliding)
        {   // 04 §4.6
            if (Boosted)
            {
                if (now - BoostTime < P.RefundWindow && now - DuckTransitionStart < P.DuckTransition)
                    s = Math.Max(0, s - LastBoost);
                if (P.SlideFloorLow * P.SlideMaxJump < s && s < P.SlideMaxJump) s = P.SlideMaxJump;
            }
            Sliding = false; Boosted = false; Events.Add("slide_end");
            H = P.SlideJumpHeight;
        }
        else
        {
            double R = P.SprintSpeed * msc;
            if (tLand < P.SkipTime && s > R) s = Math.Max(R, s - P.SkipReduce);
            H = P.JumpHeight;
        }
        Vx = dir * s;
        double V = Math.Sqrt(2 * P.G * H * frac);
        Vz = 0; Vz -= 0.5 * P.G * dt; Vz += V; Vz -= 0.5 * P.G * dt;
        // jumpSurfacePush：没有墙，不起作用
        AirAccelerate(inp, msc, ducked, dt);
        X += Vx * dt; Z += Vz * dt;
        Vz -= 0.5 * P.G * dt;
        Grounded = false; LastTakeoff = now;
        Jumped = true; Events.Add("jump");
        CheckLanding(inp, now, floorZ);
    }

    void AirCommand(Input inp, double now, double dt, double msc, bool ducked, double floorZ)
    {
        Vz -= 0.5 * P.G * dt;
        AirAccelerate(inp, msc, ducked, dt);
        X += Vx * dt; Z += Vz * dt;
        Vz -= 0.5 * P.G * dt;
        CheckLanding(inp, now, floorZ);
    }

    void CheckLanding(Input inp, double now, double floorZ)
    {
        if (!(Vz < 0 && Z - floorZ <= P.GroundProbe)) return;
        if (Z < floorZ) Z = floorZ;
        double vzPre = Vz;
        Vz = 0; Grounded = true; LastLandTime = now; Landed = true; Events.Add("land");
        // 硬着陆降速（GAP-13：vz 取这条命令清零前的值）
        double f0 = Math.Clamp(P.LandA + P.LandB * vzPre * vzPre, 0, 1);
        if (f0 < 1) { Vx *= f0; LsActive = true; LsF0 = f0; LsTLand = now; }
        // 落地续滑（04 §4.4 第 2 条）
        if (inp.Duck && Hs >= P.SlideReq)
        {
            Sliding = true; Boosted = false; SlideStartTime = now;
            Events.Add("slide_start");                         // GAP-15：续滑也记 slide_start
        }
    }

    void GroundCommand(Input inp, double now, double dt, double msc, ref bool ducked, bool sprinting, double floorZ)
    {
        bool releasing = Sliding && !inp.Duck;
        double s = Hs, dir = Vx >= 0 ? 1 : -1; if (s == 0) dir = 1;
        if (releasing && s <= P.SlideMaxStopSpeed)
        {   // 04 §4.3：移动之前结束，这条命令按蹲走
            Sliding = false; Boosted = false; ducked = true; Events.Add("slide_end");
        }
        if (Sliding)
        {
            if (W.Nz < 1 - 1e-6)
            {   // 04 §4.5 坡面项（摩擦之前）
                Vx += P.G * P.SlideSlopeGravityScale * W.Nz * W.Nx * dt;
                s = Hs; dir = Vx >= 0 ? 1 : -1;
            }
            double D = releasing ? P.SlideStopDecel : P.SlideDecel;
            s = Math.Max(0, (s - D * dt) * Math.Pow(P.SlideDecay, dt));
            // 转向：只按 W，垂直分量 p = 0，方向不变
            Vx = dir * s;
            if (s < P.SlideStopSpeed) { Sliding = false; Events.Add("slide_end"); }
        }
        else GroundMove(inp, dt, msc, ducked, sprinting);
        Vz = 0;
        MoveOnGround(dt, floorZ);
    }

    // 03 §3.4 实现模板（一维：意图和速度都沿 x）
    void GroundMove(Input inp, double dt, double msc, bool ducked, bool sprinting)
    {
        double h = Hs, dir = Vx >= 0 ? 1 : -1; if (h == 0) dir = 1;
        if (inp.Fwd == 0)
        {
            double D0 = ducked ? P.CrouchDecel : P.Decel;
            h -= D0 * dt; if (h < P.StopSnap) h = 0;
            Vx = dir * h; return;
        }
        double f = inp.Fwd * (sprinting ? 1.25 : 1);
        double m = Math.Abs(f);
        if (m > 1) { f /= m; m = 1; } else { f *= (2 - m); m *= (2 - m); }
        double cap = ducked ? P.CrouchSpeed * msc : sprinting ? P.SprintSpeed * msc : P.Speed * msc;
        double wishspeed = Math.Min(m, 1) * cap;
        double w = Math.Sign(f);
        // §3.2：加速度按摩擦前的 h 选段
        double a = h > P.Speed * msc - 1 ? P.SprintAccel * msc : h < P.LowSpeed * msc ? P.LowAccel * msc : P.Accel * msc;
        double v = Vx;
        double p = v * w, k = 0;
        if (p > 0 && h > 0) k = w * p * Math.Min(1, p * wishspeed / (h * h));
        double r = v - k;
        double D = ducked ? P.CrouchDecel : (h > msc * P.Speed ? P.SprintDecel : P.Decel);
        double rl = Math.Abs(r);
        if (rl > 0) r *= Math.Max(0, rl - D * dt) / rl;
        v = k + r;
        // Accelerate
        double old = Math.Abs(v);
        double add = wishspeed - v * w;
        if (add > 0)
        {
            v += w * Math.Min(add, a * dt);
            double lim = Math.Max(old, wishspeed);
            if (Math.Abs(v) > lim) v *= lim / Math.Abs(v);
        }
        if (Math.Abs(v) < P.StopSnap) v = 0;
        Vx = v;
    }

    // 02 §2.8 / §2.2 第 3a 步：平地 pos += v·dt、z = 地面；坡上按 slopeGroundMove
    void MoveOnGround(double dt, double floorZ)
    {
        double d = Vx * dt;
        if (!W.IsSlope) { X += d; Z = floorZ; return; }
        double k = d * W.Nx;                 // d·n_h
        double dz;
        if (k < 0)
        {   // 上坡：投影后补回长度（U-1）
            double L0 = Math.Abs(d);
            double dx = d - k * W.Nx; dz = -k * W.Nz;
            double L = Math.Sqrt(dx * dx + dz * dz);
            dx *= L0 / L; dz *= L0 / L; d = dx;
        }
        else dz = -k / W.Nz;                 // 下坡：水平不变，高度跟坡面
        X += d; Z = floorZ + dz;
        double top = W.Support(X);           // afterStep 末尾：不陷进坡里
        if (Z < top) Z = top;
    }
}

sealed class Camera
{
    readonly Axis[] p1 = { new Axis(), new Axis(), new Axis() }, p2 = { new Axis(), new Axis(), new Axis() };
    double d;                    // 下蹲比例
    double q; bool lastSprint; double sprintChange = 0;   // 冲刺比例
    public double PitchPunch => p1[0].X + p2[0].X;
    public double Eye;

    static double MoveToward(double f, double t, double step) => f < t ? Math.Min(t, f + step) : Math.Max(t, f - step);
    static double Smooth(double x) { x = Math.Clamp(x, 0, 1); return x * x * (3 - 2 * x); }

    void Kick(double jp, double jy, double jr)
    {
        p1[0].V += jp; p1[1].V += jy; p1[2].V += jr;
        p2[0].V += P.SecondGroup * jp; p2[1].V += P.SecondGroup * jy; p2[2].V += P.SecondGroup * jr;
    }

    public static double KickScale(double v)
    {
        double vmin = Math.Sqrt(2 * P.G * 12 * P.KickFallMinFt), vmax = Math.Sqrt(2 * P.G * 12 * P.KickFallMaxFt);
        if (v < vmin) return v / vmin;
        if (v <= vmax) return 1 + (P.KickMaxScale - 1) * (v - vmin) / (vmax - vmin);
        return P.KickMaxScale;
    }

    // 07 §4.1 Observe：身体这条命令跑完以后
    public void Observe(Body b, int cmd, double now, double dt)
    {
        // 1. 眼高（07 §3.1）
        bool down = b.Sliding || b.DuckedUsed || b.HullCrouched;      // GAP-23：ducked 用这条命令里用到的那个
        d = MoveToward(d, down ? 1 : 0, dt / (b.Sliding ? P.SlideDuckTime : P.DuckTime));
        if (b.SprintingFlag != lastSprint) { lastSprint = b.SprintingFlag; sprintChange = now; }
        double timer = now - sprintChange;                            // GAP-24
        if (lastSprint && timer >= P.SprintRiseDelay) q = Math.Min(1, q + P.SprintRiseRate * dt);
        if (!lastSprint && timer >= P.SprintFallDelay) q = Math.Max(0, q - P.SprintFallRate * dt);
        double stand = P.StandEye + P.SprintOffset * Math.Sin(q * Math.PI / 2);
        Eye = stand + (P.CrouchEye - stand) * Smooth(d);
        // 2. 弹簧：先推进，再加 kick（GAP-20：拿枪时第二组应换武器弹簧，这里按 Unity 一直 65 / 9）
        foreach (var a in p1) a.Step(P.SpringK, P.SpringC, dt);
        foreach (var a in p2) a.Step(P.SpringK, P.SpringC, dt);
        if (b.Landed)
        {
            double v = Math.Max(0, -b.VzEndPrev);                     // 落地前一条命令结束时的向下速度
            double s = KickScale(v);
            if (s > 0)
            {
                double r1 = R5Random.R(cmd, 0x76704c58), r3 = R5Random.R(cmd, 0x76704c5a);
                Kick(s * (P.KickPitchBase + P.KickPitchRand * r1) * P.KickGain, 0, s * r3 * P.KickGain);
            }
        }
        if (b.Jumped)
        {
            double r1 = R5Random.R(cmd, 0x76704a58), r2 = R5Random.R(cmd, 0x76704a59), r3 = R5Random.R(cmd, 0x76704a5a);
            Kick((P.JumpPitchBase + P.JumpPitchRand * r1) * P.KickGain, P.JumpYawRand * r2 * P.KickGain,
                 (P.JumpRollBase + P.JumpRollRand * r3) * P.KickGain);
        }
    }
}

static class Program
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static string F(double x, int n = 4) => x.ToString("F" + n, Inv);

    sealed class Run
    {
        public string Name; public World W; public Body B; public Camera C = new Camera();
        public StringBuilder Csv = new StringBuilder();
        public int Tick;
        public double PeakSpeed, PeakPunch, MinPunch;
        public int SlideStartTick = -1, SlideEndTick = -1, FirstLandTick = -1;
        public List<string> Notes = new List<string>();
        public Run(string name, double thetaDeg, double z0, bool grounded)
        {
            Name = name; W = new World(thetaDeg); B = new Body(W);
            B.Z = W.Support(0) + z0; B.Grounded = grounded;
            Csv.AppendLine("tick,t_s,pos_x_u,pos_z_u,speed_h_u_s,vel_z_u_s,state,events,cam_pitch_punch_deg,eye_height_u");
            C.Eye = P.StandEye;
        }
        public void Step(Input inp)
        {
            B.Step(inp, Tick);
            double now = Tick / 120.0;
            C.Observe(B, Tick, now, P.Dt);
            string state = !B.Grounded ? "air" : B.Sliding ? "slide" : (inp.Duck || B.DuckedUsed) ? "crouch" : "ground";
            string ev = string.Join(";", B.Events);
            Csv.AppendLine($"{Tick},{F(now, 6)},{F(B.X)},{F(B.Z)},{F(Math.Abs(B.Vx))},{F(B.Vz)},{state},{ev},{F(C.PitchPunch)},{F(C.Eye)}");
            PeakSpeed = Math.Max(PeakSpeed, Math.Abs(B.Vx));
            PeakPunch = Math.Max(PeakPunch, C.PitchPunch); MinPunch = Math.Min(MinPunch, C.PitchPunch);
            if (B.Events.Contains("slide_start") && SlideStartTick < 0) SlideStartTick = Tick;
            if (B.Events.Contains("slide_end")) SlideEndTick = Tick;
            if (B.Events.Contains("land") && FirstLandTick < 0) FirstLandTick = Tick;
            Tick++;
        }
        public void Save(string dir) => File.WriteAllText(Path.Combine(dir, Name + ".csv"), Csv.ToString());
    }

    static Input Fwd(bool sprint, bool duck, bool jump = false) => new Input { Fwd = 1, Sprint = sprint, Duck = duck, Jump = jump };

    // S1 / S2 / S3 / S4 / S5 共用：0–2.0 s 前 + 冲刺，2.0 s（第 240 条）按下蹲
    const int CrouchTick = 240;

    static Run SlideProblem(string name, double theta, int releaseTick, int jumpTick, bool s5, int maxSlideTicks)
    {
        var r = new Run(name, theta, 0, true);
        for (int i = 0; i < CrouchTick; i++) r.Step(Fwd(true, false));
        int endTick = -1;
        bool jumped = false;
        while (true)
        {
            int t = r.Tick;
            bool duck = releaseTick < 0 || t < releaseTick;
            bool jump = t == jumpTick;
            r.Step(Fwd(true, duck, jump));
            if (jump) jumped = true;
            bool slideOver = r.B.Grounded && !r.B.Sliding && (jumpTick < 0 || jumped);
            if (slideOver) { endTick = t; break; }
            if (t - CrouchTick >= maxSlideTicks) { r.Notes.Add($"滑铲到 {maxSlideTicks / 120.0:F1} s 还没结束，截断"); endTick = t; break; }
        }
        // 结束后再 1.0 s
        for (int k = 1; k <= 120; k++)
        {
            int t = r.Tick;
            bool duck = releaseTick < 0 || t < releaseTick;
            var inp = Fwd(true, duck);
            if (s5 && k == 1) { inp.Duck = true; inp.Sprint = true; inp.ForceDuckPress = true; inp.ForceSprintPress = true; }
            if (s5) { inp.Duck = true; inp.Sprint = true; }
            r.Step(inp);
        }
        r.Notes.Add($"滑铲结束（身体着地且不在滑铲）在第 {endTick} 条");
        return r;
    }

    static Run Drop(string name, double h)
    {
        var r = new Run(name, 0, h, false);
        while (r.FirstLandTick < 0) r.Step(new Input());
        for (int k = 0; k < 180; k++) r.Step(new Input());
        return r;
    }

    static Run StandJump()
    {
        var r = new Run("L2", 0, 0, true);
        r.Step(new Input { Jump = true });
        while (r.FirstLandTick < 0) r.Step(new Input());
        for (int k = 0; k < 180; k++) r.Step(new Input());
        return r;
    }

    static void Main(string[] args)
    {
        P.Msc = args.Length > 0 ? double.Parse(args[0], Inv) : 1.0;
        string outDir = args.Length > 1 ? args[1] : "out";
        R5Random.Zero = args.Length > 2 && args[2] == "r0";
        Directory.CreateDirectory(outDir);
        var runs = new List<Run>
        {
            SlideProblem("S1", 0, -1, -1, false, 1200),
            SlideProblem("S2", 0, CrouchTick + 60, -1, false, 1200),
            SlideProblem("S3", 0, -1, CrouchTick + 25, false, 1200),     // 0.208 s × 120 = 24.96 → 25 条（GAP-08）
            SlideProblem("S4", 20, -1, -1, false, 720),                  // GAP-09：20° 下坡滑不停，6 s 截断
            SlideProblem("S5", 0, -1, -1, true, 1200),
            Drop("L1_50", 50), Drop("L1_100", 100), Drop("L1_200", 200), Drop("L1_400", 400),
            StandJump(),
        };
        var sum = new StringBuilder();
        sum.AppendLine($"msc = {P.Msc}; random = {(R5Random.Zero ? "r = 0" : "R5SharedRandom, 命令号 = tick")}");
        sum.AppendLine("problem\tpeak_speed_u_s\tslide_start_tick\tslide_end_tick\tslide_s\tfirst_land_tick\tpeak_pitch_punch_deg\tmin_pitch_punch_deg\tnotes");
        foreach (var r in runs)
        {
            r.Save(outDir);
            double slideS = r.SlideStartTick >= 0 && r.SlideEndTick >= 0 ? (r.SlideEndTick - r.SlideStartTick + 1) / 120.0 : double.NaN;
            sum.AppendLine($"{r.Name}\t{F(r.PeakSpeed, 3)}\t{r.SlideStartTick}\t{r.SlideEndTick}\t{F(slideS, 4)}\t{r.FirstLandTick}\t{F(r.PeakPunch, 3)}\t{F(r.MinPunch, 3)}\t{string.Join("; ", r.Notes)}");
        }
        File.WriteAllText(Path.Combine(outDir, "summary.tsv"), sum.ToString());
        Console.Write(sum.ToString());
    }
}
