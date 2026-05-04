data = open(r'C:\Users\26112\Desktop\SafeShrink\batch_tab.py', 'r', encoding='utf-8').read()
count = data.count('convert_to_ssd')
print(f'convert_to_ssd: {count}')
lines = data.split('\n')
for i, line in enumerate(lines[1445:1460], start=1446):
    if 'convert_to_ssd' in line or 'mode_combo' in line:
        print(f'L{i}: {line[:120]}')