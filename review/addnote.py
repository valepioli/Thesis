#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Inserimento assistito di un'annotazione nel testo annotato.

L'inserimento manuale, effettuato mediante script estemporanei, ha dato luogo
in piu' occasioni a documenti non compilabili e, in un caso, alla cancellazione
di sei frasi dell'autrice. In ciascun caso il difetto non risiedeva nel
contenuto dell'annotazione bensi' nel punto di inserimento, e in ciascun caso
l'informazione necessaria a rilevarlo era gia' disponibile.

La circostanza che accomuna tali episodi merita di essere esplicitata. I dati
numerici di un'annotazione vanno misurati sul testo dell'autrice, privo di
annotazioni (si veda `measure.py`). L'inserimento avviene invece sul file
annotato, ove la frase cui ci si intende ancorare puo' gia' costituire l'ancora
di un'annotazione precedente. La verifica `s.count(frase) == 1` non e'
sufficiente a rilevarlo: la frase e' effettivamente presente una sola volta,
ma all'interno di `\CCerr{...}`.

Le prime tre protezioni sono importate da `reanchor.py`, al fine di evitare la
duplicazione della medesima logica:

  * inserimento in una `\caption`;
  * inserimento negli argomenti di un'altra annotazione;
  * ancore di estensione inferiore a MINLEN caratteri.

Le rimanenti sono proprie del modulo, ciascuna derivante da un difetto
riscontrato:

  * ancora ambigua: qualora ricorra piu' di una volta l'inserimento e'
    respinto, anziche' selezionare la prima occorrenza;
  * annotazione gia' presente sulla medesima frase: si raccomanda in tal caso
    di integrare quella esistente anziche' affiancarne una seconda;
  * ancora in modo matematico: all'interno di `equation` o `$...$` le macro di
    annotazione non operano e LaTeX perde l'oggetto flottante;
  * argomento-ancora difforme dalla frase: e' la protezione di maggiore
    rilievo, in quanto il suo mancato intervento comporta la cancellazione del
    testo dell'autrice anziche' la sola impossibilita' di compilazione, dato
    che `place()` sostituisce la frase con il testo ricevuto;
  * riga vuota nel corpo: un `\par` nell'argomento compromette la scrittura
    degli elenchi (`\notelistentry`).

Nessuna scrittura viene effettuata se anche un solo inserimento non risulta
ammissibile, cosi' da non lasciare il file in stato intermedio.

    import sys; sys.path.insert(0, "review")
    from addnote import place
    place(percorso, [(frase, annotazione, "etichetta")])

Le annotazioni vanno composte per concatenazione e non mediante interpolazione
di stringhe: i corpi contengono frequentemente il carattere di percentuale in
forma protetta, che interferisce con la formattazione. Eseguito senza
argomenti, il modulo verifica automaticamente ciascuna protezione su testo di
prova.
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reanchor import forbidden_spans, MINLEN, NOTE, grp, ARGS, ANCHOR

MATH_ENVS = ("equation", "align", "gather", "multline", "eqnarray")


def math_spans(t):
    r"""Intervalli in modo matematico, dove una nota non puo' stare."""
    bad = []
    for env in MATH_ENVS:
        for star in ("", r"\*"):
            for m in re.finditer(r"\\begin\{" + env + star + r"\}", t):
                end = re.search(r"\\end\{" + env + star + r"\}", t[m.start():])
                if end:
                    bad.append((m.start(), m.start() + end.end()))
    for m in re.finditer(r"(?<!\\)\$[^$]*(?<!\\)\$", t, re.S):
        bad.append((m.start(), m.end()))
    for m in re.finditer(r"\\\[.*?\\\]", t, re.S):
        bad.append((m.start(), m.end()))
    return bad


def existing_note_containing(src, frase):
    """Se `frase` e' gia' dentro l'ancora o il corpo di una nota, dice quale."""
    for m in re.finditer(NOTE, src):
        try:
            a, j = grp(src, m.end() - 1)
            b, _ = grp(src, j)
        except IndexError:
            continue
        if frase in a:
            return m.group(0)[1:-1], "nell'ancora"
        if frase in b:
            return m.group(0)[1:-1], "nel corpo"
    return None


def anchor_mismatch(nota, frase):
    r"""Per le macro ancorate, l'argomento-ancora deve essere ESATTAMENTE la frase."""
    # La macro puo' non essere all'inizio: per una nota NON ancorata si passa
    # la frase seguita dalla macro, perche' place() sostituisce la frase con
    # tutto il testo che gli si da'.
    m = re.search(NOTE, nota)
    if not m:
        return "il testo non contiene nessuna macro di nota"
    name = m.group(0)[1:-1]
    idx = ANCHOR.get(name)
    if idx is None:
        # Nota NON ancorata (CCgen, CCthesis, CCnote): non porta la frase in un
        # argomento, ma place() sostituisce comunque la frase con il testo che
        # gli passi, quindi il testo deve CONTENERE la frase o la si cancella.
        # Si passa quindi frase + macro, non la sola macro.
        if frase not in nota:
            return ("\\%s non e' ancorata, quindi il testo che passi sostituisce "
                    "la frase: deve contenerla. Passa la frase seguita dalla macro"
                    % name)
        return None
    t = nota
    args, j = [], m.end() - 1
    try:
        for _ in range(ARGS[name]):
            g, j = grp(t, j)
            args.append(g)
    except IndexError:
        return "gli argomenti di \\%s non si chiudono" % name
    if args[idx] != frase:
        return ("l'argomento ancora di \\%s non e' la frase (e' %r): "
                "inserendola cancellerei il testo della studentessa"
                % (name, args[idx][:40]))
    return None


def place(path, jobs, verbose=True):
    src = io.open(path, encoding="utf-8").read()
    errori, fatte = [], 0
    for frase, nota, tag in jobs:
        if len(frase.strip()) < MINLEN:
            errori.append("%s: ancora troppo corta (%d caratteri)" % (tag, len(frase.strip())))
            continue
        n = src.count(frase)
        if n == 0:
            errori.append("%s: ancora non trovata" % tag); continue
        if n > 1:
            errori.append("%s: ancora ambigua, compare %d volte -- allungala" % (tag, n)); continue
        if re.search(r"\n[ \t]*\n", nota):
            errori.append("%s: il testo della nota contiene una riga vuota. Un \\par "
                          "dentro l'argomento rompe la scrittura delle liste "
                          "(\\notelistentry); usa ~--- per separare i capoversi" % tag)
            continue
        bad = anchor_mismatch(nota, frase)
        if bad:
            errori.append("%s: %s" % (tag, bad)); continue
        gia = existing_note_containing(src, frase)
        if gia:
            errori.append("%s: la frase e' gia' %s di \\%s -- arricchisci quella nota "
                          "invece di aggiungerne una seconda" % (tag, gia[1], gia[0]))
            continue
        i = src.find(frase)
        if any(a <= i < b for a, b in forbidden_spans(src)):
            errori.append("%s: cade dentro una \\caption" % tag); continue
        if any(a <= i < b for a, b in math_spans(src)):
            errori.append("%s: l'ancora e' in modo matematico (equation o $...$); "
                          "aggancia una frase di testo vicina" % tag); continue
        src = src[:i] + nota + src[i + len(frase):]
        fatte += 1
        if verbose:
            print("  ok   %s" % tag)
    if errori:
        print("NON HO SCRITTO NIENTE. Problemi:")
        for e in errori:
            print("   -", e)
        return 0
    io.open(path, "w", encoding="utf-8").write(src)
    if verbose:
        print("\ninserite %d note in %s" % (fatte, os.path.basename(path)))
    return fatte


def _run_case(nome, testo, frase, nota, atteso):
    """Fa scattare una protezione e verifica che rifiuti E che non scriva."""
    import tempfile, contextlib
    f = tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False, encoding="utf-8")
    f.write(testo); f.close()
    prima = io.open(f.name, encoding="utf-8").read()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = place(f.name, [(frase, nota, "prova")], verbose=False)
    dopo = io.open(f.name, encoding="utf-8").read()
    ok = (r == 0) and (dopo == prima) and (atteso in buf.getvalue())
    print("  %-24s %s" % (nome, "ok" if ok else "FALLITO -> " + buf.getvalue().strip()[:70]))
    os.unlink(f.name)
    return 0 if ok else 1


def _selftest():
    N = lambda f: r"\CCn{" + f + "}{commento}"
    casi = [
        ("nota gia' esistente", r"\CCn{la frase}{commento}", "la frase", N("la frase"), "gia' nell'ancora"),
        ("dentro una didascalia", r"\caption{la frase}", "la frase", N("la frase"), "caption"),
        ("ancora ambigua", "la frase e poi la frase", "la frase", N("la frase"), "ambigua"),
        ("ancora assente", "tutt'altro testo", "la frase", N("la frase"), "non trovata"),
        ("ancora corta", "a, b", ",", N(","), "troppo corta"),
        ("dentro un'equazione", r"x \begin{equation} la frase \end{equation} y",
         "la frase", N("la frase"), "modo matematico"),
        ("dentro $...$", "testo $con la frase dentro$ altro", "la frase", N("la frase"), "modo matematico"),
        ("ancora non nella nota", "testo con la frase dentro", "la frase",
         r"\CCn{%s}{commento}", "cancellerei il testo"),
        ("riga vuota nel corpo", "testo con la frase dentro", "la frase",
         "\\CCn{la frase}{primo capoverso\n\nsecondo}", "riga vuota"),
        ("non ancorata senza frase", "testo con la frase dentro", "la frase",
         r"\CCthesis{titolo}{corpo}", "deve contenerla"),
    ]
    ko = sum(_run_case(*c) for c in casi)
    # e un caso che deve invece riuscire
    import tempfile
    f = tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False, encoding="utf-8")
    f.write("testo normale con la frase dentro"); f.close()
    r = place(f.name, [("la frase", N("la frase"), "prova")], verbose=False)
    ok = r == 1 and r"\CCn{la frase}" in io.open(f.name, encoding="utf-8").read()
    print("  %-24s %s" % ("inserimento valido", "ok" if ok else "FALLITO"))
    ko += 0 if ok else 1
    os.unlink(f.name)
    return ko


if __name__ == "__main__":
    print("Verifica delle protezioni di addnote.py:")
    sys.exit(1 if _selftest() else 0)
