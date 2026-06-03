import re

with open(r'C:\Users\26112\Desktop\SafeShrink\SKILL.md', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 1. Check frontmatter
print("=== FRONTMATTER ===")
fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
if fm_match:
    fm = fm_match.group(1)
    for line in fm.split('\n'):
        line = line.strip()
        if not line: continue
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', line))
        has_en = bool(re.search(r'[A-Za-z]', line))
        if has_cn and not has_en:
            print(f"  pure-CN: {line[:100]}")
        elif has_cn:
            # Check if bilingual (has / separator)
            if '/' not in line:
                print(f"  NO SLASH: {line[:100]}")

# 2. Check all non-table lines for pure-CN paragraphs
print("\n=== NON-TABLE LINES ===")
lines = content.split('\n')
in_code = False
for i, line in enumerate(lines):
    # Skip code blocks
    if line.strip().startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    
    # Skip empty lines, comments, table rows
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        continue
    if stripped.startswith('|') or stripped.startswith('---') or stripped.startswith('---'):
        continue
    if stripped.startswith('-') or stripped.startswith('1.') or stripped.startswith('2.'):
        # List item - check
        pass
    
    has_cn = bool(re.search(r'[\u4e00-\u9fff]', stripped))
    has_en = bool(re.search(r'[A-Za-z]', stripped))
    
    if has_cn and not has_en:
        safe = stripped[:120].encode('ascii', 'replace').decode('ascii')
        print(f"  Line {i+1}: pure-CN: \"{safe}\"")
