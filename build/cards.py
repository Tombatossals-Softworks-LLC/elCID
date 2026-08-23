#!/usr/bin/env python3
"""El Cid ending 'story cards' — full-screen C64/C128 multicolour bitmaps.

Three heraldic cards close the game: VICTORIA (a standard win), LEYENDA (the
legendary win, all six honour gestas found) and DERROTA (death).  They are the
same GRAPHIC-3 multicolour-bitmap format the cover (portada.kla / cidpic) uses,
so the C128's KERNAL-managed graphics mode paints them without the 40-col IRQ
reverting the VIC registers.

Self-contained (like rooms.py): draw freely with the 16-colour palette, then
legalise() to the C64 multicolour cell rule — per 4x8 cell keep the 3 shared
registers (bg, mc1, mc2) plus the single best per-cell colour (0..7).  A tiny
embedded font (the C64 uppercase glyphs, so no chargen ROM is needed at build
time) draws the labels.  emit_card() writes the three chunks each loader BLOADs:
bitmap -> $2000, GRAPHIC-3 colour screen -> $1C00, colour-RAM image -> $1300.

Run:  python3 cards.py <outdir>   # writes cv/cl/cd {bm,sc,co}.prg (+ preview PNGs)
"""
import os, sys, math, zlib, struct

# colodore-ish C64 palette (matches build/c64.py and build/rooms.py previews)
PAL = [(0,0,0),(255,255,255),(150,60,55),(120,210,205),
       (155,80,165),(95,175,90),(70,60,160),(220,220,130),
       (160,100,50),(105,80,30),(200,110,100),(90,90,90),
       (140,140,140),(155,230,150),(125,115,210),(170,170,170)]
def _d(a,b): return (a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2

# C64 uppercase glyphs (screen codes 1..26 + space), 8 bytes each — embedded so
# the build has no chargen-ROM dependency.
FONT={
  'a':[24,60,102,126,102,102,102,0], 'b':[124,102,102,124,102,102,124,0],
  'c':[60,102,96,96,96,102,60,0],    'd':[120,108,102,102,102,108,120,0],
  'e':[126,96,96,120,96,96,126,0],   'f':[126,96,96,120,96,96,96,0],
  'g':[60,102,96,110,102,102,60,0],  'h':[102,102,102,126,102,102,102,0],
  'i':[60,24,24,24,24,24,60,0],      'j':[30,12,12,12,12,108,56,0],
  'k':[102,108,120,112,120,108,102,0],'l':[96,96,96,96,96,96,126,0],
  'm':[99,119,127,107,99,99,99,0],   'n':[102,118,126,126,110,102,102,0],
  'o':[60,102,102,102,102,102,60,0], 'p':[124,102,102,124,96,96,96,0],
  'q':[60,102,102,102,102,60,14,0],  'r':[124,102,102,124,120,108,102,0],
  's':[60,102,96,60,6,102,60,0],     't':[126,24,24,24,24,24,24,0],
  'u':[102,102,102,102,102,102,60,0],'v':[102,102,102,102,102,60,24,0],
  'w':[99,99,99,107,127,119,99,0],   'x':[102,102,60,24,60,102,102,0],
  'y':[102,102,102,60,24,24,24,0],   'z':[126,6,12,24,48,96,126,0],
  ' ':[0,0,0,0,0,0,0,0],
}

class MC:
    """Multicolour canvas: 160x200 px (40x25 cells of 4x8), 16-colour palette."""
    def __init__(self, cells_w=40, cells_h=25, bg=0):
        self.W, self.H = cells_w*4, cells_h*8
        self.cw, self.ch = cells_w, cells_h
        self.bg=self.mc1=self.mc2=0
        self.px = [[bg]*self.W for _ in range(self.H)]
    def rect(self,x,y,w,h,col):
        for j in range(h):
            for i in range(w):
                if 0<=y+j<self.H and 0<=x+i<self.W: self.px[y+j][x+i]=col
    def hline(self,x,y,n,col): self.rect(x,y,n,1,col)
    def vline(self,x,y,n,col): self.rect(x,y,1,n,col)
    def dot(self,x,y,col):
        if 0<=y<self.H and 0<=x<self.W: self.px[y][x]=col
    def legalise(self, bg, mc1, mc2):
        shared=[bg,mc1,mc2]; self.bg,self.mc1,self.mc2=bg,mc1,mc2
        for cy in range(self.ch):
            for cx in range(self.cw):
                x0,y0=cx*4,cy*8
                best,bestcol=1e18,0
                for X in range(8):
                    allow=shared+[X]; err=0
                    for j in range(8):
                        for i in range(4):
                            p=PAL[self.px[y0+j][x0+i]]
                            err+=min(_d(p,PAL[a]) for a in allow)
                    if err<best: best,bestcol=err,X
                allow=shared+[bestcol]
                for j in range(8):
                    for i in range(4):
                        p=PAL[self.px[y0+j][x0+i]]
                        self.px[y0+j][x0+i]=min(allow,key=lambda a:_d(p,PAL[a]))
    def to_koala(self):
        """-> (bitmap 8000, screen 1000, colour 1000, bg) C64 multicolour chunks."""
        bg,mc1,mc2=self.bg,self.mc1,self.mc2
        bm=bytearray(8000); scr=bytearray(1000); col=bytearray(1000)
        for cy in range(25):
            for cx in range(40):
                X=0
                for y in range(cy*8,cy*8+8):
                    for x in range(cx*4,cx*4+4):
                        c=self.px[y][x]
                        if c not in (bg,mc1,mc2): X=c
                scr[cy*40+cx]=((mc1&15)<<4)|(mc2&15); col[cy*40+cx]=X&15
                for row in range(8):
                    b=0
                    for pxi in range(4):
                        c=self.px[cy*8+row][cx*4+pxi]
                        bits=0 if c==bg else (1 if c==mc1 else (2 if c==mc2 else 3))
                        b|=bits<<(6-2*pxi)
                    bm[(cy*40+cx)*8+row]=b
        return bytes(bm),bytes(scr),bytes(col),bg
    def render(self,path,scale=3):
        # multicolour pixels are double-width: 160 -> 320, then *scale
        W2,H2=self.W*2*scale, self.H*scale
        buf=bytearray(W2*H2*3)
        for y in range(self.H):
            for x in range(self.W):
                col=bytes(PAL[self.px[y][x]])
                for sy in range(scale):
                    for sx in range(2*scale):
                        X,Y=x*2*scale+sx, y*scale+sy
                        o=(Y*W2+X)*3; buf[o:o+3]=col
        raw=bytearray()
        for y in range(H2): raw.append(0); raw+=buf[y*W2*3:(y+1)*W2*3]
        comp=zlib.compress(bytes(raw),9)
        def ch(t,dd): return struct.pack(">I",len(dd))+t+dd+struct.pack(">I",zlib.crc32(t+dd)&0xffffffff)
        open(path,"wb").write(b'\x89PNG\r\n\x1a\n'
            +ch(b'IHDR',struct.pack(">IIBBBBB",W2,H2,8,2,0,0,0))+ch(b'IDAT',comp)+ch(b'IEND',b''))

# ---- drawing helpers -------------------------------------------------------
def fcircle(m,cx,cy,r,col):
    for y in range(cy-r,cy+r+1):
        for x in range(cx-r,cx+r+1):
            if (x-cx)*(x-cx)+(y-cy)*(y-cy)<=r*r: m.dot(x,y,col)
def htri(m,x,y,w,h,col,dr=1):        # filled taper (banner/pennant/crown point)
    for j in range(h):
        ww=int(w*(1-j/h)) if dr else int(w*j/h)
        m.rect(x,y+j,max(1,ww),1,col)
def band(m,y,h,cols):
    for j in range(h): m.hline(0,y+j,160,cols[min(len(cols)-1,j*len(cols)//h)])
def mtext(m,cx,y,s,col):
    """centre text s (embedded uppercase font) at row y."""
    w=len(s)*8; x0=cx-w//2
    for k,c in enumerate(s):
        g=FONT.get(c.lower(),FONT[' '])
        for yy in range(8):
            for xx in range(8):
                if g[yy]&(0x80>>xx): m.dot(x0+k*8+xx,y+yy,col)
def crown(m,cx,y,w,col=7,jewel=2):
    x0=cx-w//2; m.rect(x0,y+8,w,8,col); n=5
    for k in range(n):
        px=x0+k*(w-4)//(n-1); htri(m,px,y,6,10,col); m.dot(px+2,y,1)
    for k in range(n-1):
        jx=x0+4+k*(w-4)//(n-1); m.rect(jx,y+9,4,4,jewel)

# ---- the three cards -------------------------------------------------------
def victory():
    m=MC(40,25)
    band(m,0,200,[6,4,8])                                  # radiant golden sky
    cxs,cys=80,86
    for a in range(0,360,15):                              # sunburst rays
        for r in range(20,120,2):
            x=int(cxs+math.cos(a*math.pi/180)*r); y=int(cys+math.sin(a*math.pi/180)*r*0.7)
            m.dot(x,y,7 if (r//8)%2 else 8)
    fcircle(m,cxs,cys,26,7); fcircle(m,cxs,cys,20,1)       # blazing sun disc
    m.rect(52,30,56,80,2); m.rect(52,30,56,6,7); m.rect(52,104,56,6,7)  # red field
    for yy in range(40,104,16): m.rect(52,yy,56,3,7)       # gold bars
    m.rect(76,24,8,120,15); m.rect(78,24,4,120,1)          # Tizona blade, upright
    m.rect(70,116,20,6,7); m.rect(74,116,12,6,9)           # cross-guard (gold)
    m.rect(77,122,6,16,9); fcircle(m,80,140,5,7)           # grip + pommel
    m.rect(78,20,4,6,1)                                     # gleam at the tip
    m.rect(0,168,160,32,0); mtext(m,80,174,"VICTORIA",7)
    m.legalise(bg=0, mc1=7, mc2=2)
    return m

def legendary():
    m=MC(40,25)
    band(m,0,200,[0,6,4,6,0]); cxs=80
    for a in range(0,360,20):
        for r in range(30,130,3):
            x=int(cxs+math.cos(a*.0175)*r); y=int(70+math.sin(a*.0175)*r*0.7)
            if 0<=y<160: m.dot(x,y,7 if (r//10)%2 else 4)
    crown(m,80,20,64,7,2)                                  # great golden crown
    fcircle(m,80,44,6,7); m.dot(80,44,1)
    for dr in (1,-1):                                      # crossed white swords
        for t in range(0,90):
            x=80+int((t-45)*dr*0.9); y=70+t; m.rect(x,y,3,2,1)
        hx=80+int((90-45)*dr*0.9)
        m.rect(hx-3,158,10,4,7); m.rect(hx-1,162,4,8,7)   # gold hilts
    m.rect(48,150,64,5,7)
    m.rect(0,168,160,32,0); mtext(m,80,174,"LEYENDA",7)
    m.legalise(bg=0, mc1=7, mc2=4)
    return m

def defeat():
    m=MC(40,25)
    band(m,0,110,[0,0,6]); band(m,110,50,[6,11,2])         # cold night / grim dusk
    fcircle(m,118,104,15,2); fcircle(m,118,104,9,11)       # blood-dim sinking sun
    for rx,ry in ((34,44),(120,40),(60,26),(96,58)):       # ravens wheeling
        m.dot(rx-3,ry,0); m.dot(rx-1,ry-2,0); m.dot(rx+1,ry-2,0); m.dot(rx+3,ry,0)
    for j in range(30): m.hline(52-j,150+j,56+2*j,9)       # burial mound
    m.rect(0,176,160,24,9)
    m.rect(77,84,6,74,1); m.rect(79,84,2,74,15)            # sword thrust point-down
    m.rect(69,150,22,6,7); m.rect(76,150,8,6,11)           # cross-guard low
    m.rect(78,74,4,12,7); m.dot(80,72,1)                   # grip + pommel up top
    fcircle(m,80,108,11,11); m.rect(68,100,24,10,11)       # the Cid's helm on hilt
    m.rect(70,104,20,3,0); m.rect(78,98,4,6,2)             # visor slit + crest stub
    m.rect(0,178,160,22,0); mtext(m,80,182,"DERROTA",2)
    m.legalise(bg=0, mc1=11, mc2=9)
    return m

CARDS=[("cv",victory,"victory"),("cl",legendary,"legendary"),("cd",defeat,"defeat")]

def emit_card(m, prefix, outdir="."):
    bm,scr,col,bg=m.to_koala()
    for addr,data,suf in ((0x2000,bm,"bm"),(0x1c00,scr,"sc"),(0x1300,col,"co")):
        open(os.path.join(outdir,prefix+suf+".prg"),"wb").write(
            bytes([addr&255,addr>>8])+data)
    return bg

def build_cards(outdir=".", previews=False):
    for pfx,fn,name in CARDS:
        m=fn(); bg=emit_card(m,pfx,outdir)
        if previews: m.render(os.path.join(outdir,"card_%s.png"%name), scale=3)
        assert bg==0, "card %s expected bg 0, got %d"%(pfx,bg)
    return len(CARDS)

if __name__=="__main__":
    outdir=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(outdir,exist_ok=True)
    n=build_cards(outdir, previews=True)
    print("wrote %d cards (bm/sc/co chunks + preview PNGs) to %s"%(n,outdir))
