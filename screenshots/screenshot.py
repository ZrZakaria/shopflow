import struct, zlib, ctypes, ctypes.wintypes as w

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

hwnd = user32.GetDesktopWindow()
sc_hdc = user32.GetDC(hwnd)
dc_hdc = gdi32.CreateCompatibleDC(sc_hdc)
bmp = gdi32.CreateCompatibleBitmap(sc_hdc, 1280, 800)
old_obj = gdi32.SelectObject(dc_hdc, bmp)
gdi32.BitBlt(dc_hdc, 0, 0, 1280, 800, sc_hdc, 0, 0, 0x00CC0020)

out_dir = 'C:/Users/HP/Studies/Studies/S9/GL/shopflow/screenshots'
bmp_path = out_dir + '/desktop.bmp'

# Write BMP header
bfType = 0x4D42
bfSize = 54 + 1280 * 800 * 4
bfOffBits = 54

with open(bmp_path, 'wb') as f:
    # BMP File Header (14 bytes)
    f.write(struct.pack('<H', bfType))
    f.write(struct.pack('<I', bfSize))
    f.write(struct.pack('<H', 0))
    f.write(struct.pack('<H', 0))
    f.write(struct.pack('<I', bfOffBits))

    # BITMAPINFOHEADER (40 bytes) - write each field individually
    f.write(struct.pack('<I', 40))
    f.write(struct.pack('<i', 1280))
    f.write(struct.pack('<i', -800))
    f.write(struct.pack('<H', 1))
    f.write(struct.pack('<H', 32))
    f.write(struct.pack('<I', 0))
    f.write(struct.pack('<I', 1280 * 800 * 4))
    f.write(struct.pack('<i', 2835))
    f.write(struct.pack('<i', 2835))
    f.write(struct.pack('<I', 0))
    f.write(struct.pack('<I', 0))

    # Get bitmap bits
    buf_size = 1280 * 800 * 4
    bits = ctypes.create_string_buffer(buf_size)
    info_buf = ctypes.create_string_buffer(40)
    struct.pack_into('<I', info_buf, 0, 40)
    struct.pack_into('<i', info_buf, 4, 1280)
    struct.pack_into('<i', info_buf, 8, -800)
    struct.pack_into('<H', info_buf, 12, 1)
    struct.pack_into('<H', info_buf, 14, 32)
    struct.pack_into('<I', info_buf, 16, 0)
    struct.pack_into('<I', info_buf, 20, buf_size)
    struct.pack_into('<i', info_buf, 24, 2835)
    struct.pack_into('<i', info_buf, 28, 2835)
    struct.pack_into('<I', info_buf, 32, 0)
    struct.pack_into('<I', info_buf, 36, 0)

    result = gdi32.GetDIBits(dc_hdc, bmp, 0, 800, bits, info_buf, 0)
    if result == 0:
        print(f"GetDIBits failed with error {ctypes.get_last_error()}")
    else:
        f.write(bits.raw)
        print(f"Got {result} scan lines")

print(f'BMP saved: {bmp_path}')
gdi32.SelectObject(dc_hdc, old_obj)
gdi32.DeleteObject(bmp)
gdi32.DeleteDC(dc_hdc)
user32.ReleaseDC(hwnd, sc_hdc)

# Convert BMP to PNG
rows = []
with open(bmp_path, 'rb') as f:
    data = f.read()

width, height = struct.unpack('<ii', data[18:26])
img_offset = struct.unpack('<I', data[10:14])[0]
print(f'BMP: {width}x{height}, offset={img_offset}, size={len(data)}')

for y in range(abs(height) - 1, -1, -1):
    start = img_offset + y * width * 4
    row = b'\x00' + data[start:start + width * 4]
    rows.append(row)

raw = b''.join(rows)
compressed = zlib.compress(raw)

def png_chunk(chunk_type, chunk_data):
    c = chunk_type + chunk_data
    crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    return struct.pack('>I', len(chunk_data)) + c + crc

png_data = b'\x89PNG\r\n\x1a\n'
png_data += png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, abs(height), 8, 6, 0, 0, 0))
png_data += png_chunk(b'IDAT', compressed)
png_data += png_chunk(b'IEND', b'')

png_path = out_dir + '/desktop.png'
with open(png_path, 'wb') as f:
    f.write(png_data)

print(f'PNG saved: {png_path} ({width}x{height})')
