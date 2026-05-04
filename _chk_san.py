src = open(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py', encoding='utf-8').read()
for kw in ['_sanitized', 'items_found', 'total_items', 'detected_items']:
    idx = src.find(kw)
    if idx > 0:
        line_no = src[:idx].count('\n') + 1
        print(f'{kw} at L{line_no}:')
        print(src[max(0,idx-60):idx+80])
        print()