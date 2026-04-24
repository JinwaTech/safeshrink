#!/usr/bin/env python3
"""PyQt6 to PySide6 migration script"""
import re
from pathlib import Path

# Files to migrate
files = [
    'main_window_v2.py',
    'batch_tab.py', 
    'slim_tab.py',
    'sanitize_tab.py',
    'settings_tab.py',
    'history_tab.py',
    'safe_shrink_gui.py',
    'batch_processor.py',
]

replacements = [
    ('from PyQt6.', 'from PySide6.'),
    ('import PyQt6', 'import PySide6'),
    ('pyqtSignal', 'Signal'),
    ('pyqtSlot', 'Slot'),
]

for fname in files:
    fpath = Path(fname)
    if not fpath.exists():
        print(f"Skip: {fname} not found")
        continue
    
    content = fpath.read_text(encoding='utf-8')
    original = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original:
        fpath.write_text(content, encoding='utf-8')
        print(f"Updated: {fname}")
    else:
        print(f"No changes: {fname}")

print("\nMigration complete!")
