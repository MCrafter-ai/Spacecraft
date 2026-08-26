# -*- coding: utf-8 -*-
"""Rebuild the SPACECRAFT client from the pristine download."""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
SRC = os.path.join(GAME, "minecraft.original.html")   # the untouched download
DST = os.path.join(GAME, "minecraft.html")            # what gets built

def rd(p):
    return open(p, encoding="utf-8", errors="surrogateescape").read()

d = rd(SRC)
head = rd(os.path.join(HERE, "01-head.html")).rstrip("\n")
body_top = rd(os.path.join(HERE, "02-body-top.html")).rstrip("\n")
body_bottom = rd(os.path.join(HERE, "03-body-bottom.html")).rstrip("\n")
log = []


def sub_once(old, new, label):
    global d
    n = d.count(old)
    assert n == 1, "%s: expected 1 occurrence, found %d" % (label, n)
    d = d.replace(old, new, 1)
    log.append("OK  " + label)


def span(a, b, new, label, keep_end=True):
    """Replace everything from marker a through marker b."""
    global d
    i = d.index(a)
    j = d.index(b, i) + (len(b) if keep_end else 0)
    d = d[:i] + new + d[j:]
    log.append("OK  " + label)


# ============================================================ 1. game code
# --- the "Fork me on GitHub" main-menu button -----------------------------
sub_once("f=a.A;d=new N6;Oz(d,3,(a.n/2|0)-100|0,c+24|0,U(b,B(1344)));R(f,d);", "",
         "fork button removed (no-singleplayer layout)")
sub_once("f=a.A;d=new N6;Oz(d,3,(a.n/2|0)-100|0,c+48|0,U(b,B(1344)));R(f,d);", "",
         "fork button removed (normal layout)")
sub_once("=(c+72|0)+12|0;", "=(c+48|0)+12|0;",
         "options/profile row shifted up to close the gap")

# --- corner text: "<client> 1.3 (cracked)" -> "SPACECRAFT Client" ---------
sub_once("h=Bd(J(Ct(J(Bg(),B(1359)),A.A20),B(1360)));", "h=B(1359);",
         "corner credit simplified to one string")
sub_once('"Archimedes Client 1.3"', '"SPACECRAFT Client"', "corner text renamed")

# --- every other in-game "Archimedes Client" ------------------------------
n = d.count('"Archimedes Client"')
assert n == 2, "expected 2 plain client-name strings, found %d" % n
d = d.replace('"Archimedes Client"', '"SPACECRAFT Client"')
log.append("OK  in-game client name -> SPACECRAFT Client (%d strings)" % n)

# --- the "eaglercraft readme.txt" corner link -----------------------------
sub_once('"eaglercraft readme.txt"', '""', "readme.txt label blanked")
sub_once("if(b>=((a.n-l|0)-4|0)&&b<=a.n&&c>=0&&c<=9){a.pB=1;return;}", "",
         "readme.txt click target removed")

# --- author's project links ----------------------------------------------
sub_once('"https://github.com/ArchimedesClient/ArchimedesClient"', '""',
         "project url string blanked")
sub_once("The URL to this fork\\'s GitHub repository is: https://github.com/ArchimedesClient/ArchimedesClient",
         "", "crash screen repo url removed")
sub_once("publish it in the issues feed of this fork\\'s GitHub repository.",
         "try reloading the page.", "crash screen wording made generic")

# --- default relay display names (only used if the page supplies none) ---
for _old, _new in (('"lax1dude relay #1"', '"Relay #1"'),
                   ('"lax1dude relay #2"', '"Relay #2"'),
                   ('"ayunami relay #1"', '"Relay #3"')):
    _n = d.count(_old)
    assert _n >= 1, "relay rename %s: not found" % _old
    d = d.replace(_old, _new)
    log.append("OK  relay display name %s -> %s (%d)" % (_old, _new, _n))
sub_once('"GuiButtonArchimedes"', '"GuiButtonSpacecraft"', "internal class name rebranded")

# --- source header comment -----------------------------------------------
span("Visit this link to check for newer versions of this file:",
     "-->",
     "SPACECRAFT - Minecraft 1.5.2 for the browser.\n\nBuilt from an offline eaglercraft build; everything the game needs is inside this one file.\n\n-->",
     "source header comment replaced")

# ================================================== 2. keep one asset pack
lines = d.split("\n")
opts = [i for i, ln in enumerate(lines) if ln.startswith('<option value="')]
assert len(opts) == 4, "expected 4 packs, found %d" % len(opts)
keep = opts[0]
label = lines[keep][-60:]
assert "Default Pack" in label, "first option is not the Default Pack: %r" % label
for i in reversed(opts[1:]):
    del lines[i]
d = "\n".join(lines)
log.append("OK  dropped 3 bundled packs, kept Default")

# ================================================== 3. the launcher itself
span("<title>Archimedes Client</title>", "</style>", head, "head + stylesheet replaced")

span('<script type="text/javascript">\nfunction Launch() {', "</script>",
     "<!-- launcher logic lives at the end of the body -->",
     "old launch script removed")

span('<body style="margin:0px;width:100vw;height:100vh;font-family:sans-serif;" id="game_frame">',
     '<select id="packs" class="dropdown">\n', body_top + "\n",
     "launcher markup replaced")

span("</select>", "</body>", body_bottom, "launcher scripts added")

# ========================================================== 4. write + report
open(DST, "w", encoding="utf-8", errors="surrogateescape").write(d)
for line in log:
    print(line)

print("")
print("leftover mentions:")
for word in ("Archimedes", "archimedes", "hellscaped", "lax1dude", "ayunami",
             "asspixel", "femboy", "benadryl"):
    print("   %-12s %d" % (word, d.count(word)))
print("")
print("wrote %s  (%.1f MB)" % (DST, len(d) / 1048576.0))
