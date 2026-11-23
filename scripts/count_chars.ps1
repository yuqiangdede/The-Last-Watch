param([string]$FilePath)
$txt = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
$count = ($txt.ToCharArray() | Where-Object { [int]$_ -ge 0x4e00 -and [int]$_ -le 0x9fff }).Count
Write-Output "$FilePath : $count Han characters"

