$base = 'C:\Users\26112\Desktop\SafeShrink'
Get-ChildItem $base -Directory | Where-Object { $_.Name -like 'nuitka*' } | ForEach-Object {
    $distPath = Join-Path $_.FullName 'main_window_v2.dist'
    if (Test-Path $distPath) {
        $files = Get-ChildItem $distPath -Recurse -File -ErrorAction SilentlyContinue
        $total = ($files | Measure-Object -Property Length -Sum).Sum
        [PSCustomObject]@{
            Name = $_.Name
            DistFiles = $files.Count
            DistMB = [math]::Round($total/1MB, 1)
        }
    } else {
        [PSCustomObject]@{
            Name = $_.Name
            DistFiles = 0
            DistMB = 0
        }
    }
} | Sort-Object Name | Format-Table -AutoSize
