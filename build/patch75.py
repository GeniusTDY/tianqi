import zipfile, json, os

SRC = '/workspace/build/base74.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.75-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}

# 目标：与「我的家园」已改好的信息卡一致（绝对坐标，幂等）
TITLE = {'信息卡': (None, 40.0), '背包物品': (772.0, 40.0)}  # text -> (x or None, y)
TITLE_FONT = 70
PAG = {
    '换页_上': (715.0, 521.0),
    '换页_下': (830.0, 520.0),
    '当前页数显示': (746.0, 517.0),
    '最大页数显示': (787.0, 517.0),
    '信息卡斜杠': (766.0, 518.0),
}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]

changed = []
for L in P[5]:
    if not isinstance(L, list):
        continue
    for lay in (L[6] or []):
        if not (isinstance(lay, list) and lay[0] == '信息卡'):
            continue
        for i in (lay[14] or []):
            if not isinstance(i, list) or len(i) < 2:
                continue
            tn = T[i[1]][0]
            td = i[5] if len(i) > 5 else None
            if tn == '信息卡文字':
                txt = td[0] if isinstance(td, list) and td and isinstance(td[0], str) else ''
                if txt not in TITLE:
                    continue
                nx, ny = TITLE[txt]
                if nx is not None:
                    i[0][0] = nx
                i[0][1] = ny
                if isinstance(td, list) and len(td) > 3:
                    td[3] = TITLE_FONT
                changed.append((L[0], txt, i[0][0], i[0][1], TITLE_FONT))
            elif tn in PAG:
                i[0][0], i[0][1] = PAG[tn]
                changed.append((L[0], tn, i[0][0], i[0][1]))
print('patched instances', len(changed))
layouts = sorted({c[0] for c in changed})
print('layouts touched', len(layouts))

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
