#!/usr/bin/env python3
"""Enhanced-PETSCII backgrounds for El Cid (32 rooms), 10x40 screen+colour.
Grid-only (no chargen needed); packed_blob()/rle_blob() feed the ML blitters.
2x2 quarter-block mosaic (all 16 PETSCII combos) gives the scenes an 80x20
subpixel "pixel art" layer on top of the cell art.  The authored look is
verified by the preview tooling and byte-proofed in VICE."""

class Grid:
    def __init__(self, rows=10, cols=40, bg=0):
        self.rows, self.cols, self.bg = rows, cols, bg
        self.grid = [[(32, bg)] * cols for _ in range(rows)]
    def set(self, r, c, sc, co):
        if 0 <= r < self.rows and 0 <= c < self.cols: self.grid[r][c] = (sc & 255, co & 15)
    def rect(self, r, c, w, h, sc, co):
        for y in range(h):
            for x in range(w): self.set(r+y, c+x, sc, co)
        return self
    def hline(self, r, c, n, sc, co):
        for x in range(n): self.set(r, c+x, sc, co)
        return self
    def vline(self, r, c, n, sc, co):
        for y in range(n): self.set(r+y, c, sc, co)
        return self
    def cell(self, r, c, sc, co): self.set(r, c, sc, co); return self
    def mset(self, sy, sx, co):
        """set one 80x20 subpixel (mosaic layer; merges with mosaic glyphs)"""
        if not (0 <= sy < self.rows*2 and 0 <= sx < self.cols*2): return
        r, c = sy >> 1, sx >> 1
        bit = (8, 4, 2, 1)[(sy & 1)*2 + (sx & 1)]
        cur = MINV.get(self.grid[r][c][0], 0)
        self.set(r, c, MOS[cur | bit], co)
    def mclear(self, sy, sx):
        """clear one subpixel (cuts shapes: crescents, arches)"""
        if not (0 <= sy < self.rows*2 and 0 <= sx < self.cols*2): return
        r, c = sy >> 1, sx >> 1
        bit = (8, 4, 2, 1)[(sy & 1)*2 + (sx & 1)]
        cur = MINV.get(self.grid[r][c][0], 0)
        nc = cur & ~bit
        self.set(r, c, MOS[nc], self.grid[r][c][1])

class Sil:
    """A black-silhouette mask drawn at 80x20 subpixel resolution.  apply(s)
    composites it over whatever is already painted: full cells go black,
    partial cells get the INVERSE mosaic glyph inked in the cell's own
    background colour — clean subpixel silhouette edges over any sky bands."""
    def __init__(self): self.m = [[0]*80 for _ in range(20)]
    def px(self, sy, sx):
        if 0 <= sy < 20 and 0 <= sx < 80: self.m[sy][sx] = 1
    def rect(self, sy, sx, w, h):
        for y in range(sy, sy+h):
            for x in range(sx, sx+w): self.px(y, x)
    def disc(self, cy, cx, r):
        for y in range(cy-r, cy+r+1):
            for x in range(cx-r, cx+r+1):
                if (x-cx)**2 + (y-cy)**2 <= r*r: self.px(y, x)
    def tri(self, apex_y, apex_x, base_y, half_w):
        """isoceles triangle, apex up (gables, spires, tents)"""
        h = base_y - apex_y
        for y in range(apex_y, base_y+1):
            w = int(half_w * (y - apex_y) / max(1, h))
            for x in range(apex_x - w, apex_x + w + 1): self.px(y, x)
    def apply(self, s):
        for r in range(10):
            for c in range(40):
                pat = (self.m[r*2][c*2]*8 + self.m[r*2][c*2+1]*4 +
                       self.m[r*2+1][c*2]*2 + self.m[r*2+1][c*2+1])
                if pat == 0: continue
                if pat == 15: s.set(r, c, 32, 0); continue
                base = self.grid_bg(s, r, c)
                s.set(r, c, MOS[15 - pat], base)
    @staticmethod
    def grid_bg(s, r, c):
        code, col = s.grid[r][c]
        return col if code != 32 else 0

# 2x2 subpixel mosaic: pattern bits UL=8 UR=4 LL=2 LR=1 -> PETSCII quarter
# blocks (the missing combos are the reverse-video complements).
MOS = {0:32, 8:126, 4:124, 2:123, 1:108, 12:226, 3:98, 10:97, 5:225,
       9:127, 6:255, 14:236, 13:251, 11:252, 7:254, 15:160}
MINV = {v: k for k, v in MOS.items()}

def HiresScene(rows=10, cols=40, bg=0): return Grid(rows, cols, bg)
FULL,LH,RH,LOW,UP=160,97,225,98,226
QUL,QUR,QLL,QLR=126,124,123,108
CHK,VL,VSLIT,HL=102,93,221,64
DTL,DTR=77,78
CIRC,BALL=87,81
# colours: 0blk 1wht 2red 3cyn 5grn 6blu 7yel 8org 9brn 11dgry 12mgry 13lgrn 14lblu 15lgry

def sky(s, r=5, col=14):
    s.rect(0,0,40,r,FULL,col)

def vivar():
    """Dawn of the exile. Solid dawn bands; manor and oak as clean subpixel
    silhouettes cut against the sky; a great sun-dome on the horizon and the
    Cid riding east across it. Black is the ink."""
    s=HiresScene(10,40,0)
    # --- dawn bands (violet -> rose -> ember), land black from row 5 ---
    s.rect(0,0,40,2,FULL,4)
    s.rect(2,0,40,2,FULL,10)
    s.rect(4,0,40,2,FULL,8)
    s.rect(6,0,40,4,FULL,0)
    # --- the sun-dome on the horizon, right of centre ---
    for w,rr in ((7,3),(9,4),(11,5)):                    # stacked dome rows
        s.rect(rr,30-(w//2),w,1,FULL,7)
    s.mclear(6,54); s.mclear(6,66)                       # rounded crown shoulders
    # --- silhouettes: manor + tower, the lone oak, far hills ---
    si=Sil()
    si.rect(6,18,22,4)                                   # manor main mass
    si.tri(3,26,6,7)                                     # west gable
    si.rect(2,34,4,8)                                    # the square tower
    si.rect(1,35,2,1)                                    # tower cap
    si.rect(4,4,2,12)                                    # oak trunk
    si.disc(4,6,4); si.disc(3,11,3); si.disc(5,13,3)     # oak canopy masses
    si.disc(11,72,3); si.disc(11,78,4)                   # far hill shoulders
    si.apply(s)
    # --- warm accents ON the silhouettes ---
    s.cell(4,14,FULL,7)                                  # one lamp-lit window
    s.mset(3,70,2); s.mset(3,71,2); s.mset(4,71,2)       # pennant on the tower
    s.mset(2,70,15)                                      # its white spearpoint
    # --- the crow of the omen, high in the violet (black strokes) ---
    s.cell(0,6,205,4); s.cell(0,7,206,4)
    # --- the Cid on Babieca crossing the sun (negative-space rider) ---
    rid=Sil()
    rid.rect(9,57,5,1)                                   # horse body
    rid.px(9,62); rid.px(8,62)                           # neck+head
    rid.rect(7,59,1,2)                                   # rider torso
    rid.px(6,59)                                         # helm
    rid.px(10,58); rid.px(10,61)                         # legs
    rid.px(8,56)                                         # tail
    rid.apply(s)
    s.mset(5,59,15)                                      # spear point above him
    # --- ember reflections on the black plain ---
    for c in (3,9,15,25,37): s.cell(9,c,HL,9)
    s.cell(9,30,HL,8)
    return s

def valencia():
    s=HiresScene(10,40,0)
    sky(s,4,14)
    sun(s,0,4,7)
    s.cell(1,30,RH,15); s.cell(1,31,LH,15)              # cloud
    # the white alcazar / city walls, rows 1-6
    s.rect(1,6,28,6,FULL,1)                              # white walls
    s.rect(1,6,28,1,LOW,15)                              # lit cap
    s.vline(1,6,6,RH,15); s.vline(1,33,6,LH,12)          # edges
    # merlons
    for i in range(6,34,4): s.cell(0,i,FULL,1); s.cell(0,i+2,FULL,14)
    # horseshoe-arched windows (Moorish)
    for wx in (10,17,24):
        s.cell(3,wx,74,6); s.cell(3,wx+1,75,6)          # arch top
        s.rect(4,wx,2,2,FULL,6)                          # dark opening
    # tall mirador tower on the right
    s.rect(0,32,5,9,FULL,1); s.vline(0,32,9,RH,15)
    for i in (0,2,4): s.cell(0,32+i,FULL,1);
    s.cell(2,34,74,6); s.cell(3,34,FULL,6)               # tower window
    # the Cid's banner atop the tower
    s.vline(0,37,3,VL,1); s.cell(0,38,FULL,2); s.cell(0,39,DTR,2)
    # the sea below the walls
    s.rect(6,0,40,4,FULL,6)
    s.hline(6,0,40,UP,14)                                # bright waterline
    for c in range(0,40,4): s.cell(7,c,DTR,14); s.cell(8,c+2,DTL,14)   # wavelets
    _REC.append(("w", 7))                            # harbour sparkle
    # two palms flanking
    for px in (2,36):
        s.vline(2,px,4,VL,9); s.cell(1,px-1,DTL,5); s.cell(1,px,FULL,5); s.cell(1,px+1,DTR,5)
    return s

def corpes():
    """The oak wood of Corpes at night.  Cold moonlit blue behind a wall of
    gnarled black trunks; the two daughters, pale, abandoned at their feet."""
    s=HiresScene(10,40,0)
    # --- cold night: black above, one deep-blue moonlit gap in the trees ---
    s.rect(2,0,40,4,FULL,6)
    s.cell(0,10,46,15); s.cell(1,3,46,12); s.cell(0,25,46,12)   # stars
    s.cell(1,36,46,15)
    s.cell(1,29,BALL,15)                                 # cold moon
    # --- the oaks: lean trunks against the moonlit gap, arms in the dark ---
    si=Sil()
    for tx in (6,62):                                    # flanking oaks
        si.rect(4,tx,2,8)                                # trunk
        si.px(11,tx-1); si.px(11,tx+2)                   # root flare
        si.rect(6,tx+2,2,1); si.rect(5,tx+4,2,1)         # rising right arm
        si.rect(7,tx-3,3,1); si.px(8,tx-4)               # drooping left arm
    si.rect(4,37,3,8)                                    # the great oak
    si.px(11,36); si.px(11,40)                           # its root flare
    si.rect(5,40,2,1); si.rect(4,42,2,1)                 # great arms
    si.rect(5,34,3,1); si.rect(4,32,2,1)
    si.rect(4,0,1,8); si.rect(4,78,2,8)                  # edge trunks
    si.disc(11,22,2); si.disc(11,52,2)                   # understory bushes
    si.rect(12,0,80,8)                                   # forest floor darkness
    si.apply(s)
    # --- dona Elvira y dona Sol, pale at the great oak's foot ---
    s.mset(12,34,1)                                      # Elvira: head
    s.mset(13,33,1); s.mset(13,34,1)                     # huddled body
    s.mset(14,33,1); s.mset(14,34,1); s.mset(14,35,1)
    s.mset(12,43,10)                                     # Sol: head
    s.mset(13,43,10); s.mset(13,44,10)                   # huddled body
    s.mset(14,42,10); s.mset(14,43,10); s.mset(14,44,10)
    # --- cold glints of moonlight on the leaf litter ---
    for c,co in ((5,11),(14,15),(23,11),(33,15),(38,11)): s.cell(8,c,HL,co)
    s.cell(9,18,HL,11); s.cell(9,29,HL,11)
    return s

def cardena():
    """San Pedro de Cardena at dawn — the Cid takes leave of dona Jimena
    and his daughters.  The monastery a black Romanesque mass against the
    first light, its bell-tower cross the highest thing; lamps lit within,
    dark cypresses standing guard, one small figure at the great door."""
    s=HiresScene(10,40,0)
    # --- dawn bands: violet, rose, a seam of gold at the horizon ---
    s.rect(0,0,40,2,FULL,4)
    s.rect(2,0,40,1,FULL,10)
    s.rect(3,0,40,1,FULL,8)
    # --- the sun rising in the clear sky, right of the church ---
    for w,rr in ((7,1),(9,2)):
        s.rect(rr,32-(w//2),w,1,FULL,7)
    s.mclear(2,56); s.mclear(2,71)
    # --- the monastery as one black silhouette on the horizon ---
    ch=Sil()
    ch.rect(7,8,40,3)                                   # long low nave
    ch.tri(4,20,7,9)                                    # gabled roof over the crossing
    ch.rect(1,12,7,7)                                   # the bell tower, piercing the sky
    ch.rect(0,13,3,5)                                   # belfry cap
    for cx in (2,74): ch.rect(5,cx,3,9); ch.disc(4,cx+1,3)   # flanking cypresses
    ch.apply(s)
    # --- the white cross crowning the bell tower ---
    s.vline(0,7,2,VL,1); s.cell(0,6,LOW,1); s.cell(0,8,LOW,1)
    # --- lamps lit within: the belfry and a row of arched windows ---
    s.cell(2,7,FULL,7)                                  # belfry lamp
    for wx in (12,16,20,24,28): s.cell(4,wx,FULL,8)    # nave windows aglow
    # --- the dim stone courtyard before the church ---
    s.rect(5,0,40,5,FULL,11); s.hline(5,0,40,UP,0)     # forecourt, dark sill
    for c in range(1,40,4): s.cell(9,c,VSLIT,11)       # flagstone seams
    # --- the great portal, warm-lit, dona Jimena in the doorway ---
    s.cell(5,19,FULL,8); s.cell(5,20,FULL,8)           # lit arched door
    s.mclear(10,38); s.mclear(10,41)                   # round its top
    s.cell(6,20,BALL,1); s.cell(7,20,FULL,2)           # small figure: pale head, red mantle
    # --- dawn glints on the flagstones ---
    for c in (3,9,30,36): s.cell(8,c,HL,15)
    return s

def mercado():
    s=HiresScene(10,40,0)
    sky(s,3,14); sun(s,0,35,7)
    # timber-framed houses behind
    for hx,rc in ((2,2),(14,8),(28,2)):
        s.rect(3,hx,10,4,FULL,15)                       # plaster
        for i in range(11): s.cell(2,hx+i,DTR if i<5 else DTL,rc)   # roof
        s.vline(3,hx,4,VL,9); s.vline(3,hx+9,4,VL,9); s.hline(5,hx,10,HL,9)  # timber
        s.rect(4,hx+3,2,2,FULL,0); s.rect(4,hx+6,2,2,FULL,0)        # windows
    # ground / cobbles
    s.rect(7,0,40,3,FULL,9); s.hline(7,0,40,LOW,8)
    for c in range(1,40,3): s.cell(9,c,VSLIT,9)
    # market stalls with striped awnings
    for sx,c1,c2 in ((3,2,1),(15,5,7),(27,6,1)):
        for i in range(9): s.cell(6,sx+i,LOW,c1 if i%2 else c2)     # awning stripes
        s.vline(7,sx,2,VL,9); s.vline(7,sx+8,2,VL,9)               # posts
        s.rect(7,sx+2,5,1,FULL,8)                                   # goods on the counter
    # a well in the middle
    s.rect(7,20,3,2,FULL,12); s.cell(6,21,HL,9); s.vline(5,21,2,VL,9)
    # a couple of townsfolk
    s.cell(6,12,BALL,8); s.cell(7,12,FULL,4)
    s.cell(6,24,BALL,8); s.cell(7,24,FULL,5)
    return s

def duero():
    """The ford of the Duero at dusk — the exile crosses into the land of
    the Moors.  A wide river burning with the last light; the far bank a
    low black shore with a lone watchtower; the Cid and Babieca black
    against the bright water, the lance held high."""
    s=HiresScene(10,40,0)
    # --- dusk sky: violet into rose over the far bank ---
    s.rect(0,0,40,2,FULL,4)
    s.rect(2,0,40,2,FULL,10)
    # --- the low sun resting on the horizon, centre ---
    for w,rr in ((9,1),(11,2),(11,3)):
        s.rect(rr,20-(w//2),w,1,FULL,7)
    s.mclear(2,30); s.mclear(2,49)                       # round the crown
    # --- the far bank: one low black shore, a lone watchtower left ---
    fb=Sil()
    fb.rect(8,0,80,2)                                    # the dark shoreline
    fb.rect(5,10,3,3)                                    # watchtower shaft
    fb.rect(4,10,1,1); fb.rect(4,12,1,1)               # its crenellations
    fb.apply(s)
    # --- the river, dark blue, and the sun's gold road across it ---
    s.rect(5,0,40,5,FULL,6)
    s.rect(5,16,8,5,FULL,8)                              # broad gold road
    s.hline(5,16,8,FULL,7)                               # brightest at the waterline
    for c in range(0,40,4): s.cell(6,c,HL,14)          # ripples
    _REC.append(("w", 6))                               # river sparkle animates
    for c in (1,3,37,38): s.vline(7,c,2,VL,5)          # reeds at the near bank
    # --- the Cid fording on Babieca, black on the sun's gold road ---
    rid=Sil()
    rid.rect(12,36,10,2)                               # horse body
    rid.rect(10,44,2,2); rid.px(9,45)                  # neck + head
    rid.rect(9,38,2,2)                                 # rider torso
    rid.px(8,38)                                        # helm
    for lx in (37,40,43,45): rid.px(14,lx); rid.px(15,lx)   # legs wading
    rid.px(12,34); rid.px(11,34)                       # streaming tail
    for yy in range(2,10): rid.px(yy,40)               # the lance, a black spear
    rid.apply(s)
    s.mset(1,40,15)                                     # its white point above the sun
    return s

def cortes():
    """The court at Toledo — the trial of the Infantes de Carrion.  A
    great dim hall; cold light falls from the high windows onto the king
    enthroned in gold, while the assembled nobles wait in shadow and the
    Cid's cause is heard."""
    s=HiresScene(10,40,0)
    # --- the dim great hall: dark stone, black frieze above ---
    s.rect(0,0,40,8,FULL,11)
    s.rect(0,0,40,1,FULL,0); s.hline(1,0,40,LOW,9)      # cornice
    # --- high windows letting in cold daylight ---
    for wx in (5,32):
        s.cell(1,wx,74,14); s.cell(1,wx+1,75,14); s.rect(2,wx,2,2,FULL,14)
        s.vline(2,wx,2,VL,0); s.vline(2,wx+1,2,VL,0)    # mullions
    # --- tall columns framing the dais, lit on the throne side ---
    for cx in (11,28):
        s.vline(1,cx,7,FULL,12); s.vline(1,cx,7,RH,15)  # shaft, lit left edge
        s.cell(1,cx,LOW,1); s.cell(7,cx,UP,9)           # capital + base
    # --- crimson tapestries on the side walls ---
    for bx in (2,36):
        s.rect(1,bx,2,5,FULL,2); s.hline(1,bx,2,LOW,7)
        s.cell(6,bx,DTL,2); s.cell(6,bx+1,DTR,2)        # frayed hem
    # --- the royal dais, brightly lit: the spotlight of the scene ---
    s.rect(7,15,10,1,FULL,7); s.rect(6,16,8,1,FULL,15)  # two gilded steps
    # the high-backed throne
    s.rect(2,18,4,5,FULL,7); s.vline(2,18,5,RH,15); s.vline(2,21,5,LH,9)
    s.rect(2,19,2,3,FULL,2)                             # crimson backing
    s.cell(1,18,QUL,7); s.cell(1,21,QUR,7)              # finials
    s.cell(4,17,LH,7); s.cell(4,22,RH,7)               # armrests
    # the king, crowned, seated in the light
    s.cell(3,20,BALL,8); s.cell(2,20,LOW,7)            # head + gold crown
    s.cell(4,20,FULL,1)                                # white robe
    # --- two ranks of nobles waiting in shadow ---
    for fx in (5,8,31,34): s.cell(6,fx,BALL,9); s.cell(7,fx,FULL,0)
    # --- the tiled floor, catching light only at the centre ---
    for c in range(40):
        lit = 15 if 14 <= c <= 25 else 11
        s.cell(8,c,FULL,(lit if c%2 else 0)); s.cell(9,c,FULL,(0 if c%2 else lit))
    return s

# ---------- reusable helpers ----------
ARL,ARR=74,75
def H(): return HiresScene(10,40,0)
def ground(s,r=8,col=5,hi=13):
    s.rect(r,0,40,10-r,FULL,col); s.hline(r,0,40,LOW,hi)
def mdisc(s,cy,cx,rad,co):
    """filled disc in 80x20 subpixel coords"""
    for y in range(cy-rad, cy+rad+1):
        for x in range(cx-rad, cx+rad+1):
            if (x-cx)*(x-cx) + (y-cy)*(y-cy) <= rad*rad: s.mset(y, x, co)
def mcut(s,cy,cx,rad):
    for y in range(cy-rad, cy+rad+1):
        for x in range(cx-rad, cx+rad+1):
            if (x-cx)*(x-cx) + (y-cy)*(y-cy) <= rad*rad: s.mclear(y, x)
def sun(s,r=0,c=34,col=7):
    """2x2-cell sun, corners rounded by single-subpixel cuts (bg stays clean)"""
    if c > 37: c = 37
    s.rect(r, c, 2, 2 if r < 9 else 1, FULL, col)
    for sy, sx in ((r*2, c*2), (r*2, c*2+3), (r*2+3, c*2), (r*2+3, c*2+3)):
        s.mclear(sy, sx)
def moon(s,r=0,c=33,col=15):
    cy, cx = r*2+1, c*2+1
    mdisc(s, cy, cx, 2, col); mcut(s, cy, cx+2, 2)       # crescent (dark skies)
def mhill(s,base_r,c,rad,co):
    """rounded hilltop rising from cell-row base_r"""
    mdisc(s, base_r*2, c*2+1, rad, co)
def cloud(s,r,c,col=15):
    """solid slim cloud, corners rounded by single-subpixel cuts"""
    s.rect(r, c, 3, 1, FULL, col)
    for sy, sx in ((r*2, c*2), (r*2+1, c*2), (r*2, c*2+5), (r*2+1, c*2+5)):
        s.mclear(sy, sx)
    s.mset(r*2, c*2+2, col)
_REC = []   # animatable cells recorded while a scene builds (see anim_table)
def banner(s,r,c,fc,pole=1):
    s.vline(r,c,3,VL,pole); s.cell(r,c+1,FULL,fc); s.cell(r,c+2,DTR,fc)
    _REC.append(("p", r, c+2))                     # pennant tip: DTR<->DTL flutter
def water(s,r=6,col=6,hi=14):
    s.rect(r,0,40,10-r,FULL,col); s.hline(r,0,40,UP,hi)
    for cc in range(0,40,4): s.cell(r+1,cc,HL,hi)
    _REC.append(("w", r+1))                        # sparkle row: marching HL/space
def tent(s,r,c,fc,w=4):
    s.cell(r,c+w//2-1,DTR,fc); s.cell(r,c+w//2,DTL,fc)
    s.rect(r+1,c,w,2,FULL,fc); s.rect(r+2,c+w//2-1,2,1,FULL,0); s.vline(r,c+w//2,1,VL,1)
    dith(s,r+2,c,1,fc); dith(s,r+2,c+w-1,1,fc)           # shaded skirts
    glint(s,r,c+w//2-1)
def figure(s,r,c,body=2,head=8):
    s.cell(r,c,BALL,head); s.cell(r+1,c,FULL,body)
# --- Bitmap-Brothers-style surface kit: 3-tone bevels, dithered feet,
#     rivet studs and white edge glints (C64 steel ramp: 11 -> 12 -> 15 -> 1) ---
def dith(s,r,c,w,col):
    """checker half-tone band: fades a surface toward black"""
    for x in range(w): s.cell(r,c+x,CHK,col)
def rivets(s,r,c,w,step=3,col=11):
    """stud dots along a surface row"""
    for x in range(1,w-0,step): s.cell(r,c+x,46,col)
def glint(s,r,c):
    """white corner highlight (single subpixel)"""
    s.mset(r*2, c*2, 1)
def shade3(s,r,c,w,h,hi,mid,lo=11):
    """beveled slab: lit crown + left edge, mid body, shaded right + dithered foot"""
    s.rect(r,c,w,h,FULL,mid)
    s.hline(r,c,w,LOW,hi)
    if h>1: s.vline(r+1,c,h-1,RH,hi)
    if h>1: s.vline(r+1,c+w-1,h-1,LH,lo)
    if h>2: dith(s,r+h-1,c+1,w-2,mid)
def house(s,r,c,w,h,wall=8,roof=2):
    shade3(s,r,c,w,h,7,wall,9)
    for i in range(w+1): s.cell(r-1,c+i,DTR if i<w//2 else DTL,roof)
    glint(s,r-1,c+w//2)
def arch(s,r,c,w,h,fc,dk=0):
    s.cell(r,c,ARL,fc); s.cell(r,c+1,ARR,fc); s.rect(r+1,c,w,h,FULL,dk)
def stonewall(s,r,c,w,h,col=12):
    shade3(s,r,c,w,h,15,col,11)
    for cy in range(r+1,r+h,2):
        for cx in range(c+1,c+w,2): s.cell(cy,cx,VSLIT,col)
    if h>2: rivets(s,r+1,c,w,4,11)
    glint(s,r,c)
def merlontop(s,r,c,w,col=12,sky=14):
    for i in range(w): s.cell(r,c+i,FULL,col if i%2==0 else sky)
    for i in range(0,w,2): glint(s,r,c+i)

def road_burgos():   # 2
    s=H(); sky(s,5,14); sun(s,0,4); cloud(s,1,26)
    ground(s,7,9,8)
    # receding road (perspective) to the distant walls
    for i,r in enumerate(range(7,10)):
        w=6+i*8; s.rect(r,20-w//2,w,1,FULL,8)
    # distant Burgos walls on the horizon
    stonewall(s,5,10,20,2,12); merlontop(s,4,10,20,12,14)
    tower_h=4
    s.rect(3,22,4,4,FULL,12); merlontop(s,2,22,4,12,14)
    banner(s,2,24,2)
    for c in (2,36): s.vline(5,c,2,VL,9); s.cell(4,c,BALL,5)   # roadside trees
    return s

def stable():        # 3
    """Babieca's stall — the great bay warhorse standing proud in the
    lantern-light, the dim timber stable deep in shadow around him."""
    s=H()
    s.rect(0,0,40,10,FULL,0)                         # the dark stable
    for c in range(6,40,9): s.vline(0,c,6,VL,9)      # dim stall posts
    s.rect(0,0,40,1,FULL,9)                          # top beam
    # a lantern on a hook at the left, a warm point of light
    s.cell(1,3,BALL,7); s.vline(0,3,1,VL,9); s.cell(2,3,DTR,8)
    # a hay net on the far wall
    s.rect(2,33,3,2,CHK,9)
    # the stall's half-door
    s.rect(7,8,20,1,FULL,8); s.hline(7,8,20,LOW,7)   # lit top rail
    s.rect(8,8,20,2,FULL,9); s.vline(7,8,3,VL,8); s.vline(7,27,3,VL,8)  # door + posts
    for c in range(11,27,3): s.vline(8,c,2,VL,0)     # plank shadows
    # Babieca looking out over the door — a great bay head and neck
    s.rect(4,15,4,3,FULL,9); s.hline(4,15,4,LOW,8)   # thick neck, lit crest
    s.cell(5,14,FULL,9); s.cell(6,15,FULL,9)         # neck curving to the head
    s.rect(3,11,4,2,FULL,9)                          # the long face / jaw
    s.cell(4,10,DTL,9); s.cell(3,10,FULL,9); s.cell(4,9,BALL,9)    # muzzle + nose
    s.cell(2,13,VL,9); s.cell(2,14,VL,9)             # two pricked ears
    s.cell(3,12,BALL,1)                              # the eye, a pale glint
    s.cell(3,11,FULL,8)                              # lit cheek
    for i in range(4): s.cell(2+i,15+i,DTL,0)        # black mane down the crest
    s.cell(2,12,DTR,0)                               # forelock
    # straw on the floor
    s.rect(9,0,40,1,FULL,9)
    for c in range(2,38,3): s.cell(9,c,DTR,8)
    return s

def glera():         # 7  Glera del Arlanzon: first night of exile
    """The first night of the exile — the Cid camps on the sandy glera of
    the Arlanzon.  A cold blue night over the dark river; his tent and the
    watchfire the only warmth, the mesnada gathered close in the dark."""
    s=H()
    # --- night sky, a scatter of stars, the moon low ---
    s.rect(0,0,40,3,FULL,6)
    s.rect(0,0,40,1,FULL,0)
    for c,co in ((6,15),(14,12),(25,15),(35,12)): s.cell(0,c,46,co)
    s.cell(1,31,BALL,15)                                 # low moon
    # --- the dark river, a thread of moonlight running on it ---
    s.rect(3,0,40,1,FULL,6); s.hline(3,0,40,UP,14)
    for c in range(2,40,6): s.cell(3,c,HL,14)
    _REC.append(("w",3))                                 # moonlit river animates
    # --- the broad sand, dim under the night ---
    s.rect(4,0,40,6,FULL,11); s.hline(4,0,40,LOW,9)
    for c in range(3,38,7): s.cell(9,c,DTR,9)            # sand ripples
    # --- the Cid's tent, firelight glowing within ---
    tx=13
    for i,rr in enumerate(range(4,8)): s.rect(rr,tx+3-i,1+i*2,1,FULL,2)  # red tent
    s.vline(2,tx+3,2,VL,1); s.cell(2,tx+4,DTR,2)         # finial + pennant
    s.rect(6,tx+2,2,2,FULL,8); s.cell(6,tx+2,FULL,7)     # firelit doorway
    banner(s,3,7,5)
    # --- a watchfire, the mesnada around it as black shapes ---
    fx=25
    s.cell(6,fx,BALL,7); s.cell(7,fx,DTR,8); s.cell(7,fx+1,DTL,7)   # flames
    s.rect(8,fx-1,4,1,FULL,9)                            # embers / logs
    for gx in (22,29,32): s.cell(7,gx,BALL,0); s.cell(8,gx,FULL,0)  # seated men
    for c in (21,27,33): s.cell(8,c,HL,8)               # firelight on the sand
    return s

def plateau():       # 12 frontier plateau, watchtowers
    s=H(); sky(s,5,14); sun(s,0,4); cloud(s,1,20); cloud(s,0,30)
    # layered mesas
    s.rect(4,0,40,2,FULL,9); s.hline(4,0,40,LOW,8)
    for x in (6,22,33):                             # watchtowers on the ridge
        s.rect(2,x,3,4,FULL,11); merlontop(s,1,x,3,11,14); s.cell(3,x+1,VSLIT,11)
    ground(s,6,8,10)
    for c in range(2,38,4): s.cell(6,c,DTR,9); s.cell(8,c+2,DTL,9)  # scrub
    return s

def castejon():      # 13 Castejon dawn
    s=H()
    # dawn sky: rose to gold
    s.rect(0,0,40,2,FULL,4); s.rect(2,0,40,1,FULL,10); s.rect(3,0,40,1,FULL,8)
    s.rect(3,30,3,1,FULL,7); mdisc(s,5,62,3,7)      # rising half-sun on the horizon
    ground(s,7,9,8)
    # the little walled town, still asleep
    stonewall(s,4,8,24,3,15); merlontop(s,3,8,24,15,4)
    for wx in (12,18,24): arch(s,5,wx,2,1,15,0)     # dark windows/gates
    s.rect(4,20,4,3,FULL,15); merlontop(s,3,20,4,15,10)  # a tower
    banner(s,2,22,2)
    return s

def levante():       # 18 road to Levante, orchards, sea, sun
    s=H(); sky(s,2,14); sun(s,0,34,7); cloud(s,0,8)
    s.rect(2,0,40,1,FULL,6); s.hline(2,0,40,UP,14)  # sea at the horizon
    ground(s,3,5,13)                                # green orchard land rows 3-9
    # orange trees planted in rows on the green
    for x in range(4,38,6):
        s.vline(5,x,4,VL,9)                         # trunk into the ground
        s.rect(3,x-2,5,2,FULL,5); s.cell(2,x,BALL,5)   # leafy canopy
        s.cell(4,x-1,BALL,8); s.cell(4,x+1,BALL,8)     # oranges
    # the coast road winding through
    for i,r in enumerate(range(8,10)): s.rect(r,17-i*3,6+i*6,1,FULL,8)
    return s

# ---------- interior helpers ----------
def wall(s,col=9,fl=11,flhi=15,fr=8):
    s.rect(0,0,40,fr,FULL,col); s.rect(fr,0,40,10-fr,FULL,fl); s.hline(fr,0,40,LOW,flhi)
def chest(s,r,c,body=9,band=7):
    s.rect(r,c,4,2,FULL,body); s.hline(r,c,4,LOW,15); s.cell(r+1,c+1,BALL,band); s.cell(r+1,c+2,BALL,band)
    s.cell(r,c,ARL,band); s.cell(r,c+3,ARR,band)
def candle(s,r,c,wax=1):
    s.cell(r,c,DTR,7); s.cell(r,c,BALL,7)          # flame
    s.vline(r+1,c,2,VL,wax)

def raquel_vidas():  # 6
    """The house of Raquel and Vidas by night — the arcas de arena.  One
    candle throws its light on the two heavy chests and the money-lenders
    leaning greedily in; all else is swallowed in the dark."""
    s=H()
    s.rect(0,0,40,10,FULL,0)                         # the dark room
    for c in range(0,40,7): s.vline(0,c,8,VL,11)     # dim timber posts
    s.rect(8,0,40,2,FULL,9); s.hline(8,0,40,UP,0)   # plank floor
    for c in range(2,38,5): s.cell(9,c,VSLIT,0)      # floorboards
    # a shuttered night window, a scrap of moonlight
    s.rect(1,33,4,3,FULL,6); s.rect(1,33,4,1,FULL,0)
    s.cell(2,34,VL,0); s.cell(2,35,VL,0)             # shutter bars
    # the table and the one candle, a warm pool of light
    s.rect(6,15,11,1,FULL,9); s.hline(6,15,11,LOW,8)
    candle(s,3,20); s.cell(4,20,FULL,7); s.cell(5,20,DTR,8)   # candle + halo
    # the two arcas de arena, lids catching the light
    chest(s,4,14,9,7); chest(s,4,23,9,7)
    s.rect(4,14,4,1,LOW,8); s.rect(4,23,4,1,LOW,8)   # lids lit warm
    # Raquel and Vidas leaning in, lit from below by the flame
    s.cell(4,11,BALL,8); s.cell(5,11,FULL,2); s.cell(5,12,DTR,9)   # Raquel, red
    s.cell(4,29,BALL,8); s.cell(5,29,FULL,6); s.cell(5,28,DTL,9)   # Vidas, blue
    return s

def chapel():        # 9
    """The oratory — the Cid at prayer before he rides.  A dim stone
    chapel; the altar-cloth and the golden crucifix glow in the candle-
    light, and coloured glass burns in the little apse window."""
    s=H()
    s.rect(0,0,40,8,FULL,0)                          # the dark nave
    s.vline(0,0,8,RH,11); s.vline(0,39,8,LH,11)      # faint side walls
    # the apse arch behind the altar
    s.rect(1,15,10,5,FULL,11)
    for i in range(4): s.rect(1+i,15+i,10-2*i,1,FULL,0)     # dark arch void
    s.cell(2,18,FULL,6); s.cell(2,19,FULL,2); s.cell(2,20,FULL,4); s.cell(3,19,FULL,7)  # stained glass
    s.rect(0,19,2,1,FULL,7)                          # keystone catches light
    # the altar, white cloth glowing in the gloom
    s.rect(6,17,6,2,FULL,1); s.hline(6,17,6,LOW,15); s.rect(7,17,6,1,FULL,15)
    # the crucifix, gold above the altar
    s.vline(2,19,4,VL,7); s.hline(4,18,3,HL,7); s.cell(4,19,BALL,8)
    # two candles flanking, each a warm halo
    candle(s,5,15); candle(s,5,23); s.cell(5,15,FULL,8); s.cell(5,23,FULL,8)
    # the dark flagstone floor
    s.rect(8,0,40,2,FULL,11); s.hline(8,0,40,UP,0)
    for c in range(0,40,4): s.cell(9,c,VSLIT,0)
    return s

def cellar():        # 10
    """The cellar under the keep — tinajas of oil and wine and ranked
    sacks of grain, half-seen in the light of a single wall-torch beneath
    the dark stone vaults."""
    s=H()
    s.rect(0,0,40,8,FULL,0)                          # the dark vault
    for x in (5,17,29):                              # vault ribs, dimly lit
        s.cell(0,x,ARL,11); s.cell(0,x+1,ARR,11); s.cell(1,x,DTR,11); s.cell(1,x+1,DTL,11)
    s.rect(8,0,40,2,FULL,9); s.hline(8,0,40,UP,0)   # earth floor
    # a torch on the wall, a warm pool of light
    s.cell(1,35,BALL,7); s.cell(2,35,DTL,8); s.vline(2,36,2,VL,9)
    # rows of tinajas (great jars), lit warm on the torch side
    for jx in (5,10,15):
        s.rect(4,jx,3,3,FULL,9); s.vline(4,jx,3,RH,8); s.cell(3,jx+1,LOW,8)
        s.cell(4,jx,ARL,9); s.cell(4,jx+2,ARR,9); s.cell(5,jx+1,VSLIT,0)
    # a barrel
    s.rect(4,28,4,3,FULL,9); s.vline(4,28,3,RH,10); s.hline(5,28,4,HL,8); s.hline(6,28,4,HL,8)
    # sacks of grain
    for sx in (25,29,33): s.rect(6,sx,3,2,FULL,11); s.cell(5,sx+1,BALL,11); s.hline(6,sx,3,LOW,15)
    return s

def daughters_chamber():  # 24
    """The bright bower of dona Elvira and dona Sol in the alcazar — a great
    loom by a window onto the garden, the two young noblewomen at their
    weaving, an open arca of fine cloth and the gold wedding-cloak, the Cid's
    arms hung on the warm plaster."""
    s=H(); wall(s,8,9,15,7)                          # warm plaster chamber, wood floor
    s.vline(0,0,7,RH,7); s.vline(0,39,7,LH,9)
    s.hline(0,0,40,LOW,7)                            # warm cornice
    # an arched window onto the garden — blue daylight, a green tree beyond
    arch(s,1,3,4,3,15,14); s.rect(2,3,4,2,FULL,14)
    s.rect(4,3,4,1,FULL,5); s.cell(3,4,BALL,13)      # garden hedge + a tree beyond
    s.cell(2,4,VL,1); s.cell(2,6,VL,1)               # window mullions
    # a rich hanging tapestry of the Cid's arms
    s.rect(1,32,4,4,FULL,2); s.hline(1,32,4,LOW,7)
    s.cell(2,33,BALL,7); s.cell(4,32,DTL,2); s.cell(4,35,DTR,2)   # blazon + fringe
    # the great loom, warp strung, cloth growing on it
    s.rect(1,24,6,5,FULL,9); s.hline(1,24,6,LOW,8); s.hline(5,24,6,UP,8)  # frame+beams
    for c in range(25,29): s.vline(2,c,3,VL,15)      # warp threads
    s.rect(4,25,4,1,FULL,2); s.cell(5,26,BALL,7)     # woven red cloth + shuttle
    # the two young noblewomen seated at their weaving
    s.cell(5,21,BALL,8); s.cell(6,21,FULL,2); s.cell(7,21,DTL,2)   # Elvira, red gown
    s.cell(5,23,BALL,8); s.cell(6,23,FULL,6); s.cell(7,23,DTR,6)   # Sol, blue gown
    # an open arca of fine cloth, the gold wedding-cloak folded within
    s.rect(5,13,7,2,FULL,9); s.hline(5,13,7,LOW,15)  # chest body + lit rim
    s.rect(4,13,7,1,FULL,11)                          # raised lid
    s.rect(6,14,5,1,FULL,7); s.cell(6,16,BALL,3)     # gold cloak + a fold of silk
    return s

def treasury():      # 25
    """The treasury of Valencia — Tizona bright on the wall between the
    shields, the arcas brimming with gold, all lit by two torches in the
    deep dark of the vault."""
    s=H()
    s.rect(0,0,40,8,FULL,0)                          # the dark vault
    s.vline(0,0,8,RH,11); s.vline(0,39,8,LH,11)      # faint side walls
    s.rect(8,0,40,2,FULL,9); s.hline(8,0,40,UP,0)   # stone floor
    # two torches, warm pools of light
    s.cell(1,4,BALL,7); s.cell(2,4,DTR,8)
    s.cell(1,35,BALL,7); s.cell(2,35,DTL,8)
    # Tizona mounted, the blade catching the torchlight
    s.cell(0,20,DTR,15); s.vline(1,20,4,VL,15)       # point + blade
    s.hline(4,19,3,HL,7); s.cell(5,20,FULL,7); s.cell(6,20,BALL,9)  # guard, grip, pommel
    # shields flanking the sword
    s.rect(2,14,3,3,FULL,2); s.vline(2,14,3,RH,10); s.cell(1,15,DTR,7); s.cell(3,15,BALL,7)
    s.rect(2,24,3,3,FULL,6); s.vline(2,24,3,RH,14); s.cell(1,25,DTR,7); s.cell(3,25,BALL,7)
    # open arcas spilling gold, lit warm
    for cx in (5,30):
        chest(s,6,cx,9,7); s.rect(5,cx,4,1,FULL,7); s.cell(5,cx+1,BALL,7); s.cell(5,cx+3,BALL,7)
    for c in (12,15,22,27): s.cell(9,c,BALL,7)       # loose coins on the floor
    return s

def spring():        # 30
    """The cold spring among the ferns, past the oak wood.  Dawn filters
    green-gold through the high leaves; black oaks frame a mossy glade where
    Felez Munoz kneels to revive dona Elvira and dona Sol with water carried
    in his hat."""
    s=H()
    # --- green-gold dawn glimpsed through the high oak leaves ---
    s.rect(1,0,40,3,FULL,5)                              # leaf-lit green behind
    s.rect(4,0,40,1,FULL,13)                             # brighter glade floor-light
    for c,co in ((11,7),(20,13),(29,7)): s.cell(1,c,BALL,co)   # sun-flecks in the leaves
    # --- the black oak canopy overhead and two trunks framing the glade ---
    si=Sil()
    si.rect(0,0,80,2)                                    # dense canopy at the very top
    for x in range(0,80,5): si.rect(2,x,3,1)             # ragged hanging leaf-fringe
    si.rect(2,4,3,9); si.rect(2,73,3,9)                  # the two framing trunks
    si.px(3,3); si.px(4,8); si.px(3,76); si.px(4,71)     # low boughs
    si.apply(s)
    # --- the mossy floor of the glade ---
    s.rect(7,0,40,3,FULL,0); s.hline(7,0,40,UP,5)        # dark moss, soft grassy edge
    # --- ferns crowding either side of the spring ---
    for c in (2,7,32,37):
        s.cell(7,c,VL,5); s.cell(6,c-1,DTR,13); s.cell(6,c+1,DTL,13); s.cell(8,c,DTL,5)
    # --- the cold spring: a stone basin brimming with bright water ---
    s.rect(5,14,12,2,FULL,3); s.hline(5,14,12,UP,14)     # cyan water + cool rim
    s.hline(4,14,12,LOW,12); s.cell(4,14,DTR,12); s.cell(4,25,DTL,12)  # grey stone lip
    for c in range(16,25,3): s.cell(5,c,HL,1)            # cold glints
    s.cell(6,19,BALL,3)                                  # water welling over the lip
    # --- Felez Munoz kneeling with his brimming hat, a daughter to each side ---
    s.cell(4,20,BALL,8); s.cell(5,20,FULL,11); s.cell(4,21,LOW,15)   # knight + tipping hat
    s.cell(7,11,BALL,8); s.cell(6,11,DTL,7); s.cell(8,11,FULL,7)     # Elvira, gold gown
    s.cell(7,28,BALL,8); s.cell(6,28,DTR,1); s.cell(8,28,FULL,1)     # Sol, white gown
    return s

# ---------- more helpers ----------
def horse(s,r,c,col=8,tack=2):
    s.rect(r,c,5,1,FULL,col)                        # body
    s.cell(r,c-1,DTL,col)                           # tail
    s.cell(r,c+5,FULL,col); s.cell(r-1,c+5,BALL,col); s.cell(r-1,c+4,LH,9)  # neck+head+mane
    s.vline(r+1,c+1,2,VL,col); s.vline(r+1,c+4,2,VL,col)   # legs
    s.rect(r,c+1,3,1,FULL,tack)                     # saddle/caparison
def pine(s,r,c,h,col=5,tc=9):
    for i in range(h): s.rect(r+i,c-i,1+2*i,1,FULL,col)
    s.vline(r+h,c,2,VL,tc)
def spears(s,r,c,n,col=15,pt=1):
    for i in range(n): s.vline(r,c+i*2,3,VL,col); s.cell(r-1,c+i*2,DTR,pt)

def loot():          # 14
    """The spoils of Castejon heaped in the open field — gold spilling from
    an arca, stacked silver, bolts of Moorish silk, a rack of captured lances
    and the richly caparisoned corcel; the Cid's fifth set apart for the king."""
    s=H(); sky(s,3,14); sun(s,0,4); cloud(s,1,28)
    ground(s,4,5,13)                                # green field the spoils are heaped on
    banner(s,1,35,2)
    # the captured Moorish horse, richly caparisoned, right of the heap
    horse(s,5,29,8,4); s.cell(4,34,BALL,7)          # jewelled bridle glint
    # an open arca, gold spilling onto the grass
    chest(s,6,2,9,7); s.rect(5,2,4,1,FULL,7); s.cell(5,3,BALL,15)   # lid up, gold within
    for c in (2,5,7): s.cell(8,c,BALL,7)           # loose coins in the grass
    # a stack of silver plate and cups
    s.cell(6,9,BALL,15); s.cell(6,10,BALL,1); s.hline(7,9,2,LOW,12)
    # three bolts of Moorish silk, rolled, their ends catching the sun
    for c,co in ((12,2),(14,4),(16,6)):
        s.vline(6,c,2,FULL,co); s.cell(6,c,BALL,15)     # bright roll-end
    # a rack of captured lances, and a round shield leaned against it
    spears(s,4,20,3,15,2)
    s.cell(7,25,CIRC,6); s.cell(7,25,DTR,7)         # shield rim + boss glint
    return s

def alcocer():       # 15
    """Alcocer, the hill town won by the feigned retreat.  A dark hill
    fort crowned with towers stands black against a bright morning; the
    river Jalon curls bright around its foot, the Cid's banner high."""
    s=H()
    # --- bright morning sky ---
    s.rect(0,0,40,4,FULL,14)
    cloud(s,0,7,15); cloud(s,1,31,15)
    sun(s,0,34,7)
    # --- the green motte the town stands on ---
    for i,r in enumerate(range(4,8)):
        w=18+i*6; s.rect(r,20-w//2,w,1,FULL,5)
    s.hline(4,11,18,LOW,13)                             # sunlit crest
    for c in range(3,38,5): s.cell(7,c,DTR,13)         # grassy tufts
    # --- the fortress crown, black on the sky, merlons biting the blue ---
    hf=Sil()
    hf.rect(4,24,32,3)                                  # curtain wall on the crest
    for k in range(24,56,4): hf.rect(3,k,2,1)          # merlons against the sky
    hf.rect(1,26,6,4); hf.rect(0,27,4,1)               # keep tower (left)
    hf.rect(2,48,5,3); hf.rect(1,49,3,1)               # gate tower (right)
    hf.apply(s)
    # --- lit slit-windows and the warm arched gate in the black wall ---
    s.cell(1,14,VSLIT,7)                                # keep slit
    s.cell(3,18,FULL,8); s.cell(3,28,FULL,8)           # wall windows aglow
    s.cell(3,23,FULL,8); s.mclear(6,46); s.mclear(6,47)   # the gate, arched
    s.cell(2,25,VSLIT,8)                                # gate-tower slit
    # --- the river Jalon curling bright round the foot ---
    water(s,8,6,14)
    for c in range(2,38,6): s.cell(9,c,HL,3)
    # --- the Cid's banner planted on the keep ---
    banner(s,0,14,2)
    return s

def fariz_galve():   # 16
    """The great pitched battle against Fariz and Galve.  A lurid dust-red
    sky, a wan sun choked by the haze; two hosts close as black hedges of
    lances, banners high, the riders clashing in the churning dust."""
    s=H()
    # --- blood-red dust sky ---
    s.rect(0,0,40,4,FULL,2)
    sun(s,0,3,10)                                        # a wan sun low in the dust
    # --- the dusty battlefield fills the lower half so silhouettes read ---
    s.rect(4,0,40,6,FULL,8); s.hline(4,0,40,LOW,10)     # ochre dust field
    for c in range(0,40,3): s.cell(9,c,CHK,9)           # churned earth
    # --- the enemy host on the right: black mass, lances, green banners ---
    s.rect(5,27,13,2,FULL,0)
    for x in range(28,39,2): s.vline(3,x,3,VL,0)        # their lances into the red
    banner(s,1,31,5); banner(s,1,37,5)
    # --- the Cid charging, black against the dust, lance leveled ---
    s.rect(6,9,7,1,FULL,0)                              # horse body
    s.cell(5,15,FULL,0); s.cell(4,16,BALL,0)           # neck + head, up-right
    s.cell(6,8,DTL,0)                                   # streaming tail
    s.cell(7,9,DTL,0); s.cell(7,11,VL,0); s.cell(7,13,VL,0); s.cell(7,15,DTR,0)  # galloping legs
    s.cell(5,12,FULL,0); s.cell(4,12,BALL,11)          # rider torso + helmed head (glint)
    s.hline(5,17,7,HL,15); s.cell(5,24,DTR,1)          # the steel lance, leveled
    banner(s,1,4,2)                                     # his crimson banner behind
    # --- the clash: sparks where the lance strikes home ---
    s.cell(5,25,CIRC,1); s.cell(4,25,DTL,7)
    return s

def tevar():         # 17
    """The pinewood of Tevar — the proud count of Barcelona taken in the
    dark stand of pines, his gold robes the one bright thing among the
    black trunks against a cold dusk sky."""
    s=H()
    # --- a pale cold dusk behind the wood ---
    s.rect(0,0,40,3,FULL,14)
    s.rect(2,0,40,1,FULL,15)
    # --- a tall stand of black pines ---
    pw=Sil()
    for px,ph in ((6,7),(15,6),(24,7),(33,5),(46,7),(58,6),(70,7)):
        pw.tri(9-ph,px,10,ph); pw.rect(10,px,1,3)       # crown + trunk
    pw.rect(12,0,80,8)                                  # dark forest floor
    pw.apply(s)
    for c in range(2,38,7): s.cell(9,c,DTR,9)          # needle litter
    # --- the count of Barcelona, gold-robed, taken among the trees ---
    s.cell(3,18,LOW,7); s.cell(4,18,BALL,8)            # crowned head
    s.rect(5,17,3,1,FULL,7); s.cell(6,18,FULL,7)       # gold robe
    s.cell(6,17,DTL,7); s.cell(6,19,DTR,7)             # robe hem
    # --- a mesnada guard with a levelled spear ---
    s.cell(4,23,BALL,11); s.cell(5,23,FULL,0); s.vline(3,24,3,VL,15)
    return s

def camp():          # 21
    s=H(); sky(s,4,14); sun(s,0,34); cloud(s,1,10)
    ground(s,7,5,13)
    # rows of the Cid's tents
    for (tx,c) in ((3,1),(11,7),(27,1),(34,6)):
        for i,rr in enumerate(range(4,8)): s.rect(rr,tx+3-i,1+i*2,1,FULL,c)
        s.vline(3,tx+3,1,VL,1); s.rect(6,tx+2,2,1,FULL,0)
    banner(s,2,19,2)
    # a campfire in the middle
    s.cell(7,20,DTR,8); s.cell(7,21,DTL,7); s.cell(6,20,BALL,7)
    s.rect(8,19,4,1,FULL,9)                          # logs
    return s

def bucar_camp():    # 26
    s=H(); sky(s,3,14); sun(s,0,4)
    s.rect(3,0,40,1,FULL,6); s.hline(3,0,40,UP,14)  # sea
    s.rect(4,0,40,1,FULL,8)                          # beach sand
    ground(s,7,8,15)
    # rows of Moorish tents (green & crimson, crescents)
    for (tx,c) in ((4,5),(12,2),(22,5),(31,2)):
        for i,rr in enumerate(range(4,8)): s.rect(rr,tx+3-i,1+i*2,1,FULL,c)
        s.cell(3,tx+3,87,7); s.rect(6,tx+2,2,1,FULL,0)   # crescent finial + door
    banner(s,2,17,5); banner(s,2,27,5)
    return s

def palm(s,r,c,tc=9):
    s.vline(r+1,c,4,VL,tc)
    s.cell(r,c,FULL,5); s.cell(r,c-1,DTL,5); s.cell(r,c+1,DTR,5); s.cell(r-1,c,BALL,5)

def valencia_huerta():  # 19
    s=H(); sky(s,3,14); sun(s,0,34); cloud(s,0,10)
    ground(s,4,5,13)                                # lush green huerta
    # irrigation channel (acequia) across the front
    s.rect(8,0,40,2,FULL,6); s.hline(8,0,40,UP,14)
    for c in range(0,40,4): s.cell(9,c,HL,14)
    # palms
    for px in (4,36): palm(s,3,px)
    # fruit trees in the garden
    for (x,fr) in ((12,8),(20,2),(28,8)):
        s.vline(5,x,3,VL,9); s.rect(3,x-2,5,2,FULL,5); s.cell(4,x-1,BALL,fr); s.cell(4,x+1,BALL,fr)
    # a well with a noria wheel
    s.rect(5,15,4,3,FULL,15); s.rect(5,15,4,1,FULL,9); s.cell(4,16,87,9); s.cell(5,16,VL,11)
    return s

def valencia_walls():   # 20
    """Valencia la Mayor, won at last — the white city gleaming against a
    deep blue sky, marble towers and domes, the Cid's crimson banners on
    every crown, and the golden gate thrown open in welcome."""
    s=H()
    # --- deep blue sky so the white marble gleams; sea at the foot ---
    s.rect(0,0,40,8,FULL,6)
    sun(s,0,35,7); s.cell(2,7,BALL,15)                  # sun + a gull
    # --- the white curtain wall between the towers ---
    s.rect(5,0,40,3,FULL,1); s.hline(5,0,40,LOW,15)
    for i in range(0,40,3): s.cell(4,i,FULL,1)          # merlons
    for wx in range(4,37,5): s.cell(6,wx,VSLIT,6)       # slit windows
    # --- two great flanking towers, marble-white, domed ---
    for tx in (0,35):
        s.rect(2,tx,5,5,FULL,1); s.vline(2,tx,5,RH,15); s.vline(2,tx+4,5,LH,12)
        s.cell(1,tx+1,QUL,15); s.cell(1,tx+2,FULL,15); s.cell(1,tx+3,QUR,15)   # dome
        s.cell(3,tx+2,VSLIT,6); s.cell(5,tx+2,VSLIT,6)  # tower windows
        s.vline(0,tx+2,1,VL,1); s.cell(0,tx+3,FULL,2); s.cell(1,tx+3,DTR,2)    # crimson banner
    # --- the central gatehouse, tallest, the golden gate open in welcome ---
    s.rect(2,15,10,6,FULL,1); s.hline(2,15,10,LOW,15)
    s.vline(2,15,6,RH,15); s.vline(2,24,6,LH,12)
    for i in range(15,25,2): s.cell(1,i,FULL,1)         # gatehouse merlons
    s.cell(5,18,74,7); s.cell(5,21,75,7); s.rect(5,19,2,3,FULL,7)  # gilt arch surround
    s.rect(6,19,2,2,FULL,0)                             # the open dark way in
    s.cell(3,17,VSLIT,6); s.cell(3,22,VSLIT,6)          # gatehouse windows
    s.vline(0,20,2,VL,1); s.cell(0,21,FULL,2); s.cell(0,22,DTR,2); s.cell(1,21,FULL,7)  # keep banner
    # --- the sea gleaming at the city's feet ---
    water(s,8,14,3)
    return s

def beach_fleet():      # 23
    """Bucar's great fleet stands in from Africa at dawn — a host of black
    lateen sails on a burning sea, come to wrest Valencia back again."""
    s=H()
    # --- dawn over the sea: violet, rose, a seam of gold ---
    s.rect(0,0,40,2,FULL,4)
    s.rect(2,0,40,1,FULL,10)
    s.rect(3,0,40,1,FULL,8)
    for w,rr in ((7,1),(9,2)): s.rect(rr,6-(w//2),w,1,FULL,7)   # rising sun, left
    s.mclear(2,6); s.mclear(2,17)
    # --- the fleet: black lateen sails in silhouette on the horizon ---
    fl=Sil()
    for sx,h in ((11,3),(20,4),(29,3),(38,5),(48,4),(57,3),(66,5)):
        fl.tri(8-h,sx,8,h-1)                            # the swept triangular sail
        fl.rect(8,sx,1,2)                                # the mast foot / hull
        fl.rect(9,sx-2,5,1)                             # the low black hull
    fl.apply(s)
    # --- the burning sea catching the dawn ---
    s.rect(5,0,40,5,FULL,6); s.hline(5,0,40,UP,14)
    for c in range(0,40,4): s.cell(6,c,HL,7)            # gold flecks
    s.cell(6,10,HL,8); s.cell(7,24,HL,8)
    _REC.append(("w", 6))                                # sea sparkle animates
    # --- the beach in the foreground ---
    s.rect(8,0,40,2,FULL,8); s.hline(8,0,40,LOW,7)
    for c in range(2,38,6): s.cell(9,c,DTR,9)
    return s

def tajo_meadow():      # 27
    s=H(); sky(s,3,14); sun(s,0,34); cloud(s,0,8)
    ground(s,4,5,13)
    # the river Tajo winding at the back
    s.rect(3,0,40,1,FULL,6); s.hline(3,0,40,UP,14)
    # the grand royal pavilion
    tx=15
    for i,rr in enumerate(range(2,7)): s.rect(rr,tx+4-i,1+i*2,1,FULL,4)   # purple royal tent
    s.rect(6,tx+1,8,2,FULL,4); s.hline(6,tx+1,8,LOW,7)  # tent base + gold trim
    s.rect(4,tx+2,4,2,FULL,7); s.rect(5,tx+3,2,1,FULL,0)  # gold-draped entrance
    s.vline(0,tx+4,2,VL,1); s.cell(0,tx+5,FULL,7)         # royal standard
    # flanking banners
    banner(s,4,6,2); banner(s,4,34,5)
    return s

def dueling_lists():    # 31
    """The judicial duel at the lists — the Cid's champions ride against
    the Infantes de Carrion for his honour.  Dawn over the palenque, the
    king enthroned beneath his canopy, two knights charging to the clash."""
    s=H()
    # --- dawn sky ---
    s.rect(0,0,40,2,FULL,4)
    s.rect(2,0,40,1,FULL,10)
    # --- the king's canopied stand at the back centre ---
    for i in range(10): s.cell(1,15+i,DTR if i<5 else DTL,(7 if i%2 else 2))  # striped canopy
    s.rect(2,16,8,1,FULL,8); s.hline(2,16,8,LOW,7)      # platform + gold rail
    s.cell(2,20,BALL,8); s.cell(3,20,FULL,1)            # the king, crowned, robed
    s.vline(0,15,1,VL,1); s.cell(0,16,FULL,2)           # royal standard
    # --- the lists: a green field with a sanded run ---
    s.rect(3,0,40,7,FULL,5); s.hline(3,0,40,LOW,13)
    s.rect(6,0,40,2,FULL,8); s.hline(6,0,40,UP,9)       # the sanded course
    # --- the two champions charging to the clash (black silhouettes) ---
    # left knight, charging right
    s.rect(6,6,5,1,FULL,0); s.cell(5,10,FULL,0); s.cell(6,5,DTL,0)
    s.cell(4,11,BALL,0); s.cell(5,8,FULL,0); s.cell(4,8,BALL,11)
    s.cell(7,6,DTL,0); s.cell(7,8,VL,0); s.cell(7,10,DTR,0)
    s.hline(5,12,6,HL,15); s.cell(5,17,DTR,1)          # lance leveled ->
    # right knight, charging left (mirror)
    s.rect(6,29,5,1,FULL,0); s.cell(5,29,FULL,0); s.cell(6,34,DTR,0)
    s.cell(4,28,BALL,0); s.cell(5,31,FULL,0); s.cell(4,31,BALL,11)
    s.cell(7,29,DTL,0); s.cell(7,31,VL,0); s.cell(7,33,DTR,0)
    s.hline(5,22,6,HL,15); s.cell(5,22,DTL,1)          # lance leveled <-
    # --- the clash in the centre, a burst of sparks ---
    s.cell(5,19,CIRC,1); s.cell(5,20,BALL,7); s.cell(4,19,DTL,7); s.cell(4,20,DTR,8)
    banner(s,3,2,2); banner(s,3,36,5)
    return s

def triumph():          # 32
    """Victory.  Valencia a black crown of towers against molten gold;
    the Cid's standards over every gate; the sea burning below."""
    s=H()
    # --- molten sunset: red crown, gold core, ember horizon ---
    s.rect(0,0,40,1,FULL,2)
    s.rect(1,0,40,3,FULL,7)
    s.rect(4,0,40,1,FULL,8)
    # --- the city skyline, black against the gold ---
    si=Sil()
    si.rect(10,0,80,6)                                   # wall base to the sea
    for sx in range(1,80,6): si.rect(9,sx,2,1)           # merlons bite the ember
    si.rect(3,34,12,7)                                   # the great keep
    for k in (0,5,10): si.rect(1,34+k,2,2)               # keep crenellations
    si.rect(5,10,8,5)                                    # west tower
    for k in (0,6): si.rect(4,10+k,2,1)
    si.rect(4,58,8,6)                                    # east tower
    for k in (0,6): si.rect(3,58+k,2,1)
    si.disc(8,26,3); si.disc(8,50,3)                     # mosque domes
    si.apply(s)
    # --- the standards: black poles, bold cloth ---
    s.cell(0,19,VSLIT,2); s.cell(0,20,FULL,7)            # gold over the keep
    s.cell(1,6,VSLIT,7); s.cell(1,7,FULL,2)              # crimson, west tower
    s.cell(1,30,VSLIT,7); s.cell(1,31,FULL,2)            # crimson, east tower
    # --- doves wheeling in the gold ---
    s.cell(1,13,205,7); s.cell(1,14,206,7)
    s.cell(2,26,205,7); s.cell(2,27,206,7)
    # --- the city alight with celebration: lamp-lit windows ---
    for sy,sx,co in ((11,8,7),(13,14,8),(12,20,7),(11,30,8),(6,38,7),
                     (7,41,8),(13,44,7),(12,56,8),(7,62,7),(11,70,7)):
        s.mset(sy,sx,co)
    # --- the sea below, burning with the sunset ---
    water(s,8,6,8)
    for c in (2,10,22,30,38): s.cell(9,c,HL,7)           # gold flecks
    s.cell(9,16,HL,8)
    return s

# ---- Burgos (scene 4): dusk at the shut gate ----

def burgos():
    """Nightfall at Burgos.  The city that dares not open is a black
    crenellated skyline against the last violet light; one torchlit gate,
    barred, and before it the nine-year-old girl who alone speaks."""
    s = HiresScene(10, 40, 0)
    # --- dusk bands: night above, violet, one rose seam of last light ---
    s.rect(2, 0, 40, 2, FULL, 4)
    s.rect(4, 0, 40, 1, FULL, 10)
    # --- the city as silhouette: wall, gate towers, roofs, the spire ---
    si = Sil()
    si.rect(10, 0, 80, 10)                               # curtain wall + below
    for sx in range(1, 80, 6): si.rect(9, sx, 2, 1)      # merlons bite the rose
    for tx in (8, 60):                                   # flanking gate towers
        si.rect(6, tx, 12, 14)
        for k in (0, 5, 10): si.rect(4, tx + k, 2, 2)    # tower crenellations
    si.tri(7, 26, 9, 3); si.tri(7, 52, 9, 3)             # rooftops beyond
    si.tri(6, 39, 9, 5)                                  # gatehouse pediment
    si.tri(4, 56, 9, 2)                                  # the cathedral spire
    si.apply(s)
    # --- night sky: first stars, the moon over the right tower ---
    for c, co in ((2, 15), (11, 12), (17, 15), (27, 12)): s.cell(0, c, 46, co)
    s.cell(1, 14, 46, 12); s.cell(1, 24, 46, 12)
    s.cell(0, 33, BALL, 15)                              # round moon
    # --- one candle behind the dark tower wall ---
    s.mset(7, 13, 7)
    # --- the torchlit gate, the only warmth left in the wall ---
    s.rect(5, 16, 8, 4, FULL, 8)                         # lamplit stone block
    s.mclear(10, 32); s.mclear(10, 47)                   # rounded top corners
    s.rect(6, 17, 6, 3, VSLIT, 9)                        # planked timber leaves
    s.hline(7, 17, 6, 192, 9)                            # iron-strap seam
    s.cell(7, 17, 209, 9); s.cell(7, 22, 209, 9)         # ring pulls
    for tcx, tsx in ((15, 30), (24, 49)):                # torches on the jambs
        s.cell(6, tcx, VL, 9)                            # bracket stem
        s.mset(12, tsx, 7); s.mset(12, tsx + 1, 7)       # flame base
        s.mset(11, tsx, 7); s.mset(11, tsx + 1, 7)       # flame
        s.mset(10, tsx + 1, 8)                           # ember tip
    # --- la nina de nueve annos, pale before the barred door ---
    s.mset(13, 39, 1)                                    # head
    s.mset(14, 39, 1); s.mset(15, 39, 1)                 # small body
    for sx in (38, 39, 40): s.mset(16, sx, 1); s.mset(17, sx, 1)   # skirt
    # --- torchlight pooling on the black street ---
    s.hline(9, 16, 8, UP, 8)
    s.cell(9, 15, CHK, 8); s.cell(9, 24, CHK, 8)
    s.cell(9, 12, HL, 9); s.cell(9, 27, HL, 9)
    s.cell(9, 4, HL, 11); s.cell(9, 34, HL, 11)          # far cobble glints
    # --- the royal standard over the left tower (the king's ban) ---
    banner(s, 0, 4, 2)
    return s


# ---- room number -> scene function ----
ROOMS = {1:vivar,2:road_burgos,3:stable,4:burgos,5:mercado,6:raquel_vidas,7:glera,
 8:cardena,9:chapel,10:cellar,11:duero,12:plateau,13:castejon,14:loot,15:alcocer,
 16:fariz_galve,17:tevar,18:levante,19:valencia_huerta,20:valencia_walls,21:camp,
 22:valencia,23:beach_fleet,24:daughters_chamber,25:treasury,26:bucar_camp,
 27:tajo_meadow,28:corpes,29:cortes,30:spring,31:dueling_lists,32:triumph}

# ============================================================================
#  Packed resident art + per-platform ML blitters.
#
#  Every room is 600 bytes: 400 screen codes + 200 colour bytes (two 4-bit
#  cells per byte, even cell in the high nibble) -> 19 200 bytes for all 32.
#  Both machines keep the WHOLE set resident and paint a room with a ~10 ms
#  machine-code blit, so a room change never touches the disk:
#    C128: the blob is appended to the game PRG itself at ART128 (bank 0 RAM
#          above the program; BASIC variables live in bank 1, so it is safe).
#    C64:  three files bulk-LOADed once at boot into RAM the BASIC interpreter
#          cannot reach: under the BASIC ROM ($A000), under the KERNAL ($E000)
#          and the free block at $C100.
# ============================================================================

# C128: the art rides RLE-compressed in one contiguous stretch at $A000
# (ends < $D000, clear of the I/O window the blit's $3E bank maps in, and the
# whole PRG ends ~$CF90 — loading much past that wedges the C128's post-load
# machinery, found empirically). Layout: 32 x 2-byte stream offsets, then the
# per-room streams (screen RLE to 400 bytes, then packed-colour RLE to 200).
ART128 = 0xA000
C64_A, C64_B, C64_C = 0xA000, 0xE000, 0xC1E0   # C64 art regions (13+13+6 rooms)
C64_SPLIT = (13, 26)     # rooms 1-13 -> A, 14-26 -> B, 27-32 -> C

def packed_blob():
    """All 32 rooms, 600 bytes each, with a pack/unpack self-proof."""
    out = bytearray()
    for n in range(1, 33):
        g = ROOMS[n]().grid
        scr = bytes(g[r][c][0] & 255 for r in range(10) for c in range(40))
        col = [g[r][c][1] & 15 for r in range(10) for c in range(40)]
        out += scr + bytes((col[i] << 4) | col[i + 1] for i in range(0, 400, 2))
    assert len(out) == 32 * 600
    for n in range(1, 33):                      # prove unpack == authored grid
        base = (n - 1) * 600
        g = ROOMS[n]().grid
        for i in range(400):
            b = out[base + 400 + i // 2]
            nib = (b >> 4) if i % 2 == 0 else (b & 15)
            assert nib == g[i // 40][i % 40][1] & 15, "room %d cell %d" % (n, i)
            assert out[base + i] == g[i // 40][i % 40][0] & 255
    return bytes(out)

class Asm:
    """Tiny two-pass 6502 helper: labelled relative branches + 16-bit fixups."""
    def __init__(self, org): self.org, self.b, self.lab, self.fix, self.wfix = org, [], {}, [], []
    def here(self): return self.org + len(self.b)
    def l(self, name): self.lab[name] = self.here()
    def db(self, *x): self.b += [v & 255 for v in x]
    def br(self, op, target):
        self.b += [op, 0]; self.fix.append((len(self.b) - 1, target))
    def jsr(self, target):
        self.b += [0x20, 0, 0]; self.wfix.append((len(self.b) - 2, target))
    def out(self):
        for pos, t in self.fix:
            off = self.lab[t] - (self.org + pos + 1)
            assert -128 <= off <= 127, t
            self.b[pos] = off & 255
        for pos, t in self.wfix:
            a = self.lab[t]
            self.b[pos], self.b[pos + 1] = a & 255, a >> 8
        return bytes(self.b)

def rle(data):
    out = bytearray(); i = 0
    while i < len(data):
        j = i
        while j < len(data) and j - i < 255 and data[j] == data[i]: j += 1
        out += bytes((j - i, data[i])); i = j
    return bytes(out)

def rle_blob():
    """C128 art: offset table (32 x 2 LE absolute addrs) + per-room streams.
    Each stream: RLE of the 400 screen codes, then RLE of the 200 packed
    colour bytes (runs never cross the phase boundary). Verified by re-
    expansion against packed_blob()."""
    blob = packed_blob()
    streams = []
    for n in range(32):
        room = blob[n*600:(n+1)*600]
        streams.append(rle(room[:400]) + rle(room[400:]))
    out = bytearray()
    pos = ART128 + 64
    for s in streams:
        out += bytes((pos & 255, pos >> 8)); pos += len(s)
    for s in streams: out += s
    assert ART128 + len(out) < 0xD000, hex(ART128 + len(out))
    # self-proof: expand every stream back
    for n in range(32):
        base = out[n*2] | (out[n*2+1] << 8)
        i = base - ART128
        dec = bytearray()
        while len(dec) < 600:
            ln, v = out[i], out[i+1]; i += 2
            dec += bytes([v]) * ln
        assert bytes(dec) == blob[n*600:(n+1)*600], "room %d rle" % (n+1)
    return bytes(out)

def anim_table():
    """5 bytes/room: pennant1 row,col, pennant2 row,col, water sparkle row
    ($FF = none). Cells come from the scene builders' own recordings."""
    out = bytearray()
    for n in range(1, 33):
        del _REC[:]
        g = ROOMS[n]().grid
        pens = [(r, c) for k, r, c in [e if len(e) == 3 else (e[0], e[1], -1) for e in _REC]
                if k == "p"][:2]
        wrow = next((e[1] for e in _REC if e[0] == "w"), None)
        for r, c in pens:
            assert g[r][c][0] & 255 == DTR, "room %d pennant cell mismatch" % n
            out += bytes((r, c))
        out += b"\xff\xff" * (2 - len(pens))
        out += bytes((wrow,)) if wrow is not None else b"\xff"
    assert len(out) == 160
    return bytes(out)

def _anim_code(a, tab_addr):
    """Append the animator to Asm a. IN: $FB=rm(1..32), $FC=tick(0/1).
    Flutters up to 2 pennant tips (DTR<->DTL) and marches the water sparkle
    row (HL/space alternating by tick). Touches only screen RAM: no banking,
    so it is IRQ-safe as-is on both machines."""
    a.l("anim")
    a.db(0xA5, 0xFB, 0x38, 0xE9, 0x01, 0x85, 0xFA)      # (rm-1) -> $FA
    a.db(0x0A, 0x0A, 0x18, 0x65, 0xFA, 0xAA)            # X = (rm-1)*5
    for _ in range(2):                                   # two pennant slots
        a.db(0xBD, tab_addr & 255, tab_addr >> 8)        # LDA tab,X   (row|$FF)
        a.db(0x85, 0xFA, 0xE8)                           # STA $FA; INX
        a.db(0xBD, tab_addr & 255, tab_addr >> 8, 0xE8)  # LDA tab,X   (col); INX
        a.jsr("psw")
    a.db(0xBD, tab_addr & 255, tab_addr >> 8)            # LDA tab,X   (water row)
    a.db(0x85, 0xFA, 0xC9, 0xFF)
    a.br(0xF0, "adone")
    a.db(0xA9, 0x00)                                     # col 0
    a.jsr("addr")
    a.db(0xA5, 0xFC, 0x85, 0xF9)                         # phase = tick
    a.db(0xA0, 0x00)                                     # LDY #0
    a.l("wl")
    a.db(0xA5, 0xF9, 0x29, 0x01)
    a.br(0xD0, "w32")
    a.db(0xA9, 0x40)                                     # HL (64)
    a.br(0xD0, "ws")
    a.l("w32"); a.db(0xA9, 0x20)                         # space
    a.l("ws"); a.db(0x91, 0xFD)                          # STA (dst),Y
    a.db(0xE6, 0xF9)
    a.db(0x98, 0x18, 0x69, 0x04, 0xA8)                   # Y += 4
    a.db(0xC0, 0x28)
    a.br(0x90, "wl")
    a.l("adone"); a.db(0x60)                             # RTS
    a.l("psw")                                           # A=col, $FA=row|$FF
    a.db(0x48, 0xA5, 0xFA, 0xC9, 0xFF)
    a.br(0xD0, "ps1")
    a.db(0x68, 0x60)                                     # skip slot
    a.l("ps1"); a.db(0x68)                               # PLA col
    a.jsr("addr")
    a.db(0xA0, 0x00, 0xB1, 0xFD, 0xC9, 0x4E)             # DTR?
    a.br(0xD0, "ps2")
    a.db(0xA9, 0x4D, 0x91, 0xFD, 0x60)                   # -> DTL
    a.l("ps2"); a.db(0xC9, 0x4D)
    a.br(0xD0, "ps3")
    a.db(0xA9, 0x4E, 0x91, 0xFD)                         # -> DTR
    a.l("ps3"); a.db(0x60)
    a.l("addr")                                          # A=col, $FA=row -> $FD/$FE = $0400+row*40+col
    a.db(0x48)                                           # PHA col
    a.db(0xA5, 0xFA, 0x0A, 0x0A, 0x0A, 0x85, 0xFD)       # row*8
    a.db(0xA9, 0x00, 0x85, 0xFE)
    a.db(0x06, 0xFD, 0x26, 0xFE, 0x06, 0xFD, 0x26, 0xFE) # *4 -> row*32 (16-bit)
    a.db(0xA5, 0xFA, 0x0A, 0x0A, 0x0A)                   # row*8 again
    a.db(0x18, 0x65, 0xFD, 0x85, 0xFD)
    a.db(0xA5, 0xFE, 0x69, 0x00, 0x85, 0xFE)             # row*40
    a.db(0x68, 0x18, 0x65, 0xFD, 0x85, 0xFD)             # + col
    a.db(0xA5, 0xFE, 0x69, 0x04, 0x85, 0xFE)             # + $0400
    a.db(0x60)

ML128 = 0x1300           # C128 blitter org (free RAM below the program)
def ml128():
    """C128 RLE blitter, one SYS per room. IN: $FB = room number (1..32).
    Banks to $3E (all bank-0 RAM + I/O), looks the room's stream up in the
    offset table at ART128, expands 400 screen codes to $0400, then expands
    200 packed colour bytes as 400 nibbles to $D800, restores bank 15.
    NMI-safe via the RAM RTI stub. ZP $F5-$FA used transiently under SEI."""
    a = Asm(ML128)
    a.db(0x78, 0xA9, 0x3E, 0x8D, 0x00, 0xFF)            # SEI; bank $3E
    a.db(0xA5, 0xFB, 0x38, 0xE9, 0x01, 0x0A, 0xA8)      # Y=(rm-1)*2
    a.db(0xB9, ART128 & 255, ART128 >> 8, 0x85, 0xF7)   # stream lo
    a.db(0xC8, 0xB9, ART128 & 255, ART128 >> 8, 0x85, 0xF8)  # stream hi
    a.db(0xA9, 0x00, 0x85, 0xFD, 0xA9, 0x04, 0x85, 0xFE)     # dst = $0400
    a.db(0xA9, 0x90, 0x85, 0xF9, 0xA9, 0x01, 0x85, 0xFA)     # remaining = 400
    a.l("srun")                                          # ---- screen phase ----
    a.jsr("pair")                                        # $F5=len,$F6=val
    a.l("s1")
    a.db(0xA5, 0xF6, 0xA0, 0x00, 0x91, 0xFD)             # write val
    a.jsr("incd")
    a.db(0xC6, 0xF5); a.br(0xD0, "s1")                   # run bytes
    a.db(0xA5, 0xF9, 0x05, 0xFA); a.br(0xD0, "srun")     # until 400 written
    # ---- colour phase: 200 packed bytes -> 400 nibbles at $D800 ----
    a.db(0xA9, 0x00, 0x85, 0xFD, 0xA9, 0xD8, 0x85, 0xFE)
    a.db(0xA9, 0xC8, 0x85, 0xF9, 0xA9, 0x00, 0x85, 0xFA)     # remaining = 200
    a.l("crun")
    a.jsr("pair")
    a.l("c1")
    a.db(0xA5, 0xF6, 0x4A, 0x4A, 0x4A, 0x4A, 0xA0, 0x00, 0x91, 0xFD)  # hi nibble
    a.jsr("incd")
    a.db(0xA5, 0xF6, 0x29, 0x0F, 0xA0, 0x00, 0x91, 0xFD)              # lo nibble
    a.jsr("incd")
    a.db(0xC6, 0xF5); a.br(0xD0, "c1")
    a.db(0xA5, 0xF9); a.br(0xD0, "crun")
    a.db(0xA9, 0x00, 0x8D, 0x00, 0xFF, 0x58, 0x60)       # bank 15; CLI; RTS
    a.l("pair")                                          # read (len,val), rem -= len
    a.db(0xA0, 0x00, 0xB1, 0xF7, 0x85, 0xF5)             # len
    a.db(0xC8, 0xB1, 0xF7, 0x85, 0xF6)                   # val
    a.db(0xA5, 0xF7, 0x18, 0x69, 0x02, 0x85, 0xF7)       # stream += 2
    a.br(0x90, "p1"); a.db(0xE6, 0xF8)
    a.l("p1")
    a.db(0xA5, 0xF9, 0x38, 0xE5, 0xF5, 0x85, 0xF9)       # remaining -= len
    a.br(0xB0, "p2"); a.db(0xC6, 0xFA)
    a.l("p2"); a.db(0x60)
    a.l("incd")                                          # dst++
    a.db(0xE6, 0xFD); a.br(0xD0, "i1"); a.db(0xE6, 0xFE)
    a.l("i1"); a.db(0x60)
    a.l("nmi"); a.db(0x40)                               # RTI (RAM NMI stub)
    tab_guess = 0
    while True:                                          # settle anim table addr
        b = Asm(ML128); b.b = list(a.b); b.lab = dict(a.lab)
        b.fix = list(a.fix); b.wfix = list(a.wfix)
        _anim_code(b, ML128 + tab_guess)
        b.l("tab")
        if b.lab["tab"] - ML128 == tab_guess: break
        tab_guess = b.lab["tab"] - ML128
    b.db(*anim_table())
    return b.out(), b.lab["nmi"], b.lab["anim"]

ML64 = 0xC000            # C64 blitter+loader org
def ml64():
    """C64 blob: SYS 49152 = KERNAL-LOAD a file (SA=1, len at $C0F7, name at
    $C0F8); SYS 49155 = blit the room at $FB/$FC. The blit banks all RAM in
    ($01=$34) to read art under the ROMs; colour writes toggle I/O back in per
    byte. NMI-safe via the RAM NMI stub (RTI) while the ROMs are out."""
    a = Asm(ML64)
    a.db(0x4C, 0x00, 0x00)                              # JMP loader (patched)
    a.l("blit")
    a.db(0x78, 0xA5, 0x01, 0x48)                        # SEI; LDA $01; PHA
    a.db(0xA9, 0x34, 0x85, 0x01)                        # all-RAM: art readable
    a.db(0xA9, 0x00, 0x85, 0xFD, 0xA9, 0x04, 0x85, 0xFE)  # dst = $0400
    a.db(0xA0, 0x00)
    a.l("s1"); a.db(0xB1, 0xFB, 0x91, 0xFD, 0xC8); a.br(0xD0, "s1")
    a.db(0xE6, 0xFC, 0xE6, 0xFE)
    a.l("s2"); a.db(0xB1, 0xFB, 0x91, 0xFD, 0xC8, 0xC0, 0x90); a.br(0xD0, "s2")
    a.db(0xA9, 0x00, 0x85, 0xFD, 0xA9, 0xD8, 0x85, 0xFE)  # dst = $D800
    a.db(0xA2, 0xC8)                                    # LDX #200
    a.l("cl")
    a.db(0xA9, 0x34, 0x85, 0x01)                        # ROMs+I/O out: read art
    a.db(0xB1, 0xFB, 0x48)                              # LDA (src),Y; PHA
    a.db(0xA9, 0x37, 0x85, 0x01)                        # I/O back in: write colour
    a.db(0x68, 0x48, 0x4A, 0x4A, 0x4A, 0x4A)            # PLA; PHA; LSR x4
    a.db(0x84, 0xFA, 0xA0, 0x00, 0x91, 0xFD)            # STY $FA; LDY #0; hi nibble
    a.db(0x68, 0x29, 0x0F, 0xC8, 0x91, 0xFD)            # PLA; AND #$0F; lo nibble
    a.db(0xA4, 0xFA, 0xC8)                              # LDY $FA; INY  (src++)
    a.br(0xD0, "ns"); a.db(0xE6, 0xFC)
    a.l("ns")
    a.db(0xE6, 0xFD); a.br(0xD0, "n1"); a.db(0xE6, 0xFE)  # dst += 2
    a.l("n1"); a.db(0xE6, 0xFD); a.br(0xD0, "n2"); a.db(0xE6, 0xFE)
    a.l("n2"); a.db(0xCA); a.br(0xD0, "cl")
    a.db(0x68, 0x85, 0x01, 0x58, 0x60)                  # PLA -> $01; CLI; RTS
    a.l("loader")                                       # SYS 49152 target
    a.l("ldnm")
    a.db(0xAD, 0x00, 0x00, 0xA2, 0x00, 0xA0, 0x00)      # LDA len; LDX/LDY name (patched)
    a.db(0x20, 0xBD, 0xFF)                              # JSR SETNAM
    a.db(0xA9, 0x02, 0xA2, 0x08, 0xA0, 0x01)            # SETLFS 2,8,1 (file addr)
    a.db(0x20, 0xBA, 0xFF, 0xA9, 0x00)
    a.db(0x20, 0xD5, 0xFF, 0x60)                        # JSR LOAD; RTS
    a.l("nmi"); a.db(0x40)                              # RTI (RAM NMI stub)
    tab_guess = 0
    while True:
        b = Asm(ML64); b.b = list(a.b); b.lab = dict(a.lab)
        b.fix = list(a.fix); b.wfix = list(a.wfix)
        _anim_code(b, ML64 + tab_guess)
        b.l("tab")
        if b.lab["tab"] - ML64 == tab_guess: break
        tab_guess = b.lab["tab"] - ML64
    b.db(*anim_table())
    b.l("namebuf"); b.db(*([0] * 17))                    # loader len+name live here
    code = bytearray(b.out())
    code[0:3] = bytes([0x4C, b.lab["loader"] & 255, b.lab["loader"] >> 8])
    nb = b.lab["namebuf"]; i = b.lab["ldnm"] - ML64
    code[i+1], code[i+2] = nb & 255, nb >> 8             # len byte
    code[i+4], code[i+6] = (nb+1) & 255, (nb+1) >> 8     # name pointer lo/hi
    code = bytes(code)
    assert b.here() <= C64_C, "ML blob overlaps the art C region"
    return code, b.lab["nmi"], b.lab["blit"], b.lab["anim"], b.lab["namebuf"]

def c64_art_files():
    """Split the packed blob into the three C64 bulk files (with PRG headers)."""
    blob = packed_blob()
    s1, s2 = C64_SPLIT
    parts = [(C64_A, blob[:s1 * 600]),
             (C64_B, blob[s1 * 600:s2 * 600]),
             (C64_C, blob[s2 * 600:])]
    assert C64_A + len(parts[0][1]) <= 0xC000
    assert C64_B + len(parts[1][1]) <= 0xFFF9   # keep clear of the CPU vectors
    assert C64_C + len(parts[2][1]) <= 0xD000
    return [(addr, bytes([addr & 255, addr >> 8]) + data) for addr, data in parts]

if __name__ == "__main__":
    blob = packed_blob()
    c, nmi = ml128()
    c64, nmi64, blit64 = ml64()
    print("packed blob %d bytes (art self-proof OK); ml128 %d bytes (nmi $%04X); "
          "ml64 %d bytes (blit $%04X, nmi $%04X)"
          % (len(blob), len(c), nmi, len(c64), blit64, nmi64))
