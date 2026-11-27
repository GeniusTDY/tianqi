import zipfile, json, os, collections

SRC = '/workspace/build/base85.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.86-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
DX = {'亚比仓库': +2.0, '亚比背包': +2.0}

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
            if nm not in DX: continue
            old = inst[0][0]
            inst[0][0] = round(old + DX[nm], 2)
            hits[nm] += 1; scenes.add(L[0])
            if hits[nm] == 1: print(nm, old, '->', inst[0][0], ' y', inst[0][1])
print('场景数', len(scenes), dict(hits))
assert len(scenes) == 39 and all(v == 39 for v in hits.values()), hits

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
