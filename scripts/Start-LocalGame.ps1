[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$config = Get-Content -LiteralPath (Join-Path $repo 'runtime\local-game.json') -Raw | ConvertFrom-Json
& $config.ServerStartScript
if (-not $?) { throw 'Existing server startup failed.' }
if (Get-Process TClient -ErrorAction SilentlyContinue) { throw 'Game client already running.' }
$client = Join-Path $config.GameDirectory 'TClient.exe'
if ((Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash -ne $config.ExpectedClientSha256) { throw 'Client hash changed; review the local installation before launch.' }
if ($config.Mode -eq 'legacy') {
    & $config.LegacyLaunchScript
    return
}
$env:DXVK_FILTER_DEVICE_NAME = 'NVIDIA GeForce GTX 1650 Ti'
$env:DXVK_HUD = 'fps,frametimes,devinfo'
$env:DXVK_LOG_PATH = Join-Path $repo 'runtime'
Start-Process -FilePath $client -ArgumentList @('127.0.0.1',[string]$config.LoginPort,'1') -WorkingDirectory $config.GameDirectory | Out-Null
Write-Output 'King Of Iberia source client launch requested.'
