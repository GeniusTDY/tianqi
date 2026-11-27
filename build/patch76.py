import zipfile, json, os, copy

SRC = '/workspace/build/base75.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.76-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}
REF = '奥拉广场'

# 1) 底部功能栏图标：统一到主城「奥拉广场」的坐标
ICONS = {
    '亚比仓库': (941.18, 633.67),
    '亚比背包': (1077.38, 637.19),
    '信息卡': (805.69, 640.5),
    '商城UI': (514.1, 632.0),
    '地图UI': (654.4, 643.0),
    '孵化UI': (203.12, 638.42),
    '天启星盘UI': (355.31, 646.0),
    '天启之巅UI': (207.0, 61.0),
}
STAR = (784.0, 556.0)          # 信息卡·星币
SKILL = (227.0, 973.0)         # 亚比背包道具描述·局外技能 4 件套
SKILL_TYPES = {'局外技能信息查看', '局外技能名', '局外技能描述', '局外技能类型'}
SEARCH = '仓库搜索输入框'

zin = zipfile.ZipFile(SRC)
data = json.loads(zin.read('assets/www/data.json').decode('utf-8'))
P = data['project']; T = P[3]

def tname(i):
    return T[i[1]][0]

# 取参考 td（奥拉广场 仓库搜索输入框）
ref_td = None
for L in P[5]:
    if isinstance(L, list) and L[0] == REF:
        for lay in L[6]:
            if isinstance(lay, list) and lay[0] == '亚比仓库界面':
                for i in (lay[14] or []):
                    if isinstance(i, list) and len(i) > 5 and tname(i) == SEARCH:
                        ref_td = i[5]
assert ref_td is not None, 'reference search box not found'

counts = {'icon': 0, 'star': 0, 'skill': 0, 'search': 0}
layouts = set()
for L in P[5]:
    if not isinstance(L, list):
        continue
    for lay in (L[6] or []):
        if not isinstance(lay, list) or len(lay) < 15:
            continue
        lname = lay[0]
        for i in (lay[14] or []):
            if not isinstance(i, list) or len(i) < 2:
                continue
            tn = tname(i)
            if lname == 'UI界面' and tn in ICONS:
                i[0][0], i[0][1] = ICONS[tn]
                counts['icon'] += 1; layouts.add(L[0])
            elif lname == '信息卡' and tn == '星币':
                i[0][0], i[0][1] = STAR
                counts['star'] += 1; layouts.add(L[0])
            elif lname == '亚比背包道具描述' and tn in SKILL_TYPES:
                i[0][0], i[0][1] = SKILL
                counts['skill'] += 1; layouts.add(L[0])
            elif lname == '亚比仓库界面' and tn == SEARCH:
                i[5] = copy.deepcopy(ref_td)
                counts['search'] += 1; layouts.add(L[0])

print('counts', counts, 'layouts touched', len(layouts))
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
