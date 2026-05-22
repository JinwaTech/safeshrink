@echo off
echo Installing VS 2022 C++ Build Tools (corrected parameters)...
"C:\temp\vs_buildtools.exe" --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --quiet --norestart --wait
echo Exit code: %ERRORLEVEL%