src = open(r'C:\Users\26112\Desktop\SafeShrink\sanitize_tab.py', encoding='utf-8').read()
# Find on_sanitize_clicked and the QMessageBox at end
idx = src.find('def on_sanitize_clicked')
if idx >= 0:
    line_no = src[:idx].count('\n') + 1
    print(f'on_sanitize_clicked at L{line_no}')
    # Print from this line to 60 lines later
    lines = src.split('\n')
    for i in range(line_no - 1, min(line_no + 60, len(lines))):
        print(f'{i+1}: {lines[i]}')
