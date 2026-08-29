#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determinazione dello stato delle annotazioni rispetto al ramo dell'autrice.

L'autrice non opera sul ramo di revisione: consulta il PDF annotato e prosegue
la stesura su `main`. Lo stato di un'annotazione non viene pertanto dichiarato
manualmente ma determinato per confronto, verificando per ciascuna annotazione
la persistenza nel ramo di riferimento della frase cui essa e' ancorata.

    ancora presente  -> il passaggio non e' stato modificato: annotazione aperta
    ancora assente   -> il passaggio e' stato riscritto: annotazione da rileggere

La verifica presenta una limitazione nota, alla quale supplisce `resolved.py`:
qualora l'autrice recepisca un'osservazione senza modificare la frase ancorata,
l'ancora sopravvive e l'annotazione risulta ancora aperta pur essendo stata
recepita.

    python3 review/status.py                # confronto con origin/main
    python3 review/status.py a3a1f66        # confronto con una revisione data
    python3 review/status.py --verbose      # comprensivo delle annotazioni aperte
    python3 review/status.py --lint         # soli controlli strutturali
"""
import io, os, re, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "Master-Thesis-main", "chapters")

MD_MACROS = r'\\MD(?:n|q|s|t|del)\{'
# \revnote / \revnoteplain arrivano sempre tramite una macro di revisore
REV_MACROS = r'\\(?:CCerr|CCn|CCref|CCnote|CCmd|[A-Z]{2})\{'


def groups(text, start, n):
    """Restituisce i primi n gruppi {...} bilanciati a partire da `start`."""
    out, j = [], start
    for _ in range(n):
        while j < len(text) and text[j] != "{":
            if text[j] not in " \t\n": return out
            j += 1
        if j >= len(text): return out
        d, k = 0, j
        while k < len(text):
            if text[k] == "{": d += 1
            elif text[k] == "}":
                d -= 1
                if d == 0:
                    out.append(text[j + 1:k]); j = k + 1; break
            k += 1
        else:
            return out
    return out


# Macro il cui primo argomento NON e' testo della tesi ma un'etichetta per
# l'elenco (\CCmd rimanda a una nota di MD, \CCnote non e' ancorata a nulla).
# Confrontarle col testo della studentessa darebbe solo falsi positivi.
UNANCHORED = {"CCmd", "CCnote"}


def notes(text):
    """(sigla, ancora_o_None) per ogni nota del file; None = non ancorata."""
    found = []
    for m in re.finditer(MD_MACROS, text):
        g = groups(text, m.end() - 1, 1)
        if g: found.append(("MD", g[0]))
    for m in re.finditer(REV_MACROS, text):
        name = m.group(0)[1:-1]
        if name.startswith("MD"): continue
        if name in UNANCHORED:
            found.append((name, None)); continue
        # \XX{categoria}{ancora}{nota} per le sigle a due lettere, altrimenti
        # \CCerr{ancora}{nota}
        n = 3 if (len(name) == 2 and name not in ("CC",)) else 1
        g = groups(text, m.end() - 1, n)
        if not g: continue
        found.append((name, g[1] if n == 3 and len(g) > 1 else g[0]))
    return found


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ref = args[0] if args else "origin/main"
    verbose = "--verbose" in sys.argv

    subprocess.run(["git", "-C", ROOT, "fetch", "origin", "-q"], capture_output=True)
    ok = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", ref],
                        capture_output=True, text=True)
    if ok.returncode:
        sys.exit("riferimento non trovato: %s" % ref)
    print("Confronto le note con: %s (%s)\n" % (
        ref, subprocess.run(["git", "-C", ROOT, "log", "--oneline", "-1", ref],
                            capture_output=True, text=True).stdout.strip()))

    tally = collections.Counter()
    changed = []
    for dirpath, _, files in os.walk(TEX):
        for fn in sorted(files):
            if not fn.endswith(".tex"): continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            mine = io.open(path, encoding="utf-8", errors="replace").read()
            theirs = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, rel)],
                                    capture_output=True, text=True).stdout
            if not theirs: continue
            tn = norm(theirs)
            for who, anchor in notes(mine):
                if anchor is None or not anchor.strip():
                    tally[(who, "non ancorata")] += 1
                    continue
                if norm(anchor) in tn:
                    tally[(who, "aperta")] += 1
                    if verbose: print("   aperta   %-6s %-26s %s" % (who, fn, norm(anchor)[:58]))
                else:
                    tally[(who, "testo cambiato")] += 1
                    changed.append((who, fn, norm(anchor)[:64]))

    print("Riepilogo")
    for who in sorted({w for w, _ in tally}):
        row = {k: v for (w, k), v in tally.items() if w == who}
        tot = sum(row.values())
        print("   %-6s  %3d note   aperte %-4d  testo cambiato %-4d  non ancorate %d"
              % (who, tot, row.get("aperta", 0), row.get("testo cambiato", 0),
                 row.get("non ancorata", 0)))

    if changed:
        print("\nDa rileggere: ha riscritto il passaggio a cui la nota era ancorata")
        for who, fn, a in changed:
            print("   %-6s %-26s %s" % (who, fn, a))
    else:
        print("\nNessuna nota superata dalle sue modifiche.")


def lint():
    """Controlli strutturali sulle note. Servono perche' due errori di questo
    tipo hanno gia' rotto la compilazione: una nota finita DENTRO il corpo di
    un'altra nota (ancora troppo corta, una virgola) e una nota finita dentro
    una \\caption (la didascalia conteneva le stesse parole del testo)."""
    import glob
    bad = 0
    for f in sorted(glob.glob(os.path.join(TEX, "*", "*.tex"))):
        t = io.open(f, encoding="utf-8", errors="replace").read()
        name = os.path.basename(f)
        # 1. note annidate
        for m in re.finditer(r'\\(MD[a-z]+|CC[a-z]*)\{', t):
            a = groups(t, m.end() - 1, 2)
            if len(a) < 2: continue
            for inner in re.finditer(r'\\(MD[a-z]+|CC[a-z]*)\{', a[0] + " " + a[1]):
                print("  ANNIDATA   %-24s %s dentro %s" % (name, inner.group(0), m.group(0)))
                bad += 1
        # 2. note dentro una didascalia
        for m in re.finditer(r'\\caption\{', t):
            cap = groups(t, m.end() - 1, 1)
            if not cap: continue
            for inner in re.finditer(r'\\(MD[a-z]+|CC[a-z]*)\{', cap[0]):
                print("  IN CAPTION %-24s %s" % (name, inner.group(0)))
                bad += 1
        # 3. ancore troppo corte: sono quelle che si agganciano al posto sbagliato
        for m in re.finditer(r'\\(MD[a-z]+|CCerr|CCn|CCref)\{', t):
            a = groups(t, m.end() - 1, 1)
            if a and 0 < len(a[0].strip()) < 4:
                print("  ANCORA MOLTO CORTA %-22s %s{%s}" % (name, m.group(0)[:-1], a[0]))
                bad += 1
    print("\nproblemi strutturali: %d" % bad)
    return bad


if __name__ == "__main__":
    if "--lint" in sys.argv:
        sys.exit(1 if lint() else 0)
    main()
