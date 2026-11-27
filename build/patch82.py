import zipfile, json, os, collections

SRC = '/workspace/build/base81.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.82-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
NEWPOS = (220, 400)   # 原 (523, 320)，400x278 居中定位

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']
n = 0
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7:
        continue
    for ly in (L[6] or []):
        if not isinstance(ly, list) or len(ly) < 15:
            continue
        for inst in (ly[14] or []):
            if isinstance(inst, list) and len(inst) > 5 and inst[1] == 1611:
                print(L[0], '/', ly[0], 'old', inst[0][0], inst[0][1], '-> new', NEWPOS)
                inst[0][0], inst[0][1] = NEWPOS
                n += 1
assert n == 1, n
print('收尾：四周留白 x', NEWPOS[0]-200, '~', NEWPOS[0]+200, ' y', NEWPOS[1]-139, '~', NEWPOS[1]+139)
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
