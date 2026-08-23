#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32 lean PETSCII scenes for El Cid, 10-row image (rows 0-9). ~38 nums/scene."""
from c64 import Scene
BL = 160
def SC(): return Scene(rows=10, bg=0)
# 0blk 1wht 2red 3cyn 4pur 5grn 6blu 7yel 8org 9brn 10lred 11dgry 12mgry 13lgrn 14lblu 15lgry
# DETAIL toggles the extra architectural detail.  build_bas.py sets it False for
# the C64 build (lean art, fits the tight RAM and paints fastest) and True for the
# C128 build (full battlements/gates/pennants -- the 128 has bank-1 RAM for arrays
# and a fast garbage collector).  The scene functions are identical either way;
# only these helpers add or skip the trimmings.
DETAIL = True
def base(c, sk=14, gc=5, gr=7):
    s = SC(); s.rect(0,0,40,gr,BL,sk); s.rect(gr,0,40,10-gr,BL,gc); return s
def ban(s,x,h,fc):
    s.vline(0,x,h,93,15)                                    # pole
    if DETAIL:
        s.rect(1,x+1,3,2,BL,fc); s.cell(1,x+4,95,fc)       # flag + pennant point
    else:
        s.rect(1,x+1,4,2,BL,fc)                            # plain flag
def tower(s,x,w,top,c):
    s.rect(top,x,w,8-top,BL,c)                              # body
    if DETAIL:
        for mx in range(x,x+w,2): s.cell(top-1,mx,BL,c)    # crenellated battlements
        if top+1 < 8: s.cell(top+1,x+w//2,BL,0)            # arrow-slit window
        if w >= 3: s.rect(7,x+w//2,2,1,BL,0)               # gate at the base
    else:
        s.cell(top-1,x+w-1,BL,c)                           # plain corner accent

SCENES = {}
def scene(n):
    def d(f): SCENES[n] = f; return f
    return d

@scene(1)
def _():  # Vivar manor, open door, two windows, crow of ill omen, sun
    s=base(14,5,6); s.rect(3,14,12,4,BL,9); s.rect(2,14,12,1,BL,2); s.rect(5,18,3,2,BL,0)
    s.cell(4,15,102,7); s.cell(4,23,102,7); s.cell(1,30,87,1); s.cell(1,35,81,7); return s
@scene(2)
def _():  # road to Burgos walls
    s=base(14,9,6); s.rect(4,27,12,3,BL,11); s.cell(3,38,BL,11); s.rect(7,0,40,1,BL,8); return s
@scene(3)
def _():  # stable, bay horse
    s=base(9,11,7); s.rect(0,0,40,1,BL,8); s.rect(3,22,11,4,BL,8); s.rect(2,22,3,2,BL,8); s.rect(6,4,30,1,BL,7); return s
@scene(4)
def _():  # shut gates of Burgos, banner, girl
    s=base(15,12,7); tower(s,9,11,3,11); tower(s,20,7,3,11); s.rect(4,17,5,4,BL,9); s.vline(4,19,4,93,0); ban(s,3,8,5); s.cell(7,32,BL,2); return s
@scene(5)
def _():  # market square
    s=base(14,12,7); s.rect(3,2,9,4,BL,9); s.rect(3,15,10,4,BL,8); s.rect(3,29,9,4,BL,9); s.cell(7,20,BL,1); return s
@scene(6)
def _():  # Raquel & Vidas, two chests, candle
    s=base(11,9,7); s.rect(5,6,7,2,BL,9); s.rect(5,26,7,2,BL,9); s.cell(3,19,81,7); s.vline(4,19,3,93,8); return s
@scene(7)
def _():  # Glera del Arlanzon: river, sand, tent
    s=base(14,8,5); s.rect(3,0,40,2,BL,6); s.rect(2,3,3,3,BL,5); s.rect(4,24,8,3,BL,1); s.cell(0,34,81,7); return s
@scene(8)
def _():  # Cardena monastery
    s=base(15,5,7); s.rect(3,8,24,4,BL,12); s.rect(2,18,4,1,BL,12); s.cell(1,19,93,7); s.cell(0,19,BL,7); s.rect(7,11,2,2,BL,2); return s
@scene(9)
def _():  # chapel, christ, candles
    s=base(4,9,7); s.rect(2,17,6,4,BL,12); s.cell(1,19,93,1); s.cell(0,19,BL,1); s.cell(3,11,81,7); s.cell(3,28,81,7); return s
@scene(10)
def _():  # cellar, wine jars, sacks
    s=base(11,0,7); s.rect(4,5,3,3,BL,2); s.rect(4,12,3,3,BL,2); s.rect(5,27,5,2,BL,7); return s
@scene(11)
def _():  # Duero ford, dusk, rider, far bank
    s=base(4,9,7); s.rect(3,0,40,4,BL,6); s.rect(2,0,40,1,BL,9); s.rect(5,16,4,4,BL,0); s.cell(1,33,87,7); return s
@scene(12)
def _():  # frontier plateau, watchtowers
    s=base(7,8,6); tower(s,6,3,2,11); tower(s,30,3,3,11); s.cell(5,18,87,5); return s
@scene(13)
def _():  # Castejon dawn
    s=base(15,5,6); s.rect(8,0,40,2,BL,6); tower(s,12,16,3,9); s.rect(5,19,2,1,BL,0); return s
@scene(14)
def _():  # loot, Moorish horse
    s=base(9,5,7); s.rect(5,4,4,2,BL,7); s.rect(5,10,4,2,BL,7); s.rect(4,24,8,3,BL,8); s.cell(3,24,93,8); return s
@scene(15)
def _():  # Alcocer walls, banner
    s=base(14,9,6); s.rect(8,0,40,2,BL,6); tower(s,8,24,3,12); ban(s,32,8,5); return s
@scene(16)
def _():  # Fariz & Galve, two banners, lances
    s=base(7,8,6); ban(s,8,6,2); ban(s,30,6,2); s.rect(4,14,12,1,BL,15); return s
@scene(17)
def _():  # Tevar pine forest, count
    s=base(14,9,5); s.rect(3,0,40,2,BL,11)
    for x in (5,14,23,32): s.vline(3,x,4,93,9); s.rect(1,x-2,5,2,BL,5)
    ban(s,37,6,7); return s
@scene(18)
def _():  # road to Levante, orchards, sea, sun
    s=base(3,5,5); s.rect(3,0,40,1,BL,14); s.rect(4,0,40,1,BL,6)
    for x in (8,18,28): s.cell(4,x,81,13)
    s.cell(0,33,81,7); return s
@scene(19)
def _():  # Valencia huerta, palms, well
    s=base(14,5,4); s.rect(3,0,40,1,BL,13)
    for x in (5,30): s.vline(2,x,3,93,9); s.rect(1,x-1,3,1,BL,13)
    s.rect(5,20,4,3,BL,15); s.cell(4,21,BL,6); return s
@scene(20)
def _():  # white walls of Valencia, banner
    s=base(14,13,6); s.rect(8,0,40,2,BL,6); tower(s,4,32,3,1); s.cell(5,19,BL,7); ban(s,2,8,5); return s
@scene(21)
def _():  # camp, tents
    s=base(14,5,7)
    for (x,c) in ((4,1),(13,7),(22,1),(31,3)): s.rect(5,x,4,2,BL,c); s.cell(4,x+1,93,2)
    return s
@scene(22)
def _():  # alcazar, mirador over sea, banner
    s=base(14,13,5); s.rect(3,0,40,2,BL,6); s.rect(2,8,20,4,BL,1); s.cell(1,21,BL,1); s.rect(0,15,3,4,BL,1); ban(s,30,7,5); return s
@scene(23)
def _():  # beach, fleet on horizon
    s=base(14,7,7); s.rect(4,0,40,3,BL,6); s.cell(4,12,86,1); s.cell(4,22,86,1); s.cell(3,33,81,7); return s
@scene(24)
def _():  # daughters chamber, chest, gold manto
    s=base(3,9,7); s.rect(4,6,7,3,BL,9); s.rect(3,24,8,3,BL,7); s.cell(2,16,87,15); return s
@scene(25)
def _():  # treasury, chests, sword on wall
    s=base(11,9,7); s.rect(5,4,5,2,BL,7); s.rect(5,11,5,2,BL,7); s.rect(4,20,3,3,BL,9); s.vline(2,30,4,93,15); s.cell(1,30,BL,7); return s
@scene(26)
def _():  # Bucar beach camp, Moorish tents
    s=base(14,7,5); s.rect(3,0,40,2,BL,6)
    for (x,c) in ((5,0),(15,2),(25,0),(33,9)): s.rect(3,x,4,2,BL,c); s.cell(2,x+1,93,5)
    return s
@scene(27)
def _():  # Tajo meadow, royal tent, banners
    s=base(14,5,6); s.rect(8,0,40,2,BL,6); s.rect(3,15,10,4,BL,4); s.cell(2,19,93,7); ban(s,4,8,2); ban(s,34,8,5); return s
@scene(28)
def _():  # dark oak grove of Corpes
    s=SC(); s.rect(0,0,40,6,BL,6); s.rect(6,0,40,4,BL,9)
    for x in (5,15,25,35): s.vline(2,x,5,93,0); s.rect(0,x-2,5,2,BL,11)
    s.cell(1,33,87,15); return s
@scene(29)
def _():  # Cortes de Toledo, throne, figures
    s=base(4,9,7); s.rect(0,0,40,1,BL,7); s.rect(2,17,6,4,BL,8); s.cell(1,18,BL,7); s.cell(1,21,BL,7); s.cell(5,7,BL,15); s.cell(5,32,BL,15); return s
@scene(30)
def _():  # spring in grove, daughters fainted
    s=SC(); s.rect(0,0,40,6,BL,0); s.rect(6,0,40,4,BL,9); s.vline(1,6,5,93,0); s.vline(1,30,5,93,0); s.rect(5,16,8,2,BL,6); s.cell(6,11,BL,2); s.cell(6,26,BL,2); return s
@scene(31)
def _():  # dueling lists, banners, king stand
    s=base(14,5,6); s.rect(5,2,36,1,BL,9); s.rect(7,2,36,1,BL,9); ban(s,4,7,2); ban(s,34,7,3); s.rect(2,16,8,2,BL,8); return s
@scene(32)
def _():  # triumph, Valencia decked
    s=base(14,5,6); tower(s,12,16,3,1); s.rect(5,19,2,2,BL,0); ban(s,4,8,5); ban(s,24,8,2); ban(s,34,8,7); s.cell(0,33,81,7); return s

if __name__ == "__main__":
    import sys
    arts = {n: SCENES[n]().emit() for n in range(1, 33)}
    cs = [len(arts[n]) for n in range(1, 33)]
    print("scenes 32 | total", sum(cs), "avg %.1f" % (sum(cs)/32), "max", max(cs))
    if "montage" in sys.argv:
        from c64 import PAL, glyph, write_png
        cols, gap, cw, ch = 4, 8, 320, 80
        rows = 8; W = cols*cw+(cols+1)*gap; H = rows*ch+(rows+1)*gap
        px = bytearray(b'\x1e'*(W*H*3))
        for n in range(1, 33):
            s = SCENES[n](); c = (n-1) % cols; r = (n-1)//cols
            ox = gap+c*(cw+gap); oy = gap+r*(ch+gap)
            for rr in range(10):
                for cc in range(40):
                    sc, co = s.grid[rr][cc]; bm = glyph(sc); col = PAL[co & 15]
                    for yy in range(8):
                        b = bm[yy]
                        for xx in range(8):
                            if b & (0x80 >> xx):
                                X = ox+cc*8+xx; Y = oy+rr*8+yy; o = (Y*W+X)*3; px[o:o+3] = bytes(col)
        write_png("montage.png", px, W, H); print("montage.png", W, "x", H)
