"""PyInstaller runtime hook: 确保 _internal 目录在 sys.path 中"""
import sys
import os

if getattr(sys, 'frozen', False):
    # PyInstaller onedir 模式: _internal 在 EXE 同级目录
    exe_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(exe_dir, '_internal')
    if os.path.isdir(internal_dir) and internal_dir not in sys.path:
        sys.path.insert(0, internal_dir)
