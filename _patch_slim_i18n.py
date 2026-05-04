"""Patch slim_tab.py to use get_translation() for all dialog strings."""
import pathlib, re

SRC = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink\slim_tab.py')
txt = SRC.read_text(encoding='utf-8')
lines = txt.splitlines()

# Find the import block at the top
new_lines = []
import_line_idx = None
for i, l in enumerate(lines):
    new_lines.append(l)
    if i < 5 and ('from settings_tab import' in l or 'import settings_tab' in l):
        import_line_idx = i

# Inject translation import after the import block
if import_line_idx is not None:
    # Find where the imports end
    pass

# Actually find the last import line
last_imp = 0
for i, l in enumerate(lines):
    if l.startswith('from ') or l.startswith('import '):
        last_imp = i

# Insert after last import
insert_after = last_imp
for i, l in enumerate(lines):
    if i <= insert_after:
        pass

# Build new content with import injected
result = []
for i, l in enumerate(lines):
    result.append(l)
    if i == last_imp and 'translations' not in txt:
        result.append('from translations import get_translation')

# Actually let's just check if the import is there
if 'from translations import get_translation' in txt:
    print('Translation import already present')
else:
    print('Need to add translation import')

# Now fix the specific QMessageBox lines (line numbers are 1-indexed)
fixes = {}
for i, l in enumerate(lines):
    # line i+1: original English QMessageBox
    if '"Done"' in l and 'QMessageBox' in l:
        # Find the exact string
        print(f'{i+1}: {l[:120]}')
