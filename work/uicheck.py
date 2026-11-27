import json, collections
d = json.load(open('/workspace/work/probe/d75.json', encoding='utf-8'))['project']
T = d[3]

UI_LAYERS = {'信息卡', '物品信息', '称号系统', '商城界面', '功能界面放置', '任务界面', '孵化器界面', '获得物品'}

def tname(i):
    return T[i[1]][0] if isinstance(i[1], int) and 0 <= i[1] < len(T) else '?'

def inst_sig(i):
    td = i[5] if len(i) > 5 else None
    txt = td[0] if isinstance(td, list) and td and isinstance(td[0], str) else ''
    font = td[3] if isinstance(td, list) and len(td) > 3 and not isinstance(td[3], list) else None
    p = i[0]
    return (tname(i), txt, round(p[0], 2), round(p[1], 2), round(p[3], 2), round(p[4], 2), font)

scenes = []
for L in d[5]:
    if not isinstance(L, list):
        continue
    layers = [lay for lay in (L[6] or []) if isinstance(lay, list)]
    if any(lay[0] == '信息卡' for lay in layers):
        scenes.append((L, layers))

print('scenes', len(scenes))
print('sizes', collections.Counter((L[1], L[2]) for L, _ in scenes))

# layer presence
pres = collections.defaultdict(list)
for L, layers in scenes:
    for lay in layers:
        pres[lay[0]].append(L[0])
print('\n--- layer presence ---')
for name, layouts in sorted(pres.items(), key=lambda kv: -len(kv[1])):
    if len(layouts) < len(scenes):
        miss = [L[0] for L, _ in scenes if L[0] not in layouts]
        print(f'{name}: {len(layouts)}/{len(scenes)}  missing in: {miss[:8]}')

# per-layer instance signature comparison (UI layers only)
print('\n--- per-layer instance consistency ---')
for layname in sorted(pres):
    if layname not in UI_LAYERS:
        continue
    sigs = collections.defaultdict(list)
    for L, layers in scenes:
        for lay in layers:
            if lay[0] != layname:
                continue
            sig = tuple(sorted(inst_sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2))
            sigs[sig].append(L[0])
    if len(sigs) <= 1:
        print(f'{layname}: 全部一致 ({len(next(iter(sigs)))} 个实例)')
        continue
    print(f'\n{layname}: {len(sigs)} 种版本')
    base = max(sigs, key=lambda s: len(sigs[s]))
    for sig, ls in sorted(sigs.items(), key=lambda kv: -len(kv[1])):
        print(f'  版本({len(ls)}): {ls[:10]}{" ..." if len(ls) > 10 else ""}')
        if sig != base:
            bs = set(base)
            for x in sig:
                if x not in bs:
                    print('     差异实例:', x)
            for x in base:
                if x not in sig:
                    print('     缺少实例:', x)
