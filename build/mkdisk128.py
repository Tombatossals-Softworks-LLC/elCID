#!/usr/bin/env python3
"""Assemble the C128 deliverables: ELCID-128.PRG and elcid128.d64.

The game PRG is self-contained: the tokenised --detail build (must end below
$A000) is zero-padded up to $A000 and the 19 200-byte packed art blob
(rooms.packed_blob) is appended, so all 32 hand-drawn scenes ride inside the
one file and a room paint is a single ~10 ms ML blit — no per-room disk access.
The SAME bytes are written as ELCID-128.PRG (standalone: run it from anywhere)
and as "elcid128" on the disk (where the ending story-cards also live; run
standalone, the TRAP-guarded endings simply skip the cards).

Disk contents:
  elcid                     the cover loader (cidpic.bas): shows portada.kla,
                            then DLOADs the game -- the front door
  cidbm/cidsc/cidco         the cover's bitmap/screen/colour chunks
  elcid128                  the game (art appended), $1C01
  cv, cl, cd                ending story-card loaders ($1C01)
  cvbm/cvsc/cvco (+cl/cd)   each card's bitmap/screen/colour chunks

The loaders end with GRAPHIC CLR before re-DLOADing the game: GRAPHIC 3
relocates BASIC text to $4001, and without the CLR the 45 KB game would load
relocated and its absolute art pointers ($A000) would read garbage.

Run from build/:  python3 mkdisk128.py [../elcid128.d64]
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ELCID = os.path.dirname(HERE)
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ELCID, "elcid128.d64")

def run(*a, **k):
    r = subprocess.run(a, capture_output=True, text=True, **k)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("FAILED: " + " ".join(a))
    return r

def build_game_prg(work):
    """--detail build, tokenised, zero-padded to rooms.ART128 ($A000), RLE art
    appended.
    The whole PRG ends below $D000 — the empirically safe zone for a big
    C128 BASIC load (past ~$F000 the post-load machinery wedges)."""
    import rooms
    run("python3", os.path.join(HERE, "build_bas.py"), "--detail", cwd=HERE)
    tok_path = os.path.join(work, "game_tok")
    run("petcat", "-w70", "-o", tok_path, "--", os.path.join(ELCID, "elcid-128.bas"))
    assert_line_lengths(tok_path)
    tok = open(tok_path, "rb").read()
    pad = (rooms.ART128 - 0x1C01) - len(tok[2:])
    assert pad >= 0, "program overflows the $%04X art base by %d bytes" % (rooms.ART128, -pad)
    prg = tok[:2] + tok[2:] + bytes(pad) + rooms.rle_blob()
    assert 0x1C01 + len(prg) - 2 < 0xD000
    return prg


def assert_line_lengths(prg_path):
    """A tokenised line >255 bytes hangs the C128 relinker (8-bit scan)."""
    d = open(prg_path, "rb").read()
    base = d[0] | (d[1] << 8); p = 2
    while True:
        nxt = d[p] | (d[p+1] << 8)
        if nxt == 0: break
        end = d.index(0, p + 4)
        assert end - p + 1 <= 250, "line %d tokenises to %d bytes" % (d[p+2] | (d[p+3] << 8), end - p + 1)
        p = nxt - base + 2

def main():
    work = tempfile.mkdtemp(prefix="elcid128_")
    try:
        prg = build_game_prg(work)
        game = os.path.join(work, "elcid128")
        open(game, "wb").write(prg)
        # the standalone PRG artifact is the very same bytes as the disk file
        open(os.path.join(ELCID, "ELCID-128.PRG"), "wb").write(prg)

        import cards
        cards.build_cards(work)                    # cv/cl/cd {bm,sc,co}.prg

        # the Koala cover: cidpic shows it, waits for FIRE/key, then DLOADs the
        # game.  It ships as "elcid", so DLOAD"ELCID" is the way in on both
        # disks and DLOAD"ELCID128" still goes straight to the game.
        import build_blit
        build_blit.emit(work, "cid")               # cidbm/cidsc/cidco.prg

        for p, src in (("cv", "cv"), ("cl", "cl"), ("cd", "cd"), ("elcid", "cidpic")):
            run("petcat", "-w70", "-o", os.path.join(work, p),
                "--", os.path.join(ELCID, "%s.bas" % src))

        if os.path.exists(OUT): os.remove(OUT)
        cmd = ["c1541", "-format", "el cid campeador,ec", "d64", OUT]
        cmd += ["-write", game, "elcid128"]
        cmd += ["-write", os.path.join(work, "elcid"), "elcid"]
        for suf in ("bm", "sc", "co"):
            cmd += ["-write", os.path.join(work, "cid" + suf + ".prg"), "cid" + suf]
        for p in ("cv", "cl", "cd"):
            cmd += ["-write", os.path.join(work, p), p]
            for suf in ("bm", "sc", "co"):
                cmd += ["-write", os.path.join(work, p + suf + ".prg"), p + suf]
        run(*cmd)
        lst = subprocess.run(["c1541", "-attach", OUT, "-list"],
                             capture_output=True, text=True).stdout
        free = [l for l in lst.splitlines() if "blocks free" in l]
        print("wrote %s + ELCID-128.PRG (%d bytes, %d files, %s)"
              % (OUT, len(prg), lst.count(" prg"), free[0].strip() if free else "?"))
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
