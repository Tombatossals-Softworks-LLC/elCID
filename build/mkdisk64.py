#!/usr/bin/env python3
"""Assemble elcid.d64 — the C64 disk build with the packed resident art.

Contents:
  elcid          the game (elcid-c64d.bas, --c64disk build, $0801)
  aa, ab, ac     the packed art blob split into the three regions the game
                 bulk-LOADs once at boot: rooms 1-13 -> $A000 (RAM under the
                 BASIC ROM), 14-26 -> $E000 (RAM under the KERNAL), 27-32 ->
                 $C100 (KERNAL LOAD writes through the ROMs into RAM)

After that one boot load a room paint is a single ~10 ms ML blit that banks
the ROMs out to read the art (NMI-safe: the RAM NMI vector points at an RTI),
so a room change never touches the disk again.  The single-file ELCID.PRG
(compact resident art) is unchanged and still ships as the lite version.

Run from build/:  python3 mkdisk64.py [../elcid.d64]
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ELCID = os.path.dirname(HERE)
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ELCID, "elcid.d64")

def run(*a, **k):
    r = subprocess.run(a, capture_output=True, text=True, **k)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("FAILED: " + " ".join(a))
    return r


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
    work = tempfile.mkdtemp(prefix="elcid64_")
    try:
        import rooms
        run("python3", os.path.join(HERE, "build_bas.py"), "--c64disk", cwd=HERE)
        game = os.path.join(work, "elcid")
        run("petcat", "-w2", "-o", game, "--", os.path.join(ELCID, "elcid-c64d.bas"))
        assert_line_lengths(game)

        names = ("aa", "ab", "ac")
        arts = rooms.c64_art_files()               # [(addr, header+data) x3]
        for name, (addr, data) in zip(names, arts):
            open(os.path.join(work, name), "wb").write(data)

        if os.path.exists(OUT): os.remove(OUT)
        cmd = ["c1541", "-format", "el cid campeador,ec", "d64", OUT,
               "-write", game, "elcid"]
        for name in names:
            cmd += ["-write", os.path.join(work, name), name]
        run(*cmd)
        lst = subprocess.run(["c1541", "-attach", OUT, "-list"],
                             capture_output=True, text=True).stdout
        free = [l for l in lst.splitlines() if "blocks free" in l]
        print("wrote %s (%d files, %s)" % (OUT, lst.count(" prg"),
                                           free[0].strip() if free else "?"))
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
