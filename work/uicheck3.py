import json, collections
d = json.load(open('/workspace/work/probe/d75.json', encoding='utf-8'))['project']
T = d[3]

def tname(i):
    return T[i[1]][0] if isinstance(i[1], int) and 0 <= i[1] < len(T) else '?'
def sig(i):
    td = i[5] if len(i) > 5 else None
    txt = td[0] if isinstance(td, list) and td and isinstance(td[0], str) else ''
    f = td[3] if isinstance(td, list) and len(td) > 3 and not isinstance(td[3], list) else None
    p = i[0]
    return (tname(i), txt, round(p[0], 2), round(p[1], 2), round(p[3], 2), round(p[4], 2), f)

scenes = {}
for L in d[5]:
    if not isinstance(L, list): continue
    layers = {lay[0]: lay for lay in (L[6] or []) if isinstance(lay, list)}
    if '信息卡' in layers:
        scenes[L[0]] = layers

def show(layname, names, limit=25):
    print(f'\n==== {layname} ====')
    for n in names:
        lay = scenes[n].get(layname)
        if not lay:
            print(f'{n}: (无此图层)'); continue
        ss = sorted(sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2)
        print(f'{n}: {len(ss)} 个实例')
        for s in ss[:limit]:
            print('    ', s)

# A. UI界面：对比 10 个活动场景 vs 多数
print('\nA. UI界面 实例数量分布')
cnt = collections.Counter(len((scenes[n].get('UI界面') or [None,0,0,0,0,0,0,0,0,0,0,0,0,0,[]])[14] or []) for n in scenes)
print(cnt)
base = sorted(sig(i) for i in (scenes['奥拉广场']['UI界面'][14] or []) if isinstance(i, list) and len(i) > 2)
for n in ('冰雕广场', '回音海岸', '我的家园'):
    lay = scenes[n]['UI界面']
    ss = sorted(sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2)
    print(f'\n{n} ({len(ss)}):')
    print('  缺少:', [x for x in base if x not in ss])
    print('  多出:', [x for x in ss if x not in base])

# B. 对话框
print('\nB. 对话框 对比（奥拉广场 vs 奇灵神树 vs 白皇殿）')
for n in ('奥拉广场', '奇灵神树', '白皇殿'):
    lay = scenes[n]['对话框']
    ss = sorted(sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2)
    print(n, len(ss))
    for s in ss: print('   ', s)

# C. 孵化器界面
print('\nC. 孵化器界面 对比')
for n in ('奥拉广场', '奥拉之树'):
    lay = scenes[n]['孵化器界面']
    ss = sorted(sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2)
    print(n, len(ss))
    for s in ss: print('   ', s)

# E. 亚比仓库界面
print('\nE. 亚比仓库界面 搜索框')
for n in ('奥拉广场', '冰雕广场'):
    lay = scenes[n]['亚比仓库界面']
    for i in (lay[14] or []):
        if tname(i) == '仓库搜索输入框':
            print(n, sig(i))

# F. 亚比背包静态UI
print('\nF. 亚比背包静态UI 对比')
base = sorted(sig(i) for i in (scenes['奥拉广场']['亚比背包静态UI'][14] or []) if isinstance(i, list) and len(i) > 2)
for n in ('奥拉之树', '基因秘境'):
    ss = sorted(sig(i) for i in (scenes[n]['亚比背包静态UI'][14] or []) if isinstance(i, list) and len(i) > 2)
    print(n, '缺少', [x for x in base if x not in ss], '多出', [x for x in ss if x not in base])
