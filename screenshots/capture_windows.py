import struct, zlib, ctypes, ctypes.wintypes as w

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def screenshot_window(title_pattern, output_path, width=1280, height=800):
    """Take a screenshot of a window matching title_pattern."""
    # Enumerate windows
    def enum_windows_proc(hwnd, lParam):
        if hwnd not in seen and user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buf = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buf, length)
            title = buf.value
            if title and title_pattern.lower() in title.lower():
                found.append((hwnd, title))
        return True
    
    seen = set()
    found = []
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)(enum_windows_proc), 0)
    
    if not found:
        print(f"No window found matching '{title_pattern}'")
        return False
    
    hwnd, title = found[0]
    print(f"Found: {title}")
    
    # Restore if minimized
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    ctypes.windll.user32.Sleep(300)
    user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.Sleep(800)
    
    # Get window rect
    rect = w.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w_w = rect.right - rect.left
    w_h = rect.bottom - rect.top
    print(f"Window size: {w_w}x{w_h}")
    
    # Capture
    hdc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hdc)
    mem_bmp = gdi32.CreateCompatibleBitmap(hdc, width, height)
    old_obj = gdi32.SelectObject(mem_dc, mem_bmp)
    gdi32.BitBlt(mem_dc, 0, 0, width, height, hdc, 0, 0, 0x00CC0020)
    gdi32.SelectObject(mem_dc, old_obj)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hdc)
    
    # Save as BMP then convert to PNG
    buf_size = width * height * 4
    bmp_path = output_path.replace('.png', '.bmp')
    
    with open(bmp_path, 'wb') as f:
        f.write(struct.pack('<H', 0x4D42))
        f.write(struct.pack('<I', 54 + buf_size))
        f.write(struct.pack('<H', 0))
        f.write(struct.pack('<H', 0))
        f.write(struct.pack('<I', 54))
        f.write(struct.pack('<I', 40))
        f.write(struct.pack('<i', width))
        f.write(struct.pack('<i', -height))
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<H', 32))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', buf_size))
        f.write(struct.pack('<i', 2835))
        f.write(struct.pack('<i', 2835))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', 0))
        bits = (ctypes.c_byte * buf_size)()
        info_buf = ctypes.create_string_buffer(40)
        struct.pack_into('<I', info_buf, 0, 40)
        struct.pack_into('<i', info_buf, 4, width)
        struct.pack_into('<i', info_buf, 8, -height)
        struct.pack_into('<H', info_buf, 12, 1)
        struct.pack_into('<H', info_buf, 14, 32)
        struct.pack_into('<I', info_buf, 16, 0)
        struct.pack_into('<I', info_buf, 20, buf_size)
        struct.pack_into('<i', info_buf, 24, 2835)
        struct.pack_into('<i', info_buf, 28, 2835)
        struct.pack_into('<I', info_buf, 32, 0)
        struct.pack_into('<I', info_buf, 36, 0)
        gdi32.GetDIBits(mem_bmp, 0, height, bits, info_buf, 0)
        f.write(bits[:buf_size])
    
    # Convert BMP to PNG
    rows = []
    with open(bmp_path, 'rb') as f:
        data = f.read()
    img_w, img_h = struct.unpack('<ii', data[18:26])
    img_off = struct.unpack('<I', data[10:14])[0]
    for y in range(img_h - 1, -1, -1):
        start = img_off + y * img_w * 4
        row = b'\x00' + data[start:start + img_w * 4]
        rows.append(row)
    raw = b''.join(rows)
    compressed = zlib.compress(raw)
    def chunk(t, d):
        c = t + d
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(d)) + c + crc
    png_data = b'\x89PNG\r\n\x1a\n'
    png_data += chunk(b'IHDR', struct.pack('>IIBBBBB', img_w, img_h, 8, 6, 0, 0, 0))
    png_data += chunk(b'IDAT', compressed)
    png_data += chunk(b'IEND', b'')
    
    with open(output_path, 'wb') as f:
        f.write(png_data)
    
    import os
    os.remove(bmp_path)
    print(f"Saved: {output_path} ({img_w}x{img_h})")
    return True

out_dir = 'C:/Users/HP/Studies/Studies/S9/GL/shopflow/screenshots'

# 1. Desktop screenshot (already done)
# 2. VS Code project explorer (Capture 3)
screenshot_window('shopflow', out_dir + '/capture3_project.png')

# 3. VS Code Panier.java (Capture 4)
screenshot_window('Panier.java', out_dir + '/capture4_panier.png')

# 4. VS Code Testing view - look for "Testing" or "Test" in title
screenshot_window('Testing', out_dir + '/capture7_testing.png')
if not any(f.startswith('capture7') for f in __import__('os').listdir(out_dir)):
    # Try alternate titles
    screenshot_window('Test', out_dir + '/capture7_testing.png')

# 5. Git Source Control (Capture 14)
screenshot_window('Source Control', out_dir + '/capture14_git.png')
if not __import__('os').path.exists(out_dir + '/capture14_git.png'):
    screenshot_window('Git', out_dir + '/capture14_git.png')

# 6. ANOMALIES.md (Capture 16)
screenshot_window('ANOMALIES', out_dir + '/capture16_anomalies.png')
if not __import__('os').path.exists(out_dir + '/capture16_anomalies.png'):
    screenshot_window('ANOMALIES.md', out_dir + '/capture16_anomalies.png')

print("\nDone!")
