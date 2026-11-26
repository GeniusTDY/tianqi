import os
from PIL import Image, ImageDraw, ImageFont

REAL = '/tmp/icons66'
F_TITLE = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 40)
F_SUB = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 20)
F_TAB = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 22)
F_SM = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', 17)

# name, image, left, right  (v3.7.66 可见区间)
NEW = [
    ('孵化',   '3805034956.webp', 163.0, 252.0),
    ('天启星盘', '3168340070.webp', 295.3, 415.3),
    ('商城',   '3147940218.webp', 463.6, 555.6),
    ('地图',   '3871956625.webp', 595.9, 712.9),
    ('信息卡',  '2316322479.webp', 761.2, 847.2),
    ('仓库',   '3458348368.webp', 895.5, 985.7),
    ('背包',   '288535618.webp', 1034.0, 1130.0),
]
SHIFTED = {'孵化', '天启星盘', '商城'}

W, H = 1760, 1120
img = Image.new('RGB', (W, H), '#0b0f17')
dr = ImageDraw.Draw(img, 'RGBA')
for i in range(H):
    dr.line([(0, i), (W, i)], fill=(28, 82, 128, int(20 * (1 - i / H))))

dr.text((60, 36), '天启竞技场 · 底栏图标排布（v3.7.66）', font=F_TITLE, fill='#eaf2ff')
dr.text((60, 92), '按 data.json 真实坐标绘制（1200×700 画布，1:1）；垂直方向按底边对齐示意',
        font=F_SUB, fill='#8ea3bf')

STAGE_X = 280
BASELINE = 400

_cache = {}
def art(fn):
    if fn not in _cache:
        _cache[fn] = Image.open(os.path.join(REAL, fn)).convert('RGBA')
    return _cache[fn]

def draw_icon(dr_, fn, left, right, baseline, ox=0.0, zoom=1.0, x0=0.0, alpha=255):
    im = art(fn)
    w = (right - left) * zoom
    h = w * im.height / im.width
    im2 = im.resize((max(1, int(round(w))), max(1, int(round(h)))), Image.LANCZOS)
    if alpha < 255:
        a = im2.getchannel('A').point(lambda v: v * alpha // 255)
        im2.putalpha(a)
    px = ox + (left - x0) * zoom
    py = baseline - h
    img.paste(im2, (int(round(px)), int(round(py))), im2)
    return px, px + w, py, baseline

# ---------- panel 1 ----------
dr.rounded_rectangle([STAGE_X - 10, BASELINE - 12, STAGE_X + 1210, BASELINE + 46], 18,
                     fill=(20, 32, 46, 240), outline=(64, 112, 152, 170), width=2)
dr.rectangle([STAGE_X - 10, BASELINE - 12, STAGE_X + 1210, BASELINE - 4], fill=(86, 164, 214, 80))

boxes = {}
for name, fn, l, r in NEW:
    boxes[name] = draw_icon(dr, fn, l, r, BASELINE, ox=STAGE_X)

# vertical guides
cxs = STAGE_X + 600
dr.line([(cxs, 160), (cxs, 470)], fill=(120, 150, 190, 120), width=2)
dr.text((cxs + 8, 164), '画布中心 600', font=F_SM, fill='#8ea3bf')
mx = (boxes['地图'][0] + boxes['地图'][1]) / 2
dr.line([(mx, 196), (mx, 470)], fill=(255, 190, 90, 230), width=3)
tw = dr.textlength('地图中心 654.4', font=F_SM)
dr.text((mx - tw - 12, 198), '地图中心 654.4', font=F_SM, fill='#ffbe5a')

for name, fn, l, r in NEW:
    b = boxes[name]
    twn = dr.textlength(name, font=F_TAB)
    dr.text(((b[0] + b[1]) / 2 - twn / 2, BASELINE + 56), name, font=F_TAB, fill='#cfe0f5')
    v = f'{(b[0] + b[1]) / 2 - STAGE_X:.1f}'
    twv = dr.textlength(v, font=F_SM)
    dr.text(((b[0] + b[1]) / 2 - twv / 2, BASELINE + 86), v, font=F_SM, fill='#6f88a8')

def gapdim(name_a, name_b, y, color, prefix='间距 '):
    a, b = boxes[name_a], boxes[name_b]
    l, r = a[1], b[0]
    dr.line([(l, y), (r, y)], fill=color, width=2)
    for xx in (l, r):
        dr.line([(xx, y - 7), (xx, y + 7)], fill=color, width=2)
    text = f'{prefix}{r - l:.1f}'
    tw = dr.textlength(text, font=F_SM)
    dr.rectangle([(l + r) / 2 - tw / 2 - 5, y - 30, (l + r) / 2 + tw / 2 + 5, y - 8], fill=(11, 15, 23, 235))
    dr.text(((l + r) / 2 - tw / 2, y - 28), text, font=F_SM, fill=color)

gapdim('商城', '地图', 250, '#7ee2a8')
gapdim('地图', '信息卡', 250, '#7ee2a8')

# ---------- panel 2 ----------
dr.text((60, 520), '局部放大 ×1.6：商城右移后与地图的间距变化（地图及其右侧未动）', font=F_TAB, fill='#eaf2ff')

Z, X0, OX = 1.45, 445.0, 300.0
rows = [('v3.7.65', 3.0, 790), ('v3.7.66', 0.0, 1040)]
for label, back, by in rows:
    dr.text((70, by - 176), label, font=F_TAB, fill='#8ea3bf')
    dr.rounded_rectangle([OX - 20, by - 8, OX + (820 - X0) * Z + 30, by + 34], 14,
                         fill=(20, 32, 46, 240), outline=(64, 112, 152, 140), width=2)
    bb = {}
    for name, fn, l, r in NEW:
        if l < X0 - 0.1 or l > 820:
            continue
        o = back if name in SHIFTED else 0.0
        bb[name] = draw_icon(dr, fn, l - o, r - o, by, ox=OX, zoom=Z, x0=X0)
    if bb.get('商城') and bb.get('地图'):
        l, r = bb['商城'][1], bb['地图'][0]
        dr.line([(l, by - 205), (r, by - 205)], fill=(126, 226, 168, 235), width=2)
        for xx in (l, r):
            dr.line([(xx, by - 212), (xx, by - 198)], fill=(126, 226, 168, 235), width=2)
        t = f'{(r - l) / Z:.1f}'
        tw = dr.textlength(t, font=F_SM)
        dr.text(((l + r) / 2 - tw / 2, by - 232), t, font=F_SM, fill=(126, 226, 168, 255))

# shift arrow on the new row
only_new = {name: None for name, fn, l, r in NEW}
def icon_box(fn, l, r, baseline, back=0.0):
    w = (r - l) * Z
    h = w * art(fn).height / art(fn).width
    px = OX + (l - back - X0) * Z
    return px, px + w, baseline - h, baseline

n0 = icon_box('3147940218.webp', 463.6, 555.6, 1040)
n1 = icon_box('3147940218.webp', 463.6, 555.6, 1040, back=3.0)
yy = n0[2] - 34
dr.line([(n1[0], yy), (n0[0], yy)], fill=(255, 170, 80, 255), width=3)
dr.polygon([(n0[0], yy), (n0[0] - 9, yy - 6), (n0[0] - 9, yy + 6)], fill=(255, 170, 80, 255))
dr.text((n0[0] - 4, yy - 30), '+3px（本版）', font=F_SM, fill=(255, 170, 80, 255))

img.save('/workspace/底栏效果-v3.7.66.png')
print('saved')
