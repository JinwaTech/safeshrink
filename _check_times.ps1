Get-ChildItem 'C:\Users\26112\Desktop\SafeShrink' -Directory | Where-Object { $_.Name -like 'nuitka*' } | ForEach-Object {
    $info = Get-Item $_.FullName
    [PSCustomObject]@{
        Name = $info.Name
        Created = $info.CreationTime.ToString('yyyy-MM-dd HH:mm')
    }
} | Sort-Object Created | Format-Table -AutoSize
