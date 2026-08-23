#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Byte-faithful El Cid screen simulator + visual regression test.

Composites a room's scene art (rows 0-9, via rooms.py) with the text the
BASIC draws (name row 10, message rows 12-20, exits 21, items 22, prompt 23)
using the real C64 chargen ROM + palette and the game's own wrap(), so you
can SEE every screen exactly as it renders on the 40x25 display and flag any
text that overflows past row 20.

  python3 screensim.py                # render every room's description screen
                                      #   -> /tmp/elcid_screens/*.png + overflow report
  python3 screensim.py <room> <text>  # render one custom screen

Needs a C64 chargen ROM for rendering (falls back through common VICE paths);
the overflow check itself is pure Python and runs without it.  Rendering also
needs Pillow.  Neither is required by the game build."""
import sys, os, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rooms
import cidspec as S

HERE = os.path.dirname(os.path.abspath(__file__))
RM = {r["id"]: r for r in json.load(open(os.path.join(HERE, "canon.json")))["rooms"]}

def _find_chargen():
    for p in ["/usr/share/vice/C64/chargen-901225-01.bin",
              "/usr/lib/vice/C64/chargen-901225-01.bin",
              os.path.expanduser("~/.local/share/vice/C64/chargen-901225-01.bin")]:
        if os.path.exists(p): return open(p, "rb").read()
    hits = glob.glob("/usr/**/C64/chargen*", recursive=True)
    return open(hits[0], "rb").read() if hits else None
CH = _find_chargen()

PAL = [(0,0,0),(255,255,255),(154,66,66),(122,207,202),(155,80,165),(93,164,88),
       (64,49,141),(191,205,116),(155,103,57),(106,84,0),(198,116,116),(80,80,80),
       (120,120,120),(158,235,154),(122,110,214),(170,170,170)]

def norm(t):
    for a,b in zip("áéíóúñü","aeiounu"): t=t.replace(a,b)
    t=t.lower()
    t="".join(c for c in t if c in "abcdefghijklmnopqrstuvwxyz0123456789 .,!?'():-/")
    return re.sub(r"\s+"," ",t).strip()

def wrap_lines(t, w=36):
    out=[]
    for seg in norm(t).split("/"):
        line=""
        for word in seg.split(" "):
            if not word: continue
            if len(line)+len(word)+(1 if line else 0)<=w: line=(line+" "+word) if line else word
            else:
                if line: out.append(line)
                line=word
        out.append(line)
    return [x for x in out if x!=""]

def txt_sc(ch):
    if ch==' ': return 32
    if 'a'<=ch<='z': return ord(ch)-96
    if '0'<=ch<='9': return ord(ch)
    return {'.':46,',':44,'!':33,'?':63,':':58,'/':47,'-':45,"'":39,'(':40,')':41,'>':62}.get(ch,32)

def build(rid, text, kind="msg", items=None, cmd=""):
    """Returns (cells 25x40 of (screencode,colour), overflow_lines)."""
    cells=[[(32,0)]*40 for _ in range(25)]
    def put(row,col,s,co):
        for i,c in enumerate(s):
            if 0<=col+i<40: cells[row][col+i]=(txt_sc(c),co)
    g=rooms.ROOMS[rid]().grid
    for r in range(10):
        for c in range(40): cells[r][c]=g[r][c]
    put(10,1,norm(RM[rid]["name"])[:38],7)
    lines=wrap_lines(text); overflow=lines[9:]
    co=15 if kind=="desc" else 7
    for i,l in enumerate(lines[:9]): put(12+i,1,l,co)
    DIRW={"n":"norte ","s":"sur ","e":"este ","o":"oeste ","u":"arriba ","d":"abajo "}
    ex="".join(DIRW[k] for k in ("n","s","e","o","u","d") if k in RM[rid]["exits"])
    put(21,1,("salidas: "+ex)[:38],3)
    if items is None: items=[S.ITEMS[i][0] for i in S.ROOMITEMS.get(rid,[])]
    if items: put(22,1,("ves: "+" ".join(items))[:38],13)
    put(23,1,">"+cmd,14)
    return cells, overflow

def render(cells, path, K=3):
    assert CH, "no C64 chargen ROM found; cannot render"
    from PIL import Image
    W,H=40*8*K,25*8*K; img=Image.new("RGB",(W,H)); px=img.load()
    for r in range(25):
        for c in range(40):
            sc,co=cells[r][c]; bm=CH[sc*8:sc*8+8]
            for yy in range(8):
                for xx in range(8):
                    rgb=PAL[co] if bm[yy]&(0x80>>xx) else PAL[0]
                    for a in range(K):
                        for b in range(K): px[(c*8+xx)*K+b,(r*8+yy)*K+a]=rgb
    img.save(path)

def render_all(outdir="/tmp/elcid_screens"):
    os.makedirs(outdir, exist_ok=True); bad=0
    for rid in range(1, S.NR+1):
        cells,ov=build(rid, S.DESC[rid], "desc")
        if CH:
            try: render(cells, os.path.join(outdir, "room_%02d.png"%rid), 2)
            except Exception as e: print("render skip:", e); return
        if ov: print("OVERFLOW room %d: lost %r"%(rid, ov)); bad+=1
    print("rendered %d room screens to %s (overflows: %d)"%(S.NR, outdir, bad))

if __name__=="__main__":
    if len(sys.argv)>=3:
        rid=int(sys.argv[1]); cells,ov=build(rid, sys.argv[2], "msg")
        render(cells, "/tmp/elcid_screen.png"); print("wrote /tmp/elcid_screen.png overflow=%r"%ov)
    else:
        render_all()
