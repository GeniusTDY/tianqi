import zipfile, json, os

SRC = '/workspace/build/base76.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.77-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}

NEW_BASE_Y = 90      # 首行方格上沿（原 63）
NEW_ROW_GAP = 106    # 行间距（原 120），保证第4行不压翻页条

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']

sheet = [s for s in P[6] if isinstance(s, list) and s[0] == '背包系统'][0]
blk = sheet[1][0][7][0]        # 首事件下的子事件 [0,0]：“背包格子刷新”循环
target = None
for a in blk[6]:
    if isinstance(a, list) and len(a) > 5 and a[0] == -1 and a[1] == 54 and isinstance(a[5], list) \
            and len(a[5]) == 4 and a[5][0] == [4, 912]:
        target = a
assert target is not None, 'grid position action not found'

before = json.dumps(target[5], ensure_ascii=False)
yexpr = target[5][3]           # [0, [4, [0,63], [6, [...], [0,120]]]]
inner = yexpr[1]
assert inner[0] == 4 and inner[1] == [0, 63], inner
inner[1] = [0, NEW_BASE_Y]
assert inner[2][0] == 6 and inner[2][2] == [0, 120], inner[2]
inner[2][2] = [0, NEW_ROW_GAP]
after = json.dumps(target[5], ensure_ascii=False)
print('before:', before)
print('after :', after)

rows = [NEW_BASE_Y + i * NEW_ROW_GAP for i in range(4)]
print('rows top-y:', rows, 'last bottom:', rows[-1] + 72, '(翻页条上沿 493)')

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
