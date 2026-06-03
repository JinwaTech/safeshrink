# -*- coding: utf-8 -*-
"""Fix i18n issues — Round 4 (2026-06-01)"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

def fix_file(filename, fixes):
    """Apply (old, new) replacements to a file."""
    with open(filename, encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in fixes:
        if old not in content:
            print(f"  WARN: not found in {filename}: {old[:60]}...")
            continue
        content = content.replace(old, new, 1)
        print(f"  OK: {old[:50]}... -> {new[:50]}...")
    if content != original:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  => {filename} SAVED")
    else:
        print(f"  => {filename} NO CHANGES")

# ============================================================
# 1. sanitize_tab.py — 4 fixes
# ============================================================
print("\n=== sanitize_tab.py ===")
fix_file("sanitize_tab.py", [
    # Fix 1: title 局部变量 -> self.sanitize_title
    (
        '        title = QLabel("脱敏类型")\n\n        title.setStyleSheet("font-weight: 600; font-size: 14px;")\n\n        layout.addWidget(title)',
        '        self.sanitize_title = QLabel("脱敏类型")\n\n        self.sanitize_title.setStyleSheet("font-weight: 600; font-size: 14px;")\n\n        layout.addWidget(self.sanitize_title)'
    ),
])

# Fix 2: Add file_label, sanitize_title, gov_label, med_label to update_language
# Find the end of update_language method (after btn_browse line)
with open("sanitize_tab.py", encoding="utf-8") as f:
    content = f.read()

# Insert after the btn_browse update block
insert_after = """        if hasattr(self, 'btn_browse'):
            self.btn_browse.setText(_('选择文件...'))"""

insert_block = """

        # ★ i18n fix4: file_label, sanitize_title, gov_label, med_label
        if hasattr(self, 'file_label'):
            if '未选择' in self.file_label.text() or 'No file' in self.file_label.text():
                self.file_label.setText(_('未选择文件'))
        if hasattr(self, 'sanitize_title'):
            self.sanitize_title.setText(_('脱敏类型'))
        if hasattr(self, 'gov_label'):
            self.gov_label.setText(_('党政公文:'))
        if hasattr(self, 'med_label'):
            self.med_label.setText(_('医疗档案:'))"""

if insert_after in content and '★ i18n fix4' not in content:
    content = content.replace(insert_after, insert_after + insert_block)
    with open("sanitize_tab.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("  OK: Added file_label/sanitize_title/gov_label/med_label to update_language")
else:
    print("  WARN: insert point not found or already patched")

# ============================================================
# 2. slim_tab.py — Fix dynamic img_info_label text
# ============================================================
print("\n=== slim_tab.py ===")
with open("slim_tab.py", encoding="utf-8") as f:
    content = f.read()

# Fix L1102: hardcoded f-string -> use _() for labels
old_1102 = 'f"尺寸: {info[\'dimensions\']} | 大小: {info[\'size_str\']} | 格式: {info[\'format\']} ({info[\'mode\']})"'
new_1102 = 'f"{_(\'尺寸\')}: {info[\'dimensions\']} | {_(\'大小\')}: {info[\'size_str\']} | {_(\'格式\')}: {info[\'format\']} ({info[\'mode\']})"'

if old_1102 in content:
    content = content.replace(old_1102, new_1102, 1)
    print("  OK: Fixed dynamic img_info_label text")
else:
    print("  WARN: L1102 pattern not found")

# Fix L1092: "无法读取图片:"
old_1092 = 'f"无法读取图片: {info[\'error\']}"'
new_1092 = 'f"{_(\'无法读取图片\')}: {info[\'error\']}"'
if old_1092 in content:
    content = content.replace(old_1092, new_1092, 1)
    print("  OK: Fixed L1092 error text")

# Fix L1120: "无法读取图片:"
old_1120 = 'f"无法读取图片: {e}"'
new_1120 = 'f"{_(\'无法读取图片\')}: {e}"'
if old_1120 in content:
    content = content.replace(old_1120, new_1120, 1)
    print("  OK: Fixed L1120 error text")

with open("slim_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
print("  => slim_tab.py SAVED")

# ============================================================
# 3. settings_tab.py — Fix hasattr double-prefix bug
# ============================================================
print("\n=== settings_tab.py ===")
fix_file("settings_tab.py", [
    ("if hasattr(self, 'self.scene_group'):", "if hasattr(self, 'scene_group'):"),
    ("if hasattr(self, 'self.scene_tip'):", "if hasattr(self, 'scene_tip'):"),
])

# ============================================================
# 4. main_window_v2.py — Fix NAV_ITEMS not updated
# ============================================================
print("\n=== main_window_v2.py ===")
with open("main_window_v2.py", encoding="utf-8") as f:
    content = f.read()

# Find the end of apply_language method and add NAV_ITEMS update
# The method ends after updating window title. We need to store translated items.
old_nav = """        # ★ i18n: 更新窗口标题"""
new_nav = """        # ★ i18n fix4: store translated NAV_ITEMS for on_nav_changed
        if lang == 'en-US':
            self.NAV_ITEMS = items

        # ★ i18n: 更新窗口标题"""

if '★ i18n fix4: store translated' not in content and old_nav in content:
    content = content.replace(old_nav, new_nav, 1)
    with open("main_window_v2.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("  OK: Added NAV_ITEMS update to apply_language")
else:
    print("  WARN: insert point not found or already patched")

# ============================================================
# 5. translations.py — add missing keys for slim_tab
# ============================================================
print("\n=== translations.py ===")
with open("translations.py", encoding="utf-8") as f:
    lines = f.readlines()

# Add '无法读取图片' near '尺寸' entries
new_keys = [
    "    '无法读取图片': 'Cannot read image',\n",
]
inserted = 0
for i, line in enumerate(lines):
    if "'尺寸: - | 大小: - | 格式: -'" in line:
        for key in new_keys:
            lines.insert(i + 1 + inserted, key)
            inserted += 1
        break

if inserted > 0:
    with open("translations.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  OK: Added {inserted} new translation keys")
else:
    print("  WARN: insert point not found")

# ============================================================
# 6. Verify all fixes with py_compile
# ============================================================
print("\n=== Verify ===")
import py_compile
for f in ["translations.py", "sanitize_tab.py", "slim_tab.py", "settings_tab.py", "main_window_v2.py"]:
    try:
        py_compile.compile(f, doraise=True)
        print(f"  OK: {f}")
    except py_compile.PyCompileError as e:
        print(f"  FAIL: {f}: {e}")

print("\nDone!")
