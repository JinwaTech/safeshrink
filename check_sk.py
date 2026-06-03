import re
with open(r'C:\Users\26112\Desktop\SafeShrink\SKILL.md', 'r', encoding='utf-8-sig') as f:
    content = f.read()
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('|') and line.count('|') >= 4:
        cols = [c.strip() for c in line.split('|')[1:-1]]
        for j, c in enumerate(cols):
            has_cn = bool(re.search(r'[\u4e00-\u9fff]', c))
            has_en = bool(re.search(r'[A-Za-z]', c))
            if has_cn and not has_en and len(c) > 2:
                safe = c[:80].encode('ascii', 'replace').decode('ascii')
                print(f'SKILL.md:{i+1}: pure-CN col[{j}]: \"{safe}\"')
