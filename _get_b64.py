import base64, pathlib

for fn in ['arrow_down.png', 'arrow_up.png', 'arrow_down2.png']:
    p = pathlib.Path(__file__).parent / 'assets' / fn
    b64 = base64.b64encode(p.read_bytes()).decode()
    print(f'# {fn} ({len(b64)} chars base64)')
    print(b64)
    print()
