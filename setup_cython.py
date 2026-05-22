from setuptools import setup
from Cython.Build import cythonize
import os

# 要编译的核心模块
modules = [
    "safe_shrink.py",
    "batch_processor.py",
    "format_to_ssd.py",
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
