import json, collections
d = json.load(open('/workspace/work/probe/d75.json', encoding='utf-8'))['project']
T = d[3]

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

print('--- all layers with >1 signature ---')
for layname in sorted({lay[0] for _, ls in scenes for lay in ls}):
    sigs = collections.defaultdict(list)
    for L, layers in scenes:
        for lay in layers:
            if lay[0] != layname:
                continue
            sig = tuple(sorted(inst_sig(i) for i in (lay[14] or []) if isinstance(i, list) and len(i) > 2))
            sigs[sig].append(L[0])
    if len(sigs) <= 1:
        continue
    base = max(sigs, key=lambda s: len(sigs[s]))
    print(f'\n【{layname}】{len(sigs)} 种版本，多数版 {len(sigs[base])}/{len(scenes)}')
    for sig, ls in sorted(sigs.items(), key=lambda kv: -len(kv[1])):
        if sig == base:
            continue
        print(f'  偏离 {len(ls)}: {ls}')
        bs = set(base)
        for x in sig:
            if x not in bs:
                print('     +', x)
        for x in base:
            if x not in sig:
                print('     -', x)
