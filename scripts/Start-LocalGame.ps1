[CmdletBinding()]
param([ValidateSet('normal','survey')][string]$Mode='normal')
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$config = Get-Content -LiteralPath (Join-Path $repo 'runtime\local-game.json') -Raw | ConvertFrom-Json
$env:KOI_SURVEY_SPEED = ''
$env:KOI_SURVEY_DIR = ''
& $config.ServerStartScript
if (-not $?) { throw 'Existing server startup failed.' }
if (Get-Process TClient -ErrorAction SilentlyContinue) { throw 'Game client already running.' }
$client = Join-Path $config.GameDirectory 'TClient.exe'
if ((Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash -ne $config.ExpectedClientSha256) { throw 'Client hash changed; review the local installation before launch.' }
if ($config.Mode -eq 'legacy') {
    if($Mode -eq 'survey'){throw 'Survey mode needs the source client.'}
    & $config.LegacyLaunchScript
    return
}
if($Mode -eq 'survey'){
    $session=Join-Path $repo ('runtime\surveys\'+(Get-Date -Format yyyyMMdd-HHmmss)+'-'+[Guid]::NewGuid().ToString('N').Substring(0,6))
    New-Item -ItemType Directory -Path $session -ErrorAction Stop | Out-Null
    @{formatVersion=1;startedAt=(Get-Date).ToString('o');clientSha256=$config.ExpectedClientSha256;maximumSpeedMultiplier=3;scope='current local player; map 0 ground candidates';speedToggle='Ctrl+Shift+F8';recordToggle='Ctrl+Shift+F9'} |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $session 'session.json') -Encoding UTF8
    $env:KOI_SURVEY_SPEED = '3'
    $env:KOI_SURVEY_DIR = $session
    Write-Output "Local mapping session: $session"
}
$env:DXVK_FILTER_DEVICE_NAME = 'NVIDIA GeForce GTX 1650 Ti'
$env:DXVK_HUD = 'fps,frametimes,devinfo'
$env:DXVK_LOG_PATH = Join-Path $repo 'runtime'
Start-Process -FilePath $client -ArgumentList @('127.0.0.1',[string]$config.LoginPort,'1') -WorkingDirectory $config.GameDirectory | Out-Null
Write-Output 'King Of Iberia source client launch requested.'
