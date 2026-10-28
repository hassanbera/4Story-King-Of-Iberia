[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (Get-Process TClient -ErrorAction SilentlyContinue) { throw 'Close the game normally before restoring the client.' }
$runtime = Join-Path $repo 'runtime'
$manifest = Get-Content -LiteralPath (Join-Path $runtime 'client-install.json') -Raw | ConvertFrom-Json
$backup = (Resolve-Path -LiteralPath $manifest.Backup).Path
$backupRoot = [IO.Path]::GetFullPath((Join-Path $runtime 'client-backups')) + '\'
if (-not $backup.StartsWith($backupRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Backup path is outside the client backup directory.' }
if ((Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash -ne $manifest.PreviousSha256) { throw 'Backup hash mismatch.' }
if ((Get-FileHash -LiteralPath $manifest.Target -Algorithm SHA256).Hash -ne $manifest.CandidateSha256) { throw 'Target changed since installation; refusing to overwrite it.' }
Copy-Item -LiteralPath $backup -Destination $manifest.Target -Force
$configPath = Join-Path $runtime 'local-game.json'
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$config.Mode = 'legacy'
$config.ExpectedClientSha256 = $manifest.PreviousSha256
$config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
Write-Output 'Previous client restored. Server and database unchanged.'

