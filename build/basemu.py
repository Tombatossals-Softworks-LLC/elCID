import re, cidspec as S

# ---- parse ALL data from elcid.bas exactly as the BASIC READs it ----
order=[]  # list of (lineno, [tokens]) preserving DATA order
for raw in open('../elcid-c64d.bas'):
    s=raw.strip()
    m=re.match(r'^(\d+)\s+data\s+(.*)$', s, re.I)
    if m:
        order.append((int(m.group(1)), m.group(2)))
order.sort(key=lambda x:x[0])

# Flatten DATA stream into a token list (strings stay strings, ints become ints)
# Mimic BASIC: read mixes numbers and strings. We tokenize per-line respecting quotes.
def toks(line):
    out=[]; i=0
    while i<len(line):
        c=line[i]
        if c=='"':
            j=line.index('"',i+1); out.append(('s',line[i+1:j])); i=j+1
            # skip following comma/space
            while i<len(line) and line[i] in ', ': i+=1
        elif c in ', ':
            i+=1
        else:
            j=i
            while j<len(line) and line[j] not in ',': j+=1
            t=line[i:j].strip()
            if t!='': out.append(('n',int(t)))
            i=j+1
    return out

stream=[]
for ln,body in order:
    stream.extend(toks(body))

pos=0
def rd():
    global pos
    v=stream[pos]; pos+=1; return v
def rdn():
    t=rd(); assert t[0]=='n', t; return t[1]
def rds():
    t=rd(); assert t[0]=='s', t; return t[1]

# line 10: nr,ni,nu
nr=rdn(); ni=rdn(); nu=rdn()
# line 12: for j=1 to nr*2+ni+nu: read z$  (skip room names/descs, item names, rule msgs as strings)
for _ in range(nr*2+ni+nu): rds()
# line 13: item names in$(1..ni)
inm=[None]+[rds() for _ in range(ni)]
# line 14: exits ex%(j,1..6)
ex={}
for j in range(1,nr+1):
    for d in range(1,7):
        ex[(j,d)]=rdn()
# line 15: il%(j),it%(j)
il={}; it={}
for j in range(1,ni+1):
    il[j]=rdn(); it[j]=rdn()
# line 16: rules ru%(0..nu-1, 0..12)  (emitted stable-sorted by room)
ru={}
for j in range(0,nu):
    for d in range(0,13):
        ru[(j,d)]=rdn()
# line 17: rs%(1..nr) first-rule-of-room index (consume; scan order is already
# the DATA order here, so the index changes nothing for the emulator)
for j in range(0,nr):
    rdn()
# line 20: the ML blitter bytes sit where the old art table lived; consume the
# numeric run (the verbs section that follows starts with a string token)
while pos < len(stream) and stream[pos][0]=='n':
    rdn()
# line 31-32: verbs until "*"
vb={}
while True:
    t=rd()
    if t[0]=='s' and t[1]=='*': break
    w=t[1]; cd=rdn(); vb[w]=cd
# line 35-36: nouns until "*"
no={}
while True:
    t=rd()
    if t[0]=='s' and t[1]=='*': break
    w=t[1]; cd=rdn(); no[w]=cd

# ---- engine state ----
class B:
    def __init__(self):
        self.rm=1; self.fl=[0]*65; self.il=dict(il); self.gw=0; self.last=''
    def dirof(self,w):
        if w in ('n','norte'): return 1
        if w in ('s','sur'): return 2
        if w in ('e','este'): return 3
        if w in ('o','oeste'): return 4
        if w in ('sube','arriba'): return 5
        if w in ('baja','abajo'): return 6
        return 0
    def do(self,cmd):
        if self.gw: return
        c=cmd.strip()
        parts=c.split(' ',1)
        w1=parts[0]
        rest=parts[1] if len(parts)>1 else ''
        w2=rest.split(' ',1)[0] if rest else ''
        va=vb.get(w1,0); ob=no.get(w2,0)
        dv=self.dirof(w1)
        if va==5: dv=self.dirof(w2)
        # rule interpreter (700)
        hd=0
        for ri in range(0,nu):
            if ru[(ri,0)]!=self.rm: continue
            if ru[(ri,1)]!=va: continue
            if ru[(ri,2)]!=0 and ru[(ri,2)]!=ob: continue
            t=ru[(ri,3)]
            if t>0 and self.fl[t]==0: continue
            t=ru[(ri,4)]
            if t>0 and self.fl[t]==0: continue
            t=ru[(ri,5)]
            if t>0 and self.fl[t]==0: continue
            t=ru[(ri,6)]
            if t>0 and self.fl[t]==1: continue
            t=ru[(ri,11)]
            if t>0 and self.il.get(t)!=-1: continue
            t=ru[(ri,7)]
            if t>0: self.fl[t]=1
            t=ru[(ri,8)]
            if t>0: self.il[t]=-1
            t=ru[(ri,9)]
            if t>0: self.il[t]=-1
            t=ru[(ri,10)]
            if t>0: self.il[t]=0
            self.last='RULE%d'%ri; hd=1
            if ru[(ri,12)]==1: self.gw=2
            if ru[(ri,12)]==2: self.gw=1
            break
        if hd==1: return
        # movement (680) with gates
        if dv>0:
            dr=dv
            if self.rm==11 and dr==3:
                if self.fl[5]==0 or self.il.get(5)!=-1:
                    self.last='GATE_DUERO'; self.gw=2; return
            if self.rm==17 and dr==3:
                if self.fl[10]==0:
                    self.last='GATE_LEVANTE'; return
            nx=ex.get((self.rm,dr),0)
            if nx==0: self.last='no puedes ir por ahi.'; return
            self.rm=nx; self.last='->%d'%nx; return
        # generic
        if va==1:
            if ob==0: self.last='look'; return
            if 1<=ob<=ni:
                if self.il.get(ob)==self.rm or self.il.get(ob)==-1: self.last='exam'; return
                self.last='no ves eso aqui.'; return
            self.last='no ves nada de particular.'; return
        if va==2:
            if ob<1 or ob>ni: self.last='coger que?'; return
            if self.il.get(ob)==-1: self.last='ya lo llevas.'; return
            if self.il.get(ob)!=self.rm: self.last='no ves eso aqui.'; return
            if it[ob]==0: self.last='no puedes llevarte eso.'; return
            self.il[ob]=-1; self.last='coges'; return
        if va==3:
            if ob<1 or ob>ni or self.il.get(ob)!=-1: self.last='no llevas eso.'; return
            self.il[ob]=self.rm; self.last='dejas'; return
        if va==4:
            self.last='inv'; return
        if va==12: self.last='help'; return
        if va==0: self.last='no conozco ese verbo.'; return
        self.last='no puedo hacer eso ahora.'

# ---- run critical path through BASIC emu ----
path=[c.strip() for c in S.__dict__ and __import__('cidsim').CRITPATH if c.strip()]
g=B()
for c in path:
    g.do(c)
    if g.gw: break
print('BASIC-emu result: gw=%d rm=%d'%(g.gw,g.rm))
print('flags set:', [i for i in range(1,64) if g.fl[i]])

print("\n=== LOSE CONDITIONS THROUGH BASIC-EMU ===")
def runB(cmds):
    g=B()
    for c in cmds:
        g.do(c)
        if g.gw: break
    return g
import cidsim as C
tests={
 'forzar puerta': "baja|monta babieca|sube|este|este|fuerza puerta".split('|'),
 'cruzar duero sin babieca': "este|este|coge ensena|este|sur|este|sur|este".split('|'),
 'abrir arcas': "este|este|este|mira antolinez|sur|coge arena|oeste|abre arcas".split('|'),
}
for n,c in tests.items():
    g=runB(c)
    print(' %-26s gw=%d last=%s'%(n,g.gw,g.last))
# beber pozo: set up r19
g=B(); 
for f in [1,2,3,4,5,6,7,8,9,10]: g.fl[f]=1
g.il[5]=-1; g.rm=19
g.do('bebe pozo')
print(' beber pozo sin purgar      gw=%d last=%s'%(g.gw,g.last))
# vence bucar sin tizona -> lose (rule 42)
g=B()
for f in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]: g.fl[f]=1
g.rm=26
g.do('vence bucar')
print(' vence bucar sin tizona     gw=%d last=%s'%(g.gw,g.last))
# carga a pie en r16 sin babieca -> lose (rule 25, forbid 5)
g=B(); g.rm=16
g.do('asalta')
print(' asalta r16 sin babieca     gw=%d last=%s'%(g.gw,g.last))
# reta sin espadas r29 -> lose (rule 53)
g=B(); g.rm=29
g.do('reta infantes')
print(' reta sin espadas r29       gw=%d last=%s'%(g.gw,g.last))
