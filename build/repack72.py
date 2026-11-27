import zipfile, os

SRC = '/workspace/build/base71.apk'
OUT = '/workspace/build/TianQi-Full-v3.7.72-unsigned.apk'
SKIP = {'META-INF/TIANQI.SF', 'META-INF/TIANQI.RSA', 'META-INF/MANIFEST.MF',
        'META-INF/TIANQITE.SF', 'META-INF/TIANQITE.RSA'}

REPLACE = {'assets/www/index.html': '/workspace/build/index72.html'}

zin = zipfile.ZipFile(SRC)
with zipfile.ZipFile(OUT, 'w') as zout:
    for info in zin.infolist():
        if info.filename in SKIP:
            continue
        raw = zin.read(info.filename)
        if info.filename in REPLACE:
            raw = open(REPLACE[info.filename], 'rb').read()
        ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        ni.compress_type = info.compress_type
        ni.external_attr = info.external_attr
        ni.create_system = info.create_system
        zout.writestr(ni, raw)
print('written', OUT, os.path.getsize(OUT))
