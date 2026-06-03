# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

# settings_tab update_language — full method
print("=" * 60)
print("settings_tab.py — FULL update_language")
print("=" * 60)
with open("settings_tab.py", encoding="utf-8") as f:
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
        if count > 80:
            break

# sanitize_tab — group1_label creation
print("\n" + "=" * 60)
print("sanitize_tab.py — group1_label / group_title creation")
print("=" * 60)
with open("sanitize_tab.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "group1_label" in line or "group_title" in line or '个人敏感' in line or "personal sensitive" in line.lower():
        print(f"L{i+1}: {line.rstrip()}")

# Check L220-240 in sanitize_tab.py
print("\nsanitize_tab.py L220-260:")
for i in range(219, min(260, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

# Check L550-590
print("\nsanitize_tab.py L550-590:")
for i in range(549, min(590, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

# Check what "个人敏感信息" translates to
print("\n" + "=" * 60)
print("translations.py — 个人敏感信息 entries")
print("=" * 60)
with open("translations.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if '个人敏感' in line or 'personal sensitive' in line.lower() or 'Personal Sensitive' in line:
            print(f"L{i+1}: {line.rstrip()}")
