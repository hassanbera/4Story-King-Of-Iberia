[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidateRange(32600,32629)][int]$FirstId,
  [Parameter(Mandatory)][ValidateRange(1,30)][int]$Count
)
$ErrorActionPreference='Stop'
if($FirstId+$Count-1 -gt 32629){throw 'Resident range exceeds 32629.'}
if(Get-Process -Name TClient -ErrorAction SilentlyContinue){throw 'Close TClient before importing residents.'}
if(Get-NetTCPConnection -State Listen -LocalPort 17442,14422,15336,11225 -ErrorAction SilentlyContinue){
  throw 'Stop the four isolated PM33 services before importing residents.'
}
Add-Type -AssemblyName System.Data
$source=[System.Data.SqlClient.SqlConnection]::new('Server=lpc:localhost;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True;Application Name=PM33 ambient read source')
$target=[System.Data.SqlClient.SqlConnection]::new('Server=(localdb)\PM33Probe20261027;Database=TGAME_GSP;Integrated Security=True;Encrypt=False;TrustServerCertificate=True;Application Name=PM33 ambient isolated target')
$tables=@(
  @{Name='TMONSTERCHART'; Key='wID'; PerResident=1},
  @{Name='TMONSPAWNCHART'; Key='wID'; PerResident=1},
  @{Name='TMAPMONCHART'; Key='wSpawnID'; PerResident=1},
  @{Name='TSPAWNPATHCHART'; Key='wSpawnID'; PerResident=4}
)
function Read-Table([System.Data.SqlClient.SqlConnection]$connection,[string]$sql){
  $command=$connection.CreateCommand();$command.CommandText=$sql;$command.CommandTimeout=120
  $adapter=[System.Data.SqlClient.SqlDataAdapter]::new($command)
  $table=[System.Data.DataTable]::new();[void]$adapter.Fill($table)
  return ,$table
}
function Run-Sql([System.Data.SqlClient.SqlConnection]$connection,[string]$sql,[System.Data.SqlClient.SqlTransaction]$transaction=$null){
  $command=$connection.CreateCommand();$command.CommandText=$sql;$command.CommandTimeout=300
  if($transaction){$command.Transaction=$transaction}
  return $command.ExecuteNonQuery()
}
function Count-Rows([System.Data.SqlClient.SqlConnection]$connection,[string]$name,[string]$key,[int]$first,[int]$last,[System.Data.SqlClient.SqlTransaction]$transaction=$null){
  $command=$connection.CreateCommand();$command.CommandText="SELECT COUNT(*) FROM dbo.[$name] WHERE [$key] BETWEEN $first AND $last"
  if($transaction){$command.Transaction=$transaction}
  return [int]$command.ExecuteScalar()
}
try{
  $source.Open();$target.Open()
  $last=$FirstId+$Count-1
  $data=@{}
  foreach($spec in $tables){
    $name=$spec.Name;$key=$spec.Key
    $schema="SELECT c.column_id,c.name,ty.name AS type,c.max_length,c.is_nullable,c.is_identity FROM sys.columns c JOIN sys.types ty ON ty.user_type_id=c.user_type_id WHERE c.object_id=OBJECT_ID('dbo.$name') ORDER BY c.column_id"
    $a=Read-Table $source $schema;$b=Read-Table $target $schema
    if($a.Rows.Count -ne $b.Rows.Count){throw "Schema column count differs: $name"}
    for($i=0;$i -lt $a.Rows.Count;$i++){
      foreach($field in @('column_id','name','type','max_length','is_nullable','is_identity')){
        if([string]$a.Rows[$i][$field] -ne [string]$b.Rows[$i][$field]){throw "Schema differs: $name/$field/$i"}
      }
    }
    if((Count-Rows $target $name $key $FirstId $last) -ne 0){throw "Target range already occupied: $name"}
    $rows=Read-Table $source "SELECT * FROM dbo.[$name] WHERE [$key] BETWEEN $FirstId AND $last"
    $wanted=$Count*$spec.PerResident
    if($rows.Rows.Count -ne $wanted){throw "Source row count differs: $name wanted=$wanted got=$($rows.Rows.Count)"}
    $data[$name]=$rows
  }

  $backupDir=Join-Path $PSScriptRoot 'backups'
  New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
  $backup=Join-Path $backupDir ("TGAME_PM33_before_residents_$FirstId`_$last`_"+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.bak')
  if(Test-Path -LiteralPath $backup){throw "Backup already exists: $backup"}
  $literal="N'"+$backup.Replace("'","''")+"'"
  [void](Run-Sql $target "BACKUP DATABASE [TGAME_GSP] TO DISK=$literal WITH COPY_ONLY,CHECKSUM,INIT")
  [void](Run-Sql $target "RESTORE VERIFYONLY FROM DISK=$literal WITH CHECKSUM")

  $transaction=$target.BeginTransaction()
  try{
    foreach($spec in $tables){
      $name=$spec.Name;$rows=$data[$name]
      $bulk=[System.Data.SqlClient.SqlBulkCopy]::new($target,[System.Data.SqlClient.SqlBulkCopyOptions]::CheckConstraints,$transaction)
      try{
        $bulk.DestinationTableName="dbo.[$name]"
        foreach($column in $rows.Columns){[void]$bulk.ColumnMappings.Add($column.ColumnName,$column.ColumnName)}
        $bulk.WriteToServer($rows)
      }finally{$bulk.Close()}
    }
    [void](Run-Sql $target "UPDATE dbo.TMONSPAWNCHART SET bRoamType=5 WHERE wID BETWEEN $FirstId AND $last" $transaction)
    foreach($spec in $tables){
      $name=$spec.Name;$wanted=$Count*$spec.PerResident
      $actual=Count-Rows $target $name $spec.Key $FirstId $last $transaction
      if($actual -ne $wanted){throw "Inserted row count differs: $name wanted=$wanted got=$actual"}
    }
    $transaction.Commit()
  }catch{$transaction.Rollback();throw}
  Write-Output "Imported $Count residents: $FirstId-$last into isolated PM33 LocalDB only"
  Write-Output "Verified backup: $backup"
}finally{$source.Dispose();$target.Dispose()}
