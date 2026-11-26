from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
CENTER = 772.0

def scene(group_cx, tag):
    W, H = 1200, 700
    img = Image.new('RGB', (W, H), '#1d5f9e')
    dr = ImageDraw.Draw(img, 'RGBA')
    # 面板内底色
    dr.rectangle([375, 12, 1169, 700], fill=(38, 110, 176, 255))
    # 最后一行方格
    gx, n, size = 402, 6, 76
    gap = (748 - n * size) / (n - 1)
    for c in range(n):
        x = gx + c * (size + gap)
        y = 74 + 3 * 108
        dr.rounded_rectangle([x, y, x + size, y + size], 12, fill=(226, 243, 228, 235),
                             outline=(180, 210, 190, 255), width=2)
    # 底部货币栏
    dr.rounded_rectangle([392, 556, 1152, 690], 14, fill=(58, 138, 200, 255), outline=(120, 190, 235, 255))
    # 翻页条
    f = ImageFont.truetype(FONT, 34)
    d = group_cx - 765  # 相对偏移
    dr.text((715 + d, 517), '<', font=f, fill=(120, 200, 255, 255), anchor='mm')
    dr.text((830 + d, 520), '>', font=f, fill=(120, 200, 255, 255), anchor='mm')
    dr.text((747 + d, 517), '1', font=ImageFont.truetype(FONT, 26), fill=(20, 40, 70, 255), anchor='mm')
    dr.text((766 + d, 518), '/', font=ImageFont.truetype(FONT, 26), fill=(20, 40, 70, 255), anchor='mm')
    dr.text((787 + d, 517), '0', font=ImageFont.truetype(FONT, 26), fill=(20, 40, 70, 255), anchor='mm')
    # 中心线
    dr.line([(CENTER, 440), (CENTER, 700)], fill=(120, 200, 255, 200), width=2)
    dr.line([(group_cx, 440), (group_cx, 700)], fill=(255, 190, 90, 230), width=2)
    # 参考线
    dr.line([(380, 474), (1160, 474)], fill=(255, 130, 130, 190), width=2)
    dr.line([(380, 556), (1160, 556)], fill=(255, 130, 130, 190), width=2)

    return img

before = scene(731, '改前 v3.7.68：翻页条中心 731')
after = scene(772, '改后 v3.7.69：翻页条中心 772')

zx0, zy0, zx1, zy1 = 630, 440, 930, 600
Z = 3.0
zw, zh = int((zx1 - zx0) * Z), int((zy1 - zy0) * Z)
z1 = before.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)
z2 = after.crop((zx0, zy0, zx1, zy1)).resize((zw, zh), Image.LANCZOS)

out = Image.new('RGB', (zw + 40, zh * 2 + 150), '#0b0f17')
d = ImageDraw.Draw(out)
d.text((20, 14), '信息卡翻页条「< 1 / 0 >」居中（×3 示意）', font=ImageFont.truetype(FONT, 24), fill='#e8f1fb')
d.text((20, 46), '青色线 = 面板中心 772；橙色线 = 翻页条中心；红色线 = 最后一行方格底边 / 货币栏上沿', font=ImageFont.truetype(FONT, 16), fill='#7e93ad')
out.paste(z1, (20, 74))
d.text((20, 74 + zh + 6), '改前：整组偏左 41px', font=ImageFont.truetype(FONT, 18), fill='#ff9c9c')
out.paste(z2, (20, 74 + zh + 34))
d.text((20, 74 + zh * 2 + 40), '改后：与面板中心对齐，上下间距更均衡', font=ImageFont.truetype(FONT, 18), fill='#7ee2a8')
out.save('/workspace/信息卡翻页条居中-示意.png')
print('ok', out.size)
