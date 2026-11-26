import os
from PIL import Image, ImageDraw, ImageFont

ICON_DIR = '/tmp/icons7'
BAR = Image.open('/tmp/v66assets/bar.webp').convert('RGBA')

F_TITLE = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 34)
F_TAG = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 20)

# name, image, base_center(v3.7.64), ink_width
ICONS = [
    ('孵化',   '3805034956.webp', 199.5, 89.0, True),
    ('天启星盘', '3168340070.webp', 352.3, 120.0, True),
    ('商城',   '3147940218.webp', 501.6, 92.0, True),
    ('地图',   '3871956625.webp', 654.4, 117.0, False),
    ('信息卡',  '2316322479.webp', 804.2, 86.0, False),
    ('仓库',   '3458348368.webp', 940.6, 90.2, False),
    ('背包',   '288535618.webp', 1082.0, 96.0, False),
]

STRIP_W, STRIP_H = 1200, 210
PAD = 8
ROWS = [
    ('v3.7.66（本版）· 左三 +8px', 8.0),
    ('v3.7.65 · 左三 +5px', 5.0),
    ('v3.7.64 · 基线（地图两侧 48.3 / 48.3）', 0.0),
]

W = STRIP_W + PAD * 2
H = 96 + len(ROWS) * (STRIP_H + 18) + 20
img = Image.new('RGB', (W, H), '#101720')
dr = ImageDraw.Draw(img, 'RGBA')
dr.text((PAD + 6, 22), '底栏图标位置对比', font=F_TITLE, fill='#e8f1fb')
dr.text((PAD + 6, 62), '按 data.json 真实坐标合成；图标取游戏原素材，底栏为原始底图',
        font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 17), fill='#7e93ad')

bar_w = STRIP_W
bar_h = int(round(BAR.height * bar_w / BAR.width))
bar_img = BAR.resize((bar_w, bar_h), Image.LANCZOS)

def ink_crop(im):
    bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(bb) if bb else im

cache = {}
def icon(name, fn):
    if name not in cache:
        cache[name] = ink_crop(Image.open(os.path.join(ICON_DIR, fn)).convert('RGBA'))
    return cache[name]

y = 96
for label, shift in ROWS:
    dr.rounded_rectangle([PAD, y, PAD + STRIP_W, y + STRIP_H], 10, fill='#0d141d')
    # bar
    bar_top = y + STRIP_H - bar_h - 4
    img.paste(bar_img, (PAD, bar_top), bar_img)
    # icons
    base = bar_top + int(bar_h * 0.58)
    for name, fn, cx, iw, moved in ICONS:
        im = icon(name, fn)
        w = iw
        h = w * im.height / im.width
        im2 = im.resize((int(round(w)), int(round(h))), Image.LANCZOS)
        x = PAD + cx + (shift if moved else 0) - w / 2
        img.paste(im2, (int(round(x)), int(round(base - h))), im2)
    # tag
    tw = dr.textlength(label, font=F_TAG)
    dr.rounded_rectangle([PAD + 10, y + 8, PAD + 22 + tw, y + 40], 6, fill=(8, 14, 22, 210))
    dr.text((PAD + 16, y + 13), label, font=F_TAG, fill='#cfe0f5')
    y += STRIP_H + 18

img.save('/workspace/底栏对比-v3.7.64-65-66.png')
print('saved', img.size)
