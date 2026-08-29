#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Annotazioni aperte il cui contesto e' stato modificato dall'autrice.

Lo strumento supplisce a una limitazione della verifica per ancora. A seguito
di un merge si accertava la persistenza dell'ancora di ciascuna annotazione, e
`reanchor.py` elenca come orfane quelle la cui frase non risulti piu'
reperibile. L'autrice, tuttavia, recepisce le osservazioni per lo piu' senza
modificare la frase ancorata: integra la sigla immediatamente dopo l'ancora,
inserisce la virgola al suo interno, aggiunge la citazione in coda. L'ancora
sopravvive, l'annotazione viene riancorata, la verifica ha esito positivo e
l'annotazione permane aperta su un testo che ormai la soddisfa. In una singola
occasione otto annotazioni si sono trovate in tale condizione, quattro di MD e
quattro di CC.

La persistenza dell'ancora non equivale pertanto alla persistenza
dell'osservazione. Lo strumento confronta il contesto: per ciascuna annotazione
aperta individua l'ancora nel testo di riferimento e in quello nuovo e ne
raffronta il seguito immediato. Le annotazioni per le quali il seguito risulti
modificato vanno rilette ed eventualmente contrassegnate come recepite.

Va eseguito dopo il fetch e prima del merge, quando il confronto fra la
versione precedentemente revisionata e quella nuova e' ancora significativo.

    python3 review/resolved.py                 # base: merge-base con origin/main
    python3 review/resolved.py f2f3af8         # base determinata
"""
import io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "review"))
from reanchor import ARGS, ANCHOR, NOTE, grp

WINDOW = 150


def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True).stdout


def strip_notes(s):
    """Toglie le note lasciando la sola ancora. Si cammina sulle graffe: una
    espressione regolare non regge le graffe annidate dentro i corpi."""
    out, i = [], 0
    while True:
        m = re.search(NOTE, s[i:])
        if not m:
            out.append(s[i:]); break
        st = i + m.start(); out.append(s[i:st])
        name = m.group(0)[1:-1]
        a, j = [], i + m.end() - 1
        try:
            for _ in range(ARGS[name]):
                g, j = grp(s, j); a.append(g)
        except IndexError:
            out.append(s[st:]); break
        idx = ANCHOR[name]
        out.append(strip_notes(a[idx]) if idx is not None else "")
        i = j
    return "".join(out)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    git("fetch", "origin", "-q")
    base = args[0] if args else git("merge-base", "HEAD", "origin/main").strip()
    if not base:
        sys.exit("non riesco a determinare la revisione di riferimento")
    print("Riferimento: %s (%s)" % (base[:8], git("log", "--oneline", "-1", base).strip()))
    print("Confronto con: origin/main (%s)\n" % git("log", "--oneline", "-1", "origin/main").strip())

    files = [f for f in git("ls-tree", "-r", "--name-only", "HEAD",
                            "Master-Thesis-main/").split() if f.endswith(".tex")]
    found = []
    for rel in files:
        try:
            s = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        except OSError:
            continue
        old = git("show", "%s:%s" % (base, rel))
        new = git("show", "origin/main:%s" % rel)
        if not old or not new:
            continue
        old = strip_notes(old)
        for m in re.finditer(NOTE, s):
            name = m.group(0)[1:-1]
            if "solved" in name.lower():
                continue
            idx = ANCHOR[name]
            if idx is None:
                continue
            a, j = [], m.end() - 1
            try:
                for _ in range(ARGS[name]):
                    g, j = grp(s, j); a.append(g)
            except IndexError:
                continue
            anc = strip_notes(a[idx]).strip()
            if len(anc) < 4:
                continue
            io_, inw = old.find(anc), new.find(anc)
            if io_ < 0 or inw < 0:
                continue                      # sparita: la prende reanchor come orfana
            co = norm(old[io_ + len(anc):io_ + len(anc) + WINDOW])
            cn = norm(new[inw + len(anc):inw + len(anc) + WINDOW])
            if co != cn:
                found.append((os.path.basename(rel), name, anc[:44], co[:62], cn[:62]))

    if not found:
        print("Nessuna nota aperta sta su testo che lei ha cambiato.")
        return 0
    print("Note APERTE il cui testo circostante e' cambiato -- da rileggere:\n")
    for f, n, a, o, x in found:
        print("  %-22s %-8s %s" % (f, n, a))
        print("       prima: %s" % o)
        print("       dopo : %s" % x)
    print("\n%d da rileggere. Se ha dato seguito alla nota, marcala SOLVED con il come." % len(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
