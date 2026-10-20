<#
.SYNOPSIS
  Start a local R5Flowstate dedicated server + client the way the launcher's
  "Play Local" does with Developer and Cheats ticked, without the launcher GUI.

.DESCRIPTION
  Mirrors launcher 0.1.62 (research-src/launcher @ 00fd923):
    dedi argv   R5Flowstate.Spawn/LaunchArgs.cs:278-366 via Shell/MainWindow.xaml.cs:3187-3210
    client argv LaunchArgs.cs:144-276, MainWindow.xaml.cs:2620-2625
    env         R5Flowstate.Spawn/ProcessSpawner.cs:335-347 (VPROJECT, FROM_R5F_LAUNCHER)
    host ready  R5F_HOST_READY named event, set by the dedi in
                s21-r5sdk/src/engine/server/sv_rcon_launcher.cpp:360-382; the client
                is only started after it fires (MainWindow.xaml.cs:2570-2627).
  Differences from the launcher, on purpose:
    - only processes whose image lives under -Root are stopped (the launcher
      also kills every r5apex_ds.exe on the machine);
    - no rcon / hosted-console pipes (optional for the SDK, sv_rcon_launcher.cpp:171-200);
    - the client window is -windowed so automation can see it;
    - -Offline (default on) adds the launcher's "Offline" args to both sides.
  The launcher writes nothing the game needs before launch except the mods\*.vdf
  policy files, which already exist; this script writes no game files.

.EXAMPLE
  .\hsd_launch.ps1 -Run 1                 # firing range, telemetry on, run label 1
  .\hsd_launch.ps1 -Stop                  # stop dedi + client started from -Root
#>
param(
    [string]$Root = (Join-Path $env:USERPROFILE 'Games\R5Flowstate'),
    [string]$Playlist = 'survival_firingrange',
    [string]$Map = 'mp_rr_canyonlands_staging_mu1',
    [int]$Port = 37015,
    [string]$ClientExe = 'r5apex_dx12.exe',
    [int]$Width = 1600,
    [int]$Height = 900,
    [bool]$Offline = $true,
    [string[]]$DediExec = @('user/hsd_dedi'),
    [string[]]$ClientExec = @('user/hsd_client', 'user/hsd_runs'),
    [int]$Run = 0,
    [string[]]$DediExtra = @(),
    [string[]]$ClientExtra = @(),
    [int]$HostReadyTimeoutSec = 300,
    [switch]$Stop
)
$ErrorActionPreference = 'Stop'
$images = 'r5apex', 'r5apex_dx12', 'r5apex_ds'

function Stop-R5 {
    $p = Get-Process -Name $images -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -and $_.Path.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase) }
    foreach ($x in $p) {
        Write-Host "[hsd_launch] stopping $($x.ProcessName) pid=$($x.Id)"
        & taskkill.exe /PID $x.Id /T /F | Out-Null
    }
    $p | ForEach-Object { $_.WaitForExit(10000) | Out-Null }
}

function Wait-PortFree([int]$port, [int]$ms) {
    $deadline = (Get-Date).AddMilliseconds($ms)
    while ($true) {
        try { $u = [Net.Sockets.UdpClient]::new($port); $u.Close(); return } catch {}
        if ((Get-Date) -gt $deadline) { throw "UDP port $port still in use" }
        Start-Sleep -Milliseconds 100
    }
}

function Start-R5([string]$exe, [string[]]$argv, [hashtable]$envs) {
    $psi = [Diagnostics.ProcessStartInfo]::new((Join-Path $Root $exe))
    $psi.WorkingDirectory = $Root
    $psi.UseShellExecute = $false
    # Windows PowerShell 5.1 (.NET Framework) has no ArgumentList; quote only what needs it.
    $psi.Arguments = ($argv | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
    $psi.EnvironmentVariables['VPROJECT'] = '1'
    $psi.EnvironmentVariables['FROM_R5F_LAUNCHER'] = '1'
    foreach ($k in $envs.Keys) { $psi.EnvironmentVariables[$k] = $envs[$k] }
    Write-Host "[hsd_launch] $exe $($argv -join ' ')"
    [Diagnostics.Process]::Start($psi)
}

function Exec-Args([string[]]$cfgs) { $out = @(); foreach ($c in $cfgs) { $out += '+exec', $c }; $out }

Stop-R5
if ($Stop) { return }
Wait-PortFree $Port 5000

$dev = '-devsdk', '-dev', '+net_usesocketsforloopback', '1', '+script_show_output', '2', '+script_show_warning', '2'
$evName = 'Local\r5f-host-' + [guid]::NewGuid().ToString('N')
$ev = [Threading.EventWaitHandle]::new($false, [Threading.EventResetMode]::ManualReset, $evName)

$dArgs = @('-dedicated', '-port', "$Port", '+sv_allowSendTableTransmitToClients', '1', '+stringtable_compress', '1') + $dev
if ($Offline) { $dArgs += '-offline', '+sv_onlineAuthEnable', '0' }
$dArgs += '+spire_host_visibility', '0', '+sv_cheats', '1'
$dArgs += Exec-Args $DediExec
if ($Run) { $dArgs += '+hsd_md_run', "$Run" }
$dArgs += '+launchplaylist', $Playlist, '+map', $Map, '+sv_modPolicy', '0'
$dArgs += $DediExtra
$dedi = Start-R5 'r5apex_ds.exe' $dArgs @{ R5F_HOST_READY = $evName }

$t0 = Get-Date
while (-not $ev.WaitOne(500)) {
    if ($dedi.HasExited) { throw "dedi exited early, code $($dedi.ExitCode)" }
    if (((Get-Date) - $t0).TotalSeconds -gt $HostReadyTimeoutSec) { throw "dedi not ready after $HostReadyTimeoutSec s" }
}
Write-Host ("[hsd_launch] dedi ready after {0:N1} s (pid {1})" -f ((Get-Date) - $t0).TotalSeconds, $dedi.Id)

$cArgs = @('-nodiscord', '-allowmultiple') + $dev
if ($Offline) { $cArgs += '-offline', '+cl_onlineAuthEnable', '0' }
$cArgs += '+timeout_during_load', '600', '-language', 'english'
$cArgs += Exec-Args $ClientExec
if ($Run) { $cArgs += '+hsd_md_run', "$Run" }
$cArgs += $ClientExtra
$cArgs += '+miles_language', 'english', '-windowed', '-width', "$Width", '-height', "$Height", '+connect', "127.0.0.1:$Port"
$client = Start-R5 $ClientExe $cArgs @{}

[pscustomobject]@{ dedi_pid = $dedi.Id; client_pid = $client.Id; playlist = $Playlist; map = $Map; run = $Run; started = $t0.ToString('s') }
