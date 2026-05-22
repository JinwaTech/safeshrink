"""
Post-build 修复脚本
将 PyInstaller 遗漏的包手动复制到 dist/_internal/
"""
import os
import shutil
from pathlib import Path

DIST_ROOT = Path(__file__).parent / "dist" / "SafeShrink" / "_internal"
VENV_SITE = Path(__file__).parent / ".venv312" / "Lib" / "site-packages"

packages = [
    "markitdown",
    "pymupdf",
    "pypdfium2",
    "pypdfium2_raw",
    "charset_normalizer",
    "idna",
    "requests",
    "urllib3",
    "certifi",
    "tqdm",
    "platformdirs",
    "pdfplumber",
    "python-docx",
    "lxml",
    "openpyxl",
    "pptx",
]

for pkg in packages:
    src = VENV_SITE / pkg
    dst = DIST_ROOT / pkg
    if src.exists() and src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  OK: {pkg}")
    else:
        # 尝试单个文件包
        src_file = VENV_SITE / f"{pkg}.py"
        if src_file.exists():
            dst_file = DIST_ROOT / f"{pkg}.py"
            shutil.copy2(src_file, dst_file)
            print(f"  OK: {pkg} (file)")
        else:
            print(f" SKIP: {pkg} (not found in venv)")

print("\nDone.")
