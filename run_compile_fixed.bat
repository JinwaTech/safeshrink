@echo off
REM SafeShrink Nuitka 修复版编译脚本
REM 修复：--include-package=io (修复Frozen io崩溃) + --windows-icon-from-ico (图标)
REM 预计耗时：40-50分钟

cd /d C:\Users\26112\Desktop\SafeShrink

echo 开始 Nuitka 编译 [%date% %time%]
echo ===============================================

"C:\Users\26112\AppData\Local\Programs\Python\Python313\python.exe" -m nuitka ^
  --standalone ^
  --follow-imports ^
  --plugin-enable=pyside6 ^
  --include-package=io ^
  --windows-icon-from-ico="C:\Users\26112\Desktop\SafeShrink\assets\icon06_light.ico" ^
  --windows-console-mode=disable ^
  --output-filename=SafeShrink.exe ^
  --output-dir=nuitka313_out ^
  --assume-yes-for-downloads ^
  main_window_v2.py

echo.
echo 编译完成 [%date% %time%]
echo ===============================================

REM 编译完成后检查 EXE
if exist "nuitka313_out\main_window_v2.dist\SafeShrink.exe" (
    for %%F in ("nuitka313_out\main_window_v2.dist\SafeShrink.exe") do echo EXE 大小: %%~zF 字节
    echo.
    echo 正在测试 EXE...
    powershell -c "Start-Process -FilePath 'nuitka313_out\main_window_v2.dist\SafeShrink.exe' -Wait -PassThru | Select-Object ExitCode"
) else (
    echo [错误] EXE 未生成
)

pause
