#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WALKTHROUGH.txt must be the critical path cidsim.py actually proves.

The published solution is hand-maintained prose, but the only path anything
verifies is CRITPATH in cidsim.py -- the one the reference engine auto-plays to
*** VICTORY *** with all seven gestas.  Nothing tied the two together, so a
change to the puzzle chain could silently leave the shipped walkthrough
describing a game that no longer exists.

This asserts they are the same list of orders, in the same order, and that the
numbering in the file is contiguous.  It reads the walkthrough's numbered steps
("  17. oeste") and ignores everything else -- headings, the parenthesised
asides, the gesta markers.

usage:  python3 walkcheck.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WALK = os.path.join(ROOT, "WALKTHROUGH.txt")

# The command is the first one or two words after the number; anything further
# out (a parenthesised note, a "* gesta" marker) is commentary.
STEP = re.compile(r"^\s*(\d+)\.\s+([a-zñáéíóúü]+(?:\s+[a-zñáéíóúü]+)?)\s*(?:\(|\*|$)")

def critpath():
    src = open(os.path.join(HERE, "cidsim.py"), encoding="utf-8").read()
    m = re.search(r'CRITPATH\s*=\s*"""(.*?)"""', src, re.S)
    assert m, "cidsim.py: CRITPATH not found"
    return [c.strip() for c in m.group(1).replace("\n", "").split("|") if c.strip()]

def walkpath():
    steps = []
    for ln, line in enumerate(open(WALK, encoding="utf-8"), 1):
        m = STEP.match(line)
        if m:
            steps.append((int(m.group(1)), " ".join(m.group(2).split()), ln))
    return steps

def main():
    sim = critpath()
    walk = walkpath()

    bad = []
    for i, (n, _, ln) in enumerate(walk, 1):
        if n != i:
            bad.append("WALKTHROUGH.txt:%d: step numbered %d, expected %d" % (ln, n, i))
            break                                  # renumbering makes the rest noise

    if len(walk) != len(sim):
        bad.append("length: WALKTHROUGH.txt has %d steps, cidsim CRITPATH has %d"
                   % (len(walk), len(sim)))

    for i in range(min(len(walk), len(sim))):
        if walk[i][1] != sim[i]:
            bad.append("WALKTHROUGH.txt:%d: step %d is %r, CRITPATH has %r"
                       % (walk[i][2], i + 1, walk[i][1], sim[i]))

    print("critical path: %d commands (cidsim) vs %d steps (WALKTHROUGH.txt)"
          % (len(sim), len(walk)))
    if bad:
        print("\n### PROBLEMS (%d):" % len(bad))
        for b in bad[:20]:
            print(" • " + b)
        if len(bad) > 20:
            print("   ... and %d more" % (len(bad) - 20))
        sys.exit(1)
    print("### WALKTHROUGH matches the proven path exactly.")

if __name__ == "__main__":
    main()
