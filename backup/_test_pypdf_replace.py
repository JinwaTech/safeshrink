# -*- coding: utf-8 -*-
"""测试 PyMuPDF 替换为 pypdf"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from safe_shrink_gui import clean_pdf_metadata
from pypdf import PdfWriter
import os

# 创建一个带元数据的测试 PDF
writer = PdfWriter()
writer.add_blank_page(width=612, height=792)
writer.add_metadata({'/Title': 'Test Document', '/Author': 'Test Author', '/Producer': 'Test Producer'})

with open('test_metadata.pdf', 'wb') as f:
    writer.write(f)

print('测试 PDF 已创建')

# 测试清理元数据
result = clean_pdf_metadata('test_metadata.pdf')
print(f'结果: success={result["success"]}')

if result['success']:
    print('PDF 元数据清理成功')
    print(f'输出: {result.get("output_path")}')
    print(f'跳过: {result.get("skipped")}')
else:
    print(f'失败: {result.get("error")}')

# 清理
if os.path.exists('test_metadata.pdf'):
    os.remove('test_metadata.pdf')
print('测试文件已清理')
