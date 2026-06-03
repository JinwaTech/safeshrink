# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

with open("sanitize_tab.py", encoding="utf-8") as f:
    lines = f.readlines()

# Check around L227 for context
print("=== L225-235 (title = QLabel) ===")
for i in range(224, min(235, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

# Check for "选择场景" or scene_tip in sanitize_tab
print("\n=== '选择场景' in sanitize_tab ===")
for i, line in enumerate(lines):
    if '选择场景' in line or 'scene_tip' in line:
        print(f"L{i+1}: {line.rstrip()}")

# Check update_language method for what's missing
print("\n=== update_language — current content (L2639-2730) ===")
for i in range(2638, min(2730, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")
