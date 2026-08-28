#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rimette le note sul testo aggiornato della studentessa, dopo un merge.

Serve perche' lei lavora su `main`, dove le note non esistono: quando si porta
il suo testo dentro il ramo di revisione, ogni file in conflitto ha da una parte
il nostro (prosa vecchia + note) e dall'altra il suo (prosa nuova, niente note).
La risoluzione giusta e' sempre: **si tiene la sua prosa e si riattaccano le
note**, mai il contrario.

Tre protezioni, tutte nate da errori veri fatti a mano:

  * mai dentro una \\caption -- una didascalia puo' ripetere le stesse parole del
    corpo, e la nota era finita li' rompendo la lista delle figure;
  * mai dentro gli argomenti di un'altra nota -- le ancore di MD coprono frasi
    intere, e una nota agganciata a parole contenute in quella frase finiva
    annidata, con il documento che non compilava piu';
  * ancore di meno di 4 caratteri rifiutate -- un'ancora ``,'' si attacca alla
    prima virgola che trova, che puo' essere ovunque.

Le note la cui ancora non esiste piu' NON vengono buttate: sono elencate come
orfane, perche' sono esattamente quelle su cui la studentessa e' intervenuta e
che vanno rilette e, se del caso, marcate SOLVED.

    python3 review/reanchor.py           # prova, non scrive nulla
    python3 review/reanchor.py --apply   # scrive
"""
import io, os, re, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = r'\\(?:MD[a-z]+|CC(?:err|n|ref|note|solved|notesolved|md))\{'
UNANCHORED = ("CCmd", "CCnote", "CCnotesolved")
MINLEN = 4


def grp(t, j):
    d = 0; k = j
    while True:
        if t[k] == "{": d += 1
        elif t[k] == "}":
            d -= 1
            if d == 0: return t[j+1:k], k + 1
        k += 1


def parse(src):
    """Note nell'ordine in cui compaiono: (testo completo, ancora o None)."""
    out = []
    for m in re.finditer(NOTE, src):
        name = m.group(0)[1:-1]
        a1, j = grp(src, m.end() - 1)
        n = 4 if name in ("CCsolved",) else 2
        a = [a1]
        for _ in range(n - 1):
            g, j = grp(src, j)
            a.append(g)
        out.append({"text": src[m.start():j],
                    "anchor": None if name in UNANCHORED else a[1] if name == "CCsolved" else a[0],
                    "name": name})
    return out


def forbidden_spans(t):
    """Intervalli in cui NON si puo' inserire: didascalie e argomenti di note."""
    bad = []
    for m in re.finditer(r'\\caption\{', t):
        try: _, end = grp(t, m.end() - 1)
        except IndexError: continue
        bad.append((m.start(), end))
    for m in re.finditer(NOTE, t):
        try:
            _, j = grp(t, m.end() - 1)
            _, end = grp(t, j)
        except IndexError: continue
        bad.append((m.start(), end))
    return bad


def safe_find(t, anchor, start):
    """Prima occorrenza di `anchor` da `start` che non cada in una zona vietata."""
    bad = forbidden_spans(t)
    i = t.find(anchor, start)
    while i >= 0:
        if not any(a <= i < b for a, b in bad):
            return i
        i = t.find(anchor, i + 1)
    return -1


def conflicted():
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=U"],
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith(".tex")]


def run(apply_it):
    files = conflicted()
    if not files:
        print("Nessun file .tex in conflitto: niente da riattaccare.")
        print("Si usa dopo `git merge origin/main`, quando i conflitti sono aperti.")
        return 0
    tot_ok = tot_orph = 0
    for rel in files:
        ours = subprocess.run(["git", "-C", ROOT, "show", ":2:" + rel],
                              capture_output=True, text=True).stdout
        theirs = subprocess.run(["git", "-C", ROOT, "show", ":3:" + rel],
                                capture_output=True, text=True).stdout
        if not ours or not theirs:
            print("  %-28s salto (non e' un conflitto a due lati)" % os.path.basename(rel)); continue
        res, cursor, last_end = theirs, 0, None
        placed, orphans = 0, []
        for n in parse(ours):
            a = n["anchor"]
            if a is None:
                if last_end is None:
                    orphans.append(("(non ancorata, nessuna nota prima)", n["name"])); continue
                res = res[:last_end] + n["text"] + res[last_end:]
                last_end += len(n["text"]); placed += 1; continue
            if len(a.strip()) < MINLEN:
                orphans.append((a, n["name"] + " -- ancora troppo corta")); continue
            i = safe_find(res, a, cursor)
            if i < 0:
                orphans.append((a[:70], n["name"])); continue
            res = res[:i] + n["text"] + res[i + len(a):]
            last_end = i + len(n["text"]); cursor = last_end; placed += 1
        if apply_it:
            io.open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(res)
        print("  %-28s riattaccate %2d   orfane %d" % (os.path.basename(rel), placed, len(orphans)))
        for a, why in orphans:
            print("       ORFANA  %-14s %s" % (why, a))
        tot_ok += placed; tot_orph += len(orphans)
    print("\n%d note riattaccate, %d orfane%s" %
          (tot_ok, tot_orph, "" if apply_it else "   (prova: non ho scritto niente)"))
    if tot_orph:
        print("Le orfane sono i punti in cui ha riscritto: rileggile e, se ha dato\n"
              "seguito alla nota, rimettila in verde con il tag SOLVED.")
    if apply_it:
        print("\nOra: python3 review/status.py --lint && bash review/build.sh && python3 review/check.py")
    return 0


if __name__ == "__main__":
    sys.exit(run("--apply" in sys.argv))
