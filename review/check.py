#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controllo di salute del ramo di revisione, in un comando solo.

Raccoglie i controlli che in questa revisione hanno trovato difetti veri. Il
punto fondamentale: **si misura il PDF, non il sorgente**. Una compilazione
senza errori non dice nulla su quante note siano finite davvero nella pagina
giusta, ed e' esattamente li' che si erano perse delle note.

    python3 review/check.py            # tutto
    python3 review/check.py --quiet    # solo le righe che falliscono

Esce 0 se tutto passa, 1 altrimenti: si puo' mettere in un hook.
"""
import io, os, re, sys, glob, subprocess, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "Master-Thesis-main")
PDF = os.path.join(BASE, "thesis_main.pdf")
LOG = os.path.join(BASE, "thesis_main.log")
TEXGLOB = os.path.join(BASE, "chapters", "*", "*.tex")
MD_BASELINE = "f2f3af8"          # le 32 note originali di MD
TEXTHEIGHT = 702.78              # blocco di testo originale della studentessa

results = []
def check(name, ok, detail=""):
    results.append((ok, name, detail))

def read(p):
    return io.open(p, encoding="utf-8", errors="replace").read()

def groups(t, start, n):
    out, j = [], start
    for _ in range(n):
        while j < len(t) and t[j] != "{": j += 1
        if j >= len(t): return out
        d, k = 0, j
        while k < len(t):
            if t[k] == "{": d += 1
            elif t[k] == "}":
                d -= 1
                if d == 0: out.append(t[j+1:k]); j = k + 1; break
            k += 1
        else: return out
    return out

# ---------------------------------------------------------------- 1. build
log = read(LOG) if os.path.exists(LOG) else ""
check("compilazione senza errori", log.count("\n! ") == 0, "%d errori" % log.count("\n! "))
check("nessun float perso", "Float(s) lost" not in log)
check("nessun avviso hyperref", "Token not allowed" not in log)
m = re.search(r'textheight=([\d.]+)pt', log)
th = float(m.group(1)) if m else -1
check("blocco di testo invariato (%.2f pt)" % TEXTHEIGHT, abs(th - TEXTHEIGHT) < 0.05,
      "trovato %.2f pt" % th)

# ---------------------------------------------------------- 2. note nel PDF
src_md = src_cc = 0
for f in glob.glob(TEXGLOB):
    t = read(f)
    src_md += len(re.findall(r'\\MD[a-z]+\{', t))
    src_cc += len(re.findall(r'\\CC(?:err|n|ref|note|solved|notesolved)\{', t))

txt = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True).stdout
pages = txt.split("\f")
body = "".join(pages[14:])
md_in_pdf = sum(body.count(l) for l in ("MD note", "MD suggestion", "MD typo", "MD question"))
check("note di MD tutte nel PDF (%d)" % src_md, md_in_pdf == src_md, "nel PDF %d" % md_in_pdf)

loc = collections.defaultdict(list)
for i, p in enumerate(pages, 1):
    for n in re.findall(r'\[CC\s*(\d+)\]', p): loc[int(n)].append(i)
check("note dei revisori tutte nel PDF (%d)" % src_cc, len(loc) == src_cc,
      "nel PDF %d" % len(loc))
split = [n for n, pg in loc.items() if not any(v >= 2 for v in collections.Counter(pg).values())]
check("marcatore e riquadro sulla stessa pagina", not split,
      "separate: %s" % split[:10])

# ------------------------------------------------------------- 3. margini
bb = subprocess.run(["pdftotext", "-bbox", PDF, "-"], capture_output=True, text=True).stdout
ps = re.split(r'<page ', bb)[1:]
if ps:
    w = float(re.search(r'width="([\d.]+)"', ps[0]).group(1))
    h = float(re.search(r'height="([\d.]+)"', ps[0]).group(1))
    xr = max(max([float(x) for x in re.findall(r'xMax="([\d.]+)"', p)] or [0]) for p in ps)
    yb = max(max([float(x) for x in re.findall(r'yMax="([\d.]+)"', p)] or [0]) for p in ps)
    clipped = sum(1 for p in ps if (lambda ys: bool(ys) and max(ys) > h - 20)(
        [float(x) for x in re.findall(r'yMax="([\d.]+)"', p)]))
    check("niente tagliato al bordo pagina", clipped == 0, "%d pagine" % clipped)
    check("margine destro > 3 mm", (w - xr) * 0.03514 > 0.3, "%.2f cm" % ((w - xr) * 0.03514))
    check("margine inferiore > 3 mm", (h - yb) * 0.03514 > 0.3, "%.2f cm" % ((h - yb) * 0.03514))

# ------------------------------------- 4. note di MD intatte e non commentate
def md_bodies(t):
    out = []
    for m in re.finditer(r'\\MD[a-z]+\{', t):
        g = groups(t, m.end() - 1, 2)
        if len(g) == 2: out.append(g[1])
    return out
orig, cur = [], []
for f in ("cap1_HCPCF", "cap1_trapping", "cap1_Conveyor_belt", "cap1_EIT", "chapter_1_main"):
    rel = "Master-Thesis-main/chapters/Chapter_1/%s.tex" % f
    orig += md_bodies(subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (MD_BASELINE, rel)],
                                     capture_output=True, text=True).stdout)
    cur += md_bodies(read(os.path.join(ROOT, rel)))
missing = [b for b in orig if b not in cur]
altered = [b for b in cur if b not in orig]
check("le %d note di MD ci sono tutte" % len(orig), not missing, "%d mancanti" % len(missing))
check("nessuna nota di MD alterata", not altered, "%d alterate" % len(altered))

ccmd = sum(len(re.findall(r'\\CCmd\{', read(f))) for f in glob.glob(TEXGLOB))
check("nessun commento alle note altrui", ccmd == 0, "%d trovati" % ccmd)

# -------------------------------------------------------- 5. lint strutturale
lint = subprocess.run([sys.executable, os.path.join(ROOT, "review", "status.py"), "--lint"],
                      capture_output=True, text=True)
check("nessun problema strutturale nelle note", lint.returncode == 0,
      lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else "")

# ------------------------------------------------------------------ report
quiet = "--quiet" in sys.argv
bad = 0
for ok, name, detail in results:
    if not ok: bad += 1
    if ok and quiet: continue
    print("  %s  %-46s %s" % ("OK  " if ok else "FALLITO", name, detail if not ok else ""))
print("\n%d controlli, %d falliti" % (len(results), bad))
sys.exit(1 if bad else 0)
