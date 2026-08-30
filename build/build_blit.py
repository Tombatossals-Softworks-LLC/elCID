#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the Koala cover (portada.kla) into the three chunks cidpic.bas BLOADs.

A C64/C128 multicolour bitmap needs ~10 KB of VIC RAM, which the 30 KB game
cannot spare, so the cover is a separate tiny program: cidpic.bas shows it in
the C128's GRAPHIC 3 mode (KERNAL-managed, so the 40-column IRQ does not revert
the VIC registers), waits for FIRE or a key, then GRAPHIC CLR and DLOADs the
game.  This is the same three-chunk layout build/cards.py emits for the ending
story cards, so both use one loader shape:

    cidbm   8000 bytes bitmap        -> $2000
    cidsc   1000 bytes colour screen -> $1C00   (hi nibble mc1, lo nibble mc2)
    cidco   1000 bytes colour-RAM    -> $1300   (copied to $D800 by the loader)

Koala format: 2-byte load address ($6000), then 8000 bitmap + 1000 screen +
1000 colour + 1 background byte.

usage:  python3 build_blit.py [outdir] [--png preview.png]
"""
import os, sys, zlib, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ELCID = os.path.dirname(HERE)
KOALA = os.path.join(ELCID, "portada.kla")

PAL = [(0,0,0),(255,255,255),(150,60,55),(120,210,205),
       (155,80,165),(95,175,90),(70,60,160),(220,220,130),
       (160,100,50),(105,80,30),(200,110,100),(90,90,90),
       (140,140,140),(155,230,150),(125,115,210),(170,170,170)]

def load_koala(path=KOALA):
    d = open(path, "rb").read()
    assert len(d) == 10003, "%s is %d bytes, not a 10003-byte Koala" % (path, len(d))
    addr = d[0] | (d[1] << 8)
    assert addr == 0x6000, "Koala load address is $%04X, expected $6000" % addr
    body = d[2:]
    return body[:8000], body[8000:9000], body[9000:10000], body[10000]

def emit(outdir, prefix="cid"):
    bm, scr, col, bg = load_koala()
    written = []
    for addr, data, suf in ((0x2000, bm, "bm"), (0x1c00, scr, "sc"), (0x1300, col, "co")):
        p = os.path.join(outdir, prefix + suf + ".prg")
        with open(p, "wb") as f:
            f.write(bytes([addr & 255, addr >> 8])); f.write(data)
        written.append(p)
    return written, bg

def preview(path):
    """Render the cover exactly as the VIC would, to prove the split is right."""
    bm, scr, col, bg = load_koala()
    K = 2
    W, H = 320 * K, 200 * K
    raw = bytearray(W * H * 3)
    for y in range(200):
        for x in range(160):
            cx, cy = x // 4, y // 8
            cell = cy * 40 + cx
            byte = bm[cell * 8 + (y & 7)]
            pair = (byte >> (6 - 2 * (x & 3))) & 3
            c = (bg, scr[cell] >> 4, scr[cell] & 15, col[cell] & 15)[pair]
            r, g, b = PAL[c & 15]
            for dy in range(K):
                for dx in range(2 * K):
                    px = ((y * K + dy) * W + (x * 2 * K + dx)) * 3
                    raw[px:px+3] = bytes((r, g, b))
    out = bytearray()
    for y in range(H): out.append(0); out += raw[y*W*3:(y+1)*W*3]
    def ch(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
    open(path, "wb").write(b'\x89PNG\r\n\x1a\n'
        + ch(b'IHDR', struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
        + ch(b'IDAT', zlib.compress(bytes(out), 9)) + ch(b'IEND', b''))
    return path

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outdir = args[0] if args else "."
    files, bg = emit(outdir)
    print("wrote %s (background colour %d)" % (", ".join(os.path.basename(f) for f in files), bg))
    if "--png" in sys.argv:
        p = sys.argv[sys.argv.index("--png") + 1]
        print("preview ->", preview(p))
