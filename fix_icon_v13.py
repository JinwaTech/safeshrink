from PIL import Image

# 读取当前v12图标
ico = Image.open('assets/icon06_light.ico')
img = ico.convert('RGBA')
width, height = img.size

# 分析背景色（取左下角区域）
pixels = list(img.getdata())
bg_samples = []
for y in range(200, 256):
    for x in range(0, 56):
        idx = y * width + x
        r, g, b, a = pixels[idx]
        if a > 128 and not (r > 250 and g > 250 and b > 250):
            bg_samples.append((r, g, b))

if bg_samples:
    avg_r = sum(c[0] for c in bg_samples) // len(bg_samples)
    avg_g = sum(c[1] for c in bg_samples) // len(bg_samples)
    avg_b = sum(c[2] for c in bg_samples) // len(bg_samples)
    bg_color = (avg_r, avg_g, avg_b)
else:
    bg_color = (245, 240, 232)

print(f'Background color: {bg_color}')

# 找到当前背景边界
min_x, min_y, max_x, max_y = 256, 256, 0, 0
for y in range(height):
    for x in range(width):
        idx = y * width + x
        r, g, b, a = pixels[idx]
        if a > 128:
            is_bg = (abs(r - bg_color[0]) < 30 and 
                    abs(g - bg_color[1]) < 30 and 
                    abs(b - bg_color[2]) < 30)
            if is_bg:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

print(f'Current bounds: ({min_x},{min_y}) - ({max_x},{max_y})')

# 创建新图像
new_img = img.copy()
new_pixels = list(new_img.getdata())

# 新边界：左上保持，右下扩展到边缘（留2px边距）
new_max_x = 253
new_max_y = 253
radius = 42

# 填充扩展区域
for y in range(min_y, new_max_y + 1):
    for x in range(min_x, new_max_x + 1):
        idx = y * width + x
        r, g, b, a = new_pixels[idx]
        
        # 检查是否在圆角矩形内
        in_corner = False
        
        # 左上角圆角（保持原样）
        if x < min_x + radius and y < min_y + radius:
            dx = x - (min_x + radius)
            dy = y - (min_y + radius)
            if dx * dx + dy * dy > radius * radius:
                in_corner = True
        # 右上角圆角
        elif x > new_max_x - radius and y < min_y + radius:
            dx = x - (new_max_x - radius)
            dy = y - (min_y + radius)
            if dx * dx + dy * dy > radius * radius:
                in_corner = True
        # 左下角圆角
        elif x < min_x + radius and y > new_max_y - radius:
            dx = x - (min_x + radius)
            dy = y - (new_max_y - radius)
            if dx * dx + dy * dy > radius * radius:
                in_corner = True
        # 右下角圆角
        elif x > new_max_x - radius and y > new_max_y - radius:
            dx = x - (new_max_x - radius)
            dy = y - (new_max_y - radius)
            if dx * dx + dy * dy > radius * radius:
                in_corner = True
        
        if in_corner:
            new_pixels[idx] = (0, 0, 0, 0)
        elif a < 128 or (r > 250 and g > 250 and b > 250):
            # 透明或纯白区域填充背景色
            new_pixels[idx] = (*bg_color, 255)

new_img.putdata(new_pixels)

# 保存测试
new_img.save('icon06_light_v13_test.png')
print('Saved: icon06_light_v13_test.png')

# 创建ICO
sizes = [16, 24, 32, 48, 64, 128, 256]
images = []
for size in sizes:
    resized = new_img.resize((size, size), Image.LANCZOS)
    images.append(resized)

images[0].save('icon06_light_v13_test.ico', format='ICO', sizes=[(s, s) for s in sizes], append_images=images[1:])
print('Saved: icon06_light_v13_test.ico')
print('Done!')
