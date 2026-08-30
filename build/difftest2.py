#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the shipped BASIC matches the proven model.

At every step of the critical path, fire EVERY verb x every noun (plus the six
directions) at both engines -- `cidsim` (the reference the winnability proof
runs on) and `basemu` (an independent re-implementation that reads the
generated DATA back out of elcid-c64d.bas) -- and diff the resulting state.
Zero mismatches means the BASIC provably behaves like the proven model, not
merely like the spec it was generated from.

`--quick` samples one representative noun per code (the default sweeps all).
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)                      # cidspec/basemu read canon.json and ../*.bas

import cidspec as S, cidsim as C
from basemu import B, nu, ru, ex, vb, no, ni, nr

# ---- state snapshots -------------------------------------------------------
# Both engines are small enough to save and restore by hand; copy.deepcopy on
# ~120 000 probe commands cost ~35 s of the ~37 s runtime, all of it spent
# re-walking two dicts and a list.
def sim_save(g):  return (g.rm, set(g.flags), dict(g.loc), g.over)
def sim_load(g, s): g.rm, g.flags, g.loc, g.over = s[0], set(s[1]), dict(s[2]), s[3]
def emu_save(g):  return (g.rm, list(g.fl), dict(g.il), g.gw)
def emu_load(g, s): g.rm, g.fl, g.il, g.gw = s[0], list(s[1]), dict(s[2]), s[3]

# normalize: sim over -1->lose, +1->win ; emu gw 2->lose, 1->win.
# Sets, not sorted tuples: equality is what is being asked, and sorting 700 000
# times to answer it was a quarter of the runtime.
SIM_OVER = {-1: 'LOSE', 1: 'WIN', 0: 'OK'}
EMU_OVER = {2: 'LOSE', 1: 'WIN', 0: 'OK'}
# fl% is DIMmed to 31 in the BASIC, so a flag above that would be a spec bug.
MAXFLAG = 31
assert max([0] + [f for r in S.R for f in r["need"] + r["forbid"] + r["setf"]]
           + [f for g in S.GATE.values() for f in g["needf"]]) <= MAXFLAG
FLAGS = range(1, MAXFLAG + 1)
def sim_norm(g):
    return (g.rm, SIM_OVER[g.over], frozenset(g.flags),
            frozenset(k for k, v in g.loc.items() if v == -1))
def emu_norm(g):
    return (g.rm, EMU_OVER[g.gw], frozenset(i for i in FLAGS if g.fl[i]),
            frozenset(k for k, v in g.il.items() if v == -1))

QUICK = "--quick" in sys.argv
verbs = sorted(set(vb.keys()))
repnoun = {}
for w, cd in no.items(): repnoun.setdefault(cd, w)
probe_nouns = [''] + [repnoun[cd] for cd in sorted(repnoun)]
if QUICK: probe_nouns = probe_nouns[::3]
dirs = ['norte', 'sur', 'este', 'oeste', 'sube', 'baja']
probes = [(v + ' ' + n).strip() for v in verbs for n in probe_nouns] + dirs
CP = [c.strip() for c in C.CRITPATH if c.strip()]

mism = []
gs = C.Game(); gb = B()
def cmp_at(tag):
    ss, sb = sim_save(gs), emu_save(gb)
    for cmd in probes:
        gs.do(cmd); gb.do(cmd)
        a, b = sim_norm(gs), emu_norm(gb)
        if a != b: mism.append((tag, cmd, a, b))
        sim_load(gs, ss); emu_load(gb, sb)

for k, c in enumerate(CP):
    cmp_at('step%d:%s' % (k, c))
    gs.do(c); gb.do(c)
    if gs.over or gb.gw: break

print("probes: %d commands x %d critical-path states = %d comparisons"
      % (len(probes), k + 1, len(probes) * (k + 1)))
print("REAL mismatches (normalized):", len(mism))
for m in mism[:40]: print(m)
sys.exit(1 if mism else 0)
