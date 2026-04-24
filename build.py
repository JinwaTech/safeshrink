# -*- coding: utf-8 -*-
"""
build.py - SafeShrink 一键打包脚本
用法: python build.py
"""

import subprocess
import shutil
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_DIR, 'main_window_v2.spec')
DIST_SRC = os.path.join(PROJECT_DIR, 'dist', 'main_window_v2')
DIST_DST = os.path.join(PROJECT_DIR, 'dist', 'SafeShrink')
EXE_DST = os.path.join(DIST_DST, 'SafeShrink.exe')


def clean():
    """清理旧的 build（dist 被占用时跳过，避免 PermissionError）"""
    for d in ['build', 'dist']:
        p = os.path.join(PROJECT_DIR, d)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
                print(f'[OK] 已清理 {d}/')
            except PermissionError:
                print(f'[WARN] {d}/ 被占用，跳过清理（PyInstaller 将覆盖）')


def build():
    """用 spec 文件打包"""
    print('[1/3] 开始打包 (使用 spec 文件)...')
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', '-m', 'PyInstaller', '--noconfirm', SPEC_FILE],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or 'Build complete' not in output:
        print(f'[ERROR] 打包失败! (exit code: {result.returncode})')
        lines = output.strip().split('\n')
        for line in lines[-10:]:
            print(f'  {line}')
        return False

    print('[OK] 打包完成')
    return True


def rename():
    """重命名输出目录和 EXE"""
    print('[2/3] 整理输出...')
    if not os.path.exists(DIST_SRC):
        print(f'[ERROR] 打包输出目录不存在: {DIST_SRC}')
        return False
    if os.path.exists(DIST_DST):
        try:
            shutil.rmtree(DIST_DST)
        except PermissionError:
            print(f'[WARN] {DIST_DST} 被占用，尝试覆盖...')
            # 直接复制，覆盖同名文件
            for root, dirs, files in os.walk(DIST_SRC):
                rel = os.path.relpath(root, DIST_SRC)
                dst_root = os.path.join(DIST_DST, rel)
                os.makedirs(dst_root, exist_ok=True)
                for f in files:
                    src_f = os.path.join(root, f)
                    dst_f = os.path.join(dst_root, f)
                    try:
                        shutil.copy2(src_f, dst_f)
                    except PermissionError:
                        print(f'[SKIP] 锁定: {f}')
            # 直接从 DIST_SRC 检查 EXE
            exe_old = os.path.join(DIST_SRC, 'SafeShrink.exe')
            if os.path.exists(exe_old):
                sz = os.path.getsize(exe_old) / 1e6
                print(f'[OK] EXE: {sz:.1f} MB')
                print(f'[OK] 路径: {exe_old}')
            return True
    shutil.copytree(DIST_SRC, DIST_DST)

    exe_old = os.path.join(DIST_DST, 'SafeShrink.exe')
    if os.path.exists(exe_old):
        os.rename(exe_old, EXE_DST)

    sz = os.path.getsize(EXE_DST) / 1e6
    print(f'[OK] EXE: {sz:.1f} MB')
    print(f'[OK] 路径: {EXE_DST}')
    return True


def verify():
    """验证 EXE 文件是否存在"""
    print('[3/3] 验证 EXE...')
    if os.path.exists(EXE_DST):
        print(f'[OK] EXE 文件存在: {EXE_DST}')
        return True
    else:
        print(f'[ERROR] EXE 文件未找到: {EXE_DST}')
        return False


if __name__ == '__main__':
    os.chdir(PROJECT_DIR)

    print('=' * 50)
    print('  SafeShrink Build Tool')
    print('=' * 50)

    clean()

    if not build():
        sys.exit(1)

    if not rename():
        sys.exit(1)

    if not verify():
        sys.exit(1)

    print()
    print('[OK] Build complete!')
    print(f'Output: {EXE_DST}')
