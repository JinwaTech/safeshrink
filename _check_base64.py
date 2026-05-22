import struct, base64, re

with open(r'C:\Users\26112\Desktop\SafeShrink\theme_manager.py', encoding='utf-8') as f:
    tmpl = f.read()

m = re.search(r"_COMBO_ARROW\s*=\s*['\"']([^'\"]+)['\"']", tmpl)
if m:
    data_url = m.group(1)
    print('Full data URL length:', len(data_url))
    print('Prefix:', data_url[:30])
    # Extract actual base64 after the comma
    if ',' in data_url:
        b64 = data_url.split(',', 1)[1]
        print('Actual base64 length:', len(b64))
        try:
            png_data = base64.b64decode(b64)
            print('Decoded size:', len(png_data), 'bytes')
            if len(png_data) >= 24:
                w = struct.unpack('>I', png_data[16:20])[0]
                h = struct.unpack('>I', png_data[20:24])[0]
                print(f'Image: {w}x{h} px')
                print('Valid PNG sig:', png_data[:8] == b'\x89PNG\r\n\x1a\n')
                print('Has IDAT:', b'IDAT' in png_data)
                print('First 24 bytes:', png_data[:24].hex())
        except Exception as e:
            print('Decode error:', e)
            # Try URL-safe base64
            b64_urlsafe = b64.replace('-', '+').replace('_', '/')
            pad = (4 - len(b64_urlsafe) % 4) % 4
            b64_urlsafe += '=' * pad
            try:
                png_data = base64.b64decode(b64_urlsafe)
                print('URL-safe decode OK, size:', len(png_data))
                w = struct.unpack('>I', png_data[16:20])[0]
                h = struct.unpack('>I', png_data[20:24])[0]
                print(f'Image: {w}x{h} px')
            except Exception as e2:
                print('URL-safe decode error:', e2)
