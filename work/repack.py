import os, sys, zipfile

SRC = "/workspace/work/slim"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tianqi-unsigned.apk"

STORE_NAMES = {"AndroidManifest.xml", "resources.arsc"}

def should_store(arc):
    if arc in STORE_NAMES:
        return True
    if arc.endswith(".so"):
        return True
    return False

entries = []
for root, dirs, files in os.walk(SRC):
    dirs.sort()
    for f in files:
        p = os.path.join(root, f)
        arc = os.path.relpath(p, SRC).replace(os.sep, "/")
        entries.append((arc, p))

def order_key(item):
    arc = item[0]
    pri = {"AndroidManifest.xml": 0, "classes.dex": 1, "resources.arsc": 2}
    return (pri.get(arc, 9), arc)

entries.sort(key=order_key)

skip_prefix = ("META-INF/TIANQI.RSA", "META-INF/TIANQI.SF", "META-INF/MANIFEST.MF")

with zipfile.ZipFile(OUT, "w", allowZip64=True) as z:
    for arc, p in entries:
        if arc in skip_prefix:
            continue
        comp = zipfile.ZIP_STORED if should_store(arc) else zipfile.ZIP_DEFLATED
        zi = zipfile.ZipInfo(arc, date_time=(2026, 11, 26, 0, 0, 0))
        zi.compress_type = comp
        zi.external_attr = 0o644 << 16
        with open(p, "rb") as fh:
            z.writestr(zi, fh.read(), compress_type=comp, compresslevel=6)

print("wrote", OUT, os.path.getsize(OUT), "entries", len(entries))
