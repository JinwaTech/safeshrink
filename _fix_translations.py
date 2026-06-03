# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

with open("translations.py", encoding="utf-8") as f:
    lines = f.readlines()

# Find the last line of the zh_to_en dict (before the closing })
# Add missing keys: '调试' and '深色模式' (without emoji)
insertions = []
for i, line in enumerate(lines):
    # Find a good insertion point — near similar keys
    if "'日志级别:'" in line and "'Log Level:'" in line:
        insertions.append((i+1, "    '调试': 'Debug',\n"))
    if "'🌙  深色模式'" in line:
        # Add non-emoji version after this line
        insertions.append((i+1, "    '深色模式': 'Dark Mode',\n"))

# Insert in reverse order to preserve line numbers
for pos, text in sorted(insertions, reverse=True):
    lines.insert(pos, text)

with open("translations.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("translations.py updated: added '调试' and '深色模式' keys")

# Verify
with open("translations.py", encoding="utf-8") as f:
    content = f.read()
for kw in ['调试', '深色模式']:
    found = [f'L{i+1}: {l.strip()}' for i, l in enumerate(content.split('\n')) if kw in l]
    for l in found:
        print(f"  {l}")
