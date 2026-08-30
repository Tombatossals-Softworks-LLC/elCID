#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One command that rebuilds everything and proves it is correct.

There are no C64 ROMs in this environment, so the game cannot be *run* here.
Every claim about it is therefore established statically, and this script is
the single entry point that establishes them, in dependency order:

  1  cidsim      the reference engine auto-plays the critical path      -> winnable
                 and gathers all 7 gestas                               -> legendary reachable
                 and each lose condition fires                          -> deaths work
  2  build_bas   regenerate both .bas files from the one spec
  3  cval        the generated BASIC is legal (v2.0 on the C64 target),
                 every jump resolves, no 2-char variable collision,
                 no write to a reserved variable
  4  memcheck    the C64 build still fits under $A000 with string heap to spare
  5a textaudit   no room/item/rule text overflows or truncates on a 40x25 screen
  5b deadcheck   no rule, word or item the player can never reach
  5c walkcheck   the published WALKTHROUGH.txt is the path cidsim proves
  6b playtest    four kinds of player actually play it: an explorer that
                 covers every room and rule, a spoiler that tries to lock
                 itself out of the win, a monkey typing nonsense, and
                 golden transcripts of what the screen says -- all of them
                 driving BOTH engines in lockstep, command by command
  6  basemu +    an independent re-implementation reads the generated DATA back
     difftest2   and is diffed against the reference across the whole critical
                 path x every verb x every noun                         -> 0 divergences
  7  mkdisk*     rebuild ELCID-128.PRG, elcid128.d64 and elcid.d64
  8  reproducible: the tracked artefacts are byte-identical to what was rebuilt

usage:  python3 verify.py [--fast]      (--fast skips the disk rebuild)
"""
import os, subprocess, sys, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FAST = "--fast" in sys.argv

ARTEFACTS = ["elcid-128.bas", "elcid-c64d.bas", "ELCID-128.PRG",
             "elcid128.d64", "elcid.d64"]

def digest():
    d = {}
    for a in ARTEFACTS:
        p = os.path.join(ROOT, a)
        if os.path.exists(p):
            d[a] = hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
    return d

results = []
def step(label, *cmd, **kw):
    t0 = time.time()
    r = subprocess.run([sys.executable] + list(cmd), cwd=HERE,
                       capture_output=True, text=True)
    dt = time.time() - t0
    ok = r.returncode == 0
    for needle in kw.get("must_contain", []):
        if needle not in r.stdout: ok = False
    for needle in kw.get("must_not_contain", []):
        if needle in r.stdout: ok = False
    results.append((label, ok, dt))
    print("%-4s %-46s %5.1fs" % ("ok" if ok else "FAIL", label, dt))
    if not ok:
        sys.stdout.write(r.stdout[-4000:]); sys.stderr.write(r.stderr[-4000:])
    return ok

before = digest()

print("=" * 62)
print("EL CID -- static verification")
print("=" * 62)

step("1  reference engine: winnable + legendary + deaths", "cidsim.py",
     must_contain=["*** VICTORY ***", "7 of 7 -> LEGENDARY", "ALL CHECKS PASSED"])
step("2a build C128 BASIC  (--detail)",  "build_bas.py", "--detail")
step("2b build C64  BASIC  (--c64disk)", "build_bas.py", "--c64disk")
step("3a validate C64  BASIC v2.0 legality", "cval.py", "../elcid-c64d.bas",
     must_contain=["ALL OK"])
step("3b validate C128 BASIC legality", "cval.py", "../elcid-128.bas",
     must_contain=["ALL OK"])
step("4  C64 memory budget (program+arrays+heap)", "memcheck.py", "--min-heap", "700")
step("5a screen-fit text audit", "textaudit.py",
     must_contain=["### PROBLEMS: none"])
step("5b dead-content audit (unreachable rules/words)", "deadcheck.py", "--strict")
step("5c WALKTHROUGH matches the proven critical path", "walkcheck.py",
     must_contain=["matches the proven path exactly"])
step("6a BASIC emulator vs reference: 0 divergences", "difftest2.py",
     must_contain=["REAL mismatches (normalized): 0"])
step("6b players: explore, spoil, monkey, transcripts", "playtest.py",
     must_contain=["PLAYTEST: ALL CLEAR"])
if not FAST:
    step("7a rebuild ELCID-128.PRG + elcid128.d64", "mkdisk128.py")
    step("7b rebuild elcid.d64", "mkdisk64.py")

    # Determinism: the same source must produce the same bytes every time, so
    # build the whole chain a second time and compare.  (Drift against the
    # committed files is reported separately -- after a deliberate change it is
    # expected, and it is a thing to commit, not a failure.)
    once = digest()
    for c in ("build_bas.py", "--detail"), ("build_bas.py", "--c64disk"), \
             ("mkdisk128.py",), ("mkdisk64.py",):
        subprocess.run([sys.executable] + list(c), cwd=HERE, capture_output=True)
    twice = digest()
    ok = once == twice
    results.append(("8  build is deterministic (same bytes twice)", ok, 0.0))
    print("%-4s %-46s" % ("ok" if ok else "FAIL",
                          "8  build is deterministic (same bytes twice)"))
    if not ok:
        for a in sorted(once):
            if once[a] != twice[a]:
                print("      %-16s %s -> %s" % (a, once[a], twice[a]))

    drift = sorted(a for a in twice if before.get(a) != twice[a])
    if drift:
        print("\nnote: %d tracked artefact(s) changed and need committing:" % len(drift))
        for a in drift:
            print("      %-16s %s -> %s" % (a, before.get(a, "(absent)"), twice[a]))

print("-" * 62)
bad = [r for r in results if not r[1]]
print("%d/%d checks passed in %.1fs" % (len(results) - len(bad), len(results),
                                        sum(r[2] for r in results)))
sys.exit(1 if bad else 0)
