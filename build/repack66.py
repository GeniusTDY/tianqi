import zipfile, json, sys

SRC = '/workspace/build/TianQi-Full-v3.7.65.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.66-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
NAMES = {'孵化UI', '天启星盘UI', '商城UI'}
SHIFT = 3.0

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]
patched = 0
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7:
        continue
    for lay in (L[6] or []):
        if not isinstance(lay, list) or len(lay) < 15:
            continue
        for i in (lay[14] or []):
            if isinstance(i, list) and T[i[1]][0] in NAMES:
                i[0][0] += SHIFT
                patched += 1
print('patched', patched)

blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
print('data.json size', len(blob))

with zipfile.ZipFile(OUT, 'w') as zout:
    for info in zin.infolist():
        if info.filename in SKIP:
            continue
        raw = zin.read(info.filename)
        if info.filename == 'assets/www/data.json':
            raw = blob
        ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        ni.compress_type = info.compress_type
        ni.external_attr = info.external_attr
        ni.create_system = info.create_system
        zout.writestr(ni, raw)
print('written', OUT)
