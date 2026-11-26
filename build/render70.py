from PIL import Image, ImageDraw, ImageFont

ART = Image.open('/tmp/v66assets/infocard.webp').convert('RGBA')
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
W, H = 1200, 700

def nine_slice(im, rect, b=30):
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

def scene(title_x, page_cx, tag):
    img = Image.new('RGB', (W, H), '#05070c')
    dr = ImageDraw.Draw(img, 'RGBA')
    for rect in [(40, 12, 363, 700), (375, 12, 1169, 700)]:
        p = nine_slice(ART, rect)
        img.paste(p, (rect[0], rect[1]), p)
    gx, gy, n, gr, size = 402, 74, 6, 4, 76
    gap = (690 - n * size) / (n - 1)
    for r in range(gr):
        for c in range(n):
            x = gx + c * (size + gap)
            y = gy + r * 108
            dr.rounded_rectangle([x, y, x + size, y + size], 12, fill=(226, 243, 228, 235),
                                 outline=(180, 210, 190, 255), width=2)
    dr.text((218, 40), '信息卡', font=fit_font('信息卡', 45), fill=(120, 245, 170, 255), anchor='mm',
            stroke_width=3, stroke_fill=(10, 50, 80, 255))
    dr.text((title_x, 40), '背包物品', font=fit_font('背包物品', 45), fill=(120, 245, 170, 255), anchor='mm',
            stroke_width=3, stroke_fill=(10, 50, 80, 255))
    # 翻页
    fa = ImageFont.truetype(FONT, 34)
    fn = ImageFont.truetype(FONT, 24)
    d = page_cx - 765
    dr.text((715 + d, 517), '<', font=fa, fill=(120, 200, 255, 255), anchor='mm')
    dr.text((830 + d, 520), '>', font=fa, fill=(120, 200, 255, 255), anchor='mm')
    dr.text((747 + d, 517), '1', font=fn, fill=(15, 35, 65, 255), anchor='mm')
    dr.text((766 + d, 518), '/', font=fn, fill=(15, 35, 65, 255), anchor='mm')
    dr.text((787 + d, 517), '0', font=fn, fill=(15, 35, 65, 255), anchor='mm')
    # 当前称号 / 更换称号
    dr.text((90, 592), '当前称号：', font=fit_font('当前称号：', 30), fill='#ffffff', anchor='lm')
    dr.rounded_rectangle([290, 616, 400, 650], 17, fill=(70, 150, 210, 255), outline=(255, 255, 255, 200))
    dr.text((345, 633), '更换称号', font=fit_font('更换称号', 20), fill='#ffffff', anchor='mm')
    # 货币
    for cx, txt in ((470, '0'), (880, '0')):
        dr.ellipse([cx - 26, 616, cx + 26, 668], fill=(230, 190, 90, 255))
        dr.text((cx + 90, 642), txt, font=fit_font('0', 28), fill='#ffffff', anchor='mm')
    tw = dr.textlength(tag, font=ImageFont.truetype(FONT, 20))
    dr.rounded_rectangle([1160 - 16 - tw, 664, 1176, 696], 6, fill=(8, 12, 20, 225))
    dr.text((1168 - tw, 668), tag, font=ImageFont.truetype(FONT, 20), fill='#dfeaf7')
    return img

before = scene(704, 731, '改前 v3.7.68：标题 704 / 翻页 731')
after = scene(772, 772, '改后 v3.7.69：标题 772 / 翻页 772')

out = Image.new('RGB', (1240, 1570), '#0b0f17')
d = ImageDraw.Draw(out)
d.text((20, 16), '信息卡界面（合成示意，非真机截图）', font=ImageFont.truetype(FONT, 26), fill='#e8f1fb')
out.paste(before, (20, 56))
out.paste(after, (20, 790))
d.text((20, 757), '↓ 改后：标题与翻页条均对齐面板中心', font=ImageFont.truetype(FONT, 20), fill='#7ee2a8')
out.save('/workspace/信息卡界面-v3.7.69-示意.png')
print('ok', out.size)
