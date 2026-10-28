[CmdletBinding()]
param([switch]$Rollback)
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot
$package=Join-Path $repo 'runtime\soldier-caelen'
$manifest=Get-Content (Join-Path $package 'manifest.json') -Raw | ConvertFrom-Json
$local=Get-Content (Join-Path $repo 'runtime\local-game.json') -Raw | ConvertFrom-Json
$serverRoot=Split-Path $local.ServerStartScript
$map=Join-Path $serverRoot 'build-probe\TMapSvr\TMapSvr.localdb.exe'
$candidate=Join-Path $repo 'build\server\TMapSvr\TMapSvr.localdb.exe'
if(Get-Process TClient -ErrorAction SilentlyContinue){throw 'Close the game normally first.'}
if($manifest.id -ne 32700){throw 'Unexpected soldier package.'}
$expectedChart=Join-Path $local.GameDirectory 'Tcd\TMon.tcd'
if($manifest.chartPath -ne $expectedChart){throw 'Wrong game chart target.'}
function Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash}
if((Hash (Join-Path $package 'TMon.before.tcd')) -ne $manifest.beforeSha256){throw 'Chart backup changed.'}
if((Hash (Join-Path $package 'TMon.candidate.tcd')) -ne $manifest.candidateSha256){throw 'Chart candidate changed.'}
if(-not $Rollback -and (Hash $expectedChart) -ne $manifest.beforeSha256){throw 'Installed chart changed since preparation.'}
if($Rollback -and (Hash $expectedChart) -ne $manifest.candidateSha256){throw 'Installed chart changed since installation.'}
if(-not $Rollback -and (Test-Path (Join-Path $package 'installed.json'))){throw 'Already installed; do not overwrite rollback evidence.'}
& (Join-Path $serverRoot 'Stop-PM33Probe.ps1')
foreach($port in @(17442,14422,15336,11225)){
    if(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue){throw "Port still active: $port"}
}
Add-Type -AssemblyName System.Data
$connection=[System.Data.SqlClient.SqlConnection]::new('Server=(localdb)\PM33Probe20261027;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True')
$connection.Open()
function Sql([string]$text){$cmd=$connection.CreateCommand();$cmd.CommandText=$text;$cmd.CommandTimeout=180;[void]$cmd.ExecuteNonQuery()}
$remove=@'
SET XACT_ABORT ON;
BEGIN TRANSACTION;
DELETE dbo.TMAPMONCHART WHERE wSpawnID=32700 AND wMonID=32700;
DELETE dbo.TSPAWNPATHCHART WHERE wSpawnID=32700;
DELETE dbo.TMONSPAWNCHART WHERE wID=32700;
DELETE dbo.TMONSTERCHART WHERE wID=32700 AND szName='Caelen';
COMMIT;
'@
try{
    if($Rollback){
        $installed=Get-Content (Join-Path $package 'installed.json') -Raw | ConvertFrom-Json
        if((Hash $map) -ne $installed.mapAfter){throw 'Map binary changed since install.'}
        if((Hash (Join-Path $package 'TMapSvr.before.exe')) -ne $installed.mapBefore){throw 'Map backup changed.'}
        Sql $remove
        Copy-Item -LiteralPath (Join-Path $package 'TMon.before.tcd') -Destination $expectedChart
        Copy-Item -LiteralPath (Join-Path $package 'TMapSvr.before.exe') -Destination $map
        Move-Item -LiteralPath (Join-Path $package 'installed.json') -Destination (Join-Path $package ('rolled-back-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.json'))
    }else{
        $backup=Join-Path $package ('TGAME-before-soldier-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.bak')
        $escaped=$backup.Replace("'","''")
        Sql "BACKUP DATABASE [TGAME_GSP] TO DISK=N'$escaped' WITH COPY_ONLY,CHECKSUM,INIT; RESTORE VERIFYONLY FROM DISK=N'$escaped' WITH CHECKSUM;"
        Copy-Item -LiteralPath $map -Destination (Join-Path $package 'TMapSvr.before.exe')
        $mapBefore=Hash $map
        $changed=$false
        try{
            Sql (Get-Content (Join-Path $package 'install.sql') -Raw)
            $changed=$true
            Copy-Item -LiteralPath (Join-Path $package 'TMon.candidate.tcd') -Destination $expectedChart
            Copy-Item -LiteralPath $candidate -Destination $map
            if((Hash $expectedChart) -ne $manifest.candidateSha256){throw 'Installed chart hash mismatch.'}
            if((Hash $map) -ne (Hash $candidate)){throw 'Installed map hash mismatch.'}
            @{installedAt=(Get-Date).ToString('o');mapBefore=$mapBefore;mapAfter=(Hash $map);databaseBackup=$backup;chartAfter=$manifest.candidateSha256} |
                ConvertTo-Json | Set-Content (Join-Path $package 'installed.json')
        }catch{
            if($changed){Sql $remove}
            Copy-Item -LiteralPath (Join-Path $package 'TMon.before.tcd') -Destination $expectedChart
            Copy-Item -LiteralPath (Join-Path $package 'TMapSvr.before.exe') -Destination $map
            throw
        }
    }
}finally{$connection.Close()}
& $local.ServerStartScript
