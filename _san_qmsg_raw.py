"""Read sanitize_tab.py raw bytes for the QMessageBox lines."""
import pathlib, re

SRC = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py')
txt = SRC.read_text(encoding='utf-8')
lines = txt.splitlines()

with open(r'C:\Users\26112\Desktop\SafeShrink\_san_qmsg.txt', 'w', encoding='utf-8') as out:
    for i, l in enumerate(lines):
        if 'QMessageBox' in l:
            # Escape non-ASCII for display
            safe = l.encode('utf-8', errors='replace').decode('utf-8')
            out.write(f'{i+1}: {safe}\n')
            # Also write raw repr
            out.write(f'  RAW: {repr(l)}\n')
print("Done")
