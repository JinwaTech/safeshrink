# -*- coding: utf-8 -*-
"""测试批量处理 PDF"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from safe_shrink import read_file, DocSanitizer
from format_to_ssd import convert_to_ssd_v2

pdf_path = r'C:\Users\26112\Desktop\SafeShrink脱敏测试文档.pdf'

print('=== 测试 PDF 读取 ===')
try:
    text = read_file(pdf_path)
    print(f'读取成功，长度: {len(text)}')
    print(f'内容预览: {text[:200]}...')
except Exception as e:
    print(f'读取失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试 SSD 转换 ===')
try:
    result = convert_to_ssd_v2(pdf_path)
    print(f'转换成功，长度: {len(result)}')
    print(f'内容预览: {result[:200]}...')
except Exception as e:
    print(f'转换失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试脱敏 ===')
try:
    text = read_file(pdf_path)
    sanitizer = DocSanitizer()
    result = sanitizer.sanitize(text)
    print(f'脱敏成功')
    print(f'统计: {result["stats"]}')
    print(f'结果长度: {len(result["result"])}')
except Exception as e:
    print(f'脱敏失败: {e}')
    import traceback
    traceback.print_exc()
