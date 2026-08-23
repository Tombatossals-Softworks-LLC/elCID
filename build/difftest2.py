import sys, copy
sys.path.insert(0,'.')
import cidspec as S, cidsim as C
from basemu import B, nu, ru, ex, vb, no, it, ni, nr

# normalize: sim over -1->lose, +1->win ; emu gw 2->lose, 1->win
def sim_norm(g):
    o={-1:'LOSE',1:'WIN',0:'OK'}[g.over]
    return (g.rm,o,tuple(sorted(g.flags)),tuple(sorted(k for k,v in g.loc.items() if v==-1)))
def emu_norm(g):
    o={2:'LOSE',1:'WIN',0:'OK'}[g.gw]
    return (g.rm,o,tuple(i for i in range(1,64) if g.fl[i]),tuple(sorted(k for k,v in g.il.items() if v==-1)))

verbs=sorted(set(vb.keys()))
repnoun={}
for w,cd in no.items(): repnoun.setdefault(cd,w)
probe_nouns=['']+[repnoun[cd] for cd in sorted(repnoun)]
dirs=['norte','sur','este','oeste','sube','baja']
CP=[c.strip() for c in C.CRITPATH if c.strip()]

mism=[]
gs=C.Game(); gb=B()
def cmp_at(tag):
    for v in verbs:
        for nW in probe_nouns:
            cmd=(v+' '+nW).strip()
            s2=copy.deepcopy(gs); b2=copy.deepcopy(gb)
            s2.do(cmd); b2.do(cmd)
            if sim_norm(s2)!=emu_norm(b2):
                mism.append((tag,cmd,sim_norm(s2),emu_norm(b2)))
    for d in dirs:
        s2=copy.deepcopy(gs); b2=copy.deepcopy(gb)
        s2.do(d); b2.do(d)
        if sim_norm(s2)!=emu_norm(b2):
            mism.append((tag,d,sim_norm(s2),emu_norm(b2)))

for k,c in enumerate(CP):
    cmp_at('step%d:%s'%(k,c))
    gs.do(c); gb.do(c)
    if gs.over or gb.gw: break
print("REAL mismatches (normalized):", len(mism))
for m in mism[:40]: print(m)
