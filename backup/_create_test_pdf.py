# -*- coding: utf-8 -*-
"""创建包含敏感信息的测试 PDF"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
try:
    pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
    font_name = 'SimHei'
    print('使用中文字体: SimHei')
except Exception as e:
    font_name = 'Helvetica'
    print(f'中文字体不可用，使用: {font_name} ({e})')

pdf_path = 'test_sensitive_info.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# 标题
c.setFont(font_name, 16)
c.drawString(50, height - 50, 'SafeShrink Test Document - Confidential')

# 内容
c.setFont(font_name, 10)
content = [
    '',
    'This file contains sensitive information for testing:',
    '',
    '1. Phone Numbers:',
    '   - Zhang San: 13812345678',
    '   - Li Si: 13987654321',
    '   - Wang Wu: 15012345678',
    '',
    '2. ID Card Numbers:',
    '   - 110101199001011234',
    '   - 440304199205156789',
    '   - 320102198812120987',
    '',
    '3. Bank Card Numbers:',
    '   - ICBC: 6222021234567890123',
    '   - CCB: 6217001234567891234',
    '   - ABC: 6228481234567895678',
    '',
    '4. Email Addresses:',
    '   - work@example.com',
    '   - personal@company.org',
    '',
    '5. IP Addresses:',
    '   - Internal: 192.168.1.100',
    '   - Public: 202.96.134.133',
    '',
    '6. License Plates:',
    '   - Yue B12345',
    '   - Jing A88888',
    '',
    '7. Contract Numbers:',
    '   - HT-2026-001',
    '   - CONTRACT-ABC-123',
    '',
    '8. Passport Numbers:',
    '   - G12345678',
    '   - E87654321',
    '',
    'End of test document.',
]

y = height - 80
for line in content:
    c.drawString(50, y, line)
    y -= 15
    if y < 50:
        c.showPage()
        c.setFont(font_name, 10)
        y = height - 50

c.save()

file_size = os.path.getsize(pdf_path)
print(f'测试 PDF 已创建: {pdf_path}')
print(f'文件大小: {file_size} bytes')
print(f'文件路径: {os.path.abspath(pdf_path)}')
