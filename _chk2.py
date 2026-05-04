data = open(r'C:\Users\26112\Desktop\SafeShrink\batch_tab.py', 'r', encoding='utf-8').read()
lines = data.split('\n')
for i, line in enumerate(lines, start=1):
    if 'convert_to_ssd' in line:
        print(f'L{i}: {line[:150]}')