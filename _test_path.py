"""临时调试脚本：打印 EXE 环境信息"""
import sys
import os

print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'NOT SET')}")
print(f"cwd: {os.getcwd()}")
print()
print("sys.path:")
for i, p in enumerate(sys.path):
    print(f"  [{i}] {p}")
print()
# 尝试 import markitdown
try:
    from markitdown import MarkItDown
    md = MarkItDown()
    print("markitdown OK, methods:", [m for m in dir(md) if not m.startswith('_')])
except ImportError as e:
    print(f"markitdown ImportError: {e}")
except Exception as e:
    print(f"markitdown Error: {e}")
