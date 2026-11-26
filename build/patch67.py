import zipfile, json

SRC = '/workspace/build/base66.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.67-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF'}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]

NEW_Y = 40.0
NEW_FONT = 70

changed = []
for L in P[5]:
    if not (isinstance(L, list) and L[0] == '我的家园'):
        continue
    for lay in L[6]:
        if lay[0] != '信息卡':
            continue
        for i in (lay[14] or []):
            t = T[i[1]]
            if t[0] != '信息卡文字':
                continue
            td = i[5]
            if not isinstance(td, list) or len(td) < 4:
                continue
            changed.append((td[0], i[0][0], i[0][1], td[3]))
            i[0][1] = NEW_Y
            td[3] = NEW_FONT
print('changed', changed)

blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
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
