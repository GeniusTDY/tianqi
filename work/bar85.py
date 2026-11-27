from PIL import Image, ImageDraw, ImageFont
import glob
S = 2
A = '/workspace/work/art5/'
def im(n): return Image.open(A+n).convert('RGBA')
BAR = im('2422412522.webp')
BASE = {'孵化': ('3805034956.webp', 203.12, 641.06, 100, 126),
        '天启星盘': ('3168340070.webp', 355.31, 645.88, 120, 106),
        '商城': ('3147940218.webp', 514.1, 633.0, 137, 140),
        '地图': ('3871956625.webp', 654.4, 644.0, 121, 116),
        '信息卡': ('2316322479.webp', 805.69, 643.5, 139, 137),
        '仓库': ('3458348368.webp', 941.18, 637.33, 150, 140),
        '背包': ('288535618.webp', 1077.38, 638.04, 120, 131)}

def scene(dy):
    img = Image.new('RGBA', (int(1200*S), int(700*S)), (18, 26, 40, 255))
    bar = BAR.resize((int(1214.7*S), int(131.77*S)), Image.LANCZOS)
    img.paste(bar, (int((602-607.35)*S), int((679-65.88)*S)), bar)
    for nm, (n, cx, cy, w, h) in BASE.items():
        cy += dy.get(nm, 0)
        o = im(n).resize((int(w*S), int(h*S)), Image.LANCZOS)
        img.paste(o, (int((cx-w/2)*S), int((cy-h/2)*S)), o)
    dr = ImageDraw.Draw(img)
    dr.line([0, int(698*S), int(1200*S), int(698*S)], fill=(90, 255, 140, 210), width=1)
    return img.crop((int(130*S), int(560*S), int(1168*S), int(706*S)))

diff = {'天启星盘': -1.0, '仓库': +1.0}
a = scene({})
b = scene(diff)
cw, ch = a.size
cjk = glob.glob('/usr/share/fonts/truetype/wqy/*.ttc')
f = ImageFont.truetype(cjk[0], 28) if cjk else ImageFont.load_default()
out = Image.new('RGBA', (cw, 2*(ch+52)), (10, 12, 18, 255))
d = ImageDraw.Draw(out)
d.text((14, 10), 'v3.7.84　　天启星盘 645.88 / 仓库 637.33', font=f, fill=(200, 205, 215), anchor='la')
out.paste(a, (0, 46))
d.text((14, ch+62), 'v3.7.85　　天启星盘 644.88（上移1px） / 仓库 638.33（下移1px）', font=f, fill=(255, 225, 120), anchor='la')
out.paste(b, (0, ch+98))
out.save('/workspace/底栏-v3.7.85-效果.png')
print('ok', out.size)
