# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

with open("sanitize_tab.py", encoding="utf-8") as f:
    lines = f.readlines()

# Check update_language beyond L2730
print("=== update_language L2730-end ===")
for i in range(2729, min(2780, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

# Check for "适用场景" in sanitize_tab
print("\n=== '适用场景' in sanitize_tab ===")
for i, line in enumerate(lines):
    if '适用场景' in line:
        print(f"L{i+1}: {line.rstrip()}")

# Check gov_label / med_label in update_language
print("\n=== gov_label / med_label in update_language ===")
in_method = False
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
    if in_method and ('gov_label' in line or 'med_label' in line):
        print(f"L{i+1}: {line.rstrip()}")

# Check file_label creation
print("\n=== file_label creation ===")
for i, line in enumerate(lines):
    if 'file_label' in line and ('QLabel' in line or 'setText' in line or 'self.' in line):
        print(f"L{i+1}: {line.rstrip()}")
