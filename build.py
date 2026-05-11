# -*- coding: utf-8 -*-
import os, shutil, subprocess, sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_DIR, 'main_window_v2.spec')
DIST_NEW = os.path.join(PROJECT_DIR, 'dist', 'SafeShrink')  # PyInstaller 输出一致目录名
EXE_PATH = os.path.join(DIST_NEW, 'SafeShrink.exe')

# 带 _DEBUG 标记的源文件列表（打包时自动切为 False，打包后恢复 True）
DEBUG_FILES = ['slim_tab.py', 'sanitize_tab.py']

def kill_residual_processes():
    """强制终止残留的 SafeShrink 进程，避免 EXE 被锁"""
    print('[0/4] Killing residual SafeShrink processes...')
    result = subprocess.run(
        ['taskkill', '/F', '/IM', 'SafeShrink.exe', '/T'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print('[OK] Residual processes killed')
    else:
        # taskkill 返回 128/1 表示没找到进程，不算错误
        print('[OK] No residual processes')
    return True

def clean():
    for d in ['build', 'dist']:
        p = os.path.join(PROJECT_DIR, d)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
                print(f'[OK] Cleaned {d}/')
            except PermissionError:
                print(f'[WARN] {d}/ locked, PyInstaller will overwrite')

def build():
    print('[1/2] Building with spec...')
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', '-m', 'PyInstaller', '--noconfirm', SPEC_FILE],
        cwd=PROJECT_DIR, capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or 'Build complete' not in output:
        print(f'[ERROR] Build failed (exit {result.returncode})')
        for line in output.strip().split('\n')[-10:]:
            print(f'  {line}')
        return False
    print('[OK] Build complete')
    return True

def verify():
    print('[2/3] Verifying EXE...')
    if os.path.exists(EXE_PATH):
        sz = os.path.getsize(EXE_PATH) / 1e6
        print(f'[OK] EXE: {sz:.2f} MB')
        print(f'[OK] Path: {EXE_PATH}')
        # Check assets
        assets = os.path.join(DIST_NEW, '_internal', 'assets')
        if os.path.exists(assets):
            items = os.listdir(assets)
            print(f'[OK] Assets: {len(items)} files ({", ".join(items)})')
        return True
    else:
        print(f'[ERROR] EXE not found: {EXE_PATH}')
        return False

def sync_to_desktop():
    """自动复制 EXE 到桌面路径（双保险）"""
    print('[3/3] Syncing to desktop path...')
    desktop_exe = r'C:\Users\26112\Desktop\SafeShrink\dist\SafeShrink\SafeShrink.exe'
    desktop_dir = os.path.dirname(desktop_exe)
    try:
        os.makedirs(desktop_dir, exist_ok=True)
        shutil.copy2(EXE_PATH, desktop_exe)
        print(f'[OK] Copied to: {desktop_exe}')
        return True
    except Exception as e:
        print(f'[WARN] Sync failed: {e}')
        return False

def toggle_debug(to_release):
    """将 _DEBUG 在 True/False 之间切换（release 打包前改 False，打包后改回 True）。"""
    old = '_DEBUG = True' if to_release else '_DEBUG = False'
    new = '_DEBUG = False' if to_release else '_DEBUG = True'
    changed = 0
    for fname in DEBUG_FILES:
        fpath = os.path.join(PROJECT_DIR, fname)
        if not os.path.exists(fpath):
            print(f'[WARN] {fname} not found, skip')
            continue
        content = open(fpath, encoding='utf-8').read()
        if old not in content:
            print(f'[INFO] {fname}: no {old} to replace, skip')
            continue
        content = content.replace(old, new)
        open(fpath, 'w', encoding='utf-8').write(content)
        changed += 1
        print(f'[OK] {fname}: {old} -> {new}')
    return changed

if __name__ == '__main__':
    os.chdir(PROJECT_DIR)
    print('=' * 50)
    print('  SafeShrink Build Tool (Fixed)')
    print('=' * 50)
    # 1. 终止残留进程
    kill_residual_processes()
    # 2. 切换到 release 模式（_DEBUG = False）
    print('[1/4] Setting _DEBUG = False for release build...')
    toggle_debug(to_release=True)
    try:
        clean()
        if not build():
            sys.exit(1)
        if not verify():
            sys.exit(1)
        sync_to_desktop()
    finally:
        # 无论成败，恢复开发模式（_DEBUG = True）
        print('[4/4] Restoring _DEBUG = True for development...')
        toggle_debug(to_release=False)
    print()
    print('[OK] Done!')
