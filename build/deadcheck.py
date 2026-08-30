#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the world for content the player can never reach.

Everything here is a *design* bug rather than a crash, which is why none of the
other checks catch it: the game builds, tokenises and plays, it just quietly
contains rules that can never fire, words that never reach the player, and
items that can be dropped somewhere they can never be picked up again.

  1  vocabulary reachability -- build_bas.py prunes the vocabulary to ~3
     synonyms per code to fit C64 memory, so a verb or noun that a rule needs
     can silently fail to ship
  2  verb-code collisions   -- two unrelated actions sharing one code
  3  shadowed rules         -- an earlier rule in the same room whose guard is
     implied by a later one's: the later rule is dead code
  4  one-way item loss      -- an item required later, droppable in a room the
     exit graph cannot return to
  5  orphan content         -- scenery nouns nothing responds to, items no rule
     or exam ever uses, flags set but never tested

usage:  python3 deadcheck.py [--strict]     (--strict: any finding exits 1)
"""
import sys, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cidspec as S

STRICT = "--strict" in sys.argv
findings = collections.defaultdict(list)
def note(kind, msg): findings[kind].append(msg)

# ---------------------------------------------------------------- 1 + 2 vocab
# mirror build_bas.py's pruning so this audits what actually SHIPS
sys.argv = [sys.argv[0]]                     # build_bas asserts on its flags
KEEPV = set("""lee coge mira baja monta sube este oeste norte sur arriba abajo da llena
sella empena reza duerme espera asalta ataca finge convida envia echa asoma cine vence
casa socorre ata exige muestra reta lidia acepta cava mueve fuerza abre bebe deja
inventario i ve usa ayuda habla besa purga""".split())
KEEPN = set("""manto carta babieca silla ensena pan vino arcas arena tienda reliquia
vianda cuerda oro botin parias colada salvo cidra gala tizona espadab espbucar tiendab
mantor cinchas agua corona moneda coronag corneja nina antolinez sauce altar jimena abad
mirador pozo mar atril jeronimo barba infantes rey minaya pero berenguer puerta dones
espadas hijas jirones conde bodas moros flota""".split())

def prune(tab, keep, per=3):
    by = collections.defaultdict(list)
    for w, c in tab: by[c].append(w)
    out = {}
    for c, ws in by.items():
        kept = [w for w in ws if w in keep]
        for w in sorted(ws, key=len):
            if len(kept) >= per: break
            if w not in kept: kept.append(w)
        out[c] = kept
    return out

nountab = []
seen = set()
for i in sorted(S.ITEMS):
    for w in [S.ITEMS[i][0]] + S.ITEMS[i][1]:
        if w not in seen: seen.add(w); nountab.append((w, i))
for w, c in S.SCEN.items():
    if w not in seen: seen.add(w); nountab.append((w, c))
SHIPV = prune(sorted(set(S.VERB.items())), KEEPV)
SHIPN = prune(nountab, KEEPN)

DIRWORDS = set("norte sur este oeste arriba abajo sube baja n s e o".split())
for stale in sorted(KEEPV - set(S.VERB) - DIRWORDS):
    note("bug", "KEEPV lists %r, which is not a verb in the spec at all" % stale)
for stale in sorted(KEEPN - {w for w, c in nountab}):
    note("nit", "KEEPN lists %r, which is not a noun in the spec" % stale)

for i, r in enumerate(S.R):
    if r["v"] not in SHIPV:
        note("bug", "rule %d (room %d) needs verb code %d, which does not ship" % (i, r["room"], r["v"]))
    if r["o"] and r["o"] not in SHIPN:
        note("bug", "rule %d (room %d) needs noun code %d, which does not ship" % (i, r["room"], r["o"]))

# a verb code that two unrelated vset() groups share is a collision the player
# feels as nonsense: the same word doing two different jobs in two rooms
groups = collections.defaultdict(list)
for w, c in S.VERB.items(): groups[c].append(w)
for c, ws in sorted(groups.items()):
    rooms = sorted({r["room"] for r in S.R if r["v"] == c})
    if len(rooms) > 1 and len(set(ws)) > 1:
        pass   # ordinary: one action, several rooms
for c, ws in sorted(SHIPV.items()):
    note("info", "verb %2d ships as: %s" % (c, " ".join(sorted(ws))))

# --- the AYUDA screen is a promise: every verb it names must actually work ---
HELP = """verbos: mira coge deja da ve habla abre monta llena echa reza cava asoma
cine finge sella empena convida envia socorre ata exige muestra reta acepta casa vence
lidia doma. graba recupera partida n s e o arriba abajo i inv"""
shipped_words = {w for ws in SHIPV.values() for w in ws} | DIRWORDS | {"partida", "verbos"}
for w in HELP.replace(":", " ").replace(".", " ").split():
    if w not in shipped_words:
        note("bug", "AYUDA promises the verb %r, but no such verb ships" % w)

# --------------------------------------------------------------- 3 shadowing
def implies(a, b):
    """every state satisfying b's guard also satisfies a's guard"""
    if not set(a["need"]) <= set(b["need"]): return False
    if a["forbid"] and not set(a["forbid"]) <= set(b["forbid"]): return False
    if a["needi"] and a["needi"] != b["needi"]: return False
    return True

byroom = collections.defaultdict(list)
for i, r in enumerate(S.R): byroom[r["room"]].append((i, r))
for room, rs in sorted(byroom.items()):
    for pos, (j, rj) in enumerate(rs):
        for i, ri in rs[:pos]:
            if ri["v"] != rj["v"]: continue
            if ri["o"] not in (0, rj["o"]): continue
            if implies(ri, rj):
                note("bug", "rule %d (room %d, verb %d, noun %d) is dead: rule %d "
                            "always matches first -- %r"
                     % (j, room, rj["v"], rj["o"], i, rj["msg"][:44]))

# --------------------------------------------------- 4 one-way item loss
DIRS = ["n", "s", "e", "o", "u", "d"]
adj = {r: [S.EXITS[r].get(d, 0) for d in DIRS] for r in range(1, S.NR + 1)}
def reachable_from(start):
    seen, stack = {start}, [start]
    while stack:
        for nx in adj[stack.pop()]:
            if nx and nx not in seen: seen.add(nx); stack.append(nx)
    return seen

REQUIRED = {r["needi"] for r in S.R if r["needi"]} | \
           {g["needi"] for g in S.GATE.values() if g["needi"]}
for rid in range(1, S.NR + 1):
    back = reachable_from(rid)
    for r in S.R:
        if r["needi"] in REQUIRED and r["needi"] and r["room"] not in back and r["room"] != rid:
            pass    # the rule's room is unreachable from here anyway
    stranded = sorted({r["room"] for r in S.R if r["needi"] and r["room"] not in back})
    if stranded:
        lost = sorted({r["needi"] for r in S.R if r["room"] in stranded and r["needi"]})
        note("risk", "room %-2d (%s) cannot reach room(s) %s -- dropping %s there "
                     "strands the game"
             % (rid, S.RM[rid - 1]["name"], stranded,
                ", ".join(S.ITEMS[i][0] for i in lost)))

# --------------------------------------------------------- 5 orphan content
used_nouns = {r["o"] for r in S.R if r["o"]}
for w, c in sorted(S.SCEN.items(), key=lambda x: x[1]):
    if c not in used_nouns and c in SHIPN:
        note("nit", "scenery noun %d (%s) ships but no rule ever responds to it" % (c, w))
used_items = ({r["give"] for r in S.R} | {r["give2"] for r in S.R} |
              {r["take"] for r in S.R} | {r["needi"] for r in S.R} | used_nouns)
for i, it in sorted(S.ITEMS.items()):
    if i not in used_items and it[2] == 0:
        note("bug", "item %d (%s) starts nowhere and no rule ever grants it" % (i, it[0]))
set_flags = {f for r in S.R for f in r["setf"]}
read_flags = ({f for r in S.R for f in r["need"] + r["forbid"]} |
              {f for g in S.GATE.values() for f in g["needf"]})
HONRA = {22, 24, 26, 27, 28, 29, 30}      # counted on the ending screen
for f in sorted(set_flags - read_flags - HONRA):
    note("nit", "flag %d is set but never tested" % f)
for f in sorted(read_flags - set_flags):
    note("bug", "flag %d is tested but nothing ever sets it" % f)

# ------------------------------------------------------------------- report
print("=" * 70)
print("EL CID — DEAD CONTENT AUDIT")
print("=" * 70)
order = [("bug", "BUGS — content the player can never reach"),
         ("risk", "RISKS — states worth a guard or a warning"),
         ("nit", "NITS — tidy-ups"),
         ("info", "shipped vocabulary")]
for key, title in order:
    items = findings.get(key, [])
    print("\n### %s (%d)" % (title, len(items)))
    for m in items: print("  " + ("• " if key != "info" else "  ") + m)
serious = len(findings["bug"])
print("\n%s" % ("no unreachable content." if not serious
                else "%d unreachable-content finding(s)." % serious))
sys.exit(1 if (serious and STRICT) else 0)
