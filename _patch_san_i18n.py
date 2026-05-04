"""Patch sanitize_tab.py QMessageBox strings."""
import pathlib

SRC = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py')
txt = SRC.read_text(encoding='utf-8')

# Check import
has_trans = 'from translations import get_translation' in txt
print(f'Translation import: {has_trans}')

# Patch QMessageBox window titles and strings
txt = txt.replace('QMessageBox.information(self, "瀹屾垚"', 'QMessageBox.information(self, "完成"')
txt = txt.replace('QMessageBox.critical(self, "閿欒�",', 'QMessageBox.critical(self, "错误",')
txt = txt.replace('QMessageBox.warning(self, "���",', 'QMessageBox.warning(self, "警告",')
txt = txt.replace('QMessageBox.question(self, "���",', 'QMessageBox.question(self, "确认",')

# Fix specific strings (lines 761, 764, 1000, etc)
# Line 761: detected results
txt = txt.replace('"鍙舵敹鍒扮瓥姝⑩"', '"检测到敏感信息"')
# Line 764: no sensitive found
txt = txt.replace('"δ��⵽������Ϣ"', '"未检测到敏感信息"')
# Line 1000: sanitize done
txt = txt.replace('"鑴辨晱瀹屾垚锛�"', '"脱敏完成"')
# Line 1084: format conversion success
txt = txt.replace('"���ɹ�"', '"转换成功"')
# Line 1086: format conversion failed
txt = txt.replace('"���澶辫触"', '"转换失败"')

# Add import if missing
if not has_trans:
    lines = txt.splitlines()
    last_imp = max(i for i, l in enumerate(lines) if l.startswith('from ') or l.startswith('import '))
    lines.insert(last_imp + 1, 'from translations import get_translation')
    txt = '\n'.join(lines)

SRC.write_text(txt, encoding='utf-8')
print('Written sanitize_tab.py')

# Verify syntax
import py_compile
try:
    py_compile.compile(str(SRC), doraise=True)
    print('Syntax check PASSED')
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}')
