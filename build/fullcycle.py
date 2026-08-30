"""Full legendary playthrough on a real C64: play all 107 critical-path
commands, watch for OOM/errors at every step, count the 7 gesta rewards, and
capture the legendary ending — then press a key and confirm the replay loop
returns to the title.

Unlike everything else in build/, this one needs a VICE with real C64 ROMs
(Debian/Ubuntu ship VICE without them) plus xvfb-run.  When ROMs are absent the
static chain — verify.py — is what proves the game instead.

usage:  python3 fullcycle.py ../elcid.d64 6510
"""
import socket,time,subprocess,os,sys,re,signal,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import cidsim, functools
print=functools.partial(print, flush=True)
if len(sys.argv) < 3: raise SystemExit(__doc__.strip().splitlines()[-1])
DISK=sys.argv[1]; PORT=int(sys.argv[2])
signal.signal(signal.SIGALRM,lambda *a:(subprocess.run(["pkill","-9","-x","x64sc"]),print("TIMEOUT"),os._exit(0)))
signal.alarm(1500)
def drain(s):
    b=b""
    try:
        while True: b+=s.recv(65536)
    except: pass
    return b.decode("latin1")
def cmd(s,c): s.sendall((c+"\n").encode()); time.sleep(0.03); return drain(s)
def conn():
    for _ in range(30):
        try:
            s=socket.socket();s.settimeout(0.15);s.connect(("127.0.0.1",PORT));time.sleep(0.25);drain(s);return s
        except OSError: time.sleep(0.4)
    raise SystemExit("no conn")
def rd(s,a0,a1):
    out={};a=a0
    while a<=a1:
        b=min(a+0xff,a1);s.sendall(("m %04x %04x\n"%(a,b)).encode());time.sleep(0.03);buf=drain(s)
        for m in re.finditer(r'>C:([0-9a-f]{4})((?:\s+[0-9a-f]{2}){1,16})',buf,re.I):
            base=int(m.group(1),16)
            for i,t in enumerate(re.findall(r'[0-9a-f]{2}',m.group(2),re.I)): out[base+i]=int(t,16)
        a=b+1
    return out
def txt(scr,r0,r1):
    o=""
    for r in range(r0,r1+1):
        for c in range(40):
            sc=scr.get(0x0400+r*40+c,32)&0x7f
            o+=chr(64+sc) if 1<=sc<=26 else (chr(sc) if 32<=sc<=63 else " ")
    return o
def peek(s,a): return rd(s,a,a).get(a,0)
def inject_chunk(keys):
    s=conn()
    cmd(s,"> 0277 "+" ".join("%02x"%k for k in keys))
    cmd(s,"> 00c6 %02x"%len(keys)); cmd(s,"x"); s.close()
def wait_buf(tmo=5):
    t0=time.time()
    while time.time()-t0<tmo:
        s=conn(); n=peek(s,0x00c6); s.sendall(b"x\n"); s.close()
        if n==0: return
        time.sleep(0.15)
def type_cmd(t, settle=1.3):
    kb=[ord(c.upper()) if c.isalpha() else ord(c) for c in t]+[13]
    for i in range(0,len(kb),10):
        inject_chunk(kb[i:i+10]); time.sleep(0.45)
    time.sleep(settle)
def _chargen():
    for p in ["/usr/share/vice/C64/chargen-901225-01.bin",
              "/usr/lib/vice/C64/chargen-901225-01.bin",
              os.path.expanduser("~/.local/share/vice/C64/chargen-901225-01.bin")]:
        if os.path.exists(p): return open(p,"rb").read()
    for p in glob.glob("/usr/**/C64/chargen*",recursive=True): return open(p,"rb").read()
    raise SystemExit("no C64 chargen ROM found")
def snap(path):
    s=conn(); scr=rd(s,0x0400,0x07e7); col=rd(s,0xd800,0xdbe7); cmd(s,"x"); s.close()
    CH=_chargen()
    PAL=[(0,0,0),(255,255,255),(150,60,55),(120,210,205),(155,80,165),(95,175,90),(70,60,160),(220,220,130),(160,100,50),(105,80,30),(200,110,100),(90,90,90),(140,140,140),(155,230,150),(125,115,210),(170,170,170)]
    K=2;W,H=320*K,200*K;raw=bytearray(W*H*3)
    for y in range(H):
        for x in range(W):
            r,c=(y//K)//8,(x//K)//8;sc=scr.get(0x0400+r*40+c,32);co=PAL[col.get(0xd800+r*40+c,1)&15]
            bm=CH[sc*8:sc*8+8];on=bm[(y//K)%8]&(0x80>>((x//K)%8))
            raw[(y*W+x)*3:(y*W+x)*3+3]=bytes(co if on else PAL[0])
    import zlib,struct
    o=bytearray()
    for y in range(H): o.append(0);o+=raw[y*W*3:(y+1)*W*3]
    comp=zlib.compress(bytes(o),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    open(path,"wb").write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack(">IIBBBBB",W,H,8,2,0,0,0))+ch(b'IDAT',comp)+ch(b'IEND',b''))
    return scr
PATH=[c.strip() for c in cidsim.CRITPATH if c.strip()]
subprocess.run(["pkill","-9","-x","x64sc"],stderr=subprocess.DEVNULL);time.sleep(1)
subprocess.Popen(["xvfb-run","-a","x64sc","-warp","-remotemonitor","-remotemonitoraddress","ip4://127.0.0.1:%d"%PORT,"-autostart",DISK+":elcid"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(38)
inject_chunk([32]); time.sleep(5)
honra=0; crash=None
for n,c in enumerate(PATH):
    last = (n==len(PATH)-1)
    type_cmd(c, settle=3.0 if last else 1.7)
    s=conn(); scr=rd(s,0x0400,0x0427); nm=rd(s,0x0400+400,0x0400+439); s.sendall(b"x\n"); s.close(); time.sleep(0.05)
    top=txt(scr,0,0)
    if "OUT OF MEMORY" in top or "SYNTAX" in top or ("READY" in top and not last):
        crash="step %d '%s': %s"%(n,c,top.strip()); print("CRASH", crash); break
    name=txt(nm,0,0) if False else "".join(chr(64+(nm.get(0x0400+400+i,32)&0x7f)) if 1<=(nm.get(0x0400+400+i,32)&0x7f)<=26 else (chr(nm.get(0x0400+400+i,32)&0x7f) if 32<=(nm.get(0x0400+400+i,32)&0x7f)<=63 else " ") for i in range(40))
    h=name.count("/7")
    if "HONRA" in name:
        try: honra=int(name.split("HONRA")[1].strip().split("/")[0])
        except: pass
    if n%15==0 or "HONRA" in name: print("[%3d] %-16s | %s"%(n,c,name.strip()))
if not crash:
    s=conn(); scr=rd(s,0x0400,0x07e7); s.sendall(b"x\n"); s.close()
    full=txt(scr,0,24)
    print("final honra seen:", honra)
    print("legendary text present:", "LEYENDA DEL CAMPEADOR" in full or "REYES DE ESPANNA" in full)
    print("victoria present:", "VICTORIA" in full)
    inject_chunk([32]); time.sleep(4)          # dismiss the acepta message
    scr=snap("/tmp/legendary_end.png"); t1=txt(scr,0,24)
    print("legendary card text:", ("LEYENDA DEL CAMPEADOR" in t1) or ("REYES DE ESPANNA" in t1), "| victoria:", "VICTORIA" in t1)
    inject_chunk([32]); time.sleep(45)         # second key -> RUN -> title
    s=conn(); scr=rd(s,0x0400,0x07e7); s.sendall(b"x\n"); s.close()
    t2=txt(scr,0,24)
    print("replay -> title back:", "PULSA UNA TECLA, CAMPEADOR" in t2, "| READY:", "READY" in t2)
subprocess.run(["pkill","-9","-x","x64sc"],stderr=subprocess.DEVNULL)
print("DONE crash=%r"%crash)
