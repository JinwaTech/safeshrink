"""生成箭头图片的 base64 data URL"""
import base64
import os

assets_dir = r'C:\Users\26112\Desktop\SafeShrink\assets'

for name in ['arrow_down.png', 'arrow_up.png', 'arrow_down2.png']:
    path = os.path.join(assets_dir, name)
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    print(f"{name}: data:image/png;base64,{b64[:80]}...")
    print(f"  Full length: {len(b64)}")
    print()
