# Capture the R5 client window without focus or mouse. capture.ps1 <out.png> [-ListOnly]
# Prefers PrintWindow with PW_RENDERFULLCONTENT; reports window and client size. Does not bring the window forward.
param([string]$Out, [switch]$ListOnly)
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System; using System.Drawing; using System.Drawing.Imaging; using System.Runtime.InteropServices;
public static class Cap {
  [StructLayout(LayoutKind.Sequential)] public struct R { public int L, T, Rt, B; }
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  public static string Info(IntPtr h) { R c, w; GetClientRect(h, out c); GetWindowRect(h, out w); return "client " + c.Rt + "x" + c.B + " window " + (w.Rt - w.L) + "x" + (w.B - w.T) + " at " + w.L + "," + w.T + " iconic " + IsIconic(h) + " foreground " + (GetForegroundWindow() == h); }
  public static void Save(IntPtr h, string path, uint flags) {
    R c; GetClientRect(h, out c);
    using (var b = new Bitmap(c.Rt, c.B)) { using (var g = Graphics.FromImage(b)) { var dc = g.GetHdc(); PrintWindow(h, dc, flags); g.ReleaseHdc(dc); } b.Save(path, ImageFormat.Png); }
  }
}
'@
$p = Get-Process r5apex_dx12 -ErrorAction Stop | Select-Object -First 1
$h = $p.MainWindowHandle
"pid $($p.Id) title '$($p.MainWindowTitle)' " + [Cap]::Info($h)
if (-not $ListOnly) { [Cap]::Save($h, $Out, 3); "saved $Out" }
