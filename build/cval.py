#!/usr/bin/env python3
# Static validator for a C64 BASIC v2 source (lowercase, petcat -w2).
# The C128 (--detail) build is a *different target*: it may use the handful of
# BASIC 7.0 keywords listed in C128KW.  Pass a file whose name contains "128"
# (or --c128) to validate it as a C128 program instead of pure C64 v2.
import re, sys
path = sys.argv[1]
C128 = "128" in path or "--c128" in sys.argv
# BASIC 7.0 keywords the C128 build legitimately uses (fast boot, story-card
# loaders, trap-guarded endings): on the C128 target these are keywords, not
# forbidden, not variables.
C128KW = set("bload dload graphic color slow fast trap".split())
lines = [l.rstrip("\n") for l in open(path) if l.strip()]
T = {}
for l in lines:
    m = re.match(r"(\d+) ?(.*)$", l)
    T[int(m.group(1))] = m.group(2)
problems = 0
def fail(m):
    global problems; problems += 1; print("FAIL:", m)

def strip(body):
    # remove quoted strings and trailing rem
    b = re.sub(r'"[^"]*"', '""', body)
    b = re.split(r'\brem\b', b, maxsplit=1)[0]
    return b

# 1. lowercase only
for n, b in T.items():
    if re.search(r'[A-Z]', b): fail("uppercase in %d" % n)

# 2. forbidden C128/unsupported keywords (petcat -w2 would mis-tokenize these)
FORB = """else instr getkey trap resume scnclr graphic color box circle char draw
gshape sshape locate scale paint do loop while until exit begin bend fast slow
sound play vol tempo envelope filter movspr sprite sprcolor sprsav sprdef collision
rreg bank sleep dopen dclose dload dsave append record concat header scratch collect
rename backup directory catalog dverify dclear window boot width key monitor using
pudef tron troff renumber auto help dec hex rgr rclr rdot joy pot pen bump rsppos
rspcolor rwindow pointer xor stash fetch swap off""".split()
if C128:
    FORB = [k for k in FORB if k not in C128KW]
for n, b in T.items():
    s = strip(b)
    for kw in FORB:
        if re.search(r'(?<![a-z0-9$%])' + kw + r'(?![a-z0-9$(])', s):
            fail("forbidden BASIC2 keyword '%s' in line %d: %s" % (kw, n, s.strip()))

# 3. jump targets exist
ref = []
big = "\n".join("%d %s" % (n, b) for n, b in T.items())
ref += re.findall(r'\b(?:goto|gosub|then|run|restore)\s+(\d+)', big)
for n, b in T.items():
    for mm in re.finditer(r'\bon\b.*?\b(?:goto|gosub)\s+([\d,]+)', b):
        ref += mm.group(1).split(",")
    # bare "then <num>" / "if..then num"
    for mm in re.finditer(r'\bthen\s+(\d+)', b):
        ref.append(mm.group(1))
    # goto/gosub at line end like "402" used as `then 402`
bad = sorted(set(int(x) for x in ref if x and int(x) not in T))
if bad: fail("dangling jump targets: %s" % bad)
else: print("OK jumps: %d refs resolve" % len(set(ref)))

# also catch "if a$=... then 402" numeric and "goto 21"/"goto30" no-space
for n, b in T.items():
    for mm in re.finditer(r'\b(goto|gosub|then)(\d+)', b):
        if int(mm.group(2)) not in T: fail("dangling %s%s in %d" % (mm.group(1), mm.group(2), n))

# 4. reserved var assignment (C64: ti, st, ti$)
for n, b in T.items():
    s = strip(b)
    for st in s.split(":"):
        m = re.match(r'\s*(ti\$|ti|st)\s*=([^=]|$)', st)
        if m and 'ti$' != m.group(1):  # ti$ assignment is legal (sets clock) but we don't use it
            fail("reserved '%s' assigned in %d: %s" % (m.group(1), n, st.strip()))

# 5. 2-char variable collisions
KW = set("""end for next data input dim read let goto run if restore gosub return rem
stop on wait load save verify def poke print cont list clr cmd sys open close get new
tab to fn spc then not step and or sgn int abs usr fre pos sqr rnd log exp cos sin tan
atn peek len str val asc chr left right mid go st ti time""".split())
if C128: KW |= C128KW
names = {}
kwsort = sorted(KW, key=len, reverse=True)
def peel(tok):
    # strip leading keyword prefixes (BASIC allows keyword glued to operand)
    changed = True
    while changed:
        changed = False
        for kw in kwsort:
            if tok.startswith(kw) and tok != kw:
                tok = tok[len(kw):]; changed = True; break
    return tok
for n, b in T.items():
    if b.lstrip().startswith("rem"): continue
    if b.lstrip().startswith("data"): continue
    s = re.sub(r'"[^"]*"', ' ', b)
    s = re.split(r'\brem\b', s, maxsplit=1)[0]
    for m in re.finditer(r'[a-z][a-z0-9]*[$%]?', s):
        tok = peel(m.group(0))
        if not tok or not tok[0].isalpha(): continue
        if tok in KW or tok.rstrip('$%') in KW: continue
        names[tok] = 1
coll = {}
for tok in names:
    base = re.sub(r'[^a-z0-9]', '', tok)
    suf = tok[-1] if tok[-1] in '$%' else ''
    coll.setdefault(base[:2] + suf, set()).add(tok)
bad = {k: v for k, v in coll.items() if len(v) > 1}
if bad:
    for k, v in sorted(bad.items()): fail("2-char collision '%s' <= %s" % (k, sorted(v)))
else: print("OK no 2-char collisions (%d identifiers)" % len(names))

# 6. ascending unique lines
nums = [int(re.match(r"\d+", l).group(0)) for l in lines]
if nums != sorted(nums): fail("not ascending")
if len(nums) != len(set(nums)): fail("dup line numbers")
print("OK %d lines ascending/unique" % len(nums))
print("\nALL OK" if problems == 0 else "\n%d PROBLEM(S)" % problems)
sys.exit(1 if problems else 0)
