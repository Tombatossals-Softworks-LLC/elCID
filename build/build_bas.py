#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble elcid.bas (C64 BASIC v2) from the verified spec (cidspec) + scenes.
The BASIC special-handler is a generic rule-interpreter mirroring cidsim.do().

Two builds from one source (game logic identical; only the art plumbing differs):
    python3 build_bas.py --detail   -> ../elcid-128.bas   packed art in the PRG   (C128, PRG = disk file)
    python3 build_bas.py --c64disk  -> ../elcid-c64d.bas  packed art bulk-LOADed  (C64 disk)
(The old single-file C64 build with resident DATA art was retired: the full
game — lion episode, saves, sound, text caches — plus a resident art table no
longer fits 38 KB. The disk build is strictly better on every C64.)
Both builds keep ALL 32 hand-drawn scenes resident as a packed 19.2 KB
blob (rooms.packed_blob) and paint a room with one ~10 ms machine-code blit
(rooms.ml128/ml64, poked from DATA at boot) — a room change never touches the
disk.  On the C128 the blob is appended to the game PRG itself at $A000 (bank 0,
above the program; variables live in bank 1).  On the C64 it is bulk-LOADed once
at boot into RAM the interpreter cannot reach ($A000/$E000 under the ROMs and
$C100), so the game *gains* BASIC memory versus the lean build."""
import sys, cidspec as S, rooms, re

DETAIL  = "--detail"  in sys.argv     # C128: packed art appended to the PRG
C64DISK = "--c64disk" in sys.argv     # C64 disk: packed art bulk-LOADed at boot
assert DETAIL or C64DISK, "pick a build: --detail (C128) or --c64disk (C64)"
DISKART = True
OUTFILE = "../elcid-128.bas" if DETAIL else "../elcid-c64d.bas"

if DETAIL:
    BLIT_ML, NMI_STUB, ANIM_SYS = rooms.ml128()
    ML_ORG, BLIT_SYS = rooms.ML128, rooms.ML128
else:
    BLIT_ML, NMI_STUB, BLIT_SYS, ANIM_SYS, NAMEBUF = rooms.ml64()
    ML_ORG = rooms.ML64

# ---------- text helpers ----------
def norm(t):
    t = t.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    t = t.replace("ñ","n").replace("ü","u").replace("Á","a").replace("¡","").replace("¿","")
    t = t.lower()
    t = "".join(c for c in t if c in "abcdefghijklmnopqrstuvwxyz0123456789 .,!?'():-/")
    return re.sub(r"\s+", " ", t).strip()
def wrap(t, w=36):
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
    return "/".join(x for x in out if x != "")
def q(s): return '"' + s.replace('"', "") + '"'

NR, NI, NU = S.NR, S.NI, len(S.R)
NOTAKE = [i for i in sorted(S.ITEMS) if not S.ITEMS[i][3]]   # babieca, arcas, tienda

# Seven optional deeds of honour; the legendary ending needs all but one.
# Both the victory *text* (line 71) and the C128 story *card* (line 89) key off
# this one number -- they used to disagree, and a 5-deed run got the standard
# ending followed by the LEYENDA card.
HONRA_DEEDS = 7
LEGEND_AT   = HONRA_DEEDS - 1

# ---------- build noun table (word -> code) ----------
NOUNTAB = []
seen = set()
for i in sorted(S.ITEMS):
    for w in [S.ITEMS[i][0]] + S.ITEMS[i][1]:
        w = norm(w)
        if w and w not in seen: seen.add(w); NOUNTAB.append((w, i))
for w, c in S.SCEN.items():
    w = norm(w)
    if w and w not in seen: seen.add(w); NOUNTAB.append((w, c))
VERBTAB = sorted(set((norm(w), c) for w, c in S.VERB.items()))


# ---------- prune vocabulary to fit C64 memory ----------
KEEPV=set("lee coge mira baja monta sube este oeste norte sur arriba abajo da llena sella empena reza duerme espera asalta ataca finge convida envia echa asoma cine vence casa socorre ata exige muestra reta lidia acepta cava mueve empuja fuerza abre bebe deja inventario i ve usa ayuda habla examina lucha doma besa purga".split())
KEEPN=set("manto carta babieca silla ensena pan vino arcas arena tienda reliquia vianda cuerda oro botin parias colada salvo cidra gala tizona alfanje cimitarra pabellon cinchas agua corona moneda joya corneja nina antolinez sauce altar jimena abad mirador pozo mar atril jeronimo barba infantes rey minaya pero berenguer puerta dones jirones conde bodas moros flota".split())
ITEMNAME = {i: norm(S.ITEMS[i][0]) for i in S.ITEMS}
def prune_tab(tab, keep, per, names=None):
    from collections import defaultdict
    by=defaultdict(list)
    for w,c in tab: by[c].append(w)
    out=[]
    for c,ws in by.items():
        kept=[w for w in ws if w in keep]
        # never prune away the word the player can actually see on screen
        if names and c in names and names[c] in ws and names[c] not in kept:
            kept.insert(0, names[c])
        for w in sorted(ws,key=len):
            if len(kept)>=per: break
            if w not in kept: kept.append(w)
        for w in ws:
            if w in kept: out.append((w,c))
    return out
VERBTAB=prune_tab(VERBTAB,KEEPV,3)
NOUNTAB=prune_tab(NOUNTAB,KEEPN,3,ITEMNAME)
# Sort by first character so same-initial words are contiguous: the runtime
# parser builds a first-char index (vs%/ns%) and scans only that bucket
# (~4 words) instead of the whole 74-verb / 98-noun table -> ~15x fewer
# string compares per lookup.  Stable sort keeps synonyms grouped.
VERBTAB=sorted(VERBTAB, key=lambda wc: wc[0][:1])
NOUNTAB=sorted(NOUNTAB, key=lambda wc: wc[0][:1])

# ---------- engine code (BASIC v2) ----------
E = []
def L(n, code): E.append((n, code))
L(1,'rem ************ el cid campeador ************')
L(2,'rem  aventura conversacional - c64 basic v2')
L(3,'rem  (c) 2026 tombatossals softworks llc')
# hot-variable pre-pass: creation order = lookup order (linear scan per
# reference, far-fetched on the C128 where it dominated the profile at
# ~70 ms/statement). Echo-loop + parser + draw vars first, cold vars last.
L(4,'ri=0:t=0:j=0:cu=0:a$="":cx=0:sc=0:ka=0:ic=0:kc=0:co=0:ho=0:hp=0:he=0:z9=0:l8=0:sb=0:cb=0:dn$="":rt$="":bl$="":cl$="":s$="":dx=0:dy=0:w$="":fc=0:sp=0:c$=""')
L(5,'tt$="":dl=0:dz=0:p1=0:mg$="":rx=0:hd=0:va=0:ob=0:dv=0:dr=0:sq=0:w1$="":w2$="":w3$="":rm=0:nx=0:rn$="":rd$="":io$="":xt$="":kf=0:x=0:r=0:d=0:v=0:z$="":s=0:hs=0:t9=0:tk=0:en=0:ev=0:ew=0:em$=""')
L(6,'poke53280,0:poke53281,0:printchr$(147);chr$(154);')
L(19,'sb=1024:cb=55296:gw=0:l9=9:ic=sb+920:kc=cb+920:cx=2:poke54295,0:poke54296,15:poke54272,0:poke54279,0:poke54277,9:poke54278,0:poke54273,50')
if DETAIL:
    # C128: run the whole DATA-parsing boot at 2 MHz (VIC blanks; SLOW is
    # restored at line 40 just before the title paints) -> boot ~2x faster.
    L(18,'print"un momento, campeador...":fast')
    # gosub 240 = paint room rm: one SYS; the ML looks the room's RLE stream
    # up in the offset table at $A700 and expands it to screen + colour RAM.
    L(240,'poke251,rm:sys%d:return' % BLIT_SYS)
if C64DISK:
    L(18,'print"un momento, campeador..."')
    # gosub 240 = paint room rm from the bulk-loaded blob: rooms 1-13 sit under
    # the BASIC ROM, 14-26 under the KERNAL, 27-32 at $C100. One SYS blits.
    L(240,'s=%d+600*(rm-27):if rm<27 then s=%d+600*(rm-14)' % (rooms.C64_C, rooms.C64_B))
    L(241,'if rm<14 then s=%d+600*(rm-1)' % rooms.C64_A)
    L(242,'hs=int(s/256):poke251,s-256*hs:poke252,hs:sys%d:return' % BLIT_SYS)
    # gosub 245 = KERNAL-LOAD file zf$ (SA=1: to its own address) via the ML
    L(245,'poke%d,len(zf$):for j=1 to len(zf$):poke%d+j,asc(mid$(zf$,j,1)):next:sys%d:return'
          % (NAMEBUF, NAMEBUF, rooms.ML64))
L(7,'dn$="":for j=1 to 24:dn$=dn$+chr$(17):next:bl$=""')
L(8,'rt$="":for j=1 to 39:rt$=rt$+chr$(29):next:for j=1 to 40:bl$=bl$+" ":next')
L(9,'cl$=chr$(144)+chr$(5)+chr$(28)+chr$(159)+chr$(156)+chr$(30)+chr$(31)+chr$(158)+chr$(129)+chr$(149)+chr$(150)+chr$(151)+chr$(152)+chr$(153)+chr$(154)+chr$(155)')
L(10,'restore:read nr,ni,nu')
L(11,'dimvb$(%d),vk%%(%d),vs%%(26),no$(%d),nk%%(%d),ns%%(26),ru%%(nu,7),rs%%(nr),ex%%(nr,2),il%%(ni),fl%%(30),in$(ni),nn$(nr),dd$(nr),ms$(ni+nu)'
      % (len(VERBTAB), len(VERBTAB), len(NOUNTAB), len(NOUNTAB)) )
# cache every room name/desc and message once: lookups become array reads
# (READ strings cost only 3-byte descriptors on the C64: they point into the
#  program's own DATA text; the C128 copies them to roomy bank-1 string RAM)
L(12,'for j=1 to nr:read nn$(j),dd$(j):next:for j=1 to ni+nu:read ms$(j):next')
L(13,'for j=1 to ni:read in$(j):next')
L(14,'for j=1 to nr:for d=0 to 2:read ex%(j,d):next d:next j')
L(15,'for j=1 to ni:read il%(j):next')
L(16,'for j=0 to nu-1:for d=0 to 7:read ru%(j,d):next d:next j')
L(17,'for j=1 to nr:read rs%(j):next')
# read the ML blitter (from DATA, where the art table used to be) and arm the
# RAM NMI stub so RESTORE during a banked blit lands on an RTI.
L(20,'for j=0 to %d:read v:poke %d+j,v:next' % (len(BLIT_ML) - 1, ML_ORG))
L(21,'poke65530,%d:poke65531,%d' % (NMI_STUB & 255, NMI_STUB >> 8))
if C64DISK:
    # bulk-load the whole art set once: 13+13+6 rooms into $A000/$E000/$C100
    L(22,'zf$="aa":gosub 245')
    L(23,'zf$="ab":gosub 245')
    L(24,'zf$="ac":gosub 245')
L(30,'nv=0')
L(31,'read z$:if z$="*" then 34')
L(32,'read cd:nv=nv+1:vb$(nv)=z$:vk%(nv)=cd:goto 31')
L(34,'nw=0')
L(35,'read z$:if z$="*" then 37')
L(36,'read cd:nw=nw+1:no$(nw)=z$:nk%(nw)=cd:goto 35')
L(37,'for j=1 to nv:kf=asc(vb$(j))-64:if vs%(kf)=0 then vs%(kf)=j')
L(38,'next:for j=1 to nw:kf=asc(no$(j))-64:if ns%(kf)=0 then ns%(kf)=j')
L(39,'next')
L(40,'slow:gosub 995:gosub 970:rm=1' if DETAIL else 'gosub 995:gosub 970:rm=1')  # strings first: the title music tick reads tm$
L(49,'rem ===== main loop =====')
L(50,'gosub 100')
L(51,'gosub 500')
L(52,'if gw=0 then 51')
L(53,('slow:' if DETAIL else '')+'dx=0:dy=23:co=7:s$=left$("    *  pulsa una tecla  *               ",39):gosub 200')
L(54,'get a$:if a$="" then 54')
L(55,'printchr$(147)')
L(56,'if gw=2 then gosub 84')
L(57,'if gw=1 then gosub 61')
L(58,'dx=12:dy=24:co=3:s$="pulsa una tecla":gosub 200')
L(59,'get a$:if a$="" then 59')
L(60,'goto 88' if DETAIL else 'run')   # C64: replay instead of dropping to READY
if DETAIL:
    # C128: after the text ending, bloom the multicolor heraldic 'story card'.
    # Each loader (cv/cl/cd) shows a GRAPHIC-3 bitmap, waits for FIRE/key, then
    # dloads the game again (play-again). gw=2 death first; ho>=5 legendary; else
    # standard victory.  ho was set by the victory subroutine (61) for gw=1.
    # LEGEND_AT must match the threshold the victory text uses at line 71.
    # TRAP 87: run standalone (no disk / no card files) the dload error ends
    # the game cleanly instead of aborting with ?FILE NOT FOUND.
    L(87,'run')   # standalone C128 (no cards on disk): replay instead of READY
    L(88,'trap 87:if gw=2 then dload"cd"')
    L(89,'if ho>=%d then dload"cl"' % LEGEND_AT)
    L(90,'dload"cv"')
# ----- victory end-screen (computes honra from the seven deed flags) -----
# honra = count of the 7 deeds, via the C64 idiom ((x)=-1 when true) -> one line
L(61,'ho=-(fl%(24)=1)-(fl%(26)=1)-(fl%(27)=1)-(fl%(22)=1)-(fl%(28)=1)-(fl%(29)=1)-(fl%(30)=1)')
L(68,'rm=32:gosub 240')
L(69,'gosub 874:dx=15:dy=11:co=7:s$="victoria!":gosub 200')
L(70,'dx=7:dy=12:co=15:s$="valencia es del campeador":gosub 200')
L(71,'if ho>=%d then 76' % LEGEND_AT)
L(72,'dx=9:dy=15:co=15:s$="honra del cid: "+chr$(48+ho)+" de %d":gosub 200' % HONRA_DEEDS)
L(73,'dx=1:dy=17:co=11:s$="(restan secretos y gestas por hallar)":gosub 200')
L(74,'return')
L(76,'dx=9:dy=13:co=15:s$="honra del cid: "+chr$(48+ho)+" de %d":gosub 200' % HONRA_DEEDS)
L(77,'dx=8:dy=14:co=7:s$="la leyenda del campeador":gosub 200')
L(78,'dx=2:dy=16:co=15:s$="hallaste los tesoros de los godos y":gosub 200')
L(79,'dx=2:dy=17:co=15:s$="amparaste a moros y a cristianos.":gosub 200')
L(80,'dx=2:dy=19:co=7:s$="tus hijas, reinas; de su sangre, dice":gosub 200')
L(81,'dx=2:dy=20:co=7:s$="el cantar, naceran reyes de espanna:":gosub 200')
L(82,'dx=8:dy=22:co=13:s$="oy los reyes de espanna":gosub 200')
L(83,'dx=11:dy=23:co=13:s$="sos parientes son.":gosub 200:return')
# ----- death end-screen (somber, black) -----
L(84,'gosub 240:gosub 872:dx=9:dy=11:co=2:s$="has caido, campeador.":gosub 200')
L(85,'dx=1:dy=13:co=15:s$="mas tu leyenda no muere con tu cuerpo.":gosub 200')
L(86,'dx=3:dy=15:co=7:s$="el que en buen hora cinxo espada.":gosub 200:return')
L(99,'rem ===== draw room rm =====')
L(100,'printchr$(147);')
L(101,'gosub 240:gosub 870')
L(102,'gosub 950:gosub 920')
L(103,'gosub 106:gosub 210:gosub 280:gosub 104:return')
L(104,'dx=0:dy=24:co=11:s$="ayuda=verbos  i=objetos  graba/recupera":gosub 200:return')
L(106,'ho=fl%(22)+fl%(24)+fl%(26)+fl%(27)+fl%(28)+fl%(29)+fl%(30)')
L(107,'s$=left$(rn$+bl$,29)+"honra "+chr$(48+ho)+"/%d"' % HONRA_DEEDS)
L(108,'dx=0:dy=10:co=7:s$=chr$(18)+s$:gosub 200:hp=ho:return')
L(199,'rem pstr: print s$ at dx,dy colour co (home+cursor moves+petscii colour char; all-rom, zero pokes, portable c64/c128)')
L(200,'print chr$(19);left$(dn$,dy);left$(rt$,dx);mid$(cl$,co+1,1);s$;chr$(146);:return')
L(209,'rem show desc rd$ from row 12')
L(210,'tt$=rd$:dl=11:dz=14:co=15:gosub 320:l9=5:return')
L(279,'rem status: exits + items')
L(280,'dx=1:dy=21:co=3:s$=left$("salidas: "+xt$+"                       ",38):gosub 200')
L(281,'gosub 930:dx=1:dy=22:co=13:s$=left$(io$+"                                     ",38):gosub 200:return')
L(299,'rem show message mg$ (rows 12-20) + status')
L(300,'ho=fl%(22)+fl%(24)+fl%(26)+fl%(27)+fl%(28)+fl%(29)+fl%(30):he=(ho>hp)')
L(301,'tt$=mg$:dl=16:dz=20:gosub 315:dl=16:co=1:gosub 320:gosub 280')
L(302,'if ho=hp then return')
L(303,'if he then gosub 866')
L(304,'gosub 106:return')
L(314,'rem clear text rows dl..dz (print blank lines via rom editor; ~90x faster than poke loop)')
L(315,'print chr$(19);left$(dn$,dl);:z9=dl+l9-1:if z9>dz then z9=dz')
L(316,'for r=dl to z9:print bl$;:next:return')
L(319,'rem print tt$ split on / from row dl, max dz, colour co')
L(320,'p1=1:l8=dl')
# early-exit: without it the scan walks the whole remaining text for every
# output row (O(rows x len), one MID$ alloc per char) - the profiled hot spot
L(321,'sp=0:for j=p1 to len(tt$):if mid$(tt$,j,1)="/" then sp=j:j=len(tt$)')
L(322,'next')
L(323,'if sp=0 then s$=mid$(tt$,p1)')
L(324,'if sp>0 then s$=mid$(tt$,p1,sp-p1)')
L(325,'dx=1:dy=dl:gosub 200:dl=dl+1')
L(326,'if sp=0 then l9=dl-l8:return')
L(327,'if dl>dz then l9=dl-l8:return')
L(328,'p1=sp+1:goto 321')
L(397,'rem input -> c$ row 23 (echo by direct poke, no string garbage)')
# C128: SLOW here (screen back on) - every path funnels into the input draw;
# FAST at 501 the moment a command is taken -> the whole response runs at 2 MHz
L(400,('slow:' if DETAIL else '')+'cu=1:co=15:ic=sb+920:kc=cb+920:print chr$(19);left$(dn$,23);mid$(cl$,co+1,1);">";left$(bl$,38);:cx=2')
# animation tick: every ~12 jiffies the ML flutters pennants / marches the
# water sparkle for the current room, and the prompt cursor blinks
L(396,'if ti<t9 then return')
L(397,'t9=ti+12:tk=1-tk:if cu=1 then poke ic+cx,32+128*tk:poke kc+cx,co')
L(398,'poke251,rm:poke252,tk:sys'+str(ANIM_SYS)+':return')
L(402,'get a$:if a$="" then gosub 396:goto 402')
L(403,'if a$=chr$(13) then 410')
L(404,'if a$=chr$(20) and cx>2 then poke ic+cx,32:cx=cx-1:poke ic+cx,32')
L(405,'if a$=chr$(20) then 402')
L(406,'if asc(a$)<32 or asc(a$)>95 or cx>35 then 402')
L(407,'ka=asc(a$):sc=ka:if ka>63 then sc=ka-64')
L(408,'poke ic+cx,sc:poke kc+cx,co:cx=cx+1:poke54276,17:poke54276,16:goto 402')
L(410,'poke ic+cx,32:c$="":if cx<3 then return')
L(411,'for j=2 to cx-1:sc=peek(ic+j):ka=sc:if sc<32 then ka=sc+64')
L(412,'c$=c$+chr$(ka):next:return')
L(499,'rem parse + dispatch')
L(500,'gosub 400:if c$="" then return')
L(501,('fast:' if DETAIL else '')+'sp=0:for j=1 to len(c$):if mid$(c$,j,1)=" " then sp=j:j=len(c$)')
L(502,'next')
L(503,'if sp=0 then w1$=c$:w2$=""')
L(504,'if sp>0 then w1$=left$(c$,sp-1):w3$=mid$(c$,sp+1)')
L(505,'if sp=0 then 508')
L(506,'sq=0:for j=1 to len(w3$):if mid$(w3$,j,1)=" " then sq=j:j=len(w3$)')
L(507,'next:w2$=w3$:if sq>0 then w2$=left$(w3$,sq-1)')
L(508,'w$=w1$:gosub 910:va=fc')
L(509,'w$=w2$:gosub 940:ob=fc')
L(510,'dv=0:w$=w1$:gosub 900:dv=dr')
L(511,'if va=5 then w$=w2$:gosub 900:dv=dr')
L(512,'gosub 700:if hd=1 then return')
L(513,'if dv>0 then dr=dv:gosub 680:return')
L(514,'if va=1 then gosub 600:return')
L(515,'if va=2 then gosub 620:return')
L(516,'if va=3 then gosub 640:return')
L(517,'if va=4 then gosub 660:return')
L(518,'if va=12 then mg$=ha$+hb$:gosub 300:return')
L(519,'if va=0 then mg$="ese verbo no lo conozco. di ayuda.":gosub 300:gosub 867:return')
L(520,'if va=46 then gosub 850:return')
L(521,'if va=47 then gosub 860:return')
# --- global easter eggs (state-neutral jokes; CANTA gets a SID flourish) ---
L(522,'if va=48 then mg$="eso funcionaba en otra cueva, forastero. aqui se reza.":gosub 300:return')
L(523,'if va=49 then mg$="de los sos ojos tan fuertemientre llorando... el juglar, maravillado, te cede la palabra.":gosub 300:gosub 868:return')
L(524,'if va=50 then mg$="bailas una estampida castellana. babieca marca el compas con el casco.":gosub 300:return')
L(525,'if va=51 then mg$="salve, campeador! toda castilla responde al saludo.":gosub 300:return')
L(526,'mg$="eso no puedes hacerlo aqui, cid.":gosub 300:gosub 867:return')
# ----- save / load (GRABA / RECUPERA): state = room + flags + item places.
# The drive's error channel (15) makes both robust: a missing file or absent
# drive reports en>19 and we answer in prose instead of crashing. -----
# ----- SID: step / dirge / fanfare / title motif (voice 1) -----
L(867,'poke54273,6:poke54276,33:for x=1 to 45:next:poke54276,32:return')
L(868,'for j=1 to 3:poke54273,18+j*13:poke54276,17:for x=1 to 45:next:poke54276,16:next:return')
L(866,'poke53280,7:for j=1 to 6:poke54273,28+j*11:poke54276,17:for x=1 to 22:next:poke54276,16:next:poke53280,0:return')
L(870,'poke54273,10:poke54276,33:for x=1 to 12:next:poke54276,32:poke54273,7:poke54276,33:for x=1 to 12:next:poke54276,32:return')
L(872,'for j=30 to 4 step-2:poke53280,2:poke54273,j:poke54276,33:for x=1 to 15:next:poke53280,0:for x=1 to 15:next:next:poke54276,32:return')
L(874,'for j=1 to 6:poke53280,1:poke54273,asc(mid$("aeiror",j,1))-48:poke54280,7:poke54276,17:poke54283,33:for x=1 to 55:next:poke53280,0:poke54276,16:poke54283,32:next:return'
  if DETAIL else
  'for j=1 to 6:poke53280,1:poke54273,asc(mid$("aeiror",j,1))-48:poke54276,17:for x=1 to 55:next:poke53280,0:poke54276,16:next:return')
L(850,'open15,8,15:open2,8,2,"@0:partida,s,w"')
L(851,'print#2,rm:for j=0 to 31:print#2,fl%(j):next:for j=1 to ni:print#2,il%(j):next')
L(852,'close2:input#15,en,em$,ev,ew:close15:mg$="partida grabada en disco."')
L(853,'if en>19 then mg$="no pude grabar. hay disco?"')
L(854,'gosub 300:return')
L(860,'open15,8,15:open2,8,2,"partida,s,r":input#15,en,em$,ev,ew')
L(861,'if en>19 then close2:close15:mg$="no hay partida grabada.":gosub 300:return')
L(862,'input#2,rm:for j=0 to 31:input#2,fl%(j):next:for j=1 to ni:input#2,il%(j):next')
L(863,'close2:close15:gosub 100:mg$="partida recuperada. adelante, campeador.":gosub 300:return')
L(599,'rem look')
L(600,'if ob=0 then gosub 100:return')
L(601,'if ob>=1 and ob<=ni then 605')
L(602,'mg$="nada de particular hay en ello.":gosub 300:gosub 867:return')
L(605,'if il%(ob)=rm or il%(ob)=-1 then rx=ob:gosub 960:gosub 300:return')
L(606,'mg$="eso no lo ves por aqui.":gosub 300:gosub 867:return')
L(619,'rem take')
L(620,'if ob<1 or ob>ni then mg$="coger, que cosa?":gosub 300:return')
L(621,'if il%(ob)=-1 then mg$="ya lo llevas contigo.":gosub 300:return')
L(622,'if il%(ob)<>rm then mg$="eso no lo ves por aqui.":gosub 300:gosub 867:return')
L(623,'if %s then mg$="eso no has de llevarlo.":gosub 300:gosub 867:return' % " or ".join("ob=%d" % i for i in NOTAKE))
L(624,'il%(ob)=-1:mg$="tomas "+in$(ob)+".":gosub 300:return')
L(639,'rem drop')
L(640,'if ob<1 or ob>ni then mg$="dejar, que cosa?":gosub 300:return')
L(641,'if il%(ob)<>-1 then mg$="eso no lo llevas.":gosub 300:return')
L(642,'il%(ob)=rm:mg$="dejas "+in$(ob)+".":gosub 300:return')
L(659,'rem inventory')
L(660,'mg$="llevas:":for j=1 to ni:if il%(j)=-1 and len(mg$)<160 then mg$=mg$+" "+in$(j)')
L(661,'next')
L(662,'if mg$="llevas:" then mg$="nada llevas contigo, campeador."')
L(663,'gosub 300:return')
L(679,'rem move dir dr (with gates)')
L(680,'if rm=11 and dr=3 then if fl%(5)=0 or il%(5)<>-1 then mg$=gd$:gosub 300:gw=2:return')
L(681,'if rm=17 and dr=3 then if fl%(10)=0 then mg$=gl$:gosub 300:return')
L(682,'t=ex%(rm,int((dr-1)/2)):nx=t and 63:if dr=2*int(dr/2) then nx=int(t/64)')
L(683,'if nx=0 then mg$="por ahi no hay camino, cid.":gosub 300:gosub 867:return')
L(684,'rm=nx:gosub 100:return')
# ru% columns: 0 room  1 verb  2 object  3 needed-flags (packed base 32)
#              4 forbidden flag + set flag (packed base 32)
#              5 items given (packed base 32)
#              6 item taken + item required in hand (packed base 32)
#              7 kind (0 / lose / win)
# The three "needed flag" slots and the two "give" slots were separate columns
# once, but only 4 of 76 rules need a second flag and only 1 gives a second
# item, so 5 of 13 columns were zero for almost every rule -- 462 bytes of a
# build with a few hundred bytes of string heap to its name.  Packing them
# base-32 (flags and items are both <= 30, so three fit in 15 bits) is also
# *faster*: the common case is now one array read and one test where it used
# to be five of each.
L(699,'rem ===== rule interpreter -> hd =====')
L(700,'hd=0:for ri=rs%(rm) to nu-1')
L(701,'if ru%(ri,0)<>rm then 716')
L(702,'if ru%(ri,1)<>va then 720')
L(703,'if ru%(ri,2)<>0 and ru%(ri,2)<>ob then 720')
L(704,'t=ru%(ri,3)')
L(705,'if t>0 then if fl%(t and 31)=0 then 720')
L(706,'if t>31 then t=int(t/32):goto 705')
L(707,'t=ru%(ri,4) and 31:if t>0 then if fl%(t)=1 then 720')
L(708,'t=int(ru%(ri,6)/32):if t>0 then if il%(t)<>-1 then 720')
L(709,'t=int(ru%(ri,4)/32):if t>0 then fl%(t)=1')
L(710,'t=ru%(ri,5):if t>0 then il%(t and 31)=-1:if t>31 then il%(int(t/32))=-1')
L(711,'t=ru%(ri,6) and 31:if t>0 then il%(t)=0')
L(713,'rx=200+ri:gosub 960:gosub 300:hd=1')
L(714,'if ru%(ri,7)=1 then gw=2')
L(715,'if ru%(ri,7)=2 then gw=1')
L(716,'ri=nu')
L(720,'next ri:return')
L(899,'rem dirof w$ -> dr')
L(900,'dr=0')
L(901,'if w$="n" or w$="norte" then dr=1')
L(902,'if w$="s" or w$="sur" then dr=2')
L(903,'if w$="e" or w$="este" then dr=3')
L(904,'if w$="o" or w$="oeste" then dr=4')
L(905,'if w$="sube" or w$="arriba" then dr=5')
L(906,'if w$="baja" or w$="abajo" then dr=6')
L(907,'return')
# findverb / findnoun: the vocabulary is emitted sorted by first letter, so a
# lookup scans only the ~4 words sharing that initial (vs%/ns% hold the first
# index for each letter) instead of the whole 126-verb / 130-noun table.
# The bucket arrays are indexed by LETTER ORDINAL (asc-64, 1..26), not by the
# raw PETSCII code: dimensioning them to 90 left 128 cells permanently unused,
# 256 bytes the C64 build cannot spare.  Anything that is not a letter cannot
# start a known word, so it returns 0 before the subtraction can go negative.
L(909,'rem findverb w$->fc')
L(910,'fc=0:if w$="" then return')
L(911,'kf=asc(w$):if kf<65 or kf>90 then return')
L(912,'j=vs%(kf-64):if j=0 then return')
L(913,'if w$=vb$(j) then fc=vk%(j):return')
L(914,'j=j+1:if j<=nv then if asc(vb$(j))=kf then 913')
L(915,'return')
L(939,'rem findnoun w$->fc')
L(940,'fc=0:if w$="" then return')
L(941,'kf=asc(w$):if kf<65 or kf>90 then return')
L(942,'j=ns%(kf-64):if j=0 then return')
L(943,'if w$=no$(j) then fc=nk%(j):return')
L(944,'j=j+1:if j<=nw then if asc(no$(j))=kf then 943')
L(945,'return')

L(920,'xt$="":t=ex%(rm,0):if t and 63 then xt$="norte "')
L(921,'if t>63 then xt$=xt$+"sur "')
L(922,'t=ex%(rm,1):if t and 63 then xt$=xt$+"este "')
L(923,'if t>63 then xt$=xt$+"oeste "')
L(924,'t=ex%(rm,2):if t and 63 then xt$=xt$+"arriba "')
L(925,'if t>63 then xt$=xt$+"abajo "')
L(927,'if xt$="" then xt$="ninguna"')
L(928,'return')
L(929,'rem build items-here string io$')
L(930,'io$="":for j=1 to ni:if il%(j)=rm then io$=io$+in$(j)+" "')
L(931,'next')
L(932,'if io$<>"" then io$="ves: "+io$')
L(934,'return')
L(949,'rem read room rm name->rn$ desc->rd$')
L(950,'rn$=nn$(rm):rd$=dd$(rm):return')
L(959,'rem read on-demand text index ob2 -> mg$ (item exam if ob2<=ni; rule msg if ob2>=200)')
L(960,'if rx>=200 then mg$=ms$(ni+1+rx-200):return')
L(961,'mg$=ms$(rx):return')
L(969,'rem title screen + help/gate strings')
L(970,'gosub 980:return')
# title screen draws art of room 32 then title text
L(980,'rm=1:gosub 240')
L(977,'dx=0:co=0:dy=1:s$=chr$(18)+left$(bl$,40):gosub 200:dy=2:s$=chr$(18)+left$(bl$,40):gosub 200:return')
L(978,'gosub 977:dx=14:dy=1:co=7:s$="e l   c i d":gosub 200:dx=11:dy=2:co=7:s$="c a m p e a d o r":gosub 200:return')
L(981,'gosub 978')
L(982,'dx=4:dy=11:co=1:s$="de los sos ojos tan fuertemientre":gosub 200')
L(983,'dx=4:dy=12:co=1:s$="llorando, tornava la cabeza e":gosub 200')
L(984,'dx=4:dy=13:co=1:s$="estabalos catando. dios, que buen":gosub 200')
L(985,'dx=4:dy=14:co=1:s$="vassallo, si oviesse buen sennor!":gosub 200')
L(986,'dx=3:dy=16:co=15:s$="rodrigo diaz, desterrado, ha de ganar":gosub 200')
L(987,'dx=3:dy=17:co=15:s$="valencia, casar sus hijas y vengar su":gosub 200')
L(988,'dx=3:dy=18:co=15:s$="honra. ordenes de dos palabras:":gosub 200')
L(989,'dx=3:dy=19:co=15:s$="coge espada, ve norte. (ayuda=verbos)":gosub 200')
L(990,'dx=6:dy=21:co=3:s$="(c) 2026 tombatossals softworks":gosub 200')
L(991,'dx=6:dy=23:co=7:s$="* pulsa una tecla, campeador *":gosub 200')
L(878,'if ti<t8 then return')
L(879,'t8=ti+10:mu=mu+1:if mu>24 then mu=1:gosub 883')
L(880,'poke54273,asc(mid$(tm$,mu,1))-48:poke54276,16:poke54276,17')
L(881,'if (mu and 3)=1 then poke54283,32:poke54283,33')
L(882,'return')
L(883,'a9=a9+1:if a9>7 then a9=0')
L(884,'rm=asc(mid$("148;?dfp",a9+1,1))-48:gosub 240:gosub 978:return')
L(992,'cu=0:mu=0:t8=0:a9=0:poke54280,5:poke54284,9:poke54285,0')
L(993,'get a$:if a$="" then gosub 396:gosub 878:goto 993')
L(994,'poke54276,16:poke54283,16:return')
# NOTE: a tokenised BASIC line must stay under 256 bytes — the C128 relinker
# scans lines with an 8-bit index and hangs forever past that (found the
# hard way). Long strings are built in two lines.
# ---------- DATA generation ----------
D = []
# counts
D.append((10000, "data %d,%d,%d" % (NR, NI, NU)))
ln = 10010
# on-demand text: room name+desc
def emit_strings(items, start_ln):
    out = []; n = start_ln
    for s in items:
        out.append((n, "data " + q(s))); n += 1
    return out, n
names_desc = []
for r in range(1, NR+1):
    names_desc.append(norm(S.RM[r-1]["name"]))
    names_desc.append(wrap(S.DESC[r]))
blk, ln = emit_strings(names_desc, ln)
D += blk
# item exam
exam = [wrap(S.ITEMS[i][4]) for i in range(1, NI+1)]
blk, ln = emit_strings(exam, ln)
D += blk
# rule order: stable-sorted by room so the interpreter can jump straight to
# the current room's block (rs% index) instead of scanning all NU rules.
# Same-room relative order is preserved => same first-match semantics; the
# messages block is emitted in the SAME permuted order (rx = 200+ri).
RULE_ORDER = sorted(range(NU), key=lambda i: S.R[i]["room"])
RS_INDEX = []
_rooms_sorted = [S.R[i]["room"] for i in RULE_ORDER]
import bisect
for _r in range(1, NR+1):
    RS_INDEX.append(bisect.bisect_left(_rooms_sorted, _r))
# rule messages
msgs = [wrap(S.R[ri]["msg"]) for ri in RULE_ORDER]
blk, ln = emit_strings(msgs, ln)
D += blk
# item names (loaded)
itn = [norm(S.ITEMS[i][0]) for i in range(1, NI+1)]
blk, ln = emit_strings(itn, ln)
D += blk
# exits
# two exits per cell, six bits each: north|south, east|west, up|down
ex_nums = []
for r in range(1, NR+1):
    e = S.EXITS[r]
    for lo, hi in (("n","s"), ("e","o"), ("u","d")):
        a, b = e.get(lo,0), e.get(hi,0)
        assert a < 64 and b < 64, (r, lo, hi)
        ex_nums.append(a + 64*b)
# item start+take
# only the start room now: takeability is three room numbers the build inlines
# into line 623, which is 44 bytes cheaper than a 31-cell array.
it_nums = [S.ITEMS[i][2] for i in range(1, NI+1)]
# rules numeric
ru_nums = []
PACK = 32                      # flags are 1..31 and items 1..30, so 5 bits each
for r in (S.R[i] for i in RULE_ORDER):
    nd = r["need"]
    fb = (r["forbid"] + [0])[0]
    sf = (r["setf"] + [0])[0]
    assert len(nd) <= 3 and len(r["forbid"]) <= 1 and len(r["setf"]) <= 1, r
    assert all(0 < f < PACK for f in nd), ("need flag out of pack range", r)
    assert r["give2"] == 0 or r["give"] != 0, ("give2 without give", r)
    assert r["give"] < PACK and r["give2"] < PACK, ("give out of pack range", r)
    assert fb < PACK and sf < PACK and r["take"] < PACK and r["needi"] < PACK, r
    need = sum(f * PACK**k for k, f in enumerate(nd))          # base-32 little end
    give = r["give"] + PACK * r["give2"]
    flag = fb + PACK * sf                  # forbidden flag, then the flag set
    item = r["take"] + PACK * r["needi"]   # item consumed, then item required
    assert max(need, give, flag, item) < 32768
    ru_nums += [r["room"], r["v"], r["o"], need, flag, give, item, r["kind"]]
# pack a flat number list into DATA lines (<=~70 chars)
def emit_nums(nums, start_ln, tag=""):
    out = []; n = start_ln; i = 0
    while i < len(nums):
        chunk = []
        s = "data "
        while i < len(nums):
            piece = ("," if chunk else "") + str(nums[i])
            if len(s) + len(piece) > 70: break
            s += piece; chunk.append(nums[i]); i += 1
        out.append((n, s)); n += 1
    return out, n
blk, ln = emit_nums(ex_nums, ln); D += blk
blk, ln = emit_nums(it_nums, ln); D += blk
blk, ln = emit_nums(ru_nums, ln); D += blk
blk, ln = emit_nums(RS_INDEX, ln); D += blk   # rs%(1..nr): first rule of room
# ML blitter bytes — the DATA stream position where line 20 reads them
# (where the old resident art table used to live).
art_nums = list(BLIT_ML)
blk, ln = emit_nums(art_nums, ln); D += blk
# verbs
vlines = []; n = ln
s = "data "
for w, c in VERBTAB:
    piece = ("," if s != "data " else "") + q(w) + "," + str(c)
    if len(s) + len(piece) > 72: vlines.append((n, s)); n += 1; s = "data " + q(w) + "," + str(c)
    else: s += piece
vlines.append((n, s)); n += 1
vlines.append((n, 'data "*"')); n += 1
D += vlines; ln = n
# nouns
nlines = []; n = ln
s = "data "
for w, c in NOUNTAB:
    piece = ("," if s != "data " else "") + q(w) + "," + str(c)
    if len(s) + len(piece) > 72: nlines.append((n, s)); n += 1; s = "data " + q(w) + "," + str(c)
    else: s += piece
nlines.append((n, s)); n += 1
nlines.append((n, 'data "*"')); n += 1
D += nlines

# NOTE: a tokenised BASIC line must stay under 256 bytes — the C128 relinker
# scans lines with an 8-bit index and hangs forever past that (found the
# hard way). Long strings are built in two lines.
L(995,'ha$=' + q(wrap("verbos: mira habla coge deja da ve lee abre monta llena echa reza cava mueve espera asoma cine finge sella empena convida envia socorre ata exige muestra reta acepta casa vence lidia doma bebe.")))
L(996,'hb$=' + q("/" + wrap("graba/recupera: partida. n s e o arriba abajo. i inv.")))
L(997,'tm$="eefhmhfehhmquqmhmuqmhfee":gd$=' + q(wrap("cruzas el duero sin guia ni montura. la hueste se dispersa por los caminos y mueres olvidado en el yermo. fin.")))
L(998,'gl$=' + q(wrap("aun no es tiempo de ir a levante. despacha antes las parias al rey por mano de minaya.")) + ':return')

# ---------- merge, sort, write ----------
alllines = E + D
# Strip rem-only lines from the generated .bas: they cost ~1.3 KB of program
# memory (precious on the C64 build) and the documentation already lives here in
# the L(...) calls.  Keep any rem line that is a jump target (none today, but be
# safe) so we never create a dangling GOTO.
_code = "\n".join("%d %s" % (n, c) for n, c in alllines)
_targets = set()
for _mm in re.finditer(r'\b(?:goto|gosub|then|run|restore)\s*(\d+)', _code):
    _targets.add(int(_mm.group(1)))
for _mm in re.finditer(r'\bon\b.*?\b(?:goto|gosub)\s+([\d,]+)', _code):
    _targets.update(int(x) for x in _mm.group(1).split(",") if x.strip().isdigit())
def _is_rem(c): return c.strip().startswith("rem")
alllines = [(n, c) for (n, c) in alllines
            if c.strip() and not (_is_rem(c) and n not in _targets)]
seen_ln = {}
for n, c in alllines:
    assert n not in seen_ln, "dup line %d: %r vs %r" % (n, c, seen_ln[n])
    seen_ln[n] = c
out = "\n".join("%d %s" % (n, c) for n, c in sorted(alllines)) + "\n"
# run from build/ (canon.json/cidspec are here); the canonical .bas lives one level up,
# next to ELCID.PRG, where basemu/cval/petcat all expect it.
open(OUTFILE, "w").write(out)
print("wrote %s (%s): %d lines, %d bytes" % (OUTFILE, "C128" if DETAIL else "C64 disk", len(alllines), len(out)))
print("rooms=%d items=%d rules=%d verbs=%d nouns=%d ml_bytes=%d" % (NR, NI, NU, len(VERBTAB), len(NOUNTAB), len(art_nums)))
# longest line check (BASIC ~80 logical, keep <88)
longest = max(alllines, key=lambda kc: len(kc[1]))
print("longest code line: %d chars @ %d" % (len(longest[1]), longest[0]))
