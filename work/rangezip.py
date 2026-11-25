import io,struct,zipfile,sys,urllib.request,os

class HttpFile(io.RawIOBase):
    def __init__(self,url):
        self.url=url; self.pos=0
        req=urllib.request.Request(url,method='HEAD')
        with urllib.request.urlopen(req) as r:
            self.size=int(r.headers['Content-Length']); self.final=r.geturl()
    def seekable(self): return True
    def readable(self): return True
    def seek(self,off,whence=0):
        if whence==0: self.pos=off
        elif whence==1: self.pos+=off
        else: self.pos=self.size+off
        return self.pos
    def tell(self): return self.pos
    def read(self,n=-1):
        if n<0: n=self.size-self.pos
        if n==0 or self.pos>=self.size: return b''
        end=min(self.pos+n,self.size)-1
        req=urllib.request.Request(self.final,headers={'Range':f'bytes={self.pos}-{end}'})
        with urllib.request.urlopen(req) as r: data=r.read()
        self.pos+=len(data)
        return data
    def readinto(self,b):
        data=self.read(len(b))
        b[:len(data)]=data
        return len(data)

url=sys.argv[1]; out=sys.argv[2]; target=sys.argv[3]
hf=HttpFile(url)
print('remote size',hf.size,hf.final)
zf=zipfile.ZipFile(io.BufferedReader(hf, buffer_size=1<<20))
info=zf.getinfo(target)
print(target,'compress_size',info.compress_size,'file_size',info.file_size)
os.makedirs(os.path.dirname(out),exist_ok=True)
with zf.open(info) as src, open(out,'wb') as dst:
    while True:
        b=src.read(1<<20)
        if not b: break
        dst.write(b)
print('saved',out,os.path.getsize(out))
