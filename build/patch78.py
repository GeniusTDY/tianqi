import zipfile, json, os

SRC = '/workspace/build/base77.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.78-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}

NEW_X = 435.5    # 原 461：左 66.5 / 右 66.5（面板 369~1174，方格宽 672）
NEW_Y = 89       # 原 90
NEW_PITCH = 104  # 原 106：第4行底部 473，距翻页条 493 留 20

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']

sheet = [s for s in P[6] if isinstance(s, list) and s[0] == '背包系统'][0]
blk = sheet[1][0][7][0]
target = None
for a in blk[6]:
    if isinstance(a, list) and len(a) > 5 and a[0] == -1 and a[1] == 54 and isinstance(a[5], list) \
            and len(a[5]) == 4 and a[5][0] == [4, 912]:
        target = a
assert target is not None, 'grid position action not found'
print('before:', json.dumps(target[5], ensure_ascii=False))

xe = target[5][2][1]   # [4, [0,461], [6, [...], [0,120]]]
ye = target[5][3][1]   # [4, [0,89],  [6, [...], [0,104]]]
assert xe[0] == 4 and xe[1] == [0, 461] and xe[2][2] == [0, 120], xe
assert ye[0] == 4 and ye[1] == [0, 90] and ye[2][2] == [0, 106], ye
xe[1] = [0, NEW_X]
ye[1] = [0, NEW_Y]
ye[2][2] = [0, NEW_PITCH]
print('after :', json.dumps(target[5], ensure_ascii=False))
print('cols', [NEW_X + c * 120 for c in range(6)])
print('rows', [NEW_Y + r * NEW_PITCH for r in range(4)], 'last bottom', NEW_Y + 3 * NEW_PITCH + 72)

blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
with zipfile.ZipFile(OUT, 'w') as zout:
    for info in zin.infolist():
        if info.filename in SKIP:
            continue
        raw = zin.read(info.filename)
        if info.filename == 'assets/www/data.json':
            raw = blob
            print('data.json', info.file_size, '->', len(raw))
        ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        ni.compress_type = info.compress_type
        ni.external_attr = info.external_attr
        ni.create_system = info.create_system
        zout.writestr(ni, raw)
print('written', OUT, os.path.getsize(OUT))
