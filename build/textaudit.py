#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static text audit for El Cid: replicate the game's wrap() and screen layout
and flag every string that would overflow or be truncated on the 40x25 screen.

Screen layout (from build_bas.py):
  row 10      room name + honra badge, reverse video  -> name kept to 29 chars
  rows 11-14  description   wrap w=36, dl=11 dz=14     -> max 4 lines; >4 TRUNCATED
  row 15      rule
  rows 16-20  message       wrap w=36, dl=16 dz=20     -> max 5 lines; >5 TRUNCATED
  row 21      "salidas: "+exits    left$(...,38)       -> max 38 chars
  row 22      "ves: "+items        left$(...,38)       -> max 38 chars
  row 24      hint bar (static)

The description block is smaller than the message block on purpose: the
description now PERSISTS while you play, so it has to share the screen with
whatever the game answers, instead of being overwritten by it.
"""
import sys, re, json
import cidspec as S

ACC = str.maketrans("", "")
def norm(t):
    t = t.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    t = t.replace("ñ","n").replace("ü","u").replace("Á","a").replace("¡","").replace("¿","")
    t = t.lower()
    t = "".join(c for c in t if c in "abcdefghijklmnopqrstuvwxyz0123456789 .,!?'():-/")
    return re.sub(r"\s+", " ", t).strip()

def wrap_lines(t, w=36):
    out = []
    for seg in norm(t).split("/"):
        line = ""
        for word in seg.split(" "):
            if not word: continue
            if len(line) + len(word) + (1 if line else 0) <= w:
                line = (line + " " + word) if line else word
            else:
                if line: out.append(line)
                line = word
        out.append(line)
    return [x for x in out if x != ""]

DESCROWS = 4      # rows 11..14 inclusive -- the persistent description
MSGROWS  = 5      # rows 16..20 inclusive -- the per-command answer
MAXROWS  = MSGROWS
WRAPW    = 36
NAMEW    = 38
NAMEBADGE = 29    # left$(rn$+bl$,29) before the honra badge is appended

problems = []
warn = []

def check_block(label, text, maxrows=MAXROWS):
    lines = wrap_lines(text)
    over_w = [l for l in lines if len(l) > WRAPW]
    if len(lines) > maxrows:
        problems.append("TRUNCATED (%d>%d lines): %s\n    last-visible: %r\n    LOST: %r"
                        % (len(lines), maxrows, label, lines[maxrows-1], " / ".join(lines[maxrows:])))
    elif len(lines) == maxrows:
        warn.append("FULL (%d lines, no margin): %s" % (len(lines), label))
    for l in over_w:
        problems.append("LINE>%d (%d): %s\n    %r" % (WRAPW, len(l), label, l))
    return lines

# ---- room names (row 10, <=38) ----
RM = {r["id"]: r for r in S.RM}
for rid in range(1, S.NR+1):
    nm = norm(RM[rid]["name"])
    if len(nm) > NAMEBADGE:
        problems.append("ROOMNAME>%d (%d) -- the honra badge would eat it: room %d %r"
                        % (NAMEBADGE, len(nm), rid, nm))

# ---- descriptions (rows 11-14) ----
for rid in range(1, S.NR+1):
    check_block("desc room %d (%s)" % (rid, RM[rid]["name"]), S.DESC[rid], DESCROWS)

# ---- item exam texts (MIRA <item>) ----
for i in S.ITEMS:
    check_block("exam item %d (%s)" % (i, S.ITEMS[i][0]), S.ITEMS[i][4])

# ---- rule messages ----
for k, r in enumerate(S.R):
    check_block("rule %d (room %d v%d o%d)" % (k, r["room"], r["v"], r["o"]), r["msg"])

# ---- gate messages ----
for key, g in S.GATE.items():
    check_block("gate %s" % (key,), g["msg"])

# ---- exits line per room: "salidas: " + exits (<=38) ----
DIRW = {1:"norte ",2:"sur ",3:"este ",4:"oeste ",5:"arriba ",6:"abajo "}
DIRK = {"n":1,"s":2,"e":3,"o":4,"u":5,"d":6}
for rid in range(1, S.NR+1):
    ex = RM[rid]["exits"]
    xt = "".join(DIRW[DIRK[k]] for k in ("n","s","e","o","u","d") if k in ex)
    line = "salidas: " + xt
    if len(line.rstrip()) > NAMEW:
        problems.append("EXITS>%d (%d): room %d %r" % (NAMEW, len(line.rstrip()), rid, line.rstrip()))

# ---- items line per room (start items): "ves: " + names (<=38) ----
# names are the *display* names shown by the game (io$). Worst case = all start items.
for rid in range(1, S.NR+1):
    names = [S.ITEMS[i][0] for i in S.ROOMITEMS.get(rid, [])]
    if not names: continue
    line = "ves: " + " ".join(names)
    if len(line) > NAMEW:
        warn.append("ITEMS line %d chars (may clip) room %d: %r" % (len(line), rid, line))

print("="*70)
print("EL CID — STATIC TEXT AUDIT (screen fit)")
print("="*70)
print("checked: %d rooms, %d items, %d rules, %d gates" % (S.NR, len(S.ITEMS), len(S.R), len(S.GATE)))
print()
if problems:
    print("### PROBLEMS (%d) — text truncated / overflows the screen:" % len(problems))
    for p in problems: print(" ✗ " + p)
else:
    print("### PROBLEMS: none — nothing truncates or overflows.")
print()
print("### WARNINGS (%d) — full/tight, worth reviewing:" % len(warn))
for w in warn: print(" • " + w)
print()
# distribution of message line-counts
counts = {}
for r in S.R:
    n = len(wrap_lines(r["msg"])); counts[n] = counts.get(n,0)+1
print("rule-message line-count distribution:", dict(sorted(counts.items())),
      "(message area holds %d)" % MSGROWS)
dcounts = {}
for rid in range(1, S.NR+1):
    n = len(wrap_lines(S.DESC[rid])); dcounts[n] = dcounts.get(n,0)+1
print("description line-count distribution:", dict(sorted(dcounts.items())),
      "(description area holds %d)" % DESCROWS)
longest = max(S.R, key=lambda r: len(wrap_lines(r["msg"])))
print("longest rule message: %d lines (room %d) — %r" % (len(wrap_lines(longest["msg"])), longest["room"], longest["msg"][:60]+"..."))
# a truncated line is a shipped bug, so say so with the exit code too
import sys; sys.exit(1 if problems else 0)
