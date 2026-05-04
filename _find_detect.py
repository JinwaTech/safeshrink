src = open(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py', encoding='utf-8').read()
# Find detect_sensitive and how detected_items is populated
for kw in ['def detect_sensitive', 'def on_detect_clicked', '_sanitized_count', 'items_found']:
    idx = src.find(kw)
    if idx >= 0:
        line_no = src[:idx].count('\n') + 1
        print(f'{kw} at L{line_no}')
        print(src[idx:idx+300])
        print('---')