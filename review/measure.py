#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Misurazione dei dati numerici della tesi sul ramo dell'autrice.

Un'annotazione che riporti un dato numerico -- il numero di parole di un
capitolo, il numero di sigle distinte -- va redatta sulla base di una
misurazione condotta sul testo dell'autrice e non sui file annotati. La
misurazione condotta su questi ultimi includerebbe le annotazioni stesse; la
loro rimozione mediante espressione regolare non e' praticabile, in quanto i
corpi contengono parentesi graffe annidate ed espressioni matematiche.

L'inconveniente si e' verificato: nove dati numerici in altrettante annotazioni
sono risultati errati, con conteggi di parole sovrastimati fino al cinquanta
per cento nelle sezioni brevi e un conteggio di sigle falsato dall'inclusione
della sigla piu' frequente nell'elenco delle esclusioni.

Lo strumento acquisisce i file da git alla revisione dell'autrice, ove le
annotazioni non sono presenti.

    python3 review/measure.py                 # confronto con origin/main
    python3 review/measure.py c977f7c         # a una revisione determinata
    python3 review/measure.py --acronyms      # con l'elenco delle sigle
"""
import re, sys, subprocess, collections, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_ACRONYMS = {"TEX", "PDF", "AND", "THE", "OK", "UHV"}


def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True).stdout


def sources(ref):
    out = git("ls-tree", "-r", "--name-only", ref, "Master-Thesis-main/chapters/").split()
    return [f for f in out if f.endswith(".tex")]


def stats(text):
    return dict(
        parole=len(re.findall(r'\b[A-Za-z]{2,}\b', text)),
        eq=len(re.findall(r'\\begin\{equation\}', text)),
        figure=len(re.findall(r'\\begin\{(?:figure|wrapfigure)', text)),
        tabelle=len(re.findall(r'\\begin\{table\}', text)),
        citaz=len(re.findall(r'\\cite\{', text)),
        pm=len(re.findall(r'\\pm', text)),
        item=len(re.findall(r'\\item', text)),
        itemize=len(re.findall(r'\\begin\{itemize\}', text)),
    )


def add(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ref = args[0] if args else "origin/main"
    git("fetch", "origin", "-q")
    if not git("rev-parse", "--verify", ref).strip():
        sys.exit("riferimento non trovato: %s" % ref)
    files = sources(ref)
    if not files:
        sys.exit("nessun sorgente trovato a %s" % ref)
    print("Misurato su %s (%s)\n" % (ref, git("log", "--oneline", "-1", ref).strip()))

    parts = collections.OrderedDict(
        [("front", "Intro_Conc_Abs"), ("cap1", "Chapter_1/cap1"),
         ("cap2", "Chapter_2/cap2"), ("cap3", "Chapter_3/cap3"),
         ("append", "Appendix")])
    tot = {}
    hdr = ("parte", "parole", "eq", "figure", "tab", "citaz", "pm", "item")
    print("  %-8s %7s %5s %7s %5s %6s %5s %5s" % hdr)
    allt = ""
    for lbl, key in parts.items():
        fs = [f for f in files if key in f]
        s = {}
        for f in fs:
            t = git("show", "%s:%s" % (ref, f))
            allt += t
            s = add(s, stats(t))
        if not s: s = {k: 0 for k in ("parole", "eq", "figure", "tabelle", "citaz", "pm", "item")}
        tot[lbl] = s
        print("  %-8s %7d %5d %7d %5d %6d %5d %5d" % (
            lbl, s["parole"], s["eq"], s["figure"], s["tabelle"], s["citaz"], s["pm"], s["item"]))
    g = {k: sum(tot[p].get(k, 0) for p in tot) for k in ("parole", "eq", "figure", "tabelle", "citaz")}
    print("  %-8s %7d %5d %7d %5d %6d" % ("TOTALE", g["parole"], g["eq"], g["figure"], g["tabelle"], g["citaz"]))

    bg = tot["cap1"]["parole"] + tot["cap2"]["parole"]
    if tot["cap3"]["parole"]:
        print("\n  sfondo+metodi / risultati = %d / %d = %.1f a 1"
              % (bg, tot["cap3"]["parole"], bg / tot["cap3"]["parole"]))

    ac = collections.Counter(re.findall(r'\b([A-Z]{2,6})\b', allt))
    real = [(a, n) for a, n in ac.most_common() if a not in SKIP_ACRONYMS and n >= 3]
    print("  acronimi distinti usati almeno 3 volte: %d" % len(real))
    if "--acronyms" in sys.argv:
        print("   ", ", ".join("%s(%d)" % x for x in real))


if __name__ == "__main__":
    main()
