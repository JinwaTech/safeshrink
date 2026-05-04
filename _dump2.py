lines = open(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py', encoding='utf-8').read().split('\n')
for i, line in enumerate(lines, start=1):
    if 840 <= i <= 990:
        with open(r'C:\Users\26112\Desktop\SafeShrink\_out2.txt', 'a', encoding='utf-8') as f:
            f.write(f'L{i}: {line}\n')