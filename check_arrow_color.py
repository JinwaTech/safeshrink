"""检查箭头图片的颜色"""
from PIL import Image
import os

assets_dir = r'C:\Users\26112\Desktop\SafeShrink\dist\SafeShrink\_internal\assets'

for name in ['arrow_down.png', 'arrow_up.png', 'arrow_down2.png']:
    path = os.path.join(assets_dir, name)
    img = Image.open(path)
    print(f"{name}: size={img.size}, mode={img.mode}")
    
    # 检查像素颜色
    pixels = list(img.getdata())
    unique_colors = set(pixels)
    print(f"  Unique colors: {len(unique_colors)}")
    for c in list(unique_colors)[:5]:
        print(f"    {c}")
    print()
