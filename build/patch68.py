import zipfile, json

SRC = '/workspace/build/base67.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.68-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF'}
TARGET_X = 772.0

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]

changed = []
for L in P[5]:
    if not (isinstance(L, list) and L[0] == '我的家园'):
        continue
    for lay in L[6]:
        if lay[0] != '信息卡':
            continue
        for i in (lay[14] or []):
            if T[i[1]][0] != '信息卡文字':
                continue
            td = i[5]
            if isinstance(td, list) and td and td[0] == '背包物品':
                changed.append((td[0], i[0][0], i[0][1]))
                i[0][0] = TARGET_X
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
