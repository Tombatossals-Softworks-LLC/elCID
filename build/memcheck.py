#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static memory budget for the generated BASIC.

The C64 build lives at the edge of BASIC RAM: the tokenised program grows up
from $0801 and the string heap grows down from $A000, with the scalar variables
and the DIMmed arrays wedged in between.  If they meet, the game answers
?OUT OF MEMORY mid-sentence -- and there is no emulator here to find that out
the hard way, so the budget is computed instead.

CBM BASIC storage (both v2.0 and v7.0):
    scalar            7 bytes   (2 name + 5 value)
    array header      5 + 2*ndims bytes  (2 name + 2 length + 1 ndims + dims)
    array element     2 (integer) / 3 (string descriptor) / 5 (float)

usage:  python3 memcheck.py [file.bas ...] [--min-heap 400]
"""
import re, subprocess, sys, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cidspec as _S
ITEM_NAMES = [_S.ITEMS[i][0] for i in sorted(_S.ITEMS)]
MSGCAP = 5 * 36        # the message area is five rows of a 36-column wrap

# C64: program, variables, arrays and strings all share $0801..$9FFF.
# C128: the program lives in bank 0 and *all* variables/arrays/strings live in
# bank 1, so the two never compete -- only the program-vs-art ceiling matters.
MACHINES = {
    "c64":  dict(prog_start=0x0801, mem_top=0xA000, split_banks=False),
    "c128": dict(prog_start=0x1C01, mem_top=0xFF00, split_banks=True),
}

KW = set("""end for next data input dim read let goto run if restore gosub return rem
stop on wait load save verify def poke print cont list clr cmd sys open close get new
tab to fn spc then not step and or sgn int abs usr fre pos sqr rnd log exp cos sin tan
atn peek len str val asc chr left right mid go st ti time
bload dload graphic color slow fast trap""".split())
KWSORT = sorted(KW, key=len, reverse=True)

def peel(tok):
    changed = True
    while changed:
        changed = False
        for kw in KWSORT:
            if tok.startswith(kw) and tok != kw:
                tok = tok[len(kw):]; changed = True; break
    return tok

def elem_bytes(name):
    return 3 if name.endswith("$") else (2 if name.endswith("%") else 5)

def split_args(s):
    """split a comma list at paren depth 0 (dimension expressions may nest)."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip(): out.append(cur)
    return out

def analyse(path, min_heap=0):
    src = [l.rstrip("\n") for l in open(path) if l.strip()]
    T = {}
    for l in src:
        m = re.match(r"(\d+) ?(.*)$", l)
        T[int(m.group(1))] = m.group(2)
    machine = "c128" if "128" in os.path.basename(path) else "c64"
    prof = MACHINES[machine]

    # tokenised program size: petcat is the authority, else a pessimistic guess
    prg = None
    if shutil.which("petcat"):
        tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "memcheck.prg")
        subprocess.run(["petcat", "-w2", "-o", tmp, "--", path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        prg = os.path.getsize(tmp) - 2          # minus the load address
        os.unlink(tmp)
    else:
        prg = sum(len(b) + 5 for b in T.values())
        print("  (petcat not found -- program size is an estimate)")
    prog_end = prof["prog_start"] + prg

    # the DATA header gives nr, ni, nu, which the DIM expressions refer to
    counts = {}
    for n in sorted(T):
        m = re.match(r"data\s+(\d+),(\d+),(\d+)\s*$", T[n])
        if m:
            counts = dict(nr=int(m.group(1)), ni=int(m.group(2)), nu=int(m.group(3)))
            break
    if not counts:
        sys.exit("could not find the 'data nr,ni,nu' header in %s" % path)

    arrays, arybytes = [], 0
    for n in sorted(T):
        body = re.sub(r'"[^"]*"', '""', T[n])
        for m in re.finditer(r'\bdim\s*(.*)$', body):
            for decl in split_args(m.group(1)):
                d = re.match(r'\s*([a-z][a-z0-9]?[$%]?)\s*\((.*)\)\s*$', decl.strip())
                if not d: continue
                name, dims = d.group(1), split_args(d.group(2))
                sizes = [eval(x, {"__builtins__": {}}, counts) + 1 for x in dims]
                cells = 1
                for s in sizes: cells *= s
                b = 5 + 2 * len(sizes) + cells * elem_bytes(name)
                arrays.append((name, sizes, cells, b)); arybytes += b

    dimmed = {a[0] for a in arrays}
    scalars = set()
    for n in sorted(T):
        b = T[n]
        if b.lstrip().startswith(("rem", "data")): continue
        s = re.split(r'\brem\b', re.sub(r'"[^"]*"', ' ', b), maxsplit=1)[0]
        for m in re.finditer(r'([a-z][a-z0-9]*[$%]?)\s*(\(?)', s):
            tok = peel(m.group(1))
            if not tok or not tok[0].isalpha(): continue
            if tok in KW or tok.rstrip('$%') in KW: continue
            if m.group(2) == "(" and tok in dimmed: continue   # array reference
            scalars.add(tok[:2] + (tok[-1] if tok[-1] in '$%' else ''))
    scalars -= dimmed
    scalbytes = 7 * len(scalars)

    print("=" * 62)
    print("MEMORY BUDGET  %s   (%s)" % (os.path.basename(path), machine.upper()))
    print("=" * 62)
    print("  program   $%04X-$%04X %7d bytes (tokenised)" % (prof["prog_start"], prog_end - 1, prg))
    print("  arrays    %-2d declared        %8d bytes" % (len(arrays), arybytes))
    for name, sizes, cells, b in sorted(arrays, key=lambda a: -a[3]):
        print("      %-6s %-14s %5d cells %6d b" % (name, "x".join(map(str, sizes)), cells, b))
    print("  scalars   %-2d live            %8d bytes" % (len(scalars), scalbytes))

    if prof["split_banks"]:
        # The C128 keeps every variable in bank 1, so the heap never competes
        # with the program.  The ceiling that *is* real is the art blob the
        # build appends to the PRG at $A000: the tokenised program has to end
        # below it or mkdisk128 refuses to assemble the file.
        import rooms
        head = rooms.ART128 - prog_end
        print("\n  C128: variables/arrays/strings live in bank 1 (64 K of their own),")
        print("        so the string heap never competes with the program.")
        print("  bank-1 variable use     %8d bytes of ~64 K -- no pressure" % (arybytes + scalbytes))
        print("  room below the art blob %8d bytes  (art base $%04X)" % (head, rooms.ART128))
        if head < 0:
            print("\nFAIL: the program overruns the appended art by %d bytes." % -head)
            return 1
        floor = 200          # build-time gap only: nothing grows at runtime
        if head < floor:
            print("\nFAIL: only %d bytes before the art blob at $%04X, want >= %d."
                  % (head, rooms.ART128, floor))
            return 1
        print("\nOK: %d bytes before the art blob (>= %d required)." % (head, floor))
        return 0

    # ---- what the heap actually has to hold ------------------------------
    # Strings that come from READ or from a bare literal are 3-byte descriptors
    # pointing into the program text and cost no heap at all -- that is most of
    # them (nn$, dd$, ms$, in$, vb$, no$, ha$, gd$, ...).  What DOES cost heap
    # is anything built by concatenation, and CBM BASIC evaluates a+b+c
    # left-to-right into fresh temporaries, so `x$=x$+" "+y$` has three copies
    # of a growing string live at once before the old one becomes garbage.
    perm = {"dn$": 24, "rt$": 39, "bl$": 40, "cl$": 16}          # built at boot, never freed
    live = {"s$": 40, "c$": 34, "w1$+w2$+w3$": 40, "xt$": 35, "io$": 45}
    # AYUDA: mg$=ha$+hb$ is one temporary plus the result -> 2 copies.
    help_len = sum(len(re.search(r'"(.*)"', T[k]).group(1)) for k in (995, 996) if k in T)
    # inventory: mg$=mg$+" "+in$(j) leaves the old value, a temp and the result
    # live at once -> 3 copies of a growing string.  The build caps the string
    # at what the five message rows can actually show, so this is bounded.
    inv_len = min(MSGCAP, 7 + sum(1 + len(w) for w in ITEM_NAMES))
    worst, why = max((3 * inv_len, "inventory (%d chars x3)" % inv_len),
                     (2 * help_len, "ayuda text (%d chars x2)" % help_len))
    peak = sum(perm.values()) + sum(live.values()) + worst
    used = prog_end + arybytes + scalbytes
    heap = prof["mem_top"] - used
    print("  " + "-" * 58)
    print("  string heap free           %8d bytes  (top $%04X)" % (heap, prof["mem_top"]))
    print("  modelled worst-case peak   %8d bytes" % peak)
    print("      permanent (dn$/rt$/bl$/cl$)      %5d" % sum(perm.values()))
    print("      live while a command runs        %5d" % sum(live.values()))
    print("      biggest string under construction %5d  (%s)" % (worst, why))
    pct = 100.0 * (used - prof["prog_start"]) / (prof["mem_top"] - prof["prog_start"])
    print("  BASIC RAM used             %7.1f%%" % pct)
    need = max(min_heap, peak)
    if heap < need:
        print("\nFAIL: only %d bytes of string heap, need >= %d." % (heap, need))
        print("      A C64 garbage collection needs room to work; below this the")
        print("      game can answer ?OUT OF MEMORY in the middle of a response.")
        return 1
    print("\nOK: %d bytes of string heap (>= %d needed, %d to spare)."
          % (heap, need, heap - need))
    return 0

if __name__ == "__main__":
    argv = sys.argv[1:]
    mh = 400
    if "--min-heap" in argv:
        i = argv.index("--min-heap"); mh = int(argv[i + 1]); del argv[i:i + 2]
    paths = [a for a in argv if not a.startswith("--")] or [
        os.path.join(HERE, "..", "elcid-c64d.bas"),
        os.path.join(HERE, "..", "elcid-128.bas")]
    rc = 0
    for p in paths:
        rc |= analyse(p, mh)
        print()
    sys.exit(rc)
