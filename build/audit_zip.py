import io, zipfile, urllib.request, sys

class H(io.RawIOBase):
    def __init__(self, url):
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as r:
            self.size = int(r.headers['Content-Length']); self.final = r.geturl()
        self.pos = 0
    def seekable(self): return True
    def readable(self): return True
    def seek(self, o, w=0):
        self.pos = o if w == 0 else (self.pos + o if w == 1 else self.size + o); return self.pos
    def tell(self): return self.pos
    def read(self, n=-1):
        if n < 0: n = self.size - self.pos
        if n == 0 or self.pos >= self.size: return b''
        end = min(self.pos + n, self.size) - 1
        rq = urllib.request.Request(self.final, headers={'Range': f'bytes={self.pos}-{end}'})
        with urllib.request.urlopen(rq) as r: d = r.read()
        self.pos += len(d); return d
    def readinto(self, b):
        d = self.read(len(b)); b[:len(d)] = d; return len(d)

def index(url):
    zf = zipfile.ZipFile(io.BufferedReader(H(url), buffer_size=1 << 20))
    return {i.filename: (i.file_size, i.CRC, i.compress_type) for i in zf.infolist()}, zf

A = 'https://github.com/GeniusTDY/tianqi/releases/download/'
a, za = index(A + 'v3.7.65-full-signed/TianQi-Full-v3.7.65.apk')
b, zb = index(A + 'v3.7.69-full-signed/TianQi-Full-v3.7.69.apk')
print('entries 65 =', len(a), ' 69 =', len(b))
only_a = sorted(set(a) - set(b)); only_b = sorted(set(b) - set(a))
print('only in 65:', len(only_a), only_a[:10])
print('only in 69:', len(only_b), only_b[:10])
diff = [k for k in a if k in b and a[k][:2] != b[k][:2]]
print('changed entries:', len(diff))
for k in diff[:20]:
    print(' ', k, a[k], '->', b[k])
print('data.json 65:', a.get('assets/www/data.json'))
print('data.json 69:', b.get('assets/www/data.json'))
