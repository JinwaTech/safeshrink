@echo off
REM SafeShrink Nuitka 编译结果分析脚本
REM 双击运行，等待编译完成（约20-30分钟），然后自动分析结果
REM 编译命令已在 run_compile.bat

echo ============================================================
echo SafeShrink Nuitka 编译结果分析
echo ============================================================
echo.

cd /d C:\Users\26112\Desktop\SafeShrink

REM 检查 EXE 是否已生成
if exist "nuitka313_out\main_window_v2.dist\SafeShrink.exe" (
    echo [OK] EXE 已生成
    goto analyze
) else (
    echo [等待] EXE 还未生成，编译可能还在进行中...
    echo 请确保编译命令已在运行，然后再次运行本脚本
    goto end
)

:analyze
echo.
echo 运行分析脚本...
python313 build_selective.py

if exist "nuitka313_out\link_command_safeshrink.txt" (
    echo.
    echo [完成] 链接命令已保存
    type nuitka313_out\link_command_safeshrink.txt
)

if exist "nuitka313_out\safeshink_o_files.txt" (
    echo.
    echo [完成] SafeShrink .o 列表已保存
)

:end
echo.
echo ============================================================
echo 完成
echo ============================================================
pause
