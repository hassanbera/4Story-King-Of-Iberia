[CmdletBinding()]
param([switch]$Rollback)
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot
$local=Get-Content (Join-Path $repo 'runtime\local-game.json') -Raw | ConvertFrom-Json
$config=Get-Content (Join-Path $repo 'world\yesode\soldiers\caelen.json') -Raw | ConvertFrom-Json
$root=Split-Path $local.ServerStartScript
$map=(Resolve-Path (Join-Path $root 'build-probe\TMapSvr\TMapSvr.localdb.exe')).Path
$candidate=Join-Path $repo 'build\server\TMapSvr\TMapSvr.localdb.exe'
$package=Join-Path $repo 'runtime\soldier-caelen'
$record=Join-Path $package 'route-update.json'
if(Get-Process TClient -ErrorAction SilentlyContinue){throw 'Close game normally before updating its route.'}
if($config.id -ne 32700 -or $config.waypoints.Count -lt 5 -or $config.waypoints.Count -gt 190){throw 'Invalid route configuration.'}
function Hash([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
function Number($n){([double]$n).ToString('R',[Globalization.CultureInfo]::InvariantCulture)}
function RouteSql($points,$spawn){
    $rows=@();$i=1
    foreach($point in $points){$rows+="(32700,$i,$(Number $point[0]),$(Number $point[1]),$(Number $point[2]),0,0)";$i++}
    "SET XACT_ABORT ON; BEGIN TRANSACTION; IF NOT EXISTS(SELECT 1 FROM dbo.TMONSTERCHART WHERE wID=32700 AND szName='Caelen') THROW 51000,'Wrong soldier target',1; UPDATE dbo.TMONSPAWNCHART SET fPosX=$(Number $spawn[0]),fPosY=$(Number $spawn[1]),fPosZ=$(Number $spawn[2]),bRoamType=6 WHERE wID=32700; IF @@ROWCOUNT<>1 THROW 51000,'Spawn missing',1; DELETE dbo.TSPAWNPATHCHART WHERE wSpawnID=32700; INSERT dbo.TSPAWNPATHCHART(wSpawnID,bPathID,fPosX,fPosY,fPosZ,bProb,fRadius) VALUES $($rows -join ','); COMMIT;"
}
if($Rollback){
    $state=Get-Content $record -Raw | ConvertFrom-Json
    if((Hash $map) -ne $state.mapAfter -or (Hash $state.mapBackup) -ne $state.mapBefore){throw 'Map changed after route installation.'}
}else{
    if(Test-Path $record){throw 'Route update already applied; preserve its rollback package.'}
    for($i=1;$i -lt $config.waypoints.Count;$i++){
        $a=$config.waypoints[$i-1];$b=$config.waypoints[$i]
        if([Math]::Sqrt([Math]::Pow($a[0]-$b[0],2)+[Math]::Pow($a[2]-$b[2],2)) -gt 10 -or [Math]::Abs($a[1]-$b[1]) -gt 5){throw 'Do not bridge a recording gap.'}
    }
    if(-not (Test-Path $candidate)){throw 'Build candidate missing.'}
    $installed=Get-Content (Join-Path $package 'installed.json') -Raw | ConvertFrom-Json
    if((Hash $map) -ne $installed.mapAfter){throw 'Installed Map does not match reviewed version.'}
}
# Keep Login/World alive: only Map needs the new route and source binary.
Get-CimInstance Win32_Process -Filter "name='TMapSvr.localdb.exe'" | Where-Object ExecutablePath -eq $map | ForEach-Object {Stop-Process -Id $_.ProcessId -ErrorAction Stop}
if(Get-NetTCPConnection -State Listen -LocalPort 11225 -ErrorAction SilentlyContinue){throw 'Map port still active.'}
Add-Type -AssemblyName System.Data
$db=[System.Data.SqlClient.SqlConnection]::new('Server=(localdb)\PM33Probe20261027;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True')
$db.Open()
function Execute([string]$sql){$cmd=$db.CreateCommand();$cmd.CommandText=$sql;$cmd.CommandTimeout=180;[void]$cmd.ExecuteNonQuery()}
function ReadTable([string]$sql){$cmd=$db.CreateCommand();$cmd.CommandText=$sql;$table=[System.Data.DataTable]::new();[void]([System.Data.SqlClient.SqlDataAdapter]::new($cmd)).Fill($table);return ,$table}
try{
    if($Rollback){
        Execute (Get-Content $state.rollbackSql -Raw)
        Copy-Item -LiteralPath $state.mapBackup -Destination $map
        $installed=Get-Content (Join-Path $package 'installed.json') -Raw | ConvertFrom-Json
        $installed.mapAfter=$state.mapBefore
        $installed | ConvertTo-Json | Set-Content (Join-Path $package 'installed.json')
        Rename-Item -LiteralPath $record -NewName ('route-rolled-back-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.json')
    }else{
        $backup=Join-Path $package ('TGAME-before-recorded-route-'+(Get-Date -Format yyyyMMdd-HHmmss)+'.bak')
        $escaped=$backup.Replace("'","''")
        Execute "BACKUP DATABASE TGAME_GSP TO DISK=N'$escaped' WITH COPY_ONLY,CHECKSUM,INIT; RESTORE VERIFYONLY FROM DISK=N'$escaped' WITH CHECKSUM;"
        $oldPoints=ReadTable 'SELECT fPosX,fPosY,fPosZ FROM dbo.TSPAWNPATHCHART WHERE wSpawnID=32700 ORDER BY bPathID'
        $oldSpawn=ReadTable 'SELECT fPosX,fPosY,fPosZ FROM dbo.TMONSPAWNCHART WHERE wID=32700'
        if($oldSpawn.Rows.Count -ne 1 -or $oldPoints.Rows.Count -lt 1){throw 'Existing route not found.'}
        $points=@();foreach($r in $oldPoints.Rows){$points+=,@([double]$r.fPosX,[double]$r.fPosY,[double]$r.fPosZ)}
        $r=$oldSpawn.Rows[0]
        $undo=RouteSql $points @([double]$r.fPosX,[double]$r.fPosY,[double]$r.fPosZ)
        $rollbackSql=Join-Path $package 'route-before.sql'
        $undo | Set-Content $rollbackSql
        $mapBackup=Join-Path $package 'TMapSvr.before-recorded-route.exe'
        Copy-Item -LiteralPath $map -Destination $mapBackup
        $before=Hash $map
        try{
            Execute (RouteSql $config.waypoints $config.waypoints[0])
            Copy-Item -LiteralPath $candidate -Destination $map
            if((Hash $map) -ne (Hash $candidate)){throw 'Map installation hash mismatch.'}
            @{mapBefore=$before;mapAfter=(Hash $map);mapBackup=$mapBackup;rollbackSql=$rollbackSql;databaseBackup=$backup;waypointCount=$config.waypoints.Count;installedAt=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content $record
            $installed.mapAfter=Hash $map
            $installed | ConvertTo-Json | Set-Content (Join-Path $package 'installed.json')
        }catch{
            Execute $undo
            Copy-Item -LiteralPath $mapBackup -Destination $map
            throw
        }
    }
}finally{$db.Close()}
& $local.ServerStartScript
