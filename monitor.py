#!/usr/bin/env python3
"""SafeShrink Nuitka 编译监控脚本"""
import os, time, subprocess, sys

BUILD_OUT = r"C:\Users\26112\Desktop\SafeShrink\nuitka313_out"
DIST_DIR = os.path.join(BUILD_OUT, "main_window_v2.dist")
BUILD_DIR = os.path.join(BUILD_OUT, "main_window_v2.build")
EXE_PATH = os.path.join(DIST_DIR, "SafeShrink.exe")

print("=" * 60)
print("SafeShrink Nuitka 编译监控")
print("修复版: --include-package=io + --windows-icon-from-ico")
print("=" * 60)

# 等待 Python 层级编译完成（build 目录开始增长）
print("\n[阶段1] 等待 Python 层级编译完成...")
while True:
    if not os.path.exists(BUILD_DIR):
        time.sleep(10)
        continue
    total_mb = 0
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            total_mb += os.path.getsize(os.path.join(root, f)) / 1024 / 1024
    t = time.strftime("%H:%M:%S")
    print(f"  {t}  build={total_mb:.0f}MB")
    if total_mb > 10:
        print(f"  -> C 编译阶段开始")
        break
    time.sleep(15)

# 监控 C 编译
print("\n[阶段2] 监控 C 编译进度...")
last_mb = 0
same_count = 0
start_time = time.time()
while True:
    if not os.path.exists(BUILD_DIR):
        print("  [中断] build 目录消失")
        break
    total_mb = 0
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            total_mb += os.path.getsize(os.path.join(root, f)) / 1024 / 1024
    elapsed_min = (time.time() - start_time) / 60
    t = time.strftime("%H:%M:%S")
    print(f"  {t}  build={total_mb:.0f}MB  elapsed={elapsed_min:.1f}min")

    if os.path.exists(EXE_PATH):
        exe_mb = os.path.getsize(EXE_PATH) / 1024 / 1024
        print(f"\n[完成] SafeShrink.exe 生成: {exe_mb:.1f} MB")
        break

    if total_mb == last_mb:
        same_count += 1
        if same_count >= 3 and elapsed_min > 5:
            print(f"  [警告] build 大小连续3次不变（{total_mb:.0f}MB）")
    else:
        same_count = 0
    last_mb = total_mb

    if elapsed_min > 90:
        print("  [超时] 超过90分钟")
        break
    time.sleep(60)

# 测试 EXE
print("\n[阶段3] 测试 EXE...")
if os.path.exists(EXE_PATH):
    try:
        proc = subprocess.Popen(
            [EXE_PATH],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=DIST_DIR,
            startupinfo=subprocess.STARTUPINFO()
        )
        time.sleep(6)
        if proc.poll() is None:
            proc.kill()
            print("  [OK] EXE 运行正常！")
        else:
            stderr = proc.stderr.read().decode("utf-8", errors="replace")
            print(f"  [崩溃] ExitCode: {proc.returncode}")
            print(f"  [错误] {stderr[:500]}")
    except Exception as e:
        print(f"  [失败] {e}")
else:
    print("  [失败] EXE 未生成")

print("\n" + "=" * 60)
print("完成")
print("=" * 60)