#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boot elcid128.d64 on an emulated C128 in NATIVE mode and prove the cover paints.

`fullcycle.py` drives the C64 disk build; this is the C128 side, and it exists
because the C128 is the primary deliverable and nothing here had ever run it.
Three things make it different from the 64, and each one is a way to get a
false result rather than an error:

  * **Autostart lands you in C64 mode.**  `-autostart image:prg` uses the 64's
    idiom (`LOAD"…",8,1` then `RUN`), and x128 obeys it by switching to C64
    mode -- where the BASIC 7.0 cover loader cannot run and simply falls
    through to `READY.`  The disk has to be attached with `-8` and `DLOAD"ELCID"`
    typed the way a person would, in BASIC 7.0.
  * **The keyboard buffer moved.**  On the C128 it is at $034A with its count at
    $D0; poking the 64's $0277/$C6 does nothing at all, silently.
  * **The cover is a bitmap, so the text screen lies.**  The loader runs
    `GRAPHIC 3`, after which the VIC shows the bitmap and $0400 keeps whatever
    text was there before -- a text-screen dump of a working cover looks exactly
    like a machine sitting at `READY.`  What proves it is VIC register $D011
    bit 5 (bitmap mode on) plus actual content in the bitmap at $2000.

Debian and Ubuntu ship VICE without the Commodore ROMs; see the README's
"Running it on real ROMs".  The C128 also wants its national kernals, and the
distribution's default names one file it does not carry, so they are pointed at
the international kernal here -- the game runs in international mode.

usage:  python3 c128check.py ../elcid128.d64 [port]
"""
import os, re, socket, subprocess, sys, time

DISK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "elcid128.d64")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 6542
KBUF, KCNT = 0x034A, 0xD0            # C128 keyboard buffer and count
KERNAL, KERNAL_DE = "kernal-318020-05.bin", "kernal-315078-03.bin"

def drain(s):
    b = b""
    try:
        while True: b += s.recv(65536)
    except Exception: pass
    return b.decode("latin1")

def conn():
    for _ in range(50):
        try:
            s = socket.socket(); s.settimeout(0.2); s.connect(("127.0.0.1", PORT))
            time.sleep(0.3); drain(s); return s
        except OSError: time.sleep(0.4)
    raise SystemExit("no monitor connection on port %d -- is x128 running?" % PORT)

def cmd(s, c):
    s.sendall((c + "\n").encode()); time.sleep(0.05); return drain(s)

def rd(s, a0, a1):
    out = {}; a = a0
    while a <= a1:
        b = min(a + 0xFF, a1)
        s.sendall(("m %04x %04x\n" % (a, b)).encode()); time.sleep(0.05)
        for m in re.finditer(r'>C:([0-9a-f]{4})((?:\s+[0-9a-f]{2}){1,16})', drain(s), re.I):
            base = int(m.group(1), 16)
            for i, t in enumerate(re.findall(r'[0-9a-f]{2}', m.group(2), re.I)):
                out[base + i] = int(t, 16)
        a = b + 1
    return out

def type_line(text):
    """Type one line as the KERNAL editor would receive it, 9 keys at a time."""
    keys = [ord(c.upper()) if c.isalpha() else ord(c) for c in text] + [13]
    for i in range(0, len(keys), 9):
        chunk = keys[i:i + 9]
        s = conn()
        cmd(s, "> %04x " % KBUF + " ".join("%02x" % k for k in chunk))
        cmd(s, "> %04x %02x" % (KCNT, len(chunk)))
        cmd(s, "x"); s.close(); time.sleep(0.7)

def text_screen(scr):
    rows = []
    for r in range(25):
        rows.append("".join(
            chr(64 + (scr.get(0x0400 + r * 40 + c, 32) & 0x7F))
            if 1 <= (scr.get(0x0400 + r * 40 + c, 32) & 0x7F) <= 26
            else (chr(scr.get(0x0400 + r * 40 + c, 32) & 0x7F)
                  if 32 <= (scr.get(0x0400 + r * 40 + c, 32) & 0x7F) <= 63 else " ")
            for c in range(40)))
    return rows

def main():
    subprocess.run(["pkill", "-9", "-x", "x128"], stderr=subprocess.DEVNULL)
    time.sleep(1)
    subprocess.Popen(
        ["xvfb-run", "-a", "x128", "-warp", "-drive8type", "1571",
         "-kernalfi", KERNAL, "-kernalse", KERNAL, "-kernalno", KERNAL,
         "-kernalit", KERNAL, "-kernalfr", KERNAL, "-kernalch", KERNAL,
         "-kernalde", KERNAL_DE,
         "-remotemonitor", "-remotemonitoraddress", "ip4://127.0.0.1:%d" % PORT,
         "-8", DISK],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(20)
        s = conn(); scr = rd(s, 0x0400, 0x07E7); cmd(s, "x"); s.close()
        banner = " ".join(text_screen(scr)[:3])
        native = "BASIC V7.0" in banner
        print("native C128 mode: %s" % ("yes" if native else "NO -- %r" % banner[:60]))

        type_line('DLOAD"ELCID"'); time.sleep(22)
        s = conn(); scr = rd(s, 0x0400, 0x07E7); cmd(s, "x"); s.close()
        rows = text_screen(scr)
        loaded = any("LOADING" in r for r in rows)
        failed = [r.strip() for r in rows if "ERROR" in r]
        print("DLOAD\"ELCID\": %s%s"
              % ("loaded" if loaded else "did NOT load",
                 "  [%s]" % failed[0] if failed else ""))

        type_line("RUN"); time.sleep(35)
        s = conn(); vic = rd(s, 0xD011, 0xD018); bm = rd(s, 0x2000, 0x22FF)
        cmd(s, "x"); s.close()
        d011 = vic.get(0xD011, 0)
        bitmap = bool(d011 & 0x20)
        filled = sum(1 for k in bm if bm[k])
        print("after RUN: VIC $D011=%02x -> bitmap mode %s | bitmap $2000 %d/%d bytes set"
              % (d011, "ON" if bitmap else "OFF", filled, len(bm)))

        ok = native and loaded and bitmap and filled > 50 and not failed
        print("\n%s" % ("C128 OK: native mode, disk loads, cover bitmap painted."
                        if ok else "C128 CHECK FAILED"))
        return 0 if ok else 1
    finally:
        subprocess.run(["pkill", "-9", "-x", "x128"], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    sys.exit(main())
