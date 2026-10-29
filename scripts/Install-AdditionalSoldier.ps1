[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidatePattern('^[a-z][a-z0-9]{1,23}$')][string]$Name,[switch]$Rollback)
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot
$package=Join-Path $repo "runtime\soldier-$Name"
$manifest=Get-Content (Join-Path $package 'manifest.json') -Raw | ConvertFrom-Json
$local=Get-Content (Join-Path $repo 'runtime\local-game.json') -Raw | ConvertFrom-Json
$root=Split-Path $local.ServerStartScript
$map=(Resolve-Path (Join-Path $root 'build-probe\TMapSvr\TMapSvr.localdb.exe')).Path
$chart=Join-Path $local.GameDirectory 'Tcd\TMon.tcd'
$id=[int]$manifest.id
if($id -lt 32701 -or $id -gt 32767 -or $manifest.name.ToLowerInvariant() -ne $Name){throw 'Unexpected additional soldier package.'}
if($manifest.chartPath -ne $chart){throw 'Wrong client chart target.'}
if(Get-Process TClient -ErrorAction SilentlyContinue){throw 'Close game normally before changing its chart.'}
function Hash([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
if((Hash (Join-Path $package 'TMon.before.tcd')) -ne $manifest.beforeSha256 -or (Hash (Join-Path $package 'TMon.candidate.tcd')) -ne $manifest.candidateSha256){throw 'Prepared chart package changed.'}
if($Rollback){
    if(-not (Test-Path (Join-Path $package 'installed.json')) -or (Hash $chart) -ne $manifest.candidateSha256){throw 'Review newer chart edits before rollback.'}
}else{
    if(Test-Path (Join-Path $package 'installed.json')){throw 'Soldier already installed.'}
    if((Hash $chart) -ne $manifest.beforeSha256){throw 'Installed chart changed after preparation.'}
}
# New template loading needs only Map restart. Do not restart Login/World.
Get-CimInstance Win32_Process -Filter "name='TMapSvr.localdb.exe'" | Where-Object ExecutablePath -eq $map | ForEach-Object {Stop-Process -Id $_.ProcessId -ErrorAction Stop}
if(Get-NetTCPConnection -State Listen -LocalPort 11225 -ErrorAction SilentlyContinue){throw 'Map port remains active.'}
Add-Type -AssemblyName System.Data
$db=[System.Data.SqlClient.SqlConnection]::new('Server=(localdb)\PM33Probe20261027;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True')
$db.Open()
function Sql([string]$text){$cmd=$db.CreateCommand();$cmd.CommandText=$text;$cmd.CommandTimeout=180;[void]$cmd.ExecuteNonQuery()}
function Scalar([string]$text){$cmd=$db.CreateCommand();$cmd.CommandText=$text;$cmd.CommandTimeout=60;return $cmd.ExecuteScalar()}
function ProtectedProof {
    $parts=@()
    foreach($table in @(@('TMONSTERCHART','wID'),@('TMONSPAWNCHART','wID'),@('TMAPMONCHART','wSpawnID'),@('TSPAWNPATHCHART','wSpawnID'))){
        $parts+=Scalar "SELECT CONCAT(COUNT_BIG(*),':',COALESCE(CHECKSUM_AGG(BINARY_CHECKSUM(*)),0)) FROM dbo.$($table[0]) WHERE $($table[1])<>$id"
    }
    return $parts -join '|'
}
$undo="SET XACT_ABORT ON; BEGIN TRANSACTION; IF EXISTS(SELECT 1 FROM dbo.TMONSTERCHART WHERE wID=$id AND szName<>'$($manifest.name)') THROW 51000,'Soldier identity changed',1; DELETE dbo.TMAPMONCHART WHERE wSpawnID=$id AND wMonID=$id; DELETE dbo.TSPAWNPATHCHART WHERE wSpawnID=$id; DELETE dbo.TMONSPAWNCHART WHERE wID=$id; DELETE dbo.TMONSTERCHART WHERE wID=$id AND szName='$($manifest.name)'; COMMIT;"
try{
    $protected=ProtectedProof
    if($Rollback){
        Sql $undo
        Copy-Item -LiteralPath (Join-Path $package 'TMon.before.tcd') -Destination $chart
        if((Hash $chart) -ne $manifest.beforeSha256){throw 'Chart rollback hash mismatch.'}
        Rename-Item -LiteralPath (Join-Path $package 'installed.json') -NewName ('rolled-back-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.json')
    }else{
        $backup=Join-Path $package ('TGAME-before-'+$Name+'-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.bak')
        $escaped=$backup.Replace("'","''")
        Sql "BACKUP DATABASE TGAME_GSP TO DISK=N'$escaped' WITH COPY_ONLY,CHECKSUM,INIT; RESTORE VERIFYONLY FROM DISK=N'$escaped' WITH CHECKSUM;"
        $changed=$false
        try{
            Sql (Get-Content (Join-Path $package 'install.sql') -Raw)
            $changed=$true
            if((Scalar "SELECT COUNT(*) FROM dbo.TSPAWNPATHCHART WHERE wSpawnID=$id") -ne $manifest.waypointCount){throw 'Waypoint count mismatch.'}
            if((ProtectedProof) -ne $protected){throw 'Unrelated static rows changed.'}
            Copy-Item -LiteralPath (Join-Path $package 'TMon.candidate.tcd') -Destination $chart
            if((Hash $chart) -ne $manifest.candidateSha256){throw 'Installed chart hash mismatch.'}
            @{id=$id;name=$manifest.name;installedAt=(Get-Date).ToString('o');databaseBackup=$backup;protectedStaticRows=$protected;chartAfter=$manifest.candidateSha256;mapSha256=(Hash $map);waypointCount=$manifest.waypointCount} |
                ConvertTo-Json | Set-Content (Join-Path $package 'installed.json')
        }catch{
            if($changed){Sql $undo}
            Copy-Item -LiteralPath (Join-Path $package 'TMon.before.tcd') -Destination $chart
            throw
        }
    }
    if((ProtectedProof) -ne $protected){throw 'Unrelated static row proof changed.'}
}finally{$db.Close()}
& $local.ServerStartScript
