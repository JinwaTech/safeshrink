# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

with open("settings_tab.py", encoding="utf-8") as f:
    lines = f.readlines()

# Check scene_tip and scene_group in settings_tab
print("=== settings_tab.py — scene_tip / scene_group / 适用场景 ===")
for i, line in enumerate(lines):
    if 'scene_tip' in line or 'scene_group' in line or '适用场景' in line:
        print(f"L{i+1}: {line.rstrip()}")

# Check update_language for scene_group
print("\n=== settings_tab.py update_language — scene section ===")
in_method = False
for i, line in enumerate(lines):
    if "def update_language" in line:
        in_method = True
        start = i
    if in_method and ('scene' in line.lower() or '适用' in line or '场景' in line):
        print(f"L{i+1}: {line.rstrip()}")

# Check sanitize_tab for gov_label/med_label creation
print("\n=== sanitize_tab.py — gov_label / med_label ===")
with open("sanitize_tab.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if 'gov_label' in line or 'med_label' in line:
            print(f"L{i+1}: {line.rstrip()}")
