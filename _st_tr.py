import pathlib
f = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink\settings_tab.py')
txt = f.read_text(encoding='utf-8', errors='replace')
lines = txt.splitlines()
print(f'Total lines: {len(lines)}')
with open(r'C:\Users\26112\Desktop\SafeShrink\_st_tr.txt', 'w', encoding='utf-8') as out:
    for i in range(1055, min(len(lines), 1095)):
        out.write(f'{i+1}: {lines[i]}\n')
print('Done')
