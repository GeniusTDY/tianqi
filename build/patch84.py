import zipfile, json, os, collections
from PIL import Image

SRC = '/workspace/build/base83.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.84-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
A = '/workspace/work/art4/'

# 恢复原始尺寸，只把「可见内容的底边」对齐到 698
NEW = {
    '孵化UI':   ('3805034956', 100.00, 126.00, 641.06),
    '天启星盘UI': ('3168340070', 120.00, 106.00, 645.88),
    '商城UI':   ('3147940218', 137.00, 140.00, 633.00),
    '地图UI':   ('3871956625', 121.00, 116.00, 644.00),
    '信息卡':    ('2316322479', 139.00, 137.00, 643.50),
    '亚比仓库':  ('3458348368', 150.00, 140.00, 637.33),
    '亚比背包':  ('288535618', 120.00, 131.00, 638.04),
}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']
types = [t[0] for t in P[3]]
hits = collections.Counter(); scenes = set()
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7: continue
    for ly in (L[6] or []):
        if not isinstance(ly, list) or len(ly) < 15: continue
        for inst in (ly[14] or []):
            if not (isinstance(inst, list) and len(inst) > 5 and 0 <= inst[1] < len(types)): continue
            nm = types[inst[1]]
            if nm not in NEW: continue
            _, w, h, y = NEW[nm]
            inst[0][1], inst[0][3], inst[0][4] = y, w, h
            hits[nm] += 1; scenes.add(L[0])
print('场景数', len(scenes), dict(hits))
assert len(scenes) == 39 and all(v == 39 for v in hits.values()), hits

for nm, (img, w, h, y) in NEW.items():
    im = Image.open(A + img + '.webp').convert('RGBA'); a = im.split()[3]; iw, ih = im.size
    sy = h/ih
    rows = [r for r in range(ih) if any(a.getpixel((c, r)) >= 128 for c in range(iw))]
    print(f'{nm:6s} 实心底 = {y-h/2+max(rows)*sy:.3f}')

blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
with zipfile.ZipFile(OUT, 'w') as zout:
    for info in zin.infolist():
        if info.filename in SKIP: continue
        raw = zin.read(info.filename)
        if info.filename == 'assets/www/data.json':
            raw = blob; print('data.json', info.file_size, '->', len(raw))
        ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        ni.compress_type = info.compress_type
        ni.external_attr = info.external_attr
        ni.create_system = info.create_system
        zout.writestr(ni, raw)
print('written', OUT, os.path.getsize(OUT))
