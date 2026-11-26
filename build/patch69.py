import zipfile, json

SRC = '/workspace/build/base68.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.69-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF'}

DX = 41.0
DY = 5.0
NAMES = {'换页_上', '换页_下', '当前页数显示', '最大页数显示', '信息卡斜杠'}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]

moved = []
for L in P[5]:
    if not (isinstance(L, list) and L[0] == '我的家园'):
        continue
    for lay in L[6]:
        if lay[0] != '信息卡':
            continue
        for i in (lay[14] or []):
            n = T[i[1]][0]
            if n in NAMES:
                moved.append((n, i[0][0], i[0][1]))
                i[0][0] += DX
                i[0][1] += DY
print('moved', moved)

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
