# -*- coding: utf-8 -*-
import os, shutil, subprocess, sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_DIR, 'main_window_v2.spec')
DIST_NEW = os.path.join(PROJECT_DIR, 'dist', 'SafeShrink')  # PyInstaller 输出一致目录名
EXE_PATH = os.path.join(DIST_NEW, 'SafeShrink.exe')

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
    print('[2/2] Verifying EXE...')
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

if __name__ == '__main__':
    os.chdir(PROJECT_DIR)
    print('=' * 50)
    print('  SafeShrink Build Tool (Fixed)')
    print('=' * 50)
    clean()
    if not build():
        sys.exit(1)
    if not verify():
        sys.exit(1)
    print()
    print('[OK] Done!')
