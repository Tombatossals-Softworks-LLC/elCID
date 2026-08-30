#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Players who actually play the game, instead of one player who plays it once.

Everything else in `build/` proves a property of the artefact: the BASIC is
legal, it fits in RAM, no text overflows, nothing is statically unreachable, the
one blessed solution wins.  Nobody sits down and *plays* -- wanders off the
path, tries the wrong verb in the wrong room, drops something and walks away.
This runs four kinds of player, all of them driving both engines in lockstep
through `players.Table`, so every command is checked against the reference model
and against the shipped BASIC's own data at the same time:

  explorer   A player with perfect memory who tries everything, seeded from the
             solution corridor.  Pure breadth-first from Vivar is the wrong
             search for this game -- it is a 107-step gated chain, so breadth
             never reaches the end (100 s of it gets to 12 rooms of 32).  Seeded
             from the 108 states the proven solution passes through and expanded
             outwards, it reaches every room and fires nearly every rule in
             seconds, and each piece of content it finds comes with a witness
             session that is replayed in lockstep.

  spoiler    A player who tries to ruin their own game, and the reason this file
             exists.  At every step of the solution it takes every action
             available, then plays the rest of the solution and asks whether it
             still wins.  Each deviation is classified: harmless, an announced
             death, recoverable (some short sequence puts the solution back on
             its feet), or a SOFTLOCK -- alive, but the victory is gone.  A
             softlock is the classic adventure-game bug, the unwinnable save,
             and it is invisible to every other check here.

  monkey     A player who types nonsense: seeded random sessions mixing real
             commands, bare directions and words the vocabulary never heard, to
             shake out the parser and the fall-through paths.  Deterministic --
             the same seed replays the same session, and the report prints the
             seed to replay a failure with.

  transcript A player whose session is written down.  Named scenarios rendered
             the way the 40-column screen renders them, compared against
             committed golden files, so a change to the prose is a reviewable
             diff instead of a silent one.

usage:
    python3 playtest.py                      # all four, CI budgets (~30 s)
    python3 playtest.py --spoiler            # just the softlock hunt
    python3 playtest.py --monkey --sessions 5000
    python3 playtest.py --transcripts --update      # re-record the golden files
    python3 playtest.py --replay 41                 # re-run one monkey session
    python3 playtest.py --deep               # deeper search, more sessions
"""
import os, sys, time, random, collections, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import players as P
S, C = P.S, P.C

def _load_textaudit():
    """textaudit.py ends in sys.exit() -- it is a check, not a library.  Load it
    anyway rather than copying wrap_lines() here: the transcripts have to be laid
    out by the *game's* wrap, and a second copy of it would drift."""
    import importlib.util, contextlib, io as _io
    spec = importlib.util.spec_from_file_location("_textaudit",
                                                  os.path.join(HERE, "textaudit.py"))
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(_io.StringIO()):
        try:
            spec.loader.exec_module(m)
        except SystemExit:
            pass                      # the audit's verdict is verify.py's business
    return m
T = _load_textaudit()

GOLDEN = os.path.join(HERE, "transcripts")
SOLUTION = [c.strip() for c in C.CRITPATH if c.strip()]

# Rules the corridor search is not expected to fire, with the reason.  This list
# exists so that a rule going quiet is loud: anything uncovered and NOT named
# here fails the run.
OFF_CORRIDOR = {
    36: "the alternate well purge -- squeezing the bitter cidra instead of "
        "casting in the relic.  Both are `echa` in room 19; rule 35 wins the "
        "match whenever the relic is carried, and the solution always carries "
        "it, so firing 36 needs three moves off the path (drop the relic, take "
        "the cidra, echa).  --deep searches to depth 3 and does fire it, which "
        "is why this is a note at depth 2 and not an exemption: measured at "
        "82/82 rules, 47 467 states, 134 s.",
}

# ---------------------------------------------------------------------------
#  shared state helpers
# ---------------------------------------------------------------------------
# The state is (room, flags, item positions, over).  Everything below snapshots
# and restores by hand -- copy.deepcopy on this many probes is most of a run.
def snap(g):
    return (g.rm, frozenset(g.flags), tuple(sorted(g.loc.items())), g.over)

def load(g, st):
    g.rm, g.flags, g.loc, g.over = st[0], set(st[1]), dict(st[2]), st[3]

def corridor():
    """Every state the proven solution passes through, in order."""
    g = C.Game()
    out = [snap(g)]
    for c in SOLUTION:
        g.do(c)
        out.append(snap(g))
        if g.over:
            break
    return out

# ---------------------------------------------------------------------------
#  player 1 -- the explorer
# ---------------------------------------------------------------------------
def explore(depth=2, budget=200000, timelimit=300.0, with_drop=True):
    A = P.alphabet(drop=with_drop)
    seeds = corridor()
    states = list(seeds)
    index = {s: i for i, s in enumerate(states)}
    parent = {i: None for i in range(len(states))}
    seed_path = {}                       # sid -> commands, for the corridor seeds
    for i in range(len(seeds)):
        seed_path[i] = SOLUTION[:i]

    first_rule, first_room, first_carry = {}, {}, {}
    for i, s in enumerate(states):
        first_room.setdefault(s[0], i)
    wins, deaths = [], []
    scratch = C.Game()
    frontier = list(range(len(states)))
    t0 = time.time()
    capped = None

    for _ in range(depth):
        nxt = []
        for sid in frontier:
            st = states[sid]
            if st[3] != 0:
                continue
            for c in A:
                load(scratch, st)
                scratch.do(c)
                if scratch.rule >= 0 and scratch.rule not in first_rule:
                    first_rule[scratch.rule] = (sid, c)
                k = snap(scratch)
                if k in index:
                    continue
                nid = len(states)
                states.append(k); index[k] = nid; parent[nid] = (sid, c)
                first_room.setdefault(k[0], nid)
                for it in (i for i, v in k[2] if v == -1):
                    first_carry.setdefault(it, nid)
                if scratch.over == 1:
                    wins.append(nid)
                elif scratch.over == -1:
                    deaths.append(nid)
                else:
                    nxt.append(nid)
            if len(states) > budget:
                capped = "state budget (%d)" % budget; break
            if time.time() - t0 > timelimit:
                capped = "time limit (%.0fs)" % timelimit; break
        frontier = nxt
        if capped:
            break

    return dict(states=states, parent=parent, seed_path=seed_path,
                first_rule=first_rule, first_room=first_room,
                first_carry=first_carry, wins=wins, deaths=deaths,
                capped=capped, seconds=time.time() - t0, alphabet=len(A),
                seeds=len(seeds))

def path_to(ex, sid):
    """The commands that first reached this state, back to a corridor seed."""
    out = []
    while ex["parent"][sid] is not None:
        sid, c = ex["parent"][sid]
        out.append(c)
    return ex["seed_path"][sid] + out[::-1]

def run_explore(args):
    print("=" * 62)
    print("PLAYER 1 -- the explorer (outwards from the solution corridor)")
    print("=" * 62)
    ex = explore(depth=args.depth, budget=args.budget, timelimit=args.time)
    print("  %d corridor seeds | %d commands in the alphabet | depth %d"
          % (ex["seeds"], ex["alphabet"], args.depth))
    print("  %d states in %.1fs%s"
          % (len(ex["states"]), ex["seconds"],
             "" if not ex["capped"] else "   [STOPPED: %s]" % ex["capped"]))

    bad = 0
    rules_hit = set(ex["first_rule"])
    print("  rooms reached      %2d/%d" % (len(ex["first_room"]), S.NR))
    print("  rules fired        %2d/%d" % (len(rules_hit), len(S.R)))
    print("  items ever carried %2d/%d" % (len(ex["first_carry"]), S.NI))
    print("  victories %d | deaths %d" % (len(ex["wins"]), len(ex["deaths"])))

    if len(ex["first_room"]) != S.NR:
        bad += 1
        print("   !! unreachable rooms: %s"
              % sorted(set(range(1, S.NR + 1)) - set(ex["first_room"])))

    missing = set(range(len(S.R))) - rules_hit
    for i in sorted(missing & set(OFF_CORRIDOR)):
        print("  note: rule%d not exercised -- %s" % (i, OFF_CORRIDOR[i]))
    unexplained = missing - set(OFF_CORRIDOR)
    if unexplained:
        bad += 1
        print("   !! rules never fired, and not listed as off-corridor:")
        for i in sorted(unexplained)[:12]:
            r = S.R[i]
            print("      rule%d room%d v%d o%d: %s" % (i, r["room"], r["v"], r["o"], r["msg"][:52]))

    if not ex["wins"]:
        bad += 1
        print("   !! no victory reachable")
    best = 0
    for sid in ex["wins"]:
        st = ex["states"][sid]
        best = max(best, P.honra(st[1], frozenset(i for i, v in st[2] if v == -1)))
    print("  best honra at a victory  %d/7" % best)
    if ex["wins"] and best < 7:
        bad += 1
        print("   !! the legendary ending needs 7 gestas; best seen is %d" % best)

    lose_rules = {i for i, r in enumerate(S.R) if r["kind"] == 1}
    death_rules = set()
    for sid in ex["deaths"]:
        p = ex["parent"][sid]
        if not p:
            continue
        g = C.Game(); load(g, ex["states"][p[0]]); g.do(p[1])
        if g.rule >= 0:
            death_rules.add(g.rule)
    print("  lose rules reachable %d/%d" % (len(death_rules & lose_rules), len(lose_rules)))
    if lose_rules - death_rules:
        bad += 1
        print("   !! deaths that never happen: %s" % sorted(lose_rules - death_rules))

    # --- every witness replayed on both engines ------------------------------
    wit = {}
    for rid, (sid, cmd) in ex["first_rule"].items():
        wit["rule%03d" % rid] = path_to(ex, sid) + [cmd]
    for rm, sid in ex["first_room"].items():
        wit.setdefault("room%02d" % rm, path_to(ex, sid))
    for i, sid in enumerate(ex["deaths"][:60]):
        wit["death%03d" % i] = path_to(ex, sid)
    for i, sid in enumerate(ex["wins"][:30]):
        wit["win%03d" % i] = path_to(ex, sid)

    print("\n  replaying %d witness sessions in lockstep (reference vs BASIC)" % len(wit))
    cmds = div = 0
    for name in sorted(wit):
        t = P.Table()
        for step, c in enumerate(wit[name]):
            problems, _ = t.do(c)
            cmds += 1
            if problems:
                div += 1
                if div <= 8:
                    print("   !! %s step %d %r: %s" % (name, step, c, "; ".join(problems)))
                    print("      %s" % " | ".join(wit[name][:step + 1]))
                break
            if t.over():
                break
    print("  %d commands replayed, %d divergences" % (cmds, div))
    bad += div

    if ex["capped"] and not args.allow_partial:
        bad += 1
        print("   !! the search stopped early (%s); raise --budget/--time or pass "
              "--allow-partial" % ex["capped"])
    return bad

# ---------------------------------------------------------------------------
#  player 2 -- the spoiler (softlock hunt)
# ---------------------------------------------------------------------------
def run_spoiler(args):
    print("=" * 62)
    print("PLAYER 2 -- the spoiler (can you lock yourself out of the win?)")
    print("=" * 62)
    # Movement is left out on purpose: walking away legitimately breaks a
    # solution whose next command assumes a room, and walking back fixes it, so
    # every movement deviation would report as recoverable noise.  What is being
    # asked here is whether anything you can DO in a room can cost you the game.
    dev_cmds = [c for c in P.alphabet(drop=True) if c not in P.DIR_WORDS]
    all_cmds = P.alphabet(drop=True)
    probe = C.Game(); rep = C.Game(); walk = C.Game()

    def wins_from(st, i):
        load(rep, st)
        for c in SOLUTION[i:]:
            rep.do(c)
            if rep.over:
                break
        return rep.over == 1

    def repair(st, i, depth):
        """The shortest sequence that puts the solution back on its feet."""
        frontier, seen = {st}, {st}
        for d in range(depth):
            nxt = set()
            for s in frontier:
                for c in all_cmds:
                    load(walk, s); walk.do(c); k = snap(walk)
                    if k in seen or k[3] != 0:
                        continue
                    seen.add(k); nxt.add(k)
                    if wins_from(k, i):
                        return d + 1, c
            frontier = nxt
        return None, None

    t0 = time.time()
    g = C.Game()
    harmless = dead = 0
    recovered = collections.Counter()
    locks = []
    tried = 0
    for i, step in enumerate(SOLUTION):
        st = snap(g)
        groups = {}
        for d in dev_cmds:
            load(probe, st); probe.do(d)
            k = snap(probe)
            if k != st:
                groups.setdefault(k, d)
        tried += len(groups)
        for k, d in groups.items():
            if k[3] != 0:               # the deviation itself ended the game
                dead += 1
                continue
            if wins_from(k, i):
                harmless += 1
                continue
            moves, fix = repair(k, i, args.repair_depth)
            if moves:
                recovered[moves] += 1
            else:
                locks.append((i, step, d, k))
        g.do(step)
        if g.over:
            break

    print("  %d solution steps | %d distinct deviations tried | %.1fs"
          % (i + 1, tried, time.time() - t0))
    print("  harmless (the solution still wins)      %4d" % harmless)
    print("  ended the game there and then           %4d" % dead)
    print("  recoverable %-27s %4d   %s"
          % ("(moves needed: %s)" % dict(sorted(recovered.items())) if recovered else "",
             sum(recovered.values()), ""))
    print("  SOFTLOCKS (alive, victory gone)         %4d" % len(locks))
    for i, step, d, k in locks[:10]:
        print("   !! after %d steps, at %r, doing %r leaves you in room %d"
              % (i, step, d, k[0]))
        print("      %s | %s" % (" | ".join(SOLUTION[max(0, i - 6):i]), d))
    return len(locks)

# ---------------------------------------------------------------------------
#  player 3 -- the monkey
# ---------------------------------------------------------------------------

NOISE = ["zorro", "gato", "flux", "pepino", "xyzzyx", "asdf", "molino", "queso",
         "norteo", "cid", "rey", "", "abre abre", "coge coge coge"]

def monkey_command(rng):
    r = rng.random()
    if r < 0.42:
        return "%s %s" % (rng.choice(P.VERB_WORDS), rng.choice(P.NOUN_WORDS))
    if r < 0.70:
        return rng.choice(P.DIR_WORDS)
    if r < 0.85:
        return rng.choice(P.VERB_WORDS)
    if r < 0.93:
        return rng.choice(NOISE)
    return "%s %s" % (rng.choice(P.VERB_WORDS + NOISE), rng.choice(P.NOUN_WORDS + NOISE))

def run_monkey(args):
    print("=" * 62)
    print("PLAYER 3 -- the monkey (%d seeded sessions x %d commands)"
          % (args.sessions, args.length))
    print("=" * 62)
    bad = cmds = 0
    ends = collections.Counter()
    rules_hit = set()
    t0 = time.time()
    for seed in range(args.sessions):
        rng = random.Random(seed)
        t = P.Table()
        prev_flags, prev_honra = frozenset(), 0
        for step in range(args.length):
            c = monkey_command(rng)
            problems, resp = t.do(c)
            cmds += 1
            if resp[0] == "RULE":
                rules_hit.add(resp[1])
            v = t.sim_view()
            if not problems:
                h = P.honra(v[2], v[3])
                if not (1 <= v[0] <= S.NR):
                    problems = ["room out of range: %d" % v[0]]
                elif not prev_flags <= v[2]:
                    problems = ["a flag was cleared: %s" % sorted(prev_flags - v[2])]
                elif h > 7:
                    problems = ["honra above 7: %d" % h]
                elif h < prev_honra:
                    # All seven gestas are flags, so this can never happen.
                    problems = ["honra went down: %d -> %d" % (prev_honra, h)]
                prev_flags, prev_honra = v[2], h
            if problems:
                bad += 1
                if bad <= 8:
                    print("   !! seed %d step %d %r: %s" % (seed, step, c, "; ".join(problems)))
                    print("      replay: python3 playtest.py --replay %d" % seed)
                break
            if t.over():
                break
        ends[{0: "alive", 1: "won", -1: "died"}[t.over()]] += 1
    print("  %d commands in %.1fs | endings: %s" % (cmds, time.time() - t0, dict(ends)))
    print("  rules fired by pure chance: %d/%d" % (len(rules_hit), len(S.R)))
    print("  divergences / broken invariants: %d" % bad)
    return bad

def run_replay(args):
    rng = random.Random(args.replay)
    t = P.Table()
    print("=== replay of monkey seed %d ===" % args.replay)
    for step in range(args.length):
        c = monkey_command(rng)
        problems, resp = t.do(c)
        print(" %3d %-24s rm=%-2d %-22s %s"
              % (step, repr(c), t.sim.rm, P._rule(resp),
                 "DIVERGENCE: " + "; ".join(problems) if problems else ""))
        if problems or t.over():
            break
    return 0

# ---------------------------------------------------------------------------
#  player 4 -- the transcripts
# ---------------------------------------------------------------------------
def render(t, cmd):
    """One exchange, laid out the way the 40-column screen lays it out."""
    rm = t.sim.rm
    v = t.sim_view()
    out = ["> " + cmd,
           "[%s   honra %d/7]" % (T.norm(S.RM[rm - 1]["name"]), P.honra(v[2], v[3]))]
    for l in T.wrap_lines(S.DESC.get(rm, ""))[:T.DESCROWS]:
        out.append("  " + l)
    out.append("  --")
    # "->7 Alcocer" is the model's internal move marker, not prose the player
    # ever sees; the BASIC just repaints the room.  Say so in words instead.
    msg = t.sim.last
    body = ("(vas a %s)" % S.RM[rm - 1]["name"]) if msg.startswith("->") else msg
    for l in T.wrap_lines(body)[:T.MSGROWS]:
        out.append("  " + l)
    here = [S.ITEMS[i][0] for i in sorted(S.ITEMS) if t.sim.loc.get(i) == rm]
    if here:
        out.append("  ves: " + " ".join(here))
    return "\n".join(out)

def scenarios():
    return {
        "critical-path": SOLUTION,
        "death-forzar-puerta": "baja|monta babieca|sube|este|este|fuerza puerta".split("|"),
        "death-duero-a-pie": "este|este|coge ensena|este|sur|este|sur|este".split("|"),
        "death-arcas-selladas": ("este|este|este|mira antolinez|sur|coge arena|oeste|"
                                 "llena arcas|sella arcas|abre arcas").split("|"),
        "refusals": ["mira", "i", "coge castillo", "coge manto", "coge manto",
                     "deja manto", "deja manto", "norte", "abracadabra",
                     "zorro", "canta", "baila", "hola", "besa babieca"],
    }

def run_transcripts(args):
    print("=" * 62)
    print("PLAYER 4 -- the transcripts (what the screen actually says)")
    print("=" * 62)
    if args.update and not os.path.isdir(GOLDEN):
        os.makedirs(GOLDEN)
    bad = 0
    for name, cmds in sorted(scenarios().items()):
        t = P.Table()
        blocks = []
        for c in cmds:
            problems, _ = t.do(c)
            if problems:
                bad += 1
                print("   !! %s: %r diverged: %s" % (name, c, "; ".join(problems)))
                break
            blocks.append(render(t, c))
            if t.over():
                blocks.append("*** %s ***" % ("VICTORIA" if t.over() == 1 else "DERROTA"))
                break
        text = "\n\n".join(blocks) + "\n"
        path = os.path.join(GOLDEN, name + ".txt")
        if args.update:
            open(path, "w", encoding="utf-8").write(text)
            print("  wrote %-24s %3d exchanges" % (name + ".txt", len(blocks)))
        elif not os.path.exists(path):
            bad += 1
            print("   !! %s.txt missing -- run --transcripts --update to record it" % name)
        elif open(path, encoding="utf-8").read() != text:
            bad += 1
            import difflib
            have = open(path, encoding="utf-8").read().splitlines()
            d = list(difflib.unified_diff(have, text.splitlines(),
                                          "recorded", "now", lineterm="", n=1))
            print("   !! %s.txt no longer matches what the game says:" % name)
            for l in d[:24]:
                print("      " + l)
            print("      (%d diff lines; --update re-records if the change is wanted)" % len(d))
        else:
            print("  ok %-24s %3d exchanges" % (name + ".txt", len(blocks)))
    return bad

# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="players who actually play El Cid")
    ap.add_argument("--explore", action="store_true")
    ap.add_argument("--spoiler", action="store_true")
    ap.add_argument("--monkey", action="store_true")
    ap.add_argument("--transcripts", action="store_true")
    ap.add_argument("--update", action="store_true", help="re-record golden transcripts")
    ap.add_argument("--replay", type=int, metavar="SEED", help="re-run one monkey session")
    ap.add_argument("--sessions", type=int, default=500)
    ap.add_argument("--length", type=int, default=120)
    ap.add_argument("--depth", type=int, default=2, help="explorer radius from the corridor")
    ap.add_argument("--repair-depth", type=int, default=2,
                    help="how many moves the spoiler may use to undo a deviation")
    ap.add_argument("--budget", type=int, default=200000, help="explorer state cap")
    ap.add_argument("--time", type=float, default=300.0, help="explorer time cap (s)")
    ap.add_argument("--allow-partial", action="store_true",
                    help="do not fail when the explorer stops early")
    ap.add_argument("--deep", action="store_true", help="deeper search, more sessions")
    args = ap.parse_args()

    if args.replay is not None:
        return run_replay(args)
    if args.deep:
        args.depth = max(args.depth, 3)
        args.sessions = max(args.sessions, 5000)
        args.time = max(args.time, 1800.0)

    picked = args.explore or args.spoiler or args.monkey or args.transcripts
    bad = 0
    t0 = time.time()
    if args.explore or not picked:
        bad += run_explore(args); print()
    if args.spoiler or not picked:
        bad += run_spoiler(args); print()
    if args.monkey or not picked:
        bad += run_monkey(args); print()
    if args.transcripts or not picked:
        bad += run_transcripts(args); print()

    print("-" * 62)
    print("PLAYTEST: %s   (%.1fs)"
          % ("ALL CLEAR" if not bad else "%d PROBLEM(S)" % bad, time.time() - t0))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
