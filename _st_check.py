import pathlib
p = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink')
f = p / 'settings_tab.py'
txt = f.read_text(encoding='utf-8', errors='replace')
lines = txt.splitlines()

with open(r'C:\Users\26112\Desktop\SafeShrink\_st_check.txt', 'w', encoding='utf-8') as out:
    for i, l in enumerate(lines):
        if any(k in l for k in ['lang', 'tr(', 'translate', 'i18n', 'zh-CN', 'en-US']):
            out.write(f'{i+1}: {l}\n')
print("Done")
