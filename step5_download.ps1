$ErrorActionPreference = 'Continue'
$outfile = 'C:\temp\vs_buildtools.exe'
$uri = 'https://aka.ms/vs/17/release/vs_buildtools.exe'

Write-Host '[1/2] Disk check:'
$free = (Get-PSDrive C).Free / 1GB
Write-Host \"  C: free {0:N1} GB\" -f $free

if ($free -lt 10) {
    Write-Host '[WARNING] Less than 10GB free, proceeding anyway'
}

Write-Host '[2/2] Downloading VS 2022 Build Tools bootstrapper...'
Write-Host '  URL: https://aka.ms/vs/17/release/vs_buildtools.exe'
Write-Host '  Dest: C:\\temp\\vs_buildtools.exe'

try {
    Invoke-WebRequest -Uri $uri -OutFile $outfile -UseBasicParsing -TimeoutSec 300
    $size = (Get-Item $outfile).Length / 1MB
    Write-Host \"[OK] Downloaded ($([math]::Round($size, 1)) MB)\"
} catch {
    Write-Host \"[FAIL] Download error: $_\"
    exit 1
}