Get-ChildItem 'C:\Users\26112\Desktop\SafeShrink' -Directory | Where-Object { $_.Name -like 'nuitka*' } | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue
    $total = ($files | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{
        Name = $_.Name
        Files = $files.Count
        MB = [math]::Round($total/1MB, 0)
    }
} | Format-Table -AutoSize
