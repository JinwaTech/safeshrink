# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

with open("sanitize_tab.py", encoding="utf-8") as f:
    content = f.read()

# Check scene_tip self attribute
print("=== scene_tip references ===")
for i, line in enumerate(content.split('\n')):
    if 'scene_tip' in line:
        print(f"L{i+1}: {line.rstrip()}")

# Check if sanitize_title already exists
print("\n=== sanitize_title references ===")
for i, line in enumerate(content.split('\n')):
    if 'sanitize_title' in line:
        print(f"L{i+1}: {line.rstrip()}")

# Check title = QLabel at L227
print("\n=== title = QLabel ===")
for i, line in enumerate(content.split('\n')):
    if 'title = QLabel' in line or 'title=QLabel' in line:
        print(f"L{i+1}: {line.rstrip()}")
