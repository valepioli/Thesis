#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Riancoraggio delle annotazioni al testo aggiornato dell'autrice.

L'autrice opera su `main`, ove le annotazioni non sono presenti. Nel momento in
cui il suo testo viene acquisito nel ramo di revisione, ciascun file in
conflitto oppone il testo precedente, comprensivo di annotazioni, al testo
nuovo che ne e' privo. La risoluzione corretta consiste invariabilmente nel
conservare il testo dell'autrice e riancorare le annotazioni.

Il modulo adotta tre protezioni, ciascuna derivante da un difetto riscontrato:

  * nessun inserimento in una `\\caption`, in quanto una didascalia puo'
    riprodurre le medesime parole del corpo del testo, con conseguente
    compromissione dell'elenco delle figure;
  * nessun inserimento negli argomenti di un'altra annotazione, in quanto le
    ancore estese possono comprendere le parole cui una seconda annotazione si
    aggancia, con conseguente annidamento e impossibilita' di compilazione;
  * ancore di estensione inferiore a quattro caratteri respinte, in quanto si
    agganciano alla prima occorrenza disponibile.

Le annotazioni prive di ancora utilizzabile -- non ancorate, oppure ancorate a
una stringa vuota o troppo breve -- vengono riancorate al contesto che le
precedeva. In assenza di tale accorgimento esse venivano scartate senza
segnalazione: in una singola occasione undici annotazioni su ottantanove, fra
cui una di MD.

Le annotazioni la cui ancora non risulti piu' reperibile non vengono eliminate,
bensi' elencate come orfane, in quanto corrispondono ai passaggi effettivamente
riscritti dall'autrice e vanno pertanto rilette ed eventualmente contrassegnate
come recepite.

    python3 review/reanchor.py           # esecuzione in sola lettura
    python3 review/reanchor.py --apply   # esecuzione con scrittura
"""
import io, os, re, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Tabella delle macro: quanti argomenti prende ciascuna e quale di essi e'
# l'ancora nel testo della tesi (None = nota non ancorata a una frase).
# NON dedurre questi numeri: vanno letti dal preambolo. Una versione precedente
# di questo file assumeva due argomenti per tutte e non conosceva \CCgen ne'
# \CCthesis; su un merge avrebbe buttato 24 note e troncato a meta' le altre.
# Per questo c'e' check_table(), che confronta la tabella con il preambolo e si
# ferma se qualcuno aggiunge un tipo di nota senza aggiornarla.
ARGS = {
    "MDn": 2, "MDq": 2, "MDs": 2, "MDt": 2, "MDdel": 2,
    "MDnsolved": 3, "MDssolved": 3, "MDqsolved": 3, "MDtsolved": 3,
    "CCerr": 2, "CCn": 2, "CCref": 2, "CCnote": 2, "CCmd": 2,
    "CCsolved": 4, "CCnotesolved": 3, "CCgen": 3, "CCthesis": 2,
}
ANCHOR = {
    "MDn": 0, "MDq": 0, "MDs": 0, "MDt": 0, "MDdel": 0,
    "MDnsolved": 0, "MDssolved": 0, "MDqsolved": 0, "MDtsolved": 0,
    "CCerr": 0, "CCn": 0, "CCref": 0,
    "CCsolved": 1,
    "CCnote": None, "CCmd": None, "CCnotesolved": None,
    "CCgen": None, "CCthesis": None,
}
NOTE = r'\\(?:' + "|".join(sorted(ARGS, key=len, reverse=True)) + r')\{'
MINLEN = 4
CONTEXT = 120        # caratteri di contesto per riancorare una nota senza ancora
PREAMBLE = os.path.join(ROOT, "Master-Thesis-main", "preamble.tex")


def check_table():
    """Si ferma se il preambolo definisce una macro di nota che la tabella non
    conosce, o se il numero di argomenti non corrisponde."""
    src = io.open(PREAMBLE, encoding="utf-8", errors="replace").read()
    found = dict(re.findall(r'\\newcommand\{\\((?:MD|CC)[a-z]*)\}\[(\d)\]', src))
    found.pop("MDsolvedmark", None)          # macro interna, non una nota
    problemi = []
    for name, n in found.items():
        if name not in ARGS:
            problemi.append("il preambolo definisce \\%s ma la tabella non lo conosce" % name)
        elif ARGS[name] != int(n):
            problemi.append("\\%s ha %s argomenti nel preambolo, %d in tabella" % (name, n, ARGS[name]))
    for name in ARGS:
        if name not in found:
            problemi.append("la tabella conosce \\%s ma il preambolo non lo definisce" % name)
    if problemi:
        print("TABELLA DELLE MACRO NON ALLINEATA AL PREAMBOLO:")
        for x in problemi: print("   -", x)
        print("Aggiorna ARGS e ANCHOR in review/reanchor.py prima di usarlo.")
        return False
    return True


def grp(t, j):
    d = 0; k = j
    while True:
        if t[k] == "{": d += 1
        elif t[k] == "}":
            d -= 1
            if d == 0: return t[j+1:k], k + 1
        k += 1


def parse(src):
    """Note nell'ordine in cui compaiono: testo completo e ancora (o None)."""
    out = []
    for m in re.finditer(NOTE, src):
        name = m.group(0)[1:-1]
        n = ARGS[name]
        a, j = [], m.end() - 1
        for _ in range(n):
            g, j = grp(src, j)
            a.append(g)
        idx = ANCHOR[name]
        out.append({"text": src[m.start():j],
                    "anchor": None if idx is None else a[idx],
                    "name": name,
                    # Appiglio per le note senza ancora utilizzabile: il testo
                    # che le precede. Senza, una nota non ancorata che sia la
                    # PRIMA del file non ha dove attaccarsi e spariva in
                    # silenzio -- ed e' il caso di tutte le note generali e di
                    # quelle sulla tesi, che per convenzione stanno nel primo
                    # paragrafo dell'area che commentano.
                    "before": src[max(0, m.start() - CONTEXT):m.start()]})
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


def context_place(res, before):
    """Dove rimettere una nota priva di ancora utilizzabile.

    Si cerca nel testo nuovo il pezzo che nel vecchio la precedeva,
    accorciandolo dall'inizio finche' non lo si ritrova: se la studentessa ha
    riscritto la frase subito prima della nota, il contesto piu' lontano
    sopravvive quasi sempre. Un contesto vuoto significa che la nota stava
    all'inizio del file, e li' va rimessa. -1 se non si ritrova niente.
    """
    if not before.strip():
        return 0
    ctx = before
    while len(ctx.strip()) >= MINLEN:
        pos = safe_find(res, ctx, 0)
        if pos >= 0:
            return pos + len(ctx)
        ctx = ctx[len(ctx) // 4:]
    return -1


def conflicted():
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=U"],
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith(".tex")]


def run(apply_it):
    if not check_table():
        return 1
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
            if a is None or len(a.strip()) < MINLEN:
                # Due casi che prima sparivano in silenzio, e sono lo stesso
                # caso: la nota non ha un'ancora utilizzabile. Non ancorata
                # (CCgen, CCthesis, CCnote) oppure ancorata a una stringa vuota
                # o piu' corta di MINLEN, che e' come sono scritte le nostre
                # note sui titoli. Si riaggancia al contesto che la precedeva.
                if last_end is not None and a is None:
                    res = res[:last_end] + n["text"] + res[last_end:]
                    last_end += len(n["text"]); placed += 1; continue
                pos = context_place(res, n["before"])
                if pos < 0:
                    orphans.append(("(contesto non ritrovato)", n["name"])); continue
                res = res[:pos] + n["text"] + res[pos:]
                last_end = pos + len(n["text"]); placed += 1; continue
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
    if "--check-table" in sys.argv:
        sys.exit(0 if check_table() else 1)
    sys.exit(run("--apply" in sys.argv))
