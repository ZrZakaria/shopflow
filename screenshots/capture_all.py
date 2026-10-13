import struct, zlib, ctypes, ctypes.wintypes as wintypes
import os, time

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

out_dir = 'C:/Users/HP/Studies/Studies/S9/GL/shopflow/screenshots'

def find_vscode():
    hwnd = None
    def enum_proc(h, lParam):
        nonlocal hwnd
        if user32.IsWindowVisible(h):
            length = user32.GetWindowTextLengthW(h) + 1
            buf = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(h, buf, length)
            if 'Visual Studio Code' in buf.value:
                hwnd = h
                return False
        return True
    enum = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(enum_proc)
    user32.EnumWindows(enum, 0)
    return hwnd

def capture_window(hwnd, output_path, label=""):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    ww = rect.right - rect.left
    wh = rect.bottom - rect.top
    
    # Activate and wait
    user32.SetForegroundWindow(hwnd)
    kernel32.Sleep(1000)
    
    # Capture
    screen_dc = user32.GetDC(None)
    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    mem_bmp = gdi32.CreateCompatibleBitmap(screen_dc, ww, wh)
    old_obj = gdi32.SelectObject(mem_dc, mem_bmp)
    
    gdi32.BitBlt(mem_dc, 0, 0, ww, wh, screen_dc, rect.left, rect.top, 0x00CC0020)
    
    # GetDIBits while bitmap still selected
    buf_size = ww * wh * 4
    bits = (ctypes.c_byte * buf_size)()
    info_buf = ctypes.create_string_buffer(40)
    struct.pack_into('<I', info_buf, 0, 40)
    struct.pack_into('<i', info_buf, 4, ww)
    struct.pack_into('<i', info_buf, 8, -wh)
    struct.pack_into('<H', info_buf, 12, 1)
    struct.pack_into('<H', info_buf, 14, 32)
    struct.pack_into('<I', info_buf, 16, 0)
    struct.pack_into('<I', info_buf, 20, buf_size)
    struct.pack_into('<i', info_buf, 24, 2835)
    struct.pack_into('<i', info_buf, 28, 2835)
    struct.pack_into('<I', info_buf, 32, 0)
    struct.pack_into('<I', info_buf, 36, 0)
    
    scan_lines = gdi32.GetDIBits(mem_dc, mem_bmp, 0, wh, bits, info_buf, 0)
    
    gdi32.SelectObject(mem_dc, old_obj)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(None, screen_dc)
    
    if scan_lines <= 0:
        print(f"  FAILED: {label} (GetDIBits={scan_lines})")
        return False
    
    # Convert to PNG
    bmp_path = out_dir + '/temp_capture.bmp'
    with open(bmp_path, 'wb') as f:
        f.write(struct.pack('<H', 0x4D42))
        f.write(struct.pack('<I', 54 + buf_size))
        f.write(struct.pack('<H', 0))
        f.write(struct.pack('<H', 0))
        f.write(struct.pack('<I', 54))
        f.write(bytes(info_buf))
        f.write(bytes(bits))
    
    rows = []
    with open(bmp_path, 'rb') as f:
        data = f.read()
    img_w, img_h = struct.unpack('<ii', data[18:26])
    img_h = abs(img_h)
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
    
    os.remove(bmp_path)
    print(f"  OK: {label} ({img_w}x{img_h}, {len(png_data)} bytes)")
    return True

# Find VS Code
hwnd = find_vscode()
if not hwnd:
    print("VS Code not found!")
    exit(1)
print(f"VS Code window found")

captures = [
    ('capture3_project.png', 'Project Explorer (File Tree)'),
    ('capture4_panier.png', 'Panier.java Editor'),
    ('capture7_testing.png', 'Testing View'),
    ('capture14_git.png', 'Source Control (Git)'),
    ('capture16_anomalies.png', 'ANOMALIES.md Editor'),
]

for filename, label in captures:
    path = out_dir + '/' + filename
    # Check if already exists and is large enough
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        print(f"  SKIP: {label} (already captured)")
        continue
    capture_window(hwnd, path, label)
    time.sleep(1)

print("\nDone!")
