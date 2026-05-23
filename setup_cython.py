from setuptools import setup
from Cython.Build import cythonize
import os

# 要编译的所有模块（包含 batch_tab.py 等修改的文件）
modules = [
    "safe_shrink.py",
    "safe_shrink_gui.py",
    "batch_processor.py",
    "batch_tab.py",
    "format_to_ssd.py",
    "sanitize_ssd.py",
    "slim_tab.py",
    "sanitize_tab.py",
    "ssd_embed_images.py",
    "file_status.py",
    "_ooxml_to_ssd.py",
]

# 检查文件存在
for m in modules:
    if not os.path.exists(m):
        print(f"WARNING: {m} not found, skipping")
        modules.remove(m)

setup(
    ext_modules=cythonize(
        modules,
        compiler_directives={'language_level': "3"},
        annotate=False,
    )
)
