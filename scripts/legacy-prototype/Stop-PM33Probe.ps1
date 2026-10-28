[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

foreach ($name in @('TMapSvr','TLoginSvr','TWorldSvr','TControlSvr')) {
    $binary = (Resolve-Path (Join-Path $PSScriptRoot "build-probe\$name\$name.localdb.exe")).Path
    Get-CimInstance Win32_Process -Filter "name='$name.localdb.exe'" |
        Where-Object ExecutablePath -eq $binary |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
            Write-Output "Stopped isolated $name PID $($_.ProcessId)"
        }
}
