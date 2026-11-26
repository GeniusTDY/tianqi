from PIL import Image, ImageDraw, ImageFont

ART = Image.open('/tmp/v66assets/infocard.webp').convert('RGBA')
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
F_TITLE = ImageFont.truetype(FONT, 34)
F_TAG = ImageFont.truetype(FONT, 22)

W, H = 1200, 700

def nine_slice(im, rect, b=48):
    x0, y0, x1, y1 = rect
    tw, th = x1 - x0, y1 - y0
    iw, ih = im.size
    out = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    # corners
    out.paste(im.crop((0, 0, b, b)), (0, 0))
    out.paste(im.crop((iw - b, 0, iw, b)), (tw - b, 0))
    out.paste(im.crop((0, ih - b, b, ih)), (0, th - b))
    out.paste(im.crop((iw - b, ih - b, iw, ih)), (tw - b, th - b))
    # edges
    out.paste(im.crop((b, 0, iw - b, b)).resize((tw - 2 * b, b), Image.LANCZOS), (b, 0))
    out.paste(im.crop((b, ih - b, iw - b, ih)).resize((tw - 2 * b, b), Image.LANCZOS), (b, th - b))
    out.paste(im.crop((0, b, b, ih - b)).resize((b, th - 2 * b), Image.LANCZOS), (0, b))
    out.paste(im.crop((iw - b, b, iw, ih - b)).resize((b, th - 2 * b), Image.LANCZOS), (tw - b, b))
    # center
    out.paste(im.crop((b, b, iw - b, ih - b)).resize((tw - 2 * b, th - 2 * b), Image.LANCZOS), (b, b))
    return out

def fit_font(text, target_h):
    lo, hi = 20, 140
    best = ImageFont.truetype(FONT, 60)
    for _ in range(24):
        mid = (lo + hi) / 2
        f = ImageFont.truetype(FONT, int(mid))
        bb = f.getbbox(text)
        h = bb[3] - bb[1]
        if h < target_h:
            lo = mid
        else:
            hi = mid
        best = f
    return best

def scene(title_y, title_size, tag):
    img = Image.new('RGB', (W, H), '#05070c')
    dr = ImageDraw.Draw(img, 'RGBA')
    for rect in [(40, 12, 363, 700), (375, 12, 1169, 700)]:
        p = nine_slice(ART, rect)
        img.paste(p, (rect[0], rect[1]), p)
    # grid
    gx, gy, n, gr, size = 402, 74, 6, 4, 76
    gap = (748 - n * size) / (n - 1)
    for r in range(gr):
        for c in range(n):
            x = gx + c * (size + gap)
            y = gy + r * 108
            dr.rounded_rectangle([x, y, x + size, y + size], 12, fill=(226, 243, 228, 235),
                                 outline=(180, 210, 190, 255), width=2)
    # titles
    for text, cx in (('信息卡', 218), ('背包物品', 704)):
        f = fit_font(text, title_size)
        dr.text((cx, title_y), text, font=f, fill=(120, 240, 170, 255), anchor='mm')
    # tag
    tw = dr.textlength(tag, font=F_TAG)
    dr.rounded_rectangle([10, 10, 26 + tw, 44], 6, fill=(8, 12, 20, 215))
    dr.text((18, 15), tag, font=F_TAG, fill='#dfeaf7')
    # first-row guide
    dr.line([(375, 74), (1169, 74)], fill=(255, 120, 120, 180), width=2)
    dr.text((1050, 52), '第一行方格上沿', font=ImageFont.truetype(FONT, 16), fill=(255, 140, 140, 255))
    # annotate title bottom vs grid top
    top = title_y - title_size / 2.0
    bot = title_y + title_size / 2.0
    dr.rectangle([704 - 190, top, 704 + 190, bot], outline=(255, 235, 120, 210), width=2)
    if bot > 74:
        dr.rectangle([704 - 190, 74, 704 + 190, bot], fill=(255, 80, 80, 120))
        lab = f'标题底边 {bot:.0f}，与格子上沿 74 相切'
        col = (255, 150, 150, 255)
    else:
        dr.rectangle([704 - 190, bot, 704 + 190, 74], fill=(90, 230, 150, 90))
        lab = f'标题底边 {bot:.0f}，距格子上沿 74 留白 {74 - bot:.0f}px'
        col = (140, 240, 180, 255)
    dr.text((590, 100), lab, font=ImageFont.truetype(FONT, 20), fill=col)
    return img

before = scene(48, 52, '改前（v3.7.66）：标题 y=48 / 字号 80')
after = scene(40, 45, '改后（v3.7.67）：标题 y=40 / 字号 70')

CANVAS = Image.new('RGB', (1240, 1560), '#0b0f17')
d = ImageDraw.Draw(CANVAS)
CANVAS.paste(before, (20, 20))
CANVAS.paste(after, (20, 800))
d.text((20, 748), '↓ 改后', font=ImageFont.truetype(FONT, 20), fill='#8ea3bf')

# zoom of title area
zx0, zy0, zx1, zy1 = 560, 0, 1200, 190
Z = 2.0
zw, zh = int((zx1 - zx0) * Z), int((zy1 - zy0) * Z)
z1 = before.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)
z2 = after.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)
CANVAS.save('/workspace/信息卡标题-改前改后.png')
zoom = Image.new('RGB', (zw + 40, zh * 2 + 110), '#0b0f17')
dz = ImageDraw.Draw(zoom)
dz.text((20, 12), '局部放大 ×1.7：标题与第一行方格', font=ImageFont.truetype(FONT, 24), fill='#e8f1fb')
zoom.paste(z1, (20, 54))
dz.text((20, 54 + zh + 8), '改前', font=ImageFont.truetype(FONT, 20), fill='#ff9c9c')
zoom.paste(z2, (20, 54 + zh + 40))
dz.text((20, 54 + zh * 2 + 48), '改后', font=ImageFont.truetype(FONT, 20), fill='#7ee2a8')
zoom.save('/workspace/信息卡标题-局部放大.png')
print('ok', zoom.size)
