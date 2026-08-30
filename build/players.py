#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The lockstep table: two engines, one command at a time, diffed after every move.

`difftest2.py` already fires every verb x every noun at both engines -- but only
from the 107 states the critical path walks through, and it compares a
*normalized state*: room, over, flags, inventory.  Two things fall through that
net, and both are what a player would actually notice:

  * **Trajectories nobody walks.**  Every probe is one command deep from the one
    blessed path.  A rule that only misbehaves after you have been somewhere else
    first is invisible.
  * **The wrong rule with the right effect.**  Two rules can set the same flag and
    give the same item while printing different prose.  Comparing state cannot
    tell them apart, so the shipped BASIC could answer a command with another
    room's sentence and every check would stay green.

This module is the shared machinery the players in `playtest.py` drive: it runs
`cidsim.Game` (the reference the winnability proof runs on) and `basemu.B` (the
independent re-implementation that reads the generated DATA back out of
`elcid-c64d.bas`) side by side, and after *every single command* compares

    room, over-state, flags, carried items, item positions,
    and WHICH RULE FIRED -- by identity, not by effect.

The rule identity is what makes the prose comparable.  `basemu` reports the
index of the row it matched in the emitted table; `build_bas.py` emits that
table stable-sorted by room, so emitted row j is spec rule RULE_ORDER[j].  The
mapping is not taken on trust: `_check_rule_map()` re-derives it and verifies
every row's room/verb/object/kind against the spec before any player runs.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)                      # cidspec/basemu read canon.json and ../*.bas

import io, contextlib
_quiet = io.StringIO()
with contextlib.redirect_stdout(_quiet):   # both modules self-test noisily on import
    import cidspec as S, cidsim as C
    import basemu

# ---------------------------------------------------------------- rule mapping
# build_bas.py: RULE_ORDER = sorted(range(NU), key=lambda i: S.R[i]["room"])
# Python's sort is stable, so this reproduces the emitted order exactly.  It is
# a mirror of another module's decision, so it gets verified rather than trusted.
RULE_ORDER = sorted(range(len(S.R)), key=lambda i: S.R[i]["room"])

def _check_rule_map():
    """Emitted row j must be spec rule RULE_ORDER[j] -- verify, do not assume."""
    rows = basemu.RU
    if len(rows) != len(RULE_ORDER):
        raise SystemExit("rule map: BASIC has %d rules, spec has %d"
                         % (len(rows), len(RULE_ORDER)))
    for j, row in enumerate(rows):
        r = S.R[RULE_ORDER[j]]
        got, want = (row[0], row[1], row[2], row[7]), (r["room"], r["v"], r["o"], r["kind"])
        if got != want:
            raise SystemExit(
                "rule map broken at emitted row %d: BASIC %s, spec rule %d %s.\n"
                "build_bas.py's RULE_ORDER no longer matches the mirror in players.py."
                % (j, got, RULE_ORDER[j], want))
_check_rule_map()

# ------------------------------------------------------------------- alphabet
# The alphabet has to be the vocabulary the game SHIPS, not the one the spec
# describes.  build_bas.py prunes synonyms to fit the C64's RAM -- 186 verb words
# become 130 -- so a player can type COGE but not AGARRA.  Driving the players
# from the spec's word list makes every pruned synonym look like an engine
# divergence (the model answers, the BASIC says "no conozco ese verbo"), which is
# the pruner working, not a bug.  basemu.vb/no are read straight out of the
# generated DATA, so they are exactly what a real player can type.
def _check_vocabulary():
    """Two properties of the pruner, worth having asserted rather than assumed."""
    for w, c in basemu.vb.items():
        if S.VERB.get(w) != c:
            raise SystemExit("shipped verb %r=%s is not the spec's %r"
                             % (w, c, S.VERB.get(w)))
    for w, c in basemu.no.items():
        if C.NOUN.get(w) != c:
            raise SystemExit("shipped noun %r=%s is not the spec's %r"
                             % (w, c, C.NOUN.get(w)))
    lost_v = set(S.VERB.values()) - set(basemu.vb.values())
    lost_n = set(C.NOUN.values()) - set(basemu.no.values())
    if lost_v or lost_n:
        raise SystemExit("the pruner left a code with no word a player can type: "
                         "verbs %s nouns %s" % (sorted(lost_v), sorted(lost_n)))
_check_vocabulary()

PRUNED_VERBS = sorted(set(S.VERB) - set(basemu.vb))
PRUNED_NOUNS = sorted(set(C.NOUN) - set(basemu.no))

# Synonyms are equivalent by construction: both engines resolve a word to a code
# and then look only at the code, and difftest2 already sweeps every synonym.
# One representative per code is therefore the whole language, ~10x smaller.
_rv = {}
for _w, _c in sorted(basemu.vb.items()): _rv.setdefault(_c, _w)
_rn = {}
for _w, _c in sorted(basemu.no.items()): _rn.setdefault(_c, _w)

VERB_WORDS = [_rv[c] for c in sorted(_rv)]
NOUN_WORDS = [_rn[c] for c in sorted(_rn)]
# Bare direction words are not verbs in S.VERB -- both engines route them through
# their own direction tables -- so they have to be added by hand.  (Leaving them
# out silently reduces the explorer to the four commands you can type in Vivar.)
DIR_WORDS = ["norte", "sur", "este", "oeste", "sube", "baja"]
DROP_VERB = S.VERB.get("deja", 0)

def alphabet(drop=True, dirs=True):
    """Every distinct command the parser can distinguish, as one word per code."""
    out = list(VERB_WORDS) + [v + " " + n for v in VERB_WORDS for n in NOUN_WORDS]
    if not drop:
        out = [c for c in out if S.VERB.get(c.split()[0], 0) != DROP_VERB]
    return out + (list(DIR_WORDS) if dirs else [])

# ------------------------------------------------------------------ responses
# Where both engines model the same text, compare the text.  Where only the
# BASIC does (it distinguishes an unknown verb from a known verb that does not
# apply; the reference model answers both the same way), compare the class.
GENERIC = {
    "no puedes ir por ahi.":    "NOEXIT",
    "no ves eso aqui.":         "NOTHERE",
    "ya lo llevas.":            "HAVEIT",
    "no puedes llevarte eso.":  "NOTAKE",
    "no llevas eso.":           "NOTCARRIED",
    "coger que?":               "TAKEWHAT",
}

# A guarded exit (the Duero, the road to Levante) is a gate on the BASIC side
# and a plain message on the reference side.  Naming the gate texts lets both be
# classified the same way, so gates get compared instead of excused.
GATE_MSGS = frozenset(g["msg"] for g in S.GATE.values())

def sim_response(g):
    """Classify the reference engine's answer."""
    if g.rule >= 0: return ("RULE", g.rule)
    m = g.last
    if m in GATE_MSGS:            return ("GATE", None)
    if m.startswith("->"):        return ("MOVE", g.rm)
    if m in GENERIC:              return (GENERIC[m], None)
    if m.startswith("coges "):    return ("TAKE", None)
    if m.startswith("dejas "):    return ("DROP", None)
    if m.startswith("llevas: "):  return ("INV", None)
    if m == "miras alrededor.":   return ("LOOK", None)
    if m == "no ves nada especial.":  return ("EXAMSCENERY", None)
    if m == "no puedo hacer eso aqui.": return ("GENERIC", None)
    return ("EXAM", None)             # an item's own description

def emu_response(g):
    """Classify the BASIC emulator's answer, in the same vocabulary."""
    m = g.last
    if m.startswith("RULE"):      return ("RULE", RULE_ORDER[int(m[4:])])
    if m.startswith("->"):        return ("MOVE", g.rm)
    if m in GENERIC:              return (GENERIC[m], None)
    if m == "coges":              return ("TAKE", None)
    if m == "dejas":              return ("DROP", None)
    if m == "inv":                return ("INV", None)
    if m == "look":               return ("LOOK", None)
    if m == "exam":               return ("EXAM", None)
    if m == "no ves nada de particular.": return ("EXAMSCENERY", None)
    # The BASIC tells an unknown verb apart from a known one that does not apply;
    # the reference model has one answer for both.  Fold them together -- this is
    # a gap in the model's prose, not a disagreement about what happened.
    if m in ("no conozco ese verbo.", "no puedo hacer eso ahora."): return ("GENERIC", None)
    if m.startswith("GATE_"):     return ("GATE", None)
    if m == "help":               return ("GENERIC", None)
    return ("?" + m, None)

# ---------------------------------------------------------------------- state
SIM_OVER = {-1: "LOSE", 1: "WIN", 0: "OK"}
EMU_OVER = {2: "LOSE", 1: "WIN", 0: "OK"}
MAXFLAG = 31
# All seven gestas are flags, so honour is monotonic: a flag is never cleared,
# and nothing you do afterwards can take a deed back.  The coin used to be
# counted by being in your inventory, which made DEJA MONEDA hand back an
# honour the game had already paid you for.
HONRA_FLAGS = (22, 24, 26, 27, 28, 29, 30)

def honra(flags, carried=None):
    return sum(f in flags for f in HONRA_FLAGS)

class Table:
    """Both engines, fed the same commands, compared after each one."""
    def __init__(self):
        self.sim = C.Game()
        self.emu = basemu.B()

    # -- snapshot / restore (cheaper than deepcopy, which dominated difftest2) --
    def save(self):
        s, e = self.sim, self.emu
        return (s.rm, set(s.flags), dict(s.loc), s.over,
                e.rm, list(e.fl), dict(e.il), e.gw)
    def load(self, st):
        s, e = self.sim, self.emu
        s.rm, s.flags, s.loc, s.over = st[0], set(st[1]), dict(st[2]), st[3]
        e.rm, e.fl, e.il, e.gw = st[4], list(st[5]), dict(st[6]), st[7]

    # -- the comparable view of each engine ---------------------------------
    def sim_view(self):
        s = self.sim
        return (s.rm, SIM_OVER[s.over], frozenset(s.flags),
                frozenset(k for k, v in s.loc.items() if v == -1),
                frozenset((k, v) for k, v in s.loc.items() if v >= 0))
    def emu_view(self):
        e = self.emu
        return (e.rm, EMU_OVER[e.gw], frozenset(i for i in range(1, MAXFLAG + 1) if e.fl[i]),
                frozenset(k for k, v in e.il.items() if v == -1),
                frozenset((k, v) for k, v in e.il.items() if v >= 0))

    def key(self):
        """Identity of the shared state, for dedup in a search."""
        v = self.sim_view()
        return (v[0], v[1], v[2], v[3], v[4])

    def over(self):
        return self.sim.over

    def do(self, cmd):
        """Play one command on both engines. Returns (problems, response)."""
        self.sim.do(cmd)
        self.emu.do(cmd)
        bad = []
        a, b = self.sim_view(), self.emu_view()
        if a != b:
            names = ("room", "over", "flags", "carried", "placed")
            for i, n in enumerate(names):
                if a[i] != b[i]:
                    bad.append("%s: reference=%s BASIC=%s" % (n, _short(a[i]), _short(b[i])))
        ra, rb = sim_response(self.sim), emu_response(self.emu)
        if ra[0] == "RULE" or rb[0] == "RULE":
            if ra != rb:
                bad.append("rule: reference=%s BASIC=%s" % (_rule(ra), _rule(rb)))
        elif ra[0] != rb[0]:
            bad.append("answer: reference=%s BASIC=%s" % (ra[0], rb[0]))
        return bad, ra

def _rule(r):
    if r[0] != "RULE": return r[0]
    i = r[1]; rr = S.R[i]
    return "rule%d(room%d v%d o%d)" % (i, rr["room"], rr["v"], rr["o"])

def _short(x):
    if isinstance(x, frozenset):
        s = sorted(x)
        return "{%s}" % ", ".join(map(str, s[:8])) + (" ...+%d" % (len(s) - 8) if len(s) > 8 else "")
    return str(x)
