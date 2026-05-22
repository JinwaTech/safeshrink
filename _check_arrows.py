import re, base64, struct

with open(r'C:\Users\26112\Desktop\SafeShrink\theme_manager.py', encoding='utf-8') as f:
    txt = f.read()

for name in ['_SPIN_UP_ARROW', '_SPIN_DOWN_ARROW']:
    m = re.search(re.escape(name) + r"\s*=\s*['\"']([^'\"]+)['\"']", txt)
    if m:
        data_url = m.group(1)
        b64 = data_url.split(',', 1)[1]
        raw = base64.b64decode(b64)
        w = struct.unpack('>I', raw[16:20])[0]
        h = struct.unpack('>I', raw[20:24])[0]
        print(f'{name}: {w}x{h} px, {len(raw)} bytes')
    else:
        print(f'{name}: NOT FOUND')
