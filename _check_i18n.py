import pathlib, glob
p = pathlib.Path(r'C:\Users\26112\Desktop\SafeShrink')

# Check all python files for language/i18n patterns
results = {}
for f in p.glob('*.py'):
    txt = f.read_text(encoding='utf-8', errors='replace')
    lines = txt.splitlines()
    hits = []
    for i, l in enumerate(lines):
        if any(k in l for k in ['language', 'QLocale', 'QTranslator', 'tr(', 'locale']):
            hits.append(f'{i+1}: {l[:100]}')
    if hits:
        results[f.name] = hits

with open(r'C:\Users\26112\Desktop\SafeShrink\_i18n_check.txt', 'w', encoding='utf-8') as out:
    for fname, hits in results.items():
        out.write(f'\n=== {fname} ===\n')
        for h in hits[:10]:
            out.write(h + '\n')
print("Done, files found:", list(results.keys()))
