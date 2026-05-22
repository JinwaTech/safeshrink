@echo off
REM SafeShrink Nuitka 全量编译
REM 双击运行，约20-30分钟完成
REM 编译完成后运行 run_analysis.bat 查看结果

echo ============================================================
echo SafeShrink Nuitka 全量编译
echo ============================================================
echo 预计耗时：20-30 分钟
echo 输出目录：nuitka313_out\main_window_v2.dist\SafeShrink.exe
echo 日志：C:\Users\26112\Desktop\nuitka_stdout.txt
echo ============================================================
echo.

cd /d C:\Users\26112\Desktop\SafeShrink

REM 清理旧的编译产物
if exist nuitka313_out (
    echo 清理旧编译产物...
    rmdir /s /q nuitka313_out
)

REM 开始编译
"C:\Users\26112\AppData\Local\Programs\Python\Python313\python.exe" -m nuitka --standalone --follow-imports --plugin-enable=pyside6 --windows-console-mode=disable --output-filename=SafeShrink.exe --output-dir=nuitka313_out --assume-yes-for-downloads main_window_v2.py

echo.
echo ============================================================
echo 编译完成！
echo ============================================================
echo 运行 run_analysis.bat 查看结果
pause
