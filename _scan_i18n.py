# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r"C:\Users\26112\Desktop\SafeShrink")

def scan_file(filepath, keywords):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    print(f"\n{'='*60}\n{filepath}\n{'='*60}")
    for kw in keywords:
        lines = [f"  L{i+1}: {line.rstrip()}" for i, line in enumerate(content.split('\n')) if kw in line]
        if lines:
            print(f"\n[{kw}] found:")
            for l in lines[:5]:
                print(l)
        else:
            print(f"\n[{kw}] — NOT FOUND")

# translations.py
scan_file("translations.py", [
    "深色模式", "Dark Mode", "dark_mode", "dark_theme",
    "通用", "General", "输出", "Output", "处理", "Process",
    "界面", "Interface", "高级", "Advanced",
    "日志级别", "Log Level", "调试", "Debug",
    "未选择文件", "No file selected",
    "脱敏类型", "Sanitize Types", "Sanitize types",
    "党政公文", "Government", "医疗档案", "Medical",
    "personal sensitive", "Personal Sensitive",
    "尺寸", "Size:", "大小", "格式", "Format:",
    "批量处理", "Batch process", "Batch Process",
    "适用场景", "Preset Scenarios", "preset_scenario",
    "选择场景", "Select a scene", "auto_select_scene",
    "敏感词", "sensitive words", "custom_words",
    "正则表达式", "regex", "custom_regex",
])

# main_window_v2.py — theme button
scan_file("main_window_v2.py", [
    "深色模式", "dark_mode", "theme_btn", "toggle_theme",
    "apply_language", "_get_init_lang", "update_language",
])

# settings_tab.py
scan_file("settings_tab.py", [
    "通用", "输出", "处理", "脱敏", "界面", "高级",
    "日志级别", "调试", "Debug",
    "适用场景", "选择场景", "敏感词", "正则",
    "addTab", "tab.addTab", "log_level", "placeholder",
    "setPlaceholderText", "update_language",
])

# slim_tab.py
scan_file("slim_tab.py", [
    "尺寸", "大小", "格式", "file_info", "info_label",
    "update_language", "width", "height", "img_info",
])

# batch_tab.py
scan_file("batch_tab.py", [
    "批量处理", "subtitle", "update_language", "Batch",
])

# sanitize_tab.py
scan_file("sanitize_tab.py", [
    "未选择文件", "脱敏类型", "党政公文", "医疗档案",
    "personal sensitive", "update_language", "scene_box",
])

print("\n\nDONE.")
