# -*- coding: utf-8 -*-
"""Fix slim_tab.py Phase 4: careful QMessageBox wrapping"""
import sys, shutil, re
sys.stdout.reconfigure(encoding='utf-8')

# Restore from Phase 3 backup
shutil.copy('versions/phase3/slim_tab_0531_2205_before.py', 'slim_tab.py')

with open('slim_tab.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Re-apply Phase 3 fixes
helper = '''

    def _get_mode_key(self):
        idx = self.format_combo.currentIndex() if hasattr(self, 'format_combo') else 0
        return ['standard', 'aggressive', 'deep_clean', 'ssd'][idx] if idx < 4 else 'standard'

    def _get_img_mode_key(self):
        idx = self.img_format_combo.currentIndex() if hasattr(self, 'img_format_combo') else 0
        return ['image_compress', 'ssd'][idx] if idx < 2 else 'image_compress'
'''

pos = content.find('    def update_language(self, lang):')
end = content.find('\n    def ', pos + 10)
next_method = content.find('\n    def ', end)
content = content[:next_method] + helper + content[next_method:]

content = content.replace('mode = self.format_combo.currentText()', 'mode = self._get_mode_key()')
content = content.replace('mode = self.img_format_combo.currentText()', 'mode = self._get_img_mode_key()')
content = content.replace('mode == "deep_clean"', 'mode == "deep_clean"')  # already correct from Phase 3

# Fix Chinese mode comparisons
mode_map = [
    ('\u6df1\u5ea6\u6e05\u7406', 'deep_clean'),  # 深度清理
    ('\u6fc0\u8fdb\u538b\u7f29', 'aggressive'),   # 激进压缩
    ('\u6807\u51c6\u538b\u7f29', 'standard'),     # 标准压缩
    ('\u8f6c\u6362\u4e3aSSD', 'ssd'),             # 转换为SSD
]
for cn, en in mode_map:
    content = content.replace(f'mode == "{cn}"', f'mode == "{en}"')
    content = content.replace(f"mode == '{cn}'", f"mode == '{en}'")

# Phase 4: Fix QMessageBox titles
for qtype in ['warning', 'information', 'critical', 'question']:
    pattern = rf'(QMessageBox\.{qtype}\(self,\s*)("[^"]*[\u4e00-\u9fff][^"]*")'
    content = re.sub(pattern, rf'\1_(\2)', content)

# Fix body for single-line QMessageBox
for qtype in ['warning', 'information', 'critical', 'question']:
    pattern = rf'(QMessageBox\.{qtype}\(self,\s*_\("[^"]*"\),\s*)("[^"]*[\u4e00-\u9fff][^"]*")'
    content = re.sub(pattern, rf'\1_(\2)', content)

# Fix multi-line QMessageBox bodies
lines = content.split('\n')
result = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Match: QMessageBox.xxx(self, _("title"),
    qm = re.match(r'(\s*)QMessageBox\.(warning|information|critical|question)\(self,\s*_\("[^"]*"\),\s*$', line)
    if qm:
        indent = qm.group(1)
        result.append(line)
        i += 1
        
        # Collect body lines
        body_lines = []
        paren_depth = 1
        while i < len(lines):
            bl = lines[i]
            for ch in bl:
                if ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
            body_lines.append(bl)
            i += 1
            if paren_depth <= 0:
                break
        
        # Check if body needs wrapping
        body_text = '\n'.join(body_lines)
        if re.search(r'[\u4e00-\u9fff]', body_text):
            # Check if already wrapped
            if '_(' not in body_text:
                # Wrap: add _( before first string, add ) after last )
                if body_lines:
                    first = body_lines[0]
                    m = re.match(r'(\s*)', first)
                    bi = m.group(1) if m else ''
                    body_lines[0] = bi + '_(' + first.lstrip()
                    last = body_lines[-1].rstrip()
                    if last.endswith(')'):
                        body_lines[-1] = last[:-1] + '))'
        
        result.extend(body_lines)
    else:
        result.append(line)
        i += 1

content = '\n'.join(result)

with open('slim_tab.py', 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
try:
    py_compile.compile('slim_tab.py', doraise=True)
    print('Syntax OK')
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}')
