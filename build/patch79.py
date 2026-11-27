import zipfile, json, os, collections

SRC = '/workspace/build/base78.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.79-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}

NEW = {
    922: (535, 606),     # 晶币
    923: (915, 606),     # 星币
    925: (633, 606),     # 晶币数量
    926: (1013, 606),    # 星币数量
}
TITLE_X = {'信息卡': 211, '背包物品': 771.5}

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']

nscene = 0
hits = collections.Counter()
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7:
        continue
    layers = L[6] or []
    ly = [x for x in layers if isinstance(x, list) and x and x[0] == '信息卡']
    if not ly:
        continue
    nscene += 1
    for inst in ly[0][14]:
        if not isinstance(inst, list) or len(inst) < 6:
            continue
        t = inst[1]
        w = inst[0]
        if t in NEW:
            w[0], w[1] = NEW[t]
            hits[t] += 1
        elif t == 914:
            b = inst[5]
            if isinstance(b, list) and b and b[0] in TITLE_X:
                w[0] = TITLE_X[b[0]]
                hits[t] += 1
print('scenes', nscene, 'modified', dict(hits))
assert nscene == 50, nscene
assert hits[922] == 50 and hits[923] == 50 and hits[925] == 50 and hits[926] == 50 and hits[914] == 100, hits

# 归一性校验
def sig(i):
    w = i[0]; b = i[5]; t = b[0] if isinstance(b, list) and b else ''
    return (i[1], round(w[0], 1), round(w[1], 1), round(w[3], 1), round(w[4], 1), t)
groups = collections.defaultdict(list)
for L in P[5]:
    if not isinstance(L, list) or len(L) < 7: continue
    ly = [x for x in (L[6] or []) if isinstance(x, list) and x and x[0] == '信息卡']
    if not ly: continue
    groups[tuple(sorted(sig(i) for i in ly[0][14] if isinstance(i, list) and len(i) > 5))].append(L[0])
print('distinct layouts after patch:', len(groups))
for k, v in groups.items():
    for s in k:
        if s[0] in (914, 922, 923, 925, 926):
            print('   ', s)
    break

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
