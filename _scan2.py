# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

# Check settings_tab.update_language
print("=" * 60)
print("settings_tab.py — update_language method")
print("=" * 60)
with open("settings_tab.py", encoding="utf-8") as f:
    lines = f.readlines()
in_method = False
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
        start = i
    if in_method:
        print(f"L{i+1}: {line.rstrip()}")
        if i > start + 3:
            break

# Check slim_tab.update_language for img_info
print("\n" + "=" * 60)
print("slim_tab.py — update_language img_info section")
print("=" * 60)
with open("slim_tab.py", encoding="utf-8") as f:
    lines = f.readlines()
in_method = False
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
        start = i
    if in_method and "img_info" in line.lower():
        # Print context around this line
        for j in range(max(0, i-2), min(len(lines), i+5)):
            print(f"L{j+1}: {lines[j].rstrip()}")
        print("---")

# Check batch_tab.update_language for subtitle
print("\n" + "=" * 60)
print("batch_tab.py — update_language method (first 40 lines)")
print("=" * 60)
with open("batch_tab.py", encoding="utf-8") as f:
    lines = f.readlines()
in_method = False
count = 0
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
        start = i
    if in_method:
        print(f"L{i+1}: {line.rstrip()}")
        count += 1
        if count > 40:
            break

# Check sanitize_tab.update_language
print("\n" + "=" * 60)
print("sanitize_tab.py — update_language method (first 60 lines)")
print("=" * 60)
with open("sanitize_tab.py", encoding="utf-8") as f:
    lines = f.readlines()
in_method = False
count = 0
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
        start = i
    if in_method:
        print(f"L{i+1}: {line.rstrip()}")
        count += 1
        if count > 60:
            break

# Check main_window apply_language
print("\n" + "=" * 60)
print("main_window_v2.py — apply_language method")
print("=" * 60)
with open("main_window_v2.py", encoding="utf-8") as f:
    lines = f.readlines()
in_method = False
count = 0
for i, line in enumerate(lines):
    if "def apply_language" in line:
        in_method = True
        start = i
    if in_method:
        print(f"L{i+1}: {line.rstrip()}")
        count += 1
        if count > 50:
            break
