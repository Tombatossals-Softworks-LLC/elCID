#!/usr/bin/env python3
"""C64 PETSCII-block scene authoring + preview + BASIC DATA emit.
Single source of truth: author scenes with rect/hline/vline/cell helpers;
emit() -> art-command numbers for the .bas; render() -> PNG preview."""
import zlib, struct

# colodore-ish C64 palette (index 0..15)
PAL = [(0,0,0),(255,255,255),(150,60,55),(120,210,205),
       (155,80,165),(95,175,90),(70,60,160),(220,220,130),
       (160,100,50),(105,80,30),(200,110,100),(90,90,90),
       (140,140,140),(155,230,150),(125,115,210),(170,170,170)]

# 8x8 glyph bitmaps for BASE screen codes 0..127 we use (MSB=left).
# screen code 160 = 32+128 -> reverse of space -> solid (handled by XOR).
G = {
 32:[0,0,0,0,0,0,0,0],
 46:[0,0,0,0,0,0x18,0x18,0],
 81:[0x3c,0x7e,0xff,0xff,0xff,0xff,0x7e,0x3c],     # filled circle / ball
 87:[0x3c,0x42,0x81,0x81,0x81,0x81,0x42,0x3c],     # open circle
 90:[0x10,0x38,0x7c,0xfe,0x7c,0x38,0x10,0],        # diamond
 64:[0,0,0,0xff,0xff,0,0,0],                       # horizontal line
 93:[0x18,0x18,0x18,0x18,0x18,0x18,0x18,0x18],     # vertical line
 112:[0,0,0,0x1f,0x1f,0x18,0x18,0x18],             # top-left corner
 110:[0,0,0,0xf8,0xf8,0x18,0x18,0x18],             # top-right corner
 109:[0x18,0x18,0x18,0x1f,0x1f,0,0,0],             # bottom-left
 125:[0x18,0x18,0x18,0xf8,0xf8,0,0,0],             # bottom-right
 102:[0xcc,0xcc,0x33,0x33,0xcc,0xcc,0x33,0x33],    # checker
 119:[0xff,0xff,0xff,0xff,0,0,0,0],                # top half block
 108:[0,0,0,0,0xff,0xff,0xff,0xff],                # bottom half block
 95:[0xff,0x7f,0x3f,0x1f,0x0f,0x07,0x03,0x01],     # solid lower-left triangle
 105:[0x01,0x03,0x07,0x0f,0x1f,0x3f,0x7f,0xff],    # solid upper-left triangle
 233:[0xf0,0xf0,0xf0,0xf0,0,0,0,0],                # quad upper-left
 223:[0xf0,0xf0,0xf0,0xf0,0,0,0,0],
}
def glyph(sc):
    base = sc & 127
    bm = G.get(base, [0x66,0x99,0x99,0x66,0x66,0x99,0x99,0x66])  # fallback hatch
    if sc >= 128:
        bm = [b ^ 0xff for b in bm]
    return bm

def write_png(path, px, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += px[y*w*3:(y+1)*w*3]
    comp = zlib.compress(bytes(raw), 9)
    def ch(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    open(path, "wb").write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', ihdr) + ch(b'IDAT', comp) + ch(b'IEND', b''))

class Scene:
    def __init__(self, rows=11, cols=40, bg=0):
        self.rows, self.cols, self.bg = rows, cols, bg
        self.cmds = []           # raw art commands (numbers, op-prefixed)
        self.grid = [[(32, bg)] * cols for _ in range(rows)]
    def _set(self, r, c, sc, co):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = (sc, co)
    def rect(self, r, c, w, h, sc, co):
        self.cmds += [3, r, c, w, h, sc, co]
        for y in range(h):
            for x in range(w): self._set(r+y, c+x, sc, co)
        return self
    def hline(self, r, c, n, sc, co):
        self.cmds += [1, r, c, n, sc, co]
        for x in range(n): self._set(r, c+x, sc, co)
        return self
    def vline(self, r, c, n, sc, co):
        self.cmds += [2, r, c, n, sc, co]
        for y in range(n): self._set(r+y, c, sc, co)
        return self
    def cell(self, r, c, sc, co):
        self.cmds += [4, r, c, sc, co]; self._set(r, c, sc, co); return self
    def emit(self):
        return self.cmds + [0]
    def render(self, path, scale=12):
        w, h = self.cols*8*scale//8, self.rows*8*scale//8  # = cols*scale, rows*scale per char *8? keep 8px*scale/8
        cw, chh = 8, 8
        W, H = self.cols*cw, self.rows*chh
        px = bytearray(W*H*3)
        bgc = PAL[self.bg]
        for y in range(H):
            for x in range(W):
                o = (y*W+x)*3; px[o:o+3] = bytes(bgc)
        for r in range(self.rows):
            for c in range(self.cols):
                sc, co = self.grid[r][c]
                bm = glyph(sc); col = PAL[co & 15]
                for yy in range(8):
                    row = bm[yy]
                    for xx in range(8):
                        if row & (0x80 >> xx):
                            X, Y = c*8+xx, r*8+yy
                            o = (Y*W+X)*3; px[o:o+3] = bytes(col)
        # upscale
        if scale != 1:
            W2, H2 = W*scale, H*scale
            px2 = bytearray(W2*H2*3)
            for y in range(H2):
                sy = y//scale
                for x in range(W2):
                    sx = x//scale
                    o, o2 = (sy*W+sx)*3, (y*W2+x)*3
                    px2[o2:o2+3] = px[o:o+3]
            write_png(path, px2, W2, H2); return W2, H2
        write_png(path, px, W, H); return W, H

if __name__ == "__main__":
    # smoke test: render the 3 test scenes
    import os
    s1 = Scene(bg=0)
    s1.rect(0,0,40,8,160,14).rect(8,0,40,3,160,5).cell(1,35,81,7).rect(6,15,9,3,160,9).hline(5,15,9,160,2)
    s2 = Scene(bg=0)
    s2.rect(0,0,40,8,160,14).rect(8,0,40,3,160,9).rect(7,0,40,1,160,8)
    s3 = Scene(bg=0)
    s3.rect(0,0,40,7,160,12).rect(7,0,40,4,160,11).rect(3,12,16,5,160,9).rect(5,18,4,3,160,0)
    for i, s in enumerate([s1,s2,s3], 1):
        s.render("test_room%d.png" % i)
        print("room%d cmds:" % i, s.emit())
    print("rendered 3 test scenes")
