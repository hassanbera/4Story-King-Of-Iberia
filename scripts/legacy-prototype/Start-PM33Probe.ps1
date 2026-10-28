[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

$instance = 'PM33Probe20261027'
$localdb = 'C:\Program Files\Microsoft SQL Server\150\Tools\Binn\SqlLocalDB.exe'
if (-not (Test-Path -LiteralPath $localdb)) {
    $localdb = (Get-Command SqlLocalDB.exe -ErrorAction Stop).Source
}
& $localdb start $instance | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'LocalDB instance did not start.' }

$definitions = @(
    @{ Name = 'TControlSvr'; Port = 17442 },
    @{ Name = 'TWorldSvr'; Port = 14422 },
    @{ Name = 'TLoginSvr'; Port = 15336 },
    @{ Name = 'TMapSvr'; Port = 11225 }
)

foreach ($item in $definitions) {
    $name = $item.Name
    $binary = (Resolve-Path (Join-Path $PSScriptRoot "build-probe\$name\$name.localdb.exe")).Path
    $processes = @(Get-CimInstance Win32_Process -Filter "name='$name.localdb.exe'" |
        Where-Object ExecutablePath -eq $binary)
    if ($processes.Count -gt 1) { throw "Multiple probe processes: $name" }
    if ($processes.Count -eq 0) {
        $process = Start-Process -FilePath $binary -WorkingDirectory (Split-Path $binary) -WindowStyle Hidden -PassThru
        Write-Output "Started isolated $name PID $($process.Id)"
    }
    $deadline = (Get-Date).AddSeconds(35)
    do {
        $listener = @(Get-NetTCPConnection -LocalPort $item.Port -State Listen -ErrorAction SilentlyContinue |
            Where-Object LocalAddress -eq '127.0.0.1')
        if ($listener.Count -eq 1) { break }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    if ($listener.Count -ne 1) { throw "Probe did not listen: $name port $($item.Port)" }
}

& (Join-Path $PSScriptRoot 'Check-PM33Probe.ps1')
