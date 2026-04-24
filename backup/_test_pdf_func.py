# -*- coding: utf-8 -*-
"""测试 PDF 读取和脱敏功能"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from safe_shrink import read_pdf_pypdf, read_pdf, DEPS, DocSanitizer

print('=== 依赖状态 ===')
for dep, available in DEPS.items():
    if dep in ['pypdf', 'pdfplumber', 'PIL']:
        print(f'{dep}: {available}')

print('\n=== 测试 PDF 读取 ===')
pdf_path = 'test_sensitive_info.pdf'

# 测试 pypdf 读取
print('使用 pypdf 读取...')
try:
    text = read_pdf_pypdf(pdf_path)
    print(f'pypdf 读取成功，提取 {len(text)} 字符')
    if text.strip():
        print(f'内容预览:\n{text[:500]}...')
    else:
        print('注意: 提取内容为空（空白页 PDF 无文本）')
except Exception as e:
    print(f'pypdf 读取失败: {e}')

# 测试通用 read_pdf
print('\n使用 read_pdf 读取...')
try:
    text = read_pdf(pdf_path)
    print(f'read_pdf 读取成功，提取 {len(text)} 字符')
except Exception as e:
    print(f'read_pdf 读取失败: {e}')

# 测试元数据清理
print('\n=== 测试 PDF 元数据清理 ===')
from safe_shrink_gui import clean_pdf_metadata

result = clean_pdf_metadata(pdf_path)
if result['success']:
    print('元数据清理成功')
    print(f'  输出: {result.get("output_path")}')
    print(f'  跳过: {result.get("skipped")}')
else:
    print(f'元数据清理失败: {result.get("error")}')

print('\n=== 测试脱敏功能 ===')
# 测试文本
test_text = '''
张三的手机号是 13812345678，身份证号是 110101199001011234。
李四的银行卡号是 6222021234567890123。
联系邮箱：work@example.com
内网IP：192.168.1.100
车牌号：粤B12345
'''

print('原始文本:')
print(test_text.strip())

# 测试脱敏
sanitizer = DocSanitizer()
result = sanitizer.sanitize(test_text)

print('\n脱敏结果:')
if isinstance(result, dict):
    print(f'  success: {result.get("success")}')
    sanitized_text = result.get("result", "")
    print(f'  result:\n{sanitized_text}')
    print(f'\n  stats: {result.get("stats")}')
else:
    print(f'  {result}')
