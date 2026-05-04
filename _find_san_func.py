src = open(r'C:\Users\26112\Desktop\SafeShrink\safe_shrink_gui.py', encoding='utf-8').read()
idx = src.find('def sanitize_content')
if idx >= 0:
    line_no = src[:idx].count('\n') + 1
    print(f'sanitize_content at L{line_no}')
    print(src[idx:idx+500])