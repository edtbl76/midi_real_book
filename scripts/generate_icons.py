import io, os, urllib.request
import cairosvg
from PIL import Image

os.makedirs('public/icons', exist_ok=True)

SIZES = [(180, 'icon-180.png'), (192, 'icon-192.png'), (512, 'icon-512.png')]
BG    = '#080808'

SVG_URL = 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f3b5.svg'

req = urllib.request.Request(SVG_URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as r:
    svg_data = r.read()

def make_icon(size):
    s        = size
    note_px  = round(s * 0.75)
    png      = cairosvg.svg2png(bytestring=svg_data, output_width=note_px, output_height=note_px)
    note     = Image.open(io.BytesIO(png)).convert('RGBA')
    img      = Image.new('RGB', (s, s), BG)
    bg_layer = Image.new('RGBA', note.size, BG)
    bg_layer.paste(note, mask=note.split()[3])
    offset   = (s - note_px) // 2
    img.paste(bg_layer.convert('RGB'), (offset, offset))
    return img

for size, name in SIZES:
    make_icon(size).save(f'public/icons/{name}')
    print(f'  wrote public/icons/{name}')
