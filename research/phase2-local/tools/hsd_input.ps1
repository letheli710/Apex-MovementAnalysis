<#
.SYNOPSIS
  Scripted keyboard input and window screenshots for the local R5Flowstate test client
  started by hsd_launch.ps1. Windows PowerShell 5.1, no extra modules.

.DESCRIPTION
  Steps are a small text program, one per ';' or newline:
    wait <sec>            sleep
    hold <key> <sec>      press, keep down for <sec>, release
    tap <key>             press and release (50 ms)
    down <key> / up <key> raw edges (several keys may be down together)
    console <text>        open the console (grave key), type <text>, Enter, close it
    shot <name>           save a PNG of the client window to -ShotDir
  Keys are sent as hardware scan codes (KEYEVENTF_SCANCODE), which games read
  through raw input. Names: w a s d space ctrl shift c e q f esc enter grave tab 1-9.

.EXAMPLE
  .\hsd_input.ps1 -Steps 'shot before; wait 3; hold w 3; wait 3; tap space; wait 2; shot after'
#>
param(
    [string]$Steps = 'shot now',
    [string]$ProcessName = 'r5apex_dx12',
    [string]$WindowClass = 'Respawn001',
    [string]$ShotDir = "$env:TEMP\hsd_shots"
)
$ErrorActionPreference = 'Stop'

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class HsdIn {
    [StructLayout(LayoutKind.Sequential)] struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr extra; }
    [StructLayout(LayoutKind.Sequential)] struct MOUSEINPUT { public int dx, dy; public uint data, flags, time; public IntPtr extra; }
    [StructLayout(LayoutKind.Explicit)] struct UNION { [FieldOffset(0)] public MOUSEINPUT mi; [FieldOffset(0)] public KEYBDINPUT ki; }
    [StructLayout(LayoutKind.Sequential)] struct INPUT { public uint type; public UNION u; }
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    [DllImport("user32.dll", SetLastError = true)] static extern uint SendInput(uint n, INPUT[] inputs, int size);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
    delegate bool EnumCb(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumCb cb, IntPtr l);
    [DllImport("user32.dll")] static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassName(IntPtr h, System.Text.StringBuilder s, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    // The client process also owns a console window; the game renders into class Respawn001.
    public static IntPtr FindWindow(int pid, string cls) {
        IntPtr found = IntPtr.Zero;
        EnumWindows((h, l) => {
            int p; GetWindowThreadProcessId(h, out p);
            var c = new System.Text.StringBuilder(256); GetClassName(h, c, 256);
            if (p == pid && IsWindowVisible(h) && c.ToString() == cls) { found = h; return false; }
            return true;
        }, IntPtr.Zero);
        return found;
    }
    const uint SCANCODE = 0x0008, KEYUP = 0x0002, UNICODE = 0x0004, EXTENDED = 0x0001;
    static void Send(ushort vk, ushort scan, uint flags) {
        var i = new INPUT[1]; i[0].type = 1; i[0].u.ki.wVk = vk; i[0].u.ki.wScan = scan; i[0].u.ki.dwFlags = flags;
        if (SendInput(1, i, Marshal.SizeOf(typeof(INPUT))) != 1) throw new Exception("SendInput failed " + Marshal.GetLastWin32Error());
    }
    public static void Key(ushort scan, bool up, bool ext) { Send(0, scan, SCANCODE | (up ? KEYUP : 0) | (ext ? EXTENDED : 0)); }
    public static void Char(char c) { Send(0, c, UNICODE); Send(0, c, UNICODE | KEYUP); }
    public static void Focus(IntPtr h) {
        // Alt tap lets SetForegroundWindow succeed from a background process.
        keybd_event(0x12, 0, 0, UIntPtr.Zero); keybd_event(0x12, 0, KEYUP, UIntPtr.Zero);
        ShowWindow(h, 9); SetForegroundWindow(h);
    }
    public static void Shot(IntPtr h, string path) {
        RECT r; GetWindowRect(h, out r);
        int w = Math.Max(1, r.R - r.L), ht = Math.Max(1, r.B - r.T);
        using (var bmp = new Bitmap(w, ht)) using (var g = Graphics.FromImage(bmp)) {
            g.CopyFromScreen(r.L, r.T, 0, 0, new Size(w, ht)); bmp.Save(path, ImageFormat.Png);
        }
    }
}
'@

$scan = @{
    esc = 0x01; '1' = 0x02; '2' = 0x03; '3' = 0x04; '4' = 0x05; '5' = 0x06; '6' = 0x07; '7' = 0x08; '8' = 0x09; '9' = 0x0A
    tab = 0x0F; q = 0x10; w = 0x11; e = 0x12; enter = 0x1C; ctrl = 0x1D; a = 0x1E; s = 0x1F; d = 0x20; f = 0x21
    grave = 0x29; shift = 0x2A; c = 0x2E; space = 0x39
}
function Code([string]$k) { $k = $k.ToLower(); if (-not $scan.ContainsKey($k)) { throw "unknown key '$k'" }; [uint16]$scan[$k] }

$proc = Get-Process -Name $ProcessName -ErrorAction Stop | Select-Object -First 1
$h = [HsdIn]::FindWindow($proc.Id, $WindowClass)
if ($h -eq [IntPtr]::Zero) { throw "no visible '$WindowClass' window in $ProcessName (pid $($proc.Id))" }
New-Item -ItemType Directory -Force $ShotDir | Out-Null
[HsdIn]::Focus($h); Start-Sleep -Milliseconds 300
$held = New-Object System.Collections.Generic.HashSet[uint16]

function Ensure-Focus { if ([HsdIn]::GetForegroundWindow() -ne $h) { [HsdIn]::Focus($h); Start-Sleep -Milliseconds 200 } }

try {
    foreach ($raw in ($Steps -split "[;`n]")) {
        $line = $raw.Trim(); if (-not $line) { continue }
        $verb, $rest = $line -split '\s+', 2
        $t = (Get-Date).ToString('HH:mm:ss.fff')
        switch ($verb) {
            'wait' { Start-Sleep -Milliseconds ([int]([double]$rest * 1000)) }
            'hold' {
                $k, $sec = $rest -split '\s+'; Ensure-Focus; $c = Code $k
                [HsdIn]::Key($c, $false, $false); Start-Sleep -Milliseconds ([int]([double]$sec * 1000)); [HsdIn]::Key($c, $true, $false)
            }
            'tap' { Ensure-Focus; $c = Code $rest; [HsdIn]::Key($c, $false, $false); Start-Sleep -Milliseconds 50; [HsdIn]::Key($c, $true, $false) }
            'down' { Ensure-Focus; $c = Code $rest; [HsdIn]::Key($c, $false, $false); [void]$held.Add($c) }
            'up' { $c = Code $rest; [HsdIn]::Key($c, $true, $false); [void]$held.Remove($c) }
            'console' {
                Ensure-Focus; $g = Code 'grave'
                [HsdIn]::Key($g, $false, $false); [HsdIn]::Key($g, $true, $false); Start-Sleep -Milliseconds 400
                foreach ($ch in $rest.ToCharArray()) { [HsdIn]::Char($ch); Start-Sleep -Milliseconds 5 }
                $en = Code 'enter'; [HsdIn]::Key($en, $false, $false); [HsdIn]::Key($en, $true, $false); Start-Sleep -Milliseconds 300
                [HsdIn]::Key($g, $false, $false); [HsdIn]::Key($g, $true, $false); Start-Sleep -Milliseconds 300
            }
            'shot' { $p = Join-Path $ShotDir ("{0}_{1}.png" -f (Get-Date -Format 'HHmmss'), $rest); [HsdIn]::Shot($h, $p); Write-Host "[hsd_input] $t shot $p"; continue }
            default { throw "unknown step '$line'" }
        }
        Write-Host "[hsd_input] $t $line"
    }
}
finally {
    foreach ($c in @($held)) { [HsdIn]::Key($c, $true, $false) }
}
