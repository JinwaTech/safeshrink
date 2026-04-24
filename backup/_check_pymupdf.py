# -*- coding: utf-8 -*-
"""检查 PyMuPDF 是否被移除"""
import os
import sys

dist_path = 'dist/SafeShrink/_internal'

if os.path.exists(dist_path):
    # 搜索 fitz/pymupdf 相关文件
    found = []
    for root, dirs, files in os.walk(dist_path):
        for f in files:
            if 'fitz' in f.lower() or 'pymupdf' in f.lower() or 'mupdf' in f.lower():
                found.append(os.path.join(root, f))
    
    if found:
        print('发现 PyMuPDF 相关文件:')
        for f in found:
            print(f'  {f}')
    else:
        print('未发现 PyMuPDF 相关文件 - OK')
    
    # 检查是否有 pypdf
    pypdf_found = []
    for root, dirs, files in os.walk(dist_path):
        for f in files:
            if 'pypdf' in f.lower():
                pypdf_found.append(os.path.join(root, f))
    
    if pypdf_found:
        print('发现 pypdf 相关文件 - OK')
    else:
        print('未发现 pypdf 相关文件 - WARN')
else:
    print(f'dist 路径不存在: {dist_path}')
