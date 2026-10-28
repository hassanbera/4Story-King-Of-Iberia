[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$GameDirectory,
    [Parameter(Mandatory=$true)][string]$ServerStartScript,
    [Parameter(Mandatory=$true)][string]$LegacyLaunchScript
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (Get-Process TClient -ErrorAction SilentlyContinue) { throw 'Close the game normally before installing the client candidate.' }
$game = (Resolve-Path -LiteralPath $GameDirectory).Path
$candidate = (Resolve-Path -LiteralPath (Join-Path $repo 'build\client-local\TClient.exe')).Path
$target = Join-Path $game 'TClient.exe'
if (-not (Test-Path -LiteralPath $target)) { throw 'Existing TClient.exe not found; refusing a new installation.' }
$startScript = (Resolve-Path -LiteralPath $ServerStartScript).Path
$legacyScript = (Resolve-Path -LiteralPath $LegacyLaunchScript).Path
$runtime = Join-Path $repo 'runtime'
$manifestPath = Join-Path $runtime 'client-install.json'
$previousManifest = if (Test-Path -LiteralPath $manifestPath) { Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json } else { $null }
$backup = Join-Path $runtime ('client-backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backup -ErrorAction Stop | Out-Null
$oldHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
$newHash = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
$backupExe = Join-Path $backup 'TClient.exe'
Copy-Item -LiteralPath $target -Destination $backupExe
if ((Get-FileHash -LiteralPath $backupExe -Algorithm SHA256).Hash -ne $oldHash) { throw 'Client backup verification failed.' }
$baselineBackup = $backupExe
$baselineHash = $oldHash
if ($previousManifest -and $previousManifest.Target -eq $target -and $previousManifest.CandidateSha256 -eq $oldHash) {
    if ((Get-FileHash -LiteralPath $previousManifest.Backup -Algorithm SHA256).Hash -ne $previousManifest.PreviousSha256) { throw 'Original baseline backup hash mismatch.' }
    $baselineBackup = $previousManifest.Backup
    $baselineHash = $previousManifest.PreviousSha256
}
$manifest = @{Target=$target;Backup=$baselineBackup;PreviousSha256=$baselineHash;ReplacedClientBackup=$backupExe;CandidateSha256=$newHash;CreatedAt=(Get-Date -Format o)}
$manifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Copy-Item -LiteralPath $candidate -Destination $target -Force
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $newHash) { throw 'Installed client hash mismatch.' }
@{Mode='source';GameDirectory=$game;ServerStartScript=$startScript;LegacyLaunchScript=$legacyScript;ExpectedClientSha256=$newHash;LoginPort=15336} |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtime 'local-game.json') -Encoding UTF8
Write-Output 'Source client installed with a verified backup. Existing game data and databases preserved.'

