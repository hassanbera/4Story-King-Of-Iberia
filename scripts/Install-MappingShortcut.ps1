[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$desktop=[Environment]::GetFolderPath('Desktop')
$target=Join-Path $desktop '4Story King Of Iberia - Haritalama.cmd'
$powershell=Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$content="@echo off`r`n`"$powershell`" -NoProfile -ExecutionPolicy Bypass -File `"$repo\scripts\Start-LocalGame.ps1`" -Mode survey`r`nif errorlevel 1 pause`r`n"
if((Test-Path -LiteralPath $target) -and (Get-Content -LiteralPath $target -Raw) -ne $content){throw 'A different mapping launcher already exists; review it first.'}
[IO.File]::WriteAllText($target,$content,[Text.UTF8Encoding]::new($false))
Write-Output $target
