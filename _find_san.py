src = open(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py', encoding='utf-8').read()
# Find key function definitions
for kw in ['def on_sanitize_clicked', 'def _sanitize_native_docx', 'def _sanitize_text', 'detected_items', 'sanitized_count']:
    idx = src.find(kw)
    if idx >= 0:
        line_no = src[:idx].count('\n') + 1
        print(f'{kw} at L{line_no}')
        print(src[idx:idx+200])
        print('---')