#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dello stato del ramo di revisione.

Raccoglie i controlli che nel corso di questa revisione hanno individuato
difetti effettivi. Il criterio adottato e' che la verifica vada condotta sul
PDF e non sul sorgente: una compilazione priva di errori non fornisce alcuna
informazione sulla effettiva collocazione delle annotazioni nella pagina, ed e'
proprio in tale fase che si sono verificate perdite di annotazioni.

    python3 review/check.py            # verifica completa
    python3 review/check.py --quiet    # sole verifiche con esito negativo

Restituisce codice di uscita 0 in caso di esito positivo e 1 in caso contrario,
ed e' pertanto impiegabile in un hook.
"""
import io, os, re, sys, glob, subprocess, collections, unicodedata

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
# Un controllo che fallisce senza dire perche' invita a ridiagnosticarlo ogni
# volta. Il log sa gia' quale token e quale riga: si riportano.
_hyp = re.findall(r"removing `([^\']+)' on input line (\d+)", log)
check("nessun avviso hyperref", "Token not allowed" not in log,
      "; ".join(sorted({"%s alla riga %s" % (t, l) for t, l in _hyp})) or "")
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
# Si confrontano i TESTI delle note, non le etichette: le etichette compaiono
# anche negli elenchi, e il numero di pagine di elenco cambia a ogni giro.
# Le lettere accentate vanno ridotte alla base PRIMA di togliere il resto:
# pdftotext puo' renderle scomposte (e + accento), e togliendo solo i segni
# non alfanumerici resterebbe una lettera in piu' rispetto al sorgente.
# LaTeX compone i accentata come i SENZA PUNTO piu' accento: dopo NFKD resta
# U+0131, che non e' in [a-z] e verrebbe buttata, sfasando il confronto di una
# lettera. Stessa cosa per altre lettere speciali.
SPECIALI = {'\u0131': 'i', '\u0237': 'j', '\u0142': 'l', '\u00f8': 'o',
            '\u0111': 'd', '\u00e6': 'ae', '\u0153': 'oe', '\u00df': 'ss'}
def norm(x):
    d = unicodedata.normalize('NFKD', x.lower())
    d = ''.join(c for c in d if not unicodedata.combining(c))
    d = ''.join(SPECIALI.get(c, c) for c in d)
    return re.sub(r'[^a-z0-9]', '', d)
npdf = norm(txt)
md_bodies_src = []
for f in glob.glob(TEXGLOB):
    t = read(f)
    for m in re.finditer(r'\\MD[a-z]+\{', t):
        g = groups(t, m.end() - 1, 2)
        if len(g) == 2 and g[1].strip(): md_bodies_src.append(g[1])
absent = [b for b in md_bodies_src if norm(b)[:40] and norm(b)[:40] not in npdf]
check("testo di ogni nota di MD nel PDF (%d)" % len(md_bodies_src),
      not absent, "%d assenti" % len(absent))

loc = collections.defaultdict(list)
for i, p in enumerate(pages, 1):
    for n in re.findall(r'\[CC\s*(\d+)\]', p): loc[int(n)].append(i)
check("note dei revisori tutte nel PDF (%d)" % src_cc, len(loc) == src_cc,
      "nel PDF %d" % len(loc))
split = [n for n, pg in loc.items() if not any(v >= 2 for v in collections.Counter(pg).values())]
check("marcatore e riquadro sulla stessa pagina", not split,
      "separate: %s" % split[:10])

# Le note generali hanno numerazione propria ([CC G1]) e vanno controllate a
# parte, altrimenti sfuggirebbero del tutto a questo controllo.
src_gen = sum(len(re.findall(r'\\CCgen\{', read(f))) for f in glob.glob(TEXGLOB))
gloc = collections.defaultdict(list)
for i, p in enumerate(pages, 1):
    for n in re.findall(r'\[CC\s*G(\d+)\]', p): gloc[int(n)].append(i)
check("note generali tutte nel PDF (%d)" % src_gen, len(gloc) == src_gen,
      "nel PDF %d" % len(gloc))
gsplit = [n for n, pg in gloc.items() if not any(v >= 2 for v in collections.Counter(pg).values())]
check("note generali: marcatore e riquadro insieme", not gsplit, "separate: %s" % gsplit[:10])

# Stessa cosa per le note sull'intera tesi, numerate [CC T1].
src_tes = sum(len(re.findall(r'\\CCthesis\{', read(f))) for f in glob.glob(TEXGLOB))
tloc = collections.defaultdict(list)
for i, p in enumerate(pages, 1):
    for n in re.findall(r'\[CC\s*T(\d+)\]', p): tloc[int(n)].append(i)
check("note sulla tesi tutte nel PDF (%d)" % src_tes, len(tloc) == src_tes,
      "nel PDF %d" % len(tloc))
tsplit = [n for n, pg in tloc.items() if not any(v >= 2 for v in collections.Counter(pg).values())]
check("note sulla tesi: marcatore e riquadro insieme", not tsplit, "separate: %s" % tsplit[:10])

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

# ------------------------------------ 4b. la tabella di reanchor.py e' allineata?
# Se qualcuno aggiunge un tipo di nota e non aggiorna reanchor.py, al prossimo
# merge quelle note verrebbero buttate o troncate. Si controlla qui, cosi' il
# problema si vede subito e non fra un mese in mezzo a un merge.
# Le protezioni di addnote.py si autoverificano: ognuna viene fatta scattare su
# testo finto e si controlla che rifiuti E che non scriva. Sono la rete che
# manca agli script usa-e-getta con cui le note si aggiungono a mano.
# Annotazioni aperte il cui contesto e' stato modificato dall'autrice. Non
# costituiscono un errore bensi' materiale da rileggere, e sono pertanto
# riportate come informazione e non come esito negativo. A merge avvenuto il
# valore e' sempre nullo: la verifica e' significativa fra il fetch e il merge.
_res = subprocess.run([sys.executable, os.path.join(ROOT, "review", "resolved.py")],
                      capture_output=True, text=True).stdout
_n = re.search(r"^(\d+) da rileggere", _res, re.M)
print("  note aperte su testo che lei ha cambiato: %s" % (_n.group(1) if _n else "0"))

guard = subprocess.run([sys.executable, os.path.join(ROOT, "review", "addnote.py")],
                       capture_output=True, text=True)
check("le protezioni di addnote.py scattano", guard.returncode == 0,
      guard.stdout.strip().splitlines()[-1] if guard.stdout.strip() else "")

tab = subprocess.run([sys.executable, os.path.join(ROOT, "review", "reanchor.py"), "--check-table"],
                     capture_output=True, text=True)
check("reanchor.py conosce tutti i tipi di nota", tab.returncode == 0,
      tab.stdout.strip().splitlines()[-1] if tab.stdout.strip() else "")

# ------------------------------------------------ 4c. collisioni di colore
# Il colore identifica la PERSONA: due revisori con lo stesso colore annullano
# la regola. Si guardano anche le registrazioni commentate, perche' sono
# istruzioni pronte all'uso e una collisione li' e' una trappola.
pre = read(os.path.join(BASE, "preamble.tex"))
palette = collections.defaultdict(set)
for m in re.finditer(r'\\renewcommand\{\\(MD[a-z]+)\}\[2\]\{\\hlcolor\{([a-z]+![0-9]+)\}', pre):
    palette[m.group(2)].add("MD:" + m.group(1))
for m in re.finditer(r'^%?\s*\\DeclareReviewer\{([A-Z]{2})\}\{([a-z]+![0-9]+)\}', pre, re.M):
    palette[m.group(2)].add("revisore:" + m.group(1))
clash = {c: v for c, v in palette.items() if len(v) > 1}
check("nessuna collisione di colore fra revisori", not clash,
      "; ".join("%s -> %s" % (c, ", ".join(sorted(v))) for c, v in clash.items()))

# -------------------------------------------------------- 5. lint strutturale
lint = subprocess.run([sys.executable, os.path.join(ROOT, "review", "status.py"), "--lint"],
                      capture_output=True, text=True)
check("nessun problema strutturale nelle note", lint.returncode == 0,
      lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else "")

# ------------------------------------------------- 6. variazione rispetto a HEAD
# LIMITE NOTO: i controlli qui sopra confrontano il SORGENTE con il PDF, quindi
# vedono una nota persa in composizione ma non una nota cancellata per sbaglio
# dal sorgente (calerebbero entrambi i conteggi). Per le note di MD esiste il
# confronto con f2f3af8, che e' un vincolo assoluto; per quelle dei revisori no.
# Qui si stampa quindi la variazione rispetto al commit precedente: un calo va
# guardato, anche se non e' di per se' un errore (togliere note e' legittimo).
prev = {}
for kind, pat in (("revisori", r'\\CC(?:err|n|ref|note|solved|notesolved)\{'),
                  ("generali", r'\\CCgen\{'), ("tesi", r'\\CCthesis\{'),
                  ("MD", r'\\MD[a-z]+\{')):
    now = sum(len(re.findall(pat, read(f))) for f in glob.glob(TEXGLOB))
    old_n = 0
    for f in glob.glob(TEXGLOB):
        rel = os.path.relpath(f, ROOT)
        txt = subprocess.run(["git", "-C", ROOT, "show", "HEAD:" + rel],
                             capture_output=True, text=True).stdout
        old_n += len(re.findall(pat, txt))
    prev[kind] = (now, now - old_n)
print("  note: " + "   ".join("%s %d (%+d)" % (k, v[0], v[1]) for k, v in prev.items()))

# ------------------------------------------------------------------ report
quiet = "--quiet" in sys.argv
bad = 0
for ok, name, detail in results:
    if not ok: bad += 1
    if ok and quiet: continue
    print("  %s  %-46s %s" % ("OK  " if ok else "FALLITO", name, detail if not ok else ""))
print("\n%d controlli, %d falliti" % (len(results), bad))
sys.exit(1 if bad else 0)
