#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reference engine mirroring the C64 BASIC logic exactly. Auto-plays the
critical path to PROVE winnability, and checks lose conditions fire."""
import cidspec as S

NOUN = {}
for i, it in S.ITEMS.items():
    NOUN[it[0]] = i
    for syn in it[1]: NOUN.setdefault(syn, i)
for w, c in S.SCEN.items(): NOUN.setdefault(w, c)
DIRW = {"n":"n","norte":"n","s":"s","sur":"s","e":"e","este":"e","o":"o","oeste":"o",
        "u":"u","sube":"u","arriba":"u","d":"d","baja":"d","abajo":"d"}

class Game:
    def __init__(s):
        s.rm = 1; s.flags = set()
        s.loc = {i: S.ITEMS[i][2] for i in S.ITEMS}
        s.over = 0; s.last = ""
    def do(s, cmd):
        if s.over: return
        ws = cmd.split()
        w1 = ws[0] if ws else ""; w2 = ws[1] if len(ws) > 1 else ""
        va = S.VERB.get(w1, 0); ob = NOUN.get(w2, 0)
        di = DIRW.get(w1, "")
        if va == 5 and not di: di = DIRW.get(w2, "")
        # 1) special rules
        for r in S.R:
            if r["room"] != s.rm: continue
            if r["v"] != va: continue
            if r["o"] != 0 and r["o"] != ob: continue
            if any(f not in s.flags for f in r["need"]): continue
            if any(f in s.flags for f in r["forbid"]): continue
            if r["needi"] and s.loc.get(r["needi"]) != -1: continue
            for f in r["setf"]: s.flags.add(f)
            if r["give"]: s.loc[r["give"]] = -1
            if r["give2"]: s.loc[r["give2"]] = -1
            if r["take"]: s.loc[r["take"]] = 0
            s.last = r["msg"]
            if r["kind"] == 1: s.over = -1
            if r["kind"] == 2: s.over = 1
            return
        # 2) movement
        if di:
            g = S.GATE.get((s.rm, di))
            if g:
                ok = all(f in s.flags for f in g["needf"]) and (g["needi"] == 0 or s.loc.get(g["needi"]) == -1)
                if not ok:
                    s.last = g["msg"]
                    if g["lose"]: s.over = -1
                    return
            nx = S.EXITS[s.rm].get(di, 0)
            if not nx: s.last = "no puedes ir por ahi."; return
            s.rm = nx; s.last = "->%d %s" % (nx, S.RM[nx-1]["name"]); return
        # 3) generic
        if va == 1:
            if ob == 0: s.last = "miras alrededor."; return
            if ob <= S.NI:
                if s.loc.get(ob) in (s.rm, -1): s.last = S.ITEMS[ob][4]; return
                s.last = "no ves eso aqui."; return
            s.last = "no ves nada especial."; return
        if va == 2:
            if ob == 0 or ob > S.NI: s.last = "coger que?"; return
            if s.loc.get(ob) == -1: s.last = "ya lo llevas."; return
            if s.loc.get(ob) != s.rm: s.last = "no ves eso aqui."; return
            if not S.ITEMS[ob][3]: s.last = "no puedes llevarte eso."; return
            s.loc[ob] = -1; s.last = "coges %s." % S.ITEMS[ob][0]; return
        if va == 3:
            if ob == 0 or ob > S.NI or s.loc.get(ob) != -1: s.last = "no llevas eso."; return
            s.loc[ob] = s.rm; s.last = "dejas %s." % S.ITEMS[ob][0]; return
        if va == 4:
            inv = [S.ITEMS[i][0] for i in S.ITEMS if s.loc.get(i) == -1]
            s.last = "llevas: " + (" ".join(inv) if inv else "nada"); return
        s.last = "no puedo hacer eso aqui."
    def play(s, cmds, trace=False):
        for c in cmds:
            s.do(c)
            if trace: print("  %-18s | r%-2d %s" % (c, s.rm, s.last[:60]))
            if s.over: break
        return s.over

# Legendary critical path: wins AND gathers all 6 honra deeds (cava=moneda,
# convida moros=clemencia, da vianda=provisiones, plus reliquia/corona/angel).
CRITPATH = """lee carta|coge manto|mira corneja|baja|coge silla|monta babieca|sube|este|este|
mira nina|coge ensena|este|mira antolinez|sur|coge arena|cava|oeste|llena arcas|sella arcas|empena arcas|
este|este|da oro|mira jimena|baja|coge cuerda|coge vianda|sube|este|mira altar|oeste|sur|
duerme|este|norte|espera|asalta|este|coge botin|oeste|sur|este|finge|asalta|este|da ensena|ataca|
oeste|oeste|envia parias|sur|convida conde|este|convida moros|este|echa reliquia|este|asalta|oeste|norte|
da vianda|mira minaya|sur|este|este|asoma mirador|norte|coge gala|sur|abajo|coge tizona|mueve atril|sube|
este|mira flota|este|mira jeronimo|cine tizona|vence bucar|este|da dones|casa hijas|oeste|oeste|oeste|doma leon|este|este|este|este|coge jirones|
coge cinchas|abajo|coge agua|socorre hijas|sube|este|ata barba|exige espadas|muestra jirones|
reta infantes|sube|da tizona|da colada|lidia|este|acepta""".replace("\n", "").split("|")

print("=== CRITICAL PATH PLAYTHROUGH (%d commands) ===" % len(CRITPATH))
g = Game()
res = g.play([c.strip() for c in CRITPATH if c.strip()], trace=True)
print("\nRESULT:", {1: "*** VICTORY ***", -1: "XXX DIED XXX", 0: "...stuck (not won)"}[res])
print("final room:", g.rm, "| flags:", sorted(g.flags))
assert res == 1, "CRITICAL PATH DID NOT WIN"

# prove the LEGENDARY ending is reachable (honra computed from final state,
# mirroring the BASIC end-screen: flags 24/26/27/28/29/30 + moneda item 29).
ho = ((24 in g.flags) + (26 in g.flags) + (27 in g.flags)
      + (g.loc.get(29) == -1) + (28 in g.flags) + (29 in g.flags) + (30 in g.flags))
print("HONRA (deeds): %d of 7 -> %s" % (ho, "LEGENDARY ending" if ho >= 6 else "standard ending"))
assert ho >= 6, "CRITICAL PATH DID NOT REACH LEGENDARY ENDING (ho=%d)" % ho

# --- lose-condition spot checks ---
print("\n=== LOSE CONDITION CHECKS ===")
def check(name, cmds, want):
    g = Game(); g.play([c.strip() for c in cmds])
    ok = (g.over == want)
    print(" %-32s over=%2d %s" % (name, g.over, "OK" if ok else "!! FAIL"))
    return ok
allok = True
allok &= check("forzar puerta burgos", "baja|monta babieca|sube|este|este|fuerza puerta".split("|"), -1)
allok &= check("cruzar duero sin babieca",
   "este|este|coge ensena|este|sur|este|sur|este".split("|"), -1)
allok &= check("abrir arcas selladas (engano)",
   "este|este|este|mira antolinez|sur|coge arena|oeste|llena arcas|sella arcas|abre arcas".split("|"), -1)
allok &= check("abrir arcas vacias (ya no mata)",
   "este|este|este|mira antolinez|sur|coge arena|oeste|abre arcas".split("|"), 0)
allok &= check("beber pozo emponzonado (need reach r19; just verify rule)",
   None, None) if False else True
# direct: reach huerta and drink unpurged well -> lose (use a minimal valid path)
g2=Game()
g2.flags={1,2,3,4,5,6,7,8,9,10}; g2.loc[5]=-1; g2.rm=19
g2.do("bebe pozo"); print(" %-32s over=%2d %s"%("beber pozo sin purgar", g2.over, "OK" if g2.over==-1 else "!! FAIL")); allok &= (g2.over==-1)
print("\nALL CHECKS PASSED" if (res==1 and allok) else "\nSOME CHECKS FAILED")
