import sys,urllib.request,struct
def main(url,out,member):
    req=urllib.request.Request(url,method='HEAD')
    with urllib.request.urlopen(req,timeout=60) as r:
        size=int(r.headers['Content-Length'])
    def get(a,b):
        h={'Range':f'bytes={a}-{b}'}
        with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=120) as r:
            return r.read()
    # 读 EOCD
    tail=get(max(0,size-65536),size-1)
    i=tail.rfind(b'PK\x05\x06')
    assert i>=0
    cdoff=struct.unpack('<I',tail[i+16:i+20])[0]
    cdlen=struct.unpack('<I',tail[i+12:i+16])[0]
    cd=get(cdoff,cdoff+cdlen-1)
    j=0
    while j<len(cd):
        assert cd[j:j+4]==b'PK\x01\x02',cd[j:j+4]
        nlen=struct.unpack('<H',cd[j+28:j+30])[0]
        elen=struct.unpack('<H',cd[j+30:j+32])[0]
        clen=struct.unpack('<H',cd[j+32:j+34])[0]
        off=struct.unpack('<I',cd[j+42:j+46])[0]
        comp=struct.unpack('<H',cd[j+10:j+12])[0]
        csize=struct.unpack('<I',cd[j+20:j+24])[0]
        name=cd[j+46:j+46+nlen].decode()
        if name==member:
            hdr=get(off,off+29)
            fnlen=struct.unpack('<H',hdr[26:28])[0]
            el2=struct.unpack('<H',hdr[28:30])[0]
            dataoff=off+30+fnlen+el2
            data=get(dataoff,dataoff+csize-1)
            if comp==8:
                import zlib; data=zlib.decompress(data,-15)
            open(out,'wb').write(data)
            print('saved',out,len(data)); return
        j+=46+nlen+elen+clen
    print('not found')
main(sys.argv[1],sys.argv[2],sys.argv[3])
