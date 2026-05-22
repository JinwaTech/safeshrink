"""生成箭头图片的完整 base64 data URL，直接嵌入代码"""
import base64
import os

assets_dir = r'C:\Users\26112\Desktop\SafeShrink\assets'

print("# 箭头图标 base64 data URLs（自动生成的常量）")
for name in ['arrow_down.png', 'arrow_up.png', 'arrow_down2.png']:
    path = os.path.join(assets_dir, name)
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    var_name = name.replace('.png', '_b64').replace('-', '_')
    print(f'{var_name} = "data:image/png;base64,{b64}"')
    print()
