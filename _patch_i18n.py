"""Comprehensive i18n patch for slim_tab.py - fix all QMessageBox strings to be Chinese by default."""
import pathlib, re

SRC = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink\slim_tab.py')
txt = SRC.read_text(encoding='utf-8')
lines = txt.splitlines()

# Check for translation import
has_trans_import = 'from translations import get_translation' in txt
print(f'Translation import present: {has_trans_import}')

# Add import if missing
if not has_trans_import:
    last_imp = max(
        i for i, l in enumerate(lines)
        if l.startswith('from ') or l.startswith('import ')
    )
    lines.insert(last_imp + 1, 'from translations import get_translation')
    print(f'Inserted import after line {last_imp + 1}')

# Now patch QMessageBox strings
# Strategy: For hardcoded English strings in QMessageBox calls,
# wrap them with get_translation() using a lambda _
# and update the window title to Chinese

REPLACEMENTS = [
    # QMessageBox title "Done" -> "完成"
    ('QMessageBox.information(self, "Done",', 'QMessageBox.information(self, "完成",'),
    ('QMessageBox.information(self, "Done ",', 'QMessageBox.information(self, "完成",'),
    ('QMessageBox.critical(self, "Error",', 'QMessageBox.critical(self, "错误",'),
    ('QMessageBox.warning(self, "Warning",', 'QMessageBox.warning(self, "警告",'),
    ('QMessageBox.question(self, "Confirm",', 'QMessageBox.question(self, "确认",'),
    # Dialog button strings
    ('"Compression complete!\\n\\nOriginal:', '"压缩完成\\n\\n原文:'),
    ('"SSD conversion complete!\\n\\nChars:', '"SSD 转换完成\\n\\n字符数:'),
    ('"Done", "SSD conversion complete!', '"完成", "SSD 转换完成'),
    ('"Done", "Compression complete!', '"完成", "压缩完成'),
    ('"Error", "Conversion failed:', '"错误", "转换失败:'),
    ('"Error", "Compression failed:', '"错误", "压缩失败:'),
    ('"Error", "Processing failed:', '"错误", "处理失败:'),
    ('"Compression complete!\\n\\nOriginal: ~', None),  # mark for special handling
]

new_txt = txt

# Patch the translations import insertion point
if not has_trans_import:
    last_imp = max(
        i for i, l in enumerate(lines)
        if l.startswith('from ') or l.startswith('import ')
    )
    lines.insert(last_imp + 1, 'from translations import get_translation')

# Write the new slim_tab.py
SRC.write_text('\n'.join(lines), encoding='utf-8')
print('Written slim_tab.py with import injection')

# Now do targeted string replacements
txt2 = SRC.read_text(encoding='utf-8')

# Patch window titles
txt2 = txt2.replace('QMessageBox.information(self, "Done",', 'QMessageBox.information(self, "完成",')
txt2 = txt2.replace('QMessageBox.critical(self, "Error",', 'QMessageBox.critical(self, "错误",')
txt2 = txt2.replace('QMessageBox.warning(self, "Warning",', 'QMessageBox.warning(self, "警告",')
txt2 = txt2.replace('QMessageBox.question(self, "Confirm",', 'QMessageBox.question(self, "确认",')

# Fix the specific message strings (preserve variable interpolation)
# Line 496: SSD conversion
txt2 = txt2.replace(
    '"SSD conversion complete!\\n\\nChars: " + str(orig_len) + " -> " + str(new_len) + "\\n" + token_str)',
    '"SSD 转换完成\\n\\n原文字符: " + str(orig_len) + " → 压缩后: " + str(new_len) + "\\n" + token_str)'
)
# Line 579: depth clean SSD
txt2 = txt2.replace(
    '"SSD conversion complete!\\n\\nChars: " + str(orig_len) + " -> " + str(new_len) + "\\n" + token_str)',
    '"SSD 转换完成\\n\\n原文字符: " + str(orig_len) + " → 压缩后: " + str(new_len) + "\\n" + token_str)'
)
# Line 638: Compression complete
txt2 = txt2.replace(
    '"Compression complete!\\n\\nOriginal: ~" + str(round(orig_bytes / 1024, 1)) + " KB\\nCompressed: ~" + str(round(new_bytes / 1024, 1)) + " KB\\nRate: " + str(compress_rate) + "%")',
    '"压缩完成\\n\\n原文: ~" + str(round(orig_bytes / 1024, 1)) + " KB\\n压缩后: ~" + str(round(new_bytes / 1024, 1)) + " KB\\n压缩率: " + str(compress_rate) + "%")'
)

# Fix the _show_done_dialog function window title
txt2 = txt2.replace(
    'QMessageBox.information(self, "✅ 完成", "',
    'QMessageBox.information(self, "完成", "'
)
# Fix the QMessageBox with emoji title
txt2 = txt2.replace(
    'QMessageBox.information(self, "✅ 完成",',
    'QMessageBox.information(self, "完成",'
)

SRC.write_text(txt2, encoding='utf-8')
print('Applied string replacements')

# Verify
import py_compile
try:
    py_compile.compile(str(SRC), doraise=True)
    print('Syntax check PASSED')
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}')
