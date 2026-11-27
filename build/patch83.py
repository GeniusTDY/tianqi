import zipfile, json, os, collections
from PIL import Image

SRC = '/workspace/build/base82.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.83-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
A = '/workspace/work/art3/'

# 名称 -> (图片, 新宽, 新高, 新y)；x 不变
NEW = {
    '孵化UI':   ('3805034956', 92.86, 117.00, 642.75),
    '天启星盘UI': ('3168340070', 127.36, 112.50, 642.75),
    '商城UI':   ('3147940218', 130.61, 133.47, 635.12),
    '地图UI':   ('3871956625', 121.54, 116.52, 642.75),
    '信息卡':    ('2316322479', 137.17, 135.20, 641.27),
    '亚比仓库':  ('3458348368', 149.12, 139.18, 634.05),
    '亚比背包':  ('288535618', 119.95, 130.94, 637.22),
}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']
types = [t[0] for t in P[3]]
hits = collections.Counter()
scenes = set()
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7:
        continue
    for ly in (L[6] or []):
        if not isinstance(ly, list) or len(ly) < 15:
            continue
        for inst in (ly[14] or []):
            if not (isinstance(inst, list) and len(inst) > 5 and 0 <= inst[1] < len(types)):
                continue
            nm = types[inst[1]]
            if nm not in NEW:
                continue
            _, w, h, y = NEW[nm]
            inst[0][1] = y
            inst[0][3] = w
            inst[0][4] = h
            hits[nm] += 1
            scenes.add(L[0])
print('场景数', len(scenes), dict(hits))
assert len(scenes) == 39 and all(v == 39 for v in hits.values()), hits

# 校验：重算可见框
bad = []
for nm, (img, w, h, y) in NEW.items():
    im = Image.open(A + img + '.webp'); bb = im.split()[3].getbbox(); iw, ih = im.size
    sx, sy = w/iw, h/ih
    t = y - h/2 + bb[1]*sy; b = y - h/2 + bb[3]*sy
    print(f'{nm:6s} 可见 y {t:.3f}~{b:.3f} 高 {b-t:.3f}')
    if abs(b-699) > 0.01 or abs((b-t)-112.5) > 0.01:
        bad.append(nm)
assert not bad, bad

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
