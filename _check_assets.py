import os, struct, base64, re

assets_dir = r'C:\Users\26112\Desktop\SafeShrink\assets'
for fname in ['arrow_down.png', 'arrow_down2.png', 'arrow_up.png']:
    path = os.path.join(assets_dir, fname)
    if os.path.exists(path):
        data = open(path, 'rb').read()
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        b64 = base64.b64encode(data).decode()
        print(f'{fname}: {w}x{h}, {len(data)} bytes')
        print(f'  data URL: data:image/png;base64,{b64[:20]}...')
    else:
        print(f'{fname}: NOT FOUND')

print()

# Check how they're referenced in theme_manager.py
with open(r'C:\Users\26112\Desktop\SafeShrink\theme_manager.py', encoding='utf-8') as f:
    tmpl = f.read()

# Find QComboBox and QSpinBox CSS blocks
blocks = re.findall(r'QComboBox.*?(?=QSpinBox|$)', tmpl, re.DOTALL)
for i, b in enumerate(blocks[:2]):
    print(f'=== QComboBox block {i} (first 300 chars) ===')
    print(b[:300])
    print()
