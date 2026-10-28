[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

$services = @(& (Join-Path $PSScriptRoot 'Check-PM33Probe.ps1'))
if ($services.Count -ne 4) { throw "Expected four source-built game services; found $($services.Count)." }

$graphLog = Join-Path $PSScriptRoot 'build-probe\TMapSvr\AmbientRoutes.load.log'
$graphCsv = Join-Path $PSScriptRoot 'build-probe\TMapSvr\AmbientRoutes.csv'
if (-not (Test-Path -LiteralPath $graphCsv)) { throw 'AmbientRoutes.csv is missing from the Map service directory.' }
$expected = 'graph=1 map=0 nodes=26 edges=30 connected=yes'
if (-not (Select-String -LiteralPath $graphCsv -Pattern '^R,32600,1$' -Quiet) -or
    -not (Select-String -LiteralPath $graphCsv -Pattern '^R,32629,1$' -Quiet)) {
    throw 'The Kuznez route file does not bind the first and last residents to graph 1.'
}

$connection = [System.Data.SqlClient.SqlConnection]::new(
    'Server=(localdb)\PM33Probe20261027;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True;Application Name=Yesode read-only verification')
try {
    $connection.Open()
    $command = $connection.CreateCommand()
    $command.CommandText = @'
SELECT
  (SELECT COUNT(*) FROM dbo.TMONSTERCHART WHERE wID BETWEEN 32600 AND 32629),
  (SELECT COUNT(*) FROM dbo.TMONSPAWNCHART WHERE wID BETWEEN 32600 AND 32629),
  (SELECT COUNT(*) FROM dbo.TMAPMONCHART WHERE wSpawnID BETWEEN 32600 AND 32629),
  (SELECT COUNT(*) FROM dbo.TSPAWNPATHCHART WHERE wSpawnID BETWEEN 32600 AND 32629),
  (SELECT COUNT(*) FROM dbo.TMONSPAWNCHART WHERE wID BETWEEN 32600 AND 32629 AND bRoamType = 5)
'@
    $reader = $command.ExecuteReader()
    if (-not $reader.Read()) { throw 'Resident count query returned no row.' }
    $counts = @(for ($i = 0; $i -lt 5; $i++) { [int]$reader.GetValue($i) })
    $reader.Close()
} finally {
    $connection.Dispose()
}
if (($counts -join ',') -ne '30,30,30,120,30') {
    throw "Unexpected resident counts: $($counts -join ',')"
}

$smoke = Join-Path $PSScriptRoot 'build-ambient\TMapSvr\GraphSmoke.exe'
if (-not (Test-Path -LiteralPath $smoke)) { throw 'GraphSmoke.exe is missing.' }
Push-Location (Join-Path $PSScriptRoot 'ambient')
try {
    $graphResult = & $smoke
    if ($LASTEXITCODE -ne 0) { throw "Route graph smoke check failed: $graphResult" }
} finally {
    Pop-Location
}

$mapBinary = (Resolve-Path (Join-Path $PSScriptRoot 'build-probe\TMapSvr\TMapSvr.localdb.exe')).Path
$mapProcess = @(Get-CimInstance Win32_Process -Filter "name='TMapSvr.localdb.exe'" |
    Where-Object ExecutablePath -eq $mapBinary)
if ($mapProcess.Count -ne 1) { throw 'Source-built Map process identity changed during verification.' }
$mapStart = (Get-Process -Id $mapProcess[0].ProcessId).StartTime
$loadedThisRun = (Test-Path -LiteralPath $graphLog) -and
    ((Get-Item -LiteralPath $graphLog).LastWriteTime -ge $mapStart.AddSeconds(-3)) -and
    (Select-String -LiteralPath $graphLog -Pattern ([regex]::Escape($expected)) -Quiet)

[pscustomobject]@{
    Services = $services.Count
    Residents = $counts[0]
    SpawnPoints = $counts[1]
    MapLinks = $counts[2]
    RouteRows = $counts[3]
    GraphRoam = $counts[4]
    RoutePairsChecked = 676
    GraphLoadedThisRun = [bool]$loadedThisRun
    VisualMovementVerified = $false
}
