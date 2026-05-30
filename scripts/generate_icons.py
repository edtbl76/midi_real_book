import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('public/icons', exist_ok=True)

SIZES = [(180, 'icon-180.png'), (192, 'icon-192.png'), (512, 'icon-512.png')]
BG = '#0f766e'
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
]

def get_font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

def make_icon(size):
    img = Image.new('RGB', (size, size), BG)
    draw = ImageDraw.Draw(img)
    font = get_font(size // 4)
    text = 'MRB'
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (size - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (size - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), text, fill='white', font=font)
    return img

for size, name in SIZES:
    make_icon(size).save(f'public/icons/{name}')
    print(f'  wrote public/icons/{name}')