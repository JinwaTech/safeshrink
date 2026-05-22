@echo off
echo Checking disk space...
powershell -Command "(Get-PSDrive C).Free / 1GB | ForEach-Object { '{0:N1} GB free' -f $_ }"
echo.
echo Downloading VS 2022 Build Tools (~30MB bootstrapper)...
powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vs_buildtools.exe' -OutFile 'C:\temp\vs_buildtools.exe' -UseBasicParsing"
echo Download done. Check C:\temp\vs_buildtools.exe
echo DONE