import re
with open(r'C:\Users\26112\Desktop\SafeShrink\SKILL.md', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Check code blocks for pure-CN
in_code = False
for i, line in enumerate(content.split('\n')):
    stripped = line.strip()
    if stripped.startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', line))
        has_en = bool(re.search(r'[A-Za-z]', line))
        if has_cn and not has_en and len(stripped) > 2:
            safe = stripped[:100].encode('ascii', 'replace').decode('ascii')
            print(f'Code block Line {i+1}: {safe}')
