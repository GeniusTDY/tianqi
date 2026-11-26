from PIL import Image, ImageDraw, ImageFont

ART = Image.open('/tmp/v66assets/infocard.webp').convert('RGBA')
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
W, H = 1200, 700

def nine_slice(im, rect, b=48):
    x0, y0, x1, y1 = rect
    tw, th = x1 - x0, y1 - y0
    iw, ih = im.size
    out = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    out.paste(im.crop((0, 0, b, b)), (0, 0))
    out.paste(im.crop((iw - b, 0, iw, b)), (tw - b, 0))
    out.paste(im.crop((0, ih - b, b, ih)), (0, th - b))
    out.paste(im.crop((iw - b, ih - b, iw, ih)), (tw - b, th - b))
    out.paste(im.crop((b, 0, iw - b, b)).resize((tw - 2 * b, b), Image.LANCZOS), (b, 0))
    out.paste(im.crop((b, ih - b, iw - b, ih)).resize((tw - 2 * b, b), Image.LANCZOS), (b, th - b))
    out.paste(im.crop((0, b, b, ih - b)).resize((b, th - 2 * b), Image.LANCZOS), (0, b))
    out.paste(im.crop((iw - b, b, iw, ih - b)).resize((b, th - 2 * b), Image.LANCZOS), (tw - b, b))
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

PANEL = (375, 12, 1169, 700)
CENTER = 772.0

def scene(title_x, tag):
    img = Image.new('RGB', (W, H), '#05070c')
    dr = ImageDraw.Draw(img, 'RGBA')
    p = nine_slice(ART, PANEL)
    img.paste(p, (PANEL[0], PANEL[1]), p)
    gx, gy, n, gr, size = 402, 74, 6, 4, 76
    gap = (748 - n * size) / (n - 1)
    for r in range(gr):
        for c in range(n):
            x = gx + c * (size + gap)
            y = gy + r * 108
            dr.rounded_rectangle([x, y, x + size, y + size], 12, fill=(226, 243, 228, 235),
                                 outline=(180, 210, 190, 255), width=2)
    # panel center line
    dr.line([(CENTER, 12), (CENTER, 700)], fill=(120, 200, 255, 200), width=2)
    f = fit_font('背包物品', 45)
    dr.text((title_x, 40), '背包物品', font=f, fill=(120, 240, 170, 255), anchor='mm')
    # marker of title center
    dr.line([(title_x, 10), (title_x, 78)], fill=(255, 190, 90, 230), width=2)
    tw = dr.textlength(tag, font=ImageFont.truetype(FONT, 22))
    dr.rounded_rectangle([8, 8, 24 + tw, 42], 6, fill=(8, 12, 20, 225))
    dr.text((16, 13), tag, font=ImageFont.truetype(FONT, 22), fill='#dfeaf7')
    off = title_x - CENTER
    lab = f'标题中心 {title_x:.0f} / 面板中心 {CENTER:.0f}，偏 {off:+.0f}px'
    lw = dr.textlength(lab, font=ImageFont.truetype(FONT, 18))
    dr.rectangle([PANEL[0] + 8, 160, PANEL[0] + 24 + lw, 186], fill=(6, 10, 18, 220))
    dr.text((PANEL[0] + 16, 163), lab, font=ImageFont.truetype(FONT, 18), fill=(150, 210, 255, 255))
    return img

before = scene(704, '改前 v3.7.67：x=704')
after = scene(772, '改后 v3.7.68：x=772')

zx0, zy0, zx1, zy1 = 375, 0, 1180, 200
Z = 1.85
zw, zh = int((zx1 - zx0) * Z), int((zy1 - zy0) * Z)
z1 = before.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)
z2 = after.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)

out = Image.new('RGB', (zw + 40, zh * 2 + 150), '#0b0f17')
d = ImageDraw.Draw(out)
d.text((20, 14), '「背包物品」标题水平居中（×1.85 示意）', font=ImageFont.truetype(FONT, 26), fill='#e8f1fb')
d.text((20, 48), '青色竖线 = 右侧面板中心 772；橙色竖线 = 标题中心', font=ImageFont.truetype(FONT, 17), fill='#7e93ad')
out.paste(z1, (20, 76))
d.text((20, 76 + zh + 6), '改前：标题偏左 68px', font=ImageFont.truetype(FONT, 19), fill='#ff9c9c')
out.paste(z2, (20, 76 + zh + 36))
d.text((20, 76 + zh * 2 + 42), '改后：标题与面板中心对齐', font=ImageFont.truetype(FONT, 19), fill='#7ee2a8')
out.save('/workspace/信息卡标题居中-示意.png')
print('ok', out.size)
