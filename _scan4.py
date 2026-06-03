# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

# 1. batch_tab — find subtitle QLabel
print("=== batch_tab.py — subtitle / folder_label / page_subtitle ===")
with open("batch_tab.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if any(kw in line for kw in ['subtitle', 'page_subtitle', 'folder_label', '批量处理多个文件', 'Batch process']):
            print(f"L{i+1}: {line.rstrip()}")

# 2. slim_tab — all img_info_label.setText calls
print("\n=== slim_tab.py — all img_info_label.setText ===")
with open("slim_tab.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if 'img_info_label' in line and 'setText' in line:
            print(f"L{i+1}: {line.rstrip()}")

# 3. sanitize_tab — scene_tip creation
print("\n=== sanitize_tab.py — scene_tip ===")
with open("sanitize_tab.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if 'scene_tip' in line:
            print(f"L{i+1}: {line.rstrip()}")

# 4. main_window — subtitle for batch tab
print("\n=== main_window_v2.py — subtitle / batch ===")
with open("main_window_v2.py", encoding="utf-8") as f:
    for i, line in enumerate(f.readlines()):
        if 'subtitle' in line.lower() or ('batch' in line.lower() and 'subtitle' in line.lower()):
            print(f"L{i+1}: {line.rstrip()}")
