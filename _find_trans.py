import pathlib
p = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink')
trans = p / 'translations.py'
if trans.exists():
    print(f'translations.py: {trans.stat().st_size} bytes')
    txt = trans.read_text(encoding='utf-8', errors='replace')
    lines = txt.splitlines()
    print(f'Lines: {len(lines)}')
    with open(r'C:\Users\26112\Desktop\SafeShrink\_trans.txt', 'w', encoding='utf-8') as out:
        for i, l in enumerate(lines[:60]):
            out.write(f'{i+1}: {l}\n')
else:
    print('translations.py NOT FOUND')
    # Check translations dir
    for f in p.iterdir():
        if 'trans' in f.name.lower():
            print(f'Found: {f.name}')
